-- B6-1 | 핵심 SQL 쿼리 15개 (Q01 ~ Q15)
-- 구성: 기본 조회 4개 / 조인 4개 / 집계 3개 / 서브쿼리 1개 / 수정 및 삭제 2개 / 인덱스 1개
-- [SQLite 전용 문법 안내]
-- PRAGMA foreign_keys = ON, CREATE INDEX IF NOT EXISTS, EXPLAIN QUERY PLAN은 SQLite 문법입니다.
-- Q13(UPDATE)과 Q14(DELETE)는 변경 전후를 확인한 뒤 ROLLBACK하여 언제든 반복 실행할 수 있습니다.

PRAGMA foreign_keys = ON;

-- Q01 | BASIC | 50,000원 이상 상품을 낮은 가격순으로 조회한다.
SELECT id, name, price
FROM product
WHERE price >= 50000
ORDER BY price ASC, id ASC;

-- Q02 | BASIC | 가격이 20,000원 이상 50,000원 이하인 상품을 조회한다.
SELECT id, name, price
FROM product
WHERE price BETWEEN 20000 AND 50000
ORDER BY id ASC;

-- Q03 | BASIC | 상품명에 'USB'가 포함된 상품을 검색한다.
SELECT id, name, price
FROM product
WHERE name LIKE '%USB%'
ORDER BY id ASC;

-- Q04 | BASIC | 가장 최근에 들어온 주문 5건을 조회한다.
SELECT id, member_id, ordered_at
FROM orders
ORDER BY ordered_at DESC, id DESC
LIMIT 5;

-- Q05 | JOIN | 주문 목록과 주문한 회원의 이름을 함께 조회한다.
SELECT o.id AS order_id, m.name AS member_name, o.ordered_at
FROM orders AS o
INNER JOIN member AS m ON m.id = o.member_id
ORDER BY o.id ASC;

-- Q06 | JOIN | 주문 1번에 담긴 상품명, 상품 가격, 주문 수량, 항목별 합계 금액을 조회한다.
SELECT oi.order_id, p.name AS product_name, p.price, oi.quantity,
       p.price * oi.quantity AS item_total_price
FROM order_item AS oi
INNER JOIN product AS p ON p.id = oi.product_id
WHERE oi.order_id = 1
ORDER BY oi.id ASC;

-- Q07 | JOIN | 4개 테이블을 모두 연결하여 1번 회원(김하늘)의 전체 구매 내역을 조회한다.
SELECT m.name AS member_name, o.id AS order_id, o.ordered_at,
       p.name AS product_name, p.price, oi.quantity
FROM member AS m
INNER JOIN orders AS o ON o.member_id = m.id
INNER JOIN order_item AS oi ON oi.order_id = o.id
INNER JOIN product AS p ON p.id = oi.product_id
WHERE m.id = 1
ORDER BY o.id ASC, oi.id ASC;

-- Q08 | JOIN | 주문 이력이 없는 회원까지 포함하여 전체 회원의 주문 내역을 조회한다.
SELECT m.id AS member_id, m.name AS member_name,
       o.id AS order_id, o.ordered_at
FROM member AS m
LEFT JOIN orders AS o ON o.member_id = m.id
ORDER BY m.id ASC, o.id ASC;

-- Q09 | AGGREGATE | 회원별 총 주문 횟수를 구하고 주문이 많은 순서로 정렬한다.
SELECT m.id AS member_id, m.name AS member_name,
       COUNT(o.id) AS order_count
FROM member AS m
LEFT JOIN orders AS o ON o.member_id = m.id
GROUP BY m.id, m.name
ORDER BY order_count DESC, m.id ASC;

-- Q10 | AGGREGATE | 상품별 누적 판매 수량과 총 판매 금액 합계를 구한다.
SELECT p.id AS product_id, p.name AS product_name,
       COALESCE(SUM(oi.quantity), 0) AS total_quantity,
       COALESCE(SUM(p.price * oi.quantity), 0) AS total_sales_amount
FROM product AS p
LEFT JOIN order_item AS oi ON oi.product_id = p.id
GROUP BY p.id, p.name
ORDER BY total_sales_amount DESC, p.id ASC;

-- Q11 | AGGREGATE | 판매된 상품별로 주문 상세 1건당 평균 구매 수량을 구한다.
SELECT p.id AS product_id, p.name AS product_name,
       COUNT(oi.id) AS order_item_count,
       ROUND(AVG(oi.quantity), 2) AS avg_quantity
FROM product AS p
INNER JOIN order_item AS oi ON oi.product_id = p.id
GROUP BY p.id, p.name
ORDER BY p.id ASC;

-- Q12 | SUBQUERY | 전체 상품의 평균 가격보다 비싼 상품을 조회한다.
SELECT id, name, price
FROM product
WHERE price > (SELECT AVG(price) FROM product)
ORDER BY price DESC, id ASC;

-- Q13 | UPDATE | 2번 상품(무선 마우스)의 가격을 35,000원으로 수정하고 변경 결과를 확인한다.
BEGIN;
SELECT '수정 전' AS stage, id, name, price FROM product WHERE id = 2;

UPDATE product
SET price = 35000
WHERE id = 2;

SELECT '수정 후' AS stage, id, name, price FROM product WHERE id = 2;
ROLLBACK;

-- Q14 | DELETE | 주문 상세 40번 데이터를 삭제하고 전체 행 수 변화를 확인한다.
BEGIN;
SELECT '삭제 전' AS stage, COUNT(*) AS total_rows FROM order_item;

DELETE FROM order_item
WHERE id = 40;

SELECT '삭제 후' AS stage, COUNT(*) AS total_rows FROM order_item;
ROLLBACK;

-- Q15 | INDEX | 특정 회원의 주문 내역을 빠르게 검색하기 위해 인덱스를 생성한다.
-- 적용 이유: orders.member_id 조건 검색 및 member 테이블과의 JOIN 속도를 높이기 위해 적용한다.
CREATE INDEX IF NOT EXISTS idx_orders_member_id ON orders(member_id);

EXPLAIN QUERY PLAN
SELECT id, member_id, ordered_at
FROM orders
WHERE member_id = 1;
