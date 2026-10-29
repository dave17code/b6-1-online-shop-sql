-- B6-1 | 온라인 쇼핑몰 주문 관리 스키마 정의 | 대상 DB: SQLite
-- 실행 순서: 01_schema.sql -> 02_seed.sql -> 03_queries.sql
-- [SQLite 전용 문법 안내]
-- 1) PRAGMA foreign_keys = ON : SQLite에서 외래키(FK) 참조 무결성 검사를 활성화합니다.
-- 2) INTEGER PRIMARY KEY : 각 행을 식별하는 기본키(PK)로 동작합니다.
-- 3) 날짜/시간은 TEXT 타입에 'YYYY-MM-DD HH:MM:SS' 형식으로 저장합니다.

PRAGMA foreign_keys = ON;

BEGIN;

-- 1. 회원(member) 테이블: 쇼핑몰 가입 회원 정보
CREATE TABLE member (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    email     TEXT NOT NULL UNIQUE,
    joined_at TEXT NOT NULL
);

-- 2. 상품(product) 테이블: 판매 상품 이름과 가격(원 단위)
CREATE TABLE product (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0)
);

-- 3. 주문(orders) 테이블: 회원이 주문한 영수증 단위 (member와 1:N 관계)
CREATE TABLE orders (
    id         INTEGER PRIMARY KEY,
    member_id  INTEGER NOT NULL,
    ordered_at TEXT NOT NULL,
    FOREIGN KEY (member_id) REFERENCES member(id)
        ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- 4. 주문 상세(order_item) 테이블: 한 주문 안에 담긴 개별 상품과 수량 (orders, product와 각각 1:N 관계)
CREATE TABLE order_item (
    id         INTEGER PRIMARY KEY,
    order_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    UNIQUE (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY (product_id) REFERENCES product(id)
        ON DELETE RESTRICT ON UPDATE RESTRICT
);

COMMIT;
