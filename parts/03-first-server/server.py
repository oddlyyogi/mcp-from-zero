from mcp.server import MCPServer

mcp = MCPServer("TrailMart Support")

@mcp.tool()
def get_order(order_id: int) -> str:
    """Look up one order: status, items, carrier and expected delivery date."""
    return f"Order {order_id}: shipped"

if __name__ == "__main__":
    mcp.run()
