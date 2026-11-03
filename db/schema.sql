-- TrailMart support-desk schema (PostgreSQL 18)
DROP SCHEMA IF EXISTS shop CASCADE;
CREATE SCHEMA shop;
SET search_path = shop;

CREATE TABLE customers (
  id         int PRIMARY KEY,
  name       text NOT NULL,
  email      text NOT NULL UNIQUE,
  city       text NOT NULL
);

CREATE TABLE products (
  id          int PRIMARY KEY,
  sku         text NOT NULL UNIQUE,
  name        text NOT NULL,
  category    text NOT NULL,
  price_cents int  NOT NULL CHECK (price_cents > 0),
  stock       int  NOT NULL CHECK (stock >= 0)
);

CREATE TABLE orders (
  id          int PRIMARY KEY,
  customer_id int NOT NULL REFERENCES customers,
  placed_at   timestamptz NOT NULL,
  status      text NOT NULL CHECK (status IN ('placed','shipped','delivered','cancelled'))
);

CREATE TABLE order_items (
  order_id         int NOT NULL REFERENCES orders,
  product_id       int NOT NULL REFERENCES products,
  qty              int NOT NULL CHECK (qty > 0),
  unit_price_cents int NOT NULL,
  PRIMARY KEY (order_id, product_id)
);

CREATE TABLE shipments (
  order_id     int PRIMARY KEY REFERENCES orders,
  carrier      text NOT NULL,
  tracking     text NOT NULL,
  shipped_at   timestamptz NOT NULL,
  eta          date NOT NULL,
  delivered_at timestamptz
);

CREATE TABLE refunds (
  id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id        int  NOT NULL REFERENCES orders,
  amount_cents    int  NOT NULL CHECK (amount_cents > 0),
  reason          text NOT NULL,
  idempotency_key text NOT NULL UNIQUE,
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE trails (
  id   int PRIMARY KEY,
  name text NOT NULL,
  lat  numeric(8,5) NOT NULL,
  lon  numeric(8,5) NOT NULL
);
