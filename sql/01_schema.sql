-- B6-1 | 온라인 쇼핑몰 주문 관리 | 대상 DB: SQLite
-- 실행 순서: 01_schema.sql -> 02_seed.sql -> 03_queries.sql
-- SQLite 전용: PRAGMA, INTEGER PRIMARY KEY의 행 ID 동작, typeof().
-- SQLite에는 전용 DATETIME 저장 형식이 없으므로 날짜/시간은 TEXT에
-- YYYY-MM-DD HH:MM:SS 형식으로 저장합니다. 금액은 원 단위 정수입니다.
-- FK 검사는 DB 파일이 아니라 '접속 연결'마다 켜야 합니다.
PRAGMA foreign_keys = ON;

BEGIN;

-- 한 행 = 회원 한 명. 이름은 같을 수 있지만 이메일은 중복할 수 없습니다.
CREATE TABLE member (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    email     TEXT NOT NULL UNIQUE,
    joined_at TEXT NOT NULL
);

-- 한 행 = 판매 상품 하나. price는 현재 판매 가격입니다.
CREATE TABLE product (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL,
    price INTEGER NOT NULL
          CHECK (typeof(price) = 'integer' AND price >= 0)
);

-- 한 행 = 회원이 한 번에 주문한 한 건.
CREATE TABLE orders (
    id         INTEGER PRIMARY KEY,
    member_id  INTEGER NOT NULL,
    ordered_at TEXT NOT NULL,
    FOREIGN KEY (member_id) REFERENCES member(id)
        ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- 한 행 = 주문 안의 상품 한 종류. 같은 상품은 수량으로 합칩니다.
-- unit_price는 주문 당시 단가이며 product.price와 별도로 보존합니다.
CREATE TABLE order_item (
    id         INTEGER PRIMARY KEY,
    order_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL
               CHECK (typeof(quantity) = 'integer' AND quantity > 0),
    unit_price INTEGER NOT NULL
               CHECK (typeof(unit_price) = 'integer' AND unit_price >= 0),
    UNIQUE (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY (product_id) REFERENCES product(id)
        ON DELETE RESTRICT ON UPDATE RESTRICT
);

COMMIT;
