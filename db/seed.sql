SET search_path = shop;
SELECT setseed(0.42);

INSERT INTO products VALUES
 (1,'BT-ALP-01','Alpine Trail Boots','footwear',18900,14),
 (2,'BT-RDG-02','Ridge Runner Trail Shoes','footwear',12900,0),
 (3,'JK-STM-01','Storm Shell Rain Jacket','jackets',21900,7),
 (4,'JK-PUF-02','Summit Puffer Jacket','jackets',24900,3),
 (5,'TN-2P-01','Two-Person Backpacking Tent','tents',32900,5),
 (6,'TN-1P-02','Solo Ultralight Tent','tents',27900,0),
 (7,'SB-20F-01','Down Sleeping Bag 20F','sleep',29900,9),
 (8,'SP-INS-02','Insulated Sleeping Pad','sleep',13900,21),
 (9,'BP-45L-01','Trailhead 45L Backpack','packs',17900,11),
 (10,'BP-22L-02','Day Hiker 22L Pack','packs',8900,30),
 (11,'HL-400-01','Headlamp 400 Lumen','lighting',4900,52),
 (12,'WB-1L-01','Insulated Water Bottle 1L','hydration',3400,80),
 (13,'FL-SQZ-02','Squeeze Water Filter','hydration',4500,0),
 (14,'TP-CRB-01','Carbon Trekking Poles','accessories',15900,6),
 (15,'SK-MER-01','Merino Hiking Socks (2 pack)','accessories',2800,120),
 (16,'ST-CAN-01','Canister Camp Stove','cooking',7900,18);

INSERT INTO customers VALUES
 (1,'Maya Chen','maya.chen@example.com','Seattle'),
 (2,'Luis Ortega','luis.ortega@example.com','Denver'),
 (3,'Priya Nair','priya.nair@example.com','Vancouver'),
 (4,'Tom Becker','tom.becker@example.com','Portland'),
 (5,'Aisha Bello','aisha.bello@example.com','Calgary');
INSERT INTO customers
SELECT i, 'Customer ' || i, 'customer' || i || '@example.com',
       (ARRAY['Seattle','Denver','Vancouver','Portland','Calgary','Boise'])[1 + (i % 6)]
FROM generate_series(6, 300) AS i;

-- background orders 1001..1199, one or two items each
INSERT INTO orders
SELECT i, 1 + floor(random() * 300)::int,
       timestamptz '2026-08-01 09:00+00' + (i - 1001) * interval '7 hours',
       CASE WHEN i < 1180 THEN 'delivered' WHEN i < 1195 THEN 'shipped' ELSE 'placed' END
FROM generate_series(1001, 1199) AS i
WHERE i <> 1042;

INSERT INTO order_items
SELECT o.id, p.id, 1 + floor(random() * 2)::int, p.price_cents
FROM orders o
CROSS JOIN LATERAL (SELECT id, price_cents FROM products
                    WHERE id IN (1 + (o.id % 16), 1 + ((o.id * 7) % 16))) p;

-- the order from the customer's message
INSERT INTO orders VALUES (1042, 1, '2026-10-28 18:12+00', 'shipped');
INSERT INTO order_items VALUES (1042, 1, 1, 18900), (1042, 15, 2, 2800);

INSERT INTO shipments
SELECT o.id, (ARRAY['Canyon Post','Northline Freight'])[1 + o.id % 2], 'TM' || o.id || 'X',
       o.placed_at + interval '1 day', (o.placed_at + interval '5 days')::date,
       CASE WHEN o.status = 'delivered' THEN o.placed_at + interval '4 days' END
FROM orders o WHERE o.status IN ('shipped','delivered') AND o.id <> 1042;
INSERT INTO shipments VALUES (1042, 'Canyon Post', 'TM1042X', '2026-10-30 15:40+00', '2026-11-05', NULL);

INSERT INTO trails VALUES
 (1,'Skyline Trail, Mount Rainier',46.78590,-121.73530),
 (2,'Lake Agnes Trail, Banff',51.41670,-116.23850),
 (3,'Mist Trail, Yosemite',37.72720,-119.55600);
