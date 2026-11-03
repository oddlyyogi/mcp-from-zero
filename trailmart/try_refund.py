import asyncio, os
from mcp import Client, StdioServerParameters
from mcp.client.stdio import get_default_environment
from mcp.types import ElicitResult

env = {**get_default_environment(),
       "TRAILMART_READER_DSN": os.environ["TRAILMART_READER_DSN"],
       "TRAILMART_REFUNDS_DSN": os.environ["TRAILMART_REFUNDS_DSN"]}
server = StdioServerParameters(command="uv", args=["run", "server.py"], env=env)

async def ask_human(ctx, params):
    reply = input(f"[agent] {params.message} (y/n) ")
    print(reply)
    return ElicitResult(action="accept", content={"confirm": reply == "y"})

async def main():
    async with Client(server, elicitation_callback=ask_human) as mcp:
        r = await mcp.call_tool("start_refund", {"order_id": 1042, "amount": 28.0,
                                                 "reason": "socks wrong size"})
        print(r.content[0].text)

asyncio.run(main())
