CREATE ROLE tm_reader LOGIN PASSWORD 'reader-local-only';
GRANT USAGE ON SCHEMA shop TO tm_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA shop TO tm_reader;

CREATE ROLE tm_refunds LOGIN PASSWORD 'refunds-local-only';
GRANT USAGE ON SCHEMA shop TO tm_refunds;
GRANT SELECT ON shop.orders, shop.order_items, shop.refunds TO tm_refunds;
GRANT INSERT ON shop.refunds TO tm_refunds;
