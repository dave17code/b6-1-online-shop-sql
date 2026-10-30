-- sqlite
-- B6-1 | Type and execute Q01 through Q15 one block at a time.
-- 4 basic queries, 4 joins, 3 aggregates, 1 subquery, 1 update, 1 delete, 1 index.
-- UPDATE and DELETE persist. Run 04_reset.sql after practice.
-- The SELECT statements after changes are supporting result checks.
PRAGMA foreign_keys = ON;

-- Q01 | BASIC | List products priced at least 2000 KRW from lowest to highest.
SELECT product_id, product_name, price
FROM products
WHERE price >= 2000
ORDER BY price, product_id;

-- Q02 | BASIC | List products priced between 1000 and 2000 KRW.
SELECT product_id, product_name, price
FROM products
WHERE price BETWEEN 1000 AND 2000
ORDER BY product_id;

-- Q03 | BASIC | Find product names containing Pencil.
SELECT product_id, product_name, price
FROM products
WHERE product_name LIKE '%Pencil%'
ORDER BY product_id;

-- Q04 | BASIC | List the five most recent orders.
-- LIMIT is supported by SQLite, MySQL, and PostgreSQL.
SELECT order_id, customer_id, order_date
FROM orders
ORDER BY order_date DESC, order_id DESC
LIMIT 5;

-- Q05 | JOIN | Show each order with its customer name.
-- USING (customer_id) matches equal customer_id values in both tables.
SELECT order_id, customer_name, order_date
FROM orders
INNER JOIN customers USING (customer_id)
ORDER BY order_id;

-- Q06 | JOIN | Show products and item totals for order 1.
SELECT product_name, quantity, price, quantity * price AS item_total
FROM order_items
INNER JOIN products USING (product_id)
WHERE order_id = 1
ORDER BY order_item_id;

-- Q07 | JOIN | Join four tables to show purchases by customer 1.
SELECT customer_name, order_id, order_date, product_name, quantity, price
FROM customers
INNER JOIN orders USING (customer_id)
INNER JOIN order_items USING (order_id)
INNER JOIN products USING (product_id)
WHERE customer_id = 1
ORDER BY order_id, order_item_id;

-- Q08 | JOIN | Include customers who have never placed an order.
SELECT customer_id, customer_name, order_id
FROM customers
LEFT JOIN orders USING (customer_id)
ORDER BY customer_id, order_id;

-- Q09 | AGGREGATE | Count orders per customer, including zero orders.
-- COUNT(order_id) ignores NULL, so a customer without orders has a count of zero.
SELECT customer_name, COUNT(order_id) AS order_count
FROM customers
LEFT JOIN orders USING (customer_id)
GROUP BY customer_id, customer_name
ORDER BY order_count DESC, customer_id;

-- Q10 | AGGREGATE | Add quantities and sales amounts for each sold product.
SELECT product_name, SUM(quantity) AS total_quantity,
       SUM(quantity * price) AS total_amount
FROM products
INNER JOIN order_items USING (product_id)
GROUP BY product_id, product_name
ORDER BY total_amount DESC, product_id;

-- Q11 | AGGREGATE | Find the average quantity per order-item row for each sold product.
SELECT product_name, AVG(quantity) AS average_quantity
FROM products
INNER JOIN order_items USING (product_id)
GROUP BY product_id, product_name
ORDER BY product_id;

-- Q12 | SUBQUERY | Find products priced above the average product price.
SELECT product_id, product_name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products)
ORDER BY price DESC, product_id;

-- Q13 | UPDATE | Change the price of Pencil from 1000 to 1200 KRW.
-- SQLite-specific: enable foreign keys for this selected block. Changes are saved.
PRAGMA foreign_keys = ON;
UPDATE products
SET price = 1200
WHERE product_id = 1;

SELECT product_id, product_name, price
FROM products
WHERE product_id = 1;

-- Q14 | DELETE | Delete the incorrect order-item row numbered 4.
-- SQLite-specific: enable foreign keys for this selected block. Changes are saved.
PRAGMA foreign_keys = ON;
DELETE FROM order_items
WHERE order_item_id = 4;

SELECT COUNT(*) AS remaining_items
FROM order_items;

-- Q15 | INDEX | Create an index for looking up orders by customer_id.
-- Reason: support customer_id filters and joins between orders and customers.
-- SQLite-specific: sqlite_master is used only to confirm the index.
CREATE INDEX IF NOT EXISTS orders_customer_id_index ON orders(customer_id);

SELECT name AS index_name, tbl_name AS table_name
FROM sqlite_master
WHERE name = 'orders_customer_id_index';
