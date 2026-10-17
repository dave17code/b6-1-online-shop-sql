-- B6-1 | 핵심 쿼리 Q01~Q15
-- 기본 4 / 조인 4 / 집계 3 / 서브쿼리 1 / UPDATE 1 / DELETE 1 / 인덱스 1
-- Q13, Q14는 실제 변경 전/후를 조회한 다음 ROLLBACK하여 반복 실습합니다.
-- 전후 확인용 SELECT, 트랜잭션, 인덱스 확인 명령은 15개 외의 보조 문장입니다.
-- Q15의 인덱스는 생성 후 유지됩니다. IF NOT EXISTS로 재실행할 수 있습니다.
-- SQLite 전용: PRAGMA, CREATE INDEX IF NOT EXISTS, EXPLAIN QUERY PLAN.
-- LIMIT는 SQLite/MySQL/PostgreSQL에서 지원하는 행 수 제한 문법입니다.
PRAGMA foreign_keys = ON;

-- Q01 | BASIC | 50,000원 이상 상품을 낮은 가격부터 조회한다.
SELECT id, name, price
FROM product
WHERE price >= 50000
ORDER BY price ASC, id ASC;

-- Q02 | BASIC | 20,000원 이상 50,000원 이하의 상품을 조회한다.
SELECT id, name, price
FROM product
WHERE price BETWEEN 20000 AND 50000
ORDER BY id;

-- Q03 | BASIC | 상품명에 USB가 포함된 상품을 검색한다.
SELECT id, name, price
FROM product
WHERE name LIKE '%USB%'
ORDER BY id;

-- Q04 | BASIC | 가장 최근 주문 5건을 조회한다.
-- 동일 시각에도 순서가 일정하도록 id를 두 번째 정렬 기준으로 둡니다.
SELECT id, member_id, ordered_at
FROM orders
ORDER BY ordered_at DESC, id DESC
LIMIT 5;

-- Q05 | JOIN | 주문과 주문한 회원의 이름을 함께 조회한다.
SELECT o.id AS order_id, m.name AS member_name, o.ordered_at
FROM orders AS o
INNER JOIN member AS m ON m.id = o.member_id
ORDER BY o.id;

-- Q06 | JOIN | 주문 1번의 상품명, 수량, 당시 단가와 항목 금액을 조회한다.
-- 금액은 현재 product.price가 아닌 order_item.unit_price로 계산합니다.
SELECT oi.order_id, p.name AS product_name, oi.quantity, oi.unit_price,
       oi.quantity * oi.unit_price AS line_total_won
FROM order_item AS oi
INNER JOIN product AS p ON p.id = oi.product_id
WHERE oi.order_id = 1
ORDER BY oi.id;

-- Q07 | JOIN | 네 테이블을 연결하여 회원 1번의 구매 내역을 조회한다.
SELECT m.name AS member_name, o.id AS order_id, o.ordered_at,
       p.name AS product_name, oi.quantity, oi.unit_price
FROM member AS m
INNER JOIN orders AS o ON o.member_id = m.id
INNER JOIN order_item AS oi ON oi.order_id = o.id
INNER JOIN product AS p ON p.id = oi.product_id
WHERE m.id = 1
ORDER BY o.id, oi.id;

-- Q08 | JOIN | 주문이 없는 회원도 포함하여 전체 회원의 주문 내역을 조회한다.
-- 주문이 없는 회원 9, 10의 주문 컬럼에는 NULL이 표시됩니다.
SELECT m.id AS member_id, m.name AS member_name,
       o.id AS order_id, o.ordered_at
FROM member AS m
LEFT JOIN orders AS o ON o.member_id = m.id
ORDER BY m.id, o.id;

-- Q09 | AGGREGATE | 회원별 주문 횟수를 구하고 많이 주문한 순서로 정렬한다.
-- COUNT(o.id)는 NULL을 제외하므로 주문이 없는 회원의 횟수는 0입니다.
-- 상세까지 JOIN하면 주문이 반복되므로 여기서는 orders까지만 연결합니다.
SELECT m.id AS member_id, m.name AS member_name,
       COUNT(o.id) AS order_count
FROM member AS m
LEFT JOIN orders AS o ON o.member_id = m.id
GROUP BY m.id, m.name
ORDER BY order_count DESC, m.id ASC;

-- Q10 | AGGREGATE | 상품별 누적 판매 수량과 주문 금액 합계를 구한다.
-- COALESCE는 판매가 없는 상품의 SUM 결과 NULL을 0으로 표시합니다.
SELECT p.id AS product_id, p.name AS product_name,
       COALESCE(SUM(oi.quantity), 0) AS total_quantity,
       COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_amount_won
FROM product AS p
LEFT JOIN order_item AS oi ON oi.product_id = p.id
GROUP BY p.id, p.name
ORDER BY total_amount_won DESC, p.id ASC;

-- Q11 | AGGREGATE | 판매된 상품별 주문 상세 한 건당 평균 구매 수량을 구한다.
-- 평균의 단위는 '주문 상세 한 건'이며, 회원별 평균이나 전체 판매량이 아닙니다.
SELECT p.id AS product_id, p.name AS product_name,
       COUNT(oi.id) AS item_count,
       ROUND(AVG(oi.quantity), 2) AS avg_quantity_per_item
FROM product AS p
INNER JOIN order_item AS oi ON oi.product_id = p.id
GROUP BY p.id, p.name
ORDER BY p.id;

-- Q12 | SUBQUERY | 전체 상품의 평균 현재 가격보다 비싼 상품을 조회한다.
SELECT id, name, price
FROM product
WHERE price > (SELECT AVG(price) FROM product)
ORDER BY price DESC, id ASC;

-- Q13 | UPDATE | 마우스 현재 가격을 수정하고 과거 주문 단가가 유지됨을 확인한다.
-- 반복 시연: BEGIN -> 변경 전 조회 -> UPDATE -> 변경 후 조회 -> ROLLBACK.
BEGIN;
SELECT 'before' AS stage, p.price AS current_price,
       oi.unit_price AS ordered_unit_price, oi.quantity * oi.unit_price AS line_total_won
FROM product AS p
INNER JOIN order_item AS oi ON oi.product_id = p.id
WHERE p.id = 2 AND oi.order_id = 1;

UPDATE product
SET price = 35000
WHERE id = 2;

SELECT 'after' AS stage, p.price AS current_price,
       oi.unit_price AS ordered_unit_price, oi.quantity * oi.unit_price AS line_total_won
FROM product AS p
INNER JOIN order_item AS oi ON oi.product_id = p.id
WHERE p.id = 2 AND oi.order_id = 1;
ROLLBACK;
SELECT 'restored' AS stage, id, price FROM product WHERE id = 2;

-- Q14 | DELETE | 주문 상세 40번을 잘못 입력했다고 가정하여 삭제하고 결과를 확인한다.
-- 주문 20번의 다른 상세는 남습니다. 마지막에는 원래 40행으로 복원합니다.
BEGIN;
SELECT 'before' AS stage, id, order_id, product_id, quantity
FROM order_item WHERE id = 40;

DELETE FROM order_item WHERE id = 40;

SELECT 'after' AS stage, COUNT(*) AS target_rows
FROM order_item WHERE id = 40;
SELECT 'after' AS stage, COUNT(*) AS all_item_rows FROM order_item;
ROLLBACK;
SELECT 'restored' AS stage, id, order_id, product_id, quantity
FROM order_item WHERE id = 40;

-- Q15 | INDEX | 특정 회원의 주문 검색에 사용할 인덱스를 생성한다.
-- 적용 이유: orders.member_id를 조건으로 주문을 찾거나 회원과 연결할 때 활용한다.
-- 아래 생성/확인 문법은 SQLite 기준입니다. 인덱스는 데이터와 별도로 유지됩니다.
CREATE INDEX IF NOT EXISTS idx_orders_member_id ON orders(member_id);
PRAGMA index_list('orders');
PRAGMA index_info('idx_orders_member_id');
EXPLAIN QUERY PLAN
SELECT id, ordered_at FROM orders WHERE member_id = 1;
