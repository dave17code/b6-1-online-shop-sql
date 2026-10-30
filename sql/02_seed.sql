-- sqlite
-- 10 customers, 10 products, 10 orders, 12 order items.
-- Insert parents before children. Customer names remain in Korean.
-- Customers 9 and 10 have no orders. Products 9 and 10 have no sales.
-- SQLite-specific: enable foreign keys for this connection.
PRAGMA foreign_keys = ON;

INSERT INTO customers (customer_id, customer_name, email) VALUES
    (1, '김가람', 'user1@shop.test'),
    (2, '이나래', 'user2@shop.test'),
    (3, '박다온', 'user3@shop.test'),
    (4, '최라온', 'user4@shop.test'),
    (5, '정마루', 'user5@shop.test'),
    (6, '강바다', 'user6@shop.test'),
    (7, '윤보라', 'user7@shop.test'),
    (8, '임아람', 'user8@shop.test'),
    (9, '한이든', 'user9@shop.test'),
    (10, '오하늘', 'user10@shop.test');

INSERT INTO products (product_id, product_name, price) VALUES
    (1, 'Pencil', 1000),
    (2, 'Notebook', 2000),
    (3, 'Eraser', 500),
    (4, 'Pen', 1500),
    (5, 'Ruler', 1000),
    (6, 'Pen Case', 5000),
    (7, 'Scissors', 3000),
    (8, 'Glue', 1000),
    (9, 'Colored Pencil', 4000),
    (10, 'Tape', 2500);

INSERT INTO orders (order_id, customer_id, order_date) VALUES
    (1, 1, '2026-01-01'),
    (2, 2, '2026-01-02'),
    (3, 3, '2026-01-03'),
    (4, 1, '2026-01-04'),
    (5, 4, '2026-01-05'),
    (6, 5, '2026-01-06'),
    (7, 2, '2026-01-07'),
    (8, 6, '2026-01-08'),
    (9, 7, '2026-01-09'),
    (10, 8, '2026-01-10');

INSERT INTO order_items
    (order_item_id, order_id, product_id, quantity)
VALUES
    (1, 1, 1, 2),
    (2, 1, 2, 1),
    (3, 2, 3, 2),
    (4, 2, 4, 2),
    (5, 3, 1, 1),
    (6, 4, 5, 1),
    (7, 5, 6, 1),
    (8, 6, 7, 1),
    (9, 7, 2, 2),
    (10, 8, 8, 3),
    (11, 9, 3, 2),
    (12, 10, 8, 1);
