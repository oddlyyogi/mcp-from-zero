import os
from datetime import date

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

mcp = MCPServer("TrailMart Support")

reader = ConnectionPool(os.environ["TRAILMART_READER_DSN"], open=True,
                        kwargs={"row_factory": dict_row})

class Product(BaseModel):
    sku: str
    name: str
    price: float
    in_stock: int


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def find_products(query: str, in_stock_only: bool = True) -> list[Product]:
    """Search TrailMart products by name or category, for example 'boots' or 'tents'."""
    with reader.connection() as conn:
        rows = conn.execute(
            """SELECT sku, name, price_cents / 100.0 AS price, stock AS in_stock
               FROM shop.products
               WHERE (name ILIKE %(q)s OR category ILIKE %(q)s)
                 AND (stock > 0 OR NOT %(only)s)
               ORDER BY name""",
            {"q": f"%{query}%", "only": in_stock_only},
        ).fetchall()
    return [Product(**r) for r in rows]


class OrderLine(BaseModel):
    product: str
    qty: int
    unit_price: float

class Order(BaseModel):
    id: int
    customer: str
    status: str
    items: list[OrderLine]
    carrier: str | None
    eta: date | None

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def get_order(order_id: int) -> Order:
    """Look up one order: status, items, carrier and expected delivery date."""
    with reader.connection() as conn:
        head = conn.execute(
            """SELECT o.id, c.name AS customer, o.status, s.carrier, s.eta
               FROM shop.orders o
               JOIN shop.customers c ON c.id = o.customer_id
               LEFT JOIN shop.shipments s ON s.order_id = o.id
               WHERE o.id = %s""",
            (order_id,),
        ).fetchone()
        if head is None:
            raise ToolError(f"No order with id {order_id}")
        items = conn.execute(
            """SELECT p.name AS product, i.qty, i.unit_price_cents / 100.0 AS unit_price
               FROM shop.order_items i JOIN shop.products p ON p.id = i.product_id
               WHERE i.order_id = %s ORDER BY p.name""",
            (order_id,),
        ).fetchall()
    return Order(**head, items=[OrderLine(**i) for i in items])

if __name__ == "__main__":
    try:
        mcp.run()
    finally:
        reader.close()
