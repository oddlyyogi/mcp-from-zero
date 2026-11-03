import pytest
from mcp import Client
from mcp.types import ElicitResult

import server

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
def close_pools():
    yield
    server.reader.close()
    server.refunder.close()

@pytest.mark.anyio
async def test_unknown_order_is_a_tool_error():
    async with Client(server.mcp) as c:
        r = await c.call_tool("get_order", {"order_id": 99})
    assert r.is_error

@pytest.mark.anyio
async def test_sql_injection_is_just_text():
    async with Client(server.mcp) as c:
        r = await c.call_tool("find_products",
                              {"query": "x'; DROP TABLE shop.orders; --"})
    assert r.structured_content == {"result": []}

async def decline(ctx, params):
    return ElicitResult(action="decline")

@pytest.mark.anyio
async def test_refund_needs_a_human_yes():
    async with Client(server.mcp, elicitation_callback=decline) as c:
        r = await c.call_tool("start_refund",
                              {"order_id": 1043, "amount": 10, "reason": "test"})
    assert "not made" in r.content[0].text
