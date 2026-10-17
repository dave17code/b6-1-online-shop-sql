"""미션 조건과 실제 동작을 검사합니다. 현재 DB의 데이터는 변경하지 않습니다."""

from collections import Counter
import sqlite3


TABLES = ("member", "product", "orders", "order_item")


def run_checks(current, queries, schema, seed, split_statements):
    checks = []

    def record(name, passed, detail):
        checks.append((name, bool(passed), str(detail)))

    tables = {row[0] for row in current.execute("SELECT name FROM sqlite_schema WHERE type='table'")}
    record("필수 테이블 4개", set(TABLES) <= tables, ", ".join(sorted(tables)))
    if not set(TABLES) <= tables:
        return checks

    for table in TABLES:
        count = current.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        record(f"{table} 최소 10행", count >= 10, f"현재 {count}행")
    record("모든 테이블 PK", all(any(row[5] for row in current.execute(f"PRAGMA table_info({table})"))
                                for table in TABLES), "PRAGMA table_info의 pk 값 확인")
    fks = sum(len(current.execute(f"PRAGMA foreign_key_list({table})").fetchall()) for table in TABLES)
    record("FK 2개 이상", fks >= 2, f"현재 {fks}개")
    record("현재 연결 FK 검사 ON", current.execute("PRAGMA foreign_keys").fetchone()[0] == 1, "foreign_keys = 1")
    errors = current.execute("PRAGMA foreign_key_check").fetchall()
    record("현재 데이터 참조 무결성", not errors, f"FK 위반 {len(errors)}건")
    integrity = current.execute("PRAGMA integrity_check").fetchall()
    record("DB 파일 무결성", integrity == [("ok",)], integrity)
    advanced = current.execute("SELECT name FROM sqlite_schema WHERE type IN ('view', 'trigger')").fetchall()
    record("뷰/트리거 미사용", not advanced, f"{len(advanced)}개 (SQLite는 저장 프로시저 미지원)")
    index_columns = current.execute("PRAGMA index_info('idx_orders_member_id')").fetchall()
    record("회원별 주문 검색 인덱스", [row[2] for row in index_columns] == ["member_id"],
           "idx_orders_member_id / 없으면 run 15 또는 run all 실행")
    expected_categories = {"BASIC": 4, "JOIN": 4, "AGGREGATE": 3, "SUBQUERY": 1,
                           "UPDATE": 1, "DELETE": 1, "INDEX": 1}
    categories = Counter(query.category for query in queries)
    record("15개 쿼리 범주", dict(categories) == expected_categories, dict(categories))

    # 실제 DB의 복사본에서 오류 입력을 시험하므로 실습 데이터에 영향을 주지 않습니다.
    probe = sqlite3.connect(":memory:", isolation_level=None)
    current.backup(probe)
    probe.execute("PRAGMA foreign_keys = ON")
    try:
        member_id, email = probe.execute("SELECT id, email FROM member ORDER BY id LIMIT 1").fetchone()
        product_id = probe.execute("SELECT id FROM product ORDER BY id LIMIT 1").fetchone()[0]
        item_id, order_id, sold_product = probe.execute("SELECT id, order_id, product_id FROM order_item LIMIT 1").fetchone()
        referenced_member = probe.execute("SELECT member_id FROM orders WHERE id=?", (order_id,)).fetchone()[0]
        missing = {table: probe.execute(f"SELECT COALESCE(MAX(id),0)+1 FROM {table}").fetchone()[0]
                   for table in TABLES}
        cases = [
            ("PK 중복 차단", "INSERT INTO product VALUES (?, '중복 PK', 100)", (product_id,), "UNIQUE"),
            ("NOT NULL 차단", "UPDATE member SET name=NULL WHERE id=?", (member_id,), "NOT NULL"),
            ("이메일 UNIQUE 차단", "INSERT INTO member VALUES (?, '중복 이메일', ?, '2026-09-01 00:00:00')",
             (missing["member"], email), "UNIQUE"),
            ("필수 FK의 NULL 차단", "UPDATE orders SET member_id=NULL WHERE id=?", (order_id,), "NOT NULL"),
            ("없는 회원 FK 차단", "INSERT INTO orders VALUES (?, ?, '2026-09-01 00:00:00')",
             (missing["orders"], missing["member"]), "FOREIGN KEY"),
            ("없는 주문 FK 차단", "INSERT INTO order_item VALUES (?, ?, ?, 1, 100)",
             (missing["order_item"], missing["orders"], product_id), "FOREIGN KEY"),
            ("없는 상품 FK 차단", "INSERT INTO order_item VALUES (?, ?, ?, 1, 100)",
             (missing["order_item"], order_id, missing["product"]), "FOREIGN KEY"),
            ("같은 주문의 상품 중복 차단", "INSERT INTO order_item VALUES (?, ?, ?, 1, 100)",
             (missing["order_item"], order_id, sold_product), "UNIQUE"),
            ("0 수량 CHECK 차단", "UPDATE order_item SET quantity=0 WHERE id=?", (item_id,), "CHECK"),
            ("소수 수량 CHECK 차단", "UPDATE order_item SET quantity=1.5 WHERE id=?", (item_id,), "CHECK"),
            ("음수 가격 CHECK 차단", "UPDATE product SET price=-1 WHERE id=?", (product_id,), "CHECK"),
            ("소수 단가 CHECK 차단", "UPDATE order_item SET unit_price=1.5 WHERE id=?", (item_id,), "CHECK"),
            ("참조되는 회원 삭제 차단", "DELETE FROM member WHERE id=?", (referenced_member,), "FOREIGN KEY"),
            ("참조되는 주문 삭제 차단", "DELETE FROM orders WHERE id=?", (order_id,), "FOREIGN KEY"),
            ("참조되는 상품 삭제 차단", "DELETE FROM product WHERE id=?", (sold_product,), "FOREIGN KEY"),
        ]
        for name, statement, parameters, expected_error in cases:
            probe.execute("SAVEPOINT constraint_probe")
            try:
                probe.execute(statement, parameters)
                record(name, False, "차단되어야 할 입력이 허용됨")
            except sqlite3.IntegrityError as exc:
                record(name, expected_error in str(exc), str(exc))
            except sqlite3.Error as exc:
                record(name, False, f"예상과 다른 SQL 오류: {exc}")
            finally:
                probe.execute("ROLLBACK TO constraint_probe")
                probe.execute("RELEASE constraint_probe")
    except (sqlite3.Error, TypeError) as exc:
        record("제약조건 검사 준비", False, f"현재 DB의 행/관계를 확인하세요: {exc}")
    finally:
        probe.close()

    # 기준 데이터는 매번 SQL 파일로 새로 만듭니다. 사용자가 실습한 DB와 분리됩니다.
    reference = sqlite3.connect(":memory:", isolation_level=None)
    reference.execute("PRAGMA foreign_keys = ON")
    result_sets = {}
    try:
        reference.executescript(schema)
        reference.executescript(seed)
        before = {table: reference.execute(f"SELECT * FROM {table} ORDER BY id").fetchall() for table in TABLES}
        for query in queries:
            sets = []
            for statement in split_statements(query.sql):
                cursor = reference.execute(statement)
                if cursor.description:
                    sets.append(cursor.fetchall())
            result_sets[query.number] = sets
        record("SQL 3파일 순차 실행", True, "스키마/입력/15개 쿼리 실제 실행 성공")
        after = {table: reference.execute(f"SELECT * FROM {table} ORDER BY id").fetchall() for table in TABLES}
        record("Q13/Q14 원본 복원", before == after, "15개 실행 전후 네 테이블의 전체 행 비교")

        def first(number):
            return result_sets[number][0]

        for number, ids in [(1, [6, 1, 5, 9]), (2, [2, 3, 4, 8, 11]),
                            (3, [3, 10]), (4, [20, 19, 18, 17, 16]), (12, [9, 5, 1, 6, 8])]:
            actual = [row[0] for row in first(number)]
            record(f"Q{number:02d} 필터/정렬 결과", actual == ids, f"ID 순서 {actual}")
        record("Q05 회원-주문 연결", len(first(5)) == 20 and first(5)[0][1] == "김하늘", "주문 20건, 주문 1번 회원 김하늘")
        record("Q06 과거 단가로 금액 계산", len(first(6)) == 2 and sum(row[4] for row in first(6)) == 119000,
               "주문 1: 69,000 + 2 × 25,000 = 119,000원")
        rows7 = first(7)
        record("Q07 네 테이블 연결", len(rows7) == 7 and {row[1] for row in rows7} == {1, 4, 12, 19}
               and all(row[0] == "김하늘" for row in rows7), "회원 1의 4개 주문, 상세 7행")
        rows8 = first(8)
        record("Q08 LEFT JOIN의 NULL", len(rows8) == 22 and {row[0] for row in rows8 if row[2] is None} == {9, 10},
               "22행, 주문 없는 회원 9/10 유지")
        expected_counts = {1: 4, 2: 4, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 0, 10: 0}
        record("Q09 주문 횟수/0건 처리", {row[0]: row[2] for row in first(9)} == expected_counts,
               "회원 1/2: 4건, 3~8: 2건, 9/10: 0건")
        original_items = before["order_item"]
        expected_quantity = sum(row[3] for row in original_items)
        expected_amount = sum(row[3] * row[4] for row in original_items)
        rows10 = first(10)
        record("Q10 합계 및 미판매 상품", len(rows10) == 12
               and sum(row[2] for row in rows10) == expected_quantity
               and sum(row[3] for row in rows10) == expected_amount
               and {row[0] for row in rows10 if row[2] == 0 and row[3] == 0} == {11, 12},
               f"총 수량 {expected_quantity}, 총 주문 금액 {expected_amount:,}원, 미판매 2종")
        cable = [row for row in first(11) if row[0] == 10]
        record("Q11 평균의 단위", len(first(11)) == 10 and len(cable) == 1 and cable[0][2:] == (9, 2.0),
               "케이블: 상세 9건, 총 18개, 상세 한 건당 평균 2.00개")
        rows13 = result_sets[13]
        record("Q13 실제 UPDATE와 복원", rows13[0] == [("before", 30000, 25000, 50000)]
               and rows13[1] == [("after", 35000, 25000, 50000)]
               and rows13[2] == [("restored", 2, 30000)], "현재 가격만 30,000 -> 35,000 -> 30,000원")
        rows14 = result_sets[14]
        record("Q14 실제 DELETE와 복원", rows14[1] == [("after", 0)]
               and rows14[2] == [("after", 39)] and rows14[3] == [("restored", 40, 20, 7, 1)],
               "상세 40번 삭제, 전체 39행, 이후 대상 복원")
        record("Q15 인덱스 실제 생성", [row[2] for row in reference.execute("PRAGMA index_info('idx_orders_member_id')")] == ["member_id"],
               "orders.member_id 인덱스 확인")
    except (sqlite3.Error, ValueError, IndexError, KeyError, TypeError) as exc:
        record("기준 쿼리 실행/결과 검사", False, str(exc))
    finally:
        reference.close()
    return checks
