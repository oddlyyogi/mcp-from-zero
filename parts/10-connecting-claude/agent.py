import asyncio
import os
import sys
from datetime import date

import anthropic
from mcp import Client, StdioServerParameters
from mcp.client.stdio import get_default_environment
from mcp.types import ElicitResult

claude = anthropic.AsyncAnthropic()
env = {**get_default_environment(),
       "TRAILMART_READER_DSN": os.environ["TRAILMART_READER_DSN"],
       "TRAILMART_REFUNDS_DSN": os.environ["TRAILMART_REFUNDS_DSN"]}
server = StdioServerParameters(command="uv", args=["run", "server.py"], env=env)
SYSTEM = (f"You are TrailMart's support assistant. "
          f"Today is {date.today():%A %Y-%m-%d}. "
          "Use the tools; never guess order data.")

async def ask_human(ctx, params):
    reply = input(f"[agent] {params.message} (y/n) ")
    print(reply)
    return ElicitResult(action="accept", content={"confirm": reply == "y"})

async def main(question: str):
    async with Client(server, elicitation_callback=ask_human) as mcp:
        listed = await mcp.list_tools()
        tools = [{"name": t.name, "description": t.description,
                  "input_schema": t.input_schema} for t in listed.tools]
        messages = [{"role": "user", "content": question}]
        while True:
            reply = await claude.messages.create(
                model="claude-opus-5-5", max_tokens=4000, system=SYSTEM,
                tools=tools, messages=messages)
            messages.append({"role": "assistant", "content": reply.content})
            calls = [b for b in reply.content if b.type == "tool_use"]
            if not calls:
                break
            results = []
            for call in calls:
                print(f"-> {call.name}({call.input})")
                out = await mcp.call_tool(call.name, call.input)
                text = "\n".join(c.text for c in out.content if c.type == "text")
                results.append({"type": "tool_result", "tool_use_id": call.id,
                                "content": text, "is_error": out.is_error})
            messages.append({"role": "user", "content": results})
        print("\n" + "".join(b.text for b in reply.content if b.type == "text"))

asyncio.run(main(sys.argv[1]))
