import os
from datetime import date

import httpx

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


@mcp.resource("policy://returns", mime_type="text/markdown")
def returns_policy() -> str:
    """TrailMart's return and refund policy."""
    return (
        "# TrailMart returns\n"
        "- Unused items: full refund within 30 days of delivery.\n"
        "- Refunds go back to the original payment method.\n"
        "- A support agent must confirm every refund."
    )


@mcp.resource("order://{order_id}")
def order_summary(order_id: int) -> str:
    """One order as a short text summary."""
    o = get_order(order_id)
    lines = ", ".join(f"{l.qty} x {l.product}" for l in o.items)
    return (f"Order {o.id} for {o.customer}: {o.status}. {lines}. "
            f"Carrier {o.carrier}, ETA {o.eta}.")


@mcp.prompt()
def late_delivery_reply(customer: str, order_id: int) -> str:
    """Draft a friendly reply to a customer worried about a late delivery."""
    return (f"Use get_order to check order {order_id}, "
            f"then write a short, friendly reply to {customer}. "
            "Give the real expected delivery date. "
            "Do not promise anything the data does not show.")


class TrailWeather(BaseModel):
    trail: str
    day: date
    rain_mm: float
    rain_chance_percent: int
    low_c: float
    high_c: float

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
def check_trail_weather(trail: str, day: date) -> TrailWeather:
    """Forecast for a TrailMart trail on one day (up to 16 days ahead)."""
    with reader.connection() as conn:
        t = conn.execute("SELECT name, lat, lon FROM shop.trails WHERE name ILIKE %s",
                         (f"%{trail}%",)).fetchone()
    if t is None:
        raise ToolError(f"Unknown trail: {trail}")
    resp = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": float(t["lat"]), "longitude": float(t["lon"]),
            "timezone": "auto",
            "daily": "precipitation_sum,precipitation_probability_max,"
                     "temperature_2m_min,temperature_2m_max",
            "start_date": day.isoformat(), "end_date": day.isoformat(),
        },
        timeout=10,
    )
    resp.raise_for_status()
    d = resp.json()["daily"]
    return TrailWeather(trail=t["name"], day=day, rain_mm=d["precipitation_sum"][0],
                        rain_chance_percent=d["precipitation_probability_max"][0],
                        low_c=d["temperature_2m_min"][0],
                        high_c=d["temperature_2m_max"][0])

if __name__ == "__main__":
    try:
        mcp.run()
    finally:
        reader.close()
