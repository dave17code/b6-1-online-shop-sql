# B6-1 동료평가 시연 가이드

아래는 원본 SQL/샘플 기준입니다. Windows 명령의 `py`를 macOS에서는 `python3`로 바꾸세요.

## 1. 평가 전에 준비

VS Code에서 프로젝트 폴더를 열고 터미널에서 실행합니다.

```bash
py main.py reset --yes
py main.py run all
py main.py check
```

`reset --yes`는 현재 실습 DB를 초기화합니다. 이전 실습 데이터가 필요한 경우 먼저 보관하세요.
검증 보고서의 마지막 줄은 `총 45개 중 45개 통과`입니다.
`results`의 15개 결과 텍스트가 실행 결과 자료이므로 별도 스크린샷은 필수가 아닙니다.

## 2. 테이블과 관계 설명 — 약 2분

`docs/erd.png`와 `sql/01_schema.sql`을 엽니다.

- 회원 한 명은 여러 번 주문합니다: `orders.member_id → member.id`.
- 주문 한 건은 여러 상품 항목을 포함합니다: `order_item.order_id → orders.id`.
- 상품 하나는 여러 주문에 등장합니다: `order_item.product_id → product.id`.
- PK는 행을 식별하고, FK는 존재하는 부모만 참조하도록 제한합니다.
- 현재 상품 가격과 주문 당시 단가를 분리해서 과거 주문 금액을 유지합니다.

테이블별 데이터 개수는 `results/environment.txt`에서 확인합니다.
회원 10 / 상품 12 / 주문 20 / 상세 40행입니다.

## 3. 쿼리 15개 확인 — 약 3분

`sql/03_queries.sql`과 `results/query_01.txt`~`query_15.txt`를 나란히 엽니다.
전체 실행은 위에서 완료했으므로 질문받은 쿼리만 다시 실행해도 됩니다.

| 보여줄 내용 | 명령 | 설명할 점 |
|---|---|---|
| 검색·정렬·개수 제한 | `py main.py run 4` | 최근 주문 5건, 20번부터 16번 |
| 주문 상세와 과거 금액 | `py main.py run 6` | 상세 2행, 주문 금액 119,000원 |
| 네 테이블 조인 | `py main.py run 7` | 회원 1의 주문은 4건이지만 상세 결과는 7행 |
| LEFT JOIN | `py main.py run 8` | 주문 없는 회원 9/10도 남고 주문 컬럼은 NULL |
| COUNT + GROUP BY | `py main.py run 9` | 주문 없는 회원은 0건, COUNT(o.id)의 이유 |
| SUM + GROUP BY | `py main.py run 10` | 수량과 당시 단가로 금액 합계, 미판매는 0 |
| AVG + GROUP BY | `py main.py run 11` | 상세 한 건당 평균 수량, 케이블은 2.00개 |
| 서브쿼리 | `py main.py run 12` | 평균 가격을 구한 뒤 바깥 조회에서 비교 |

Q01~Q04 기본 4개, Q05~Q08 조인 4개, Q09~Q11 집계 3개,
Q12 서브쿼리 1개, Q13 UPDATE, Q14 DELETE, Q15 인덱스로 총 15개입니다.

## 4. UPDATE/DELETE 실제 실행 — 약 2분

```bash
py main.py run 13
py main.py run 14
```

Q13의 `before`, `after`, `restored`를 비교합니다.
마우스 현재 가격은 30,000 → 35,000 → 30,000원으로 바뀌고,
과거 주문 단가는 25,000원, 해당 항목 금액은 50,000원으로 유지됩니다.

Q14는 상세 40번을 실제 삭제합니다. `after`에서 대상은 0행, 전체 상세는 39행입니다.
그 뒤 ROLLBACK하여 상세 40번이 다시 나타납니다.
ROLLBACK은 실제 변경을 취소하므로 같은 시연을 반복할 수 있습니다.

## 5. 제약조건이 실제로 막는지 확인 — 약 2분

아래 명령은 **의도한 오류가 출력되는 것이 정상**입니다. 실패한 변경은 적용되지 않습니다.

없는 회원을 참조하는 주문:

```bash
py main.py sql "INSERT INTO orders (id, member_id, ordered_at) VALUES (9999, 9999, '2026-10-01 10:00:00');"
```

기대: `FOREIGN KEY constraint failed`

이미 존재하는 이메일:

```bash
py main.py sql "INSERT INTO member (id, name, email, joined_at) VALUES (9999, 'Test', 'haneul@example.com', '2026-10-01 10:00:00');"
```

기대: `UNIQUE constraint failed: member.email`

필수 정보 NULL / 수량 0:

```bash
py main.py sql "UPDATE member SET name = NULL WHERE id = 1;"
py main.py sql "UPDATE order_item SET quantity = 0 WHERE id = 1;"
```

기대: 각각 `NOT NULL constraint failed`, `CHECK constraint failed`

전체 제약조건 시험 기록은 `results/validation.txt`에 있습니다.

## 6. 인덱스 설명 — 약 1분

```bash
py main.py run 15
```

`idx_orders_member_id`가 `member_id`에 생성되었는지 확인합니다.
적용 이유는 **특정 회원의 주문을 찾거나 회원과 주문을 연결할 때 활용하기 위해서**입니다.
샘플 20건으로 대규모 성능 개선을 입증한 것은 아닙니다. 생성 여부와 실행 계획을 확인합니다.

## 7. 자주 받을 질문

| 질문 | 답변 요점 |
|---|---|
| 주문과 주문 상세를 왜 나눴나요? | 주문 시각·회원은 주문당 한 번 저장하고 여러 상품은 상세로 표현합니다. |
| 회원 이름을 FK로 쓰면 안 되나요? | 같은 이름이 있을 수 있어 PK인 id로 연결합니다. |
| 상품 현재 가격으로 주문 금액을 계산하면요? | 가격 변경이 과거 금액에 반영되므로 당시 단가를 따로 저장합니다. |
| COUNT(*)와 COUNT(o.id)가 왜 다르죠? | LEFT JOIN의 주문 없는 행은 남지만 o.id는 NULL이라 후자에서는 세지 않습니다. |
| FK를 선언하면 항상 검사하나요? | SQLite에서는 연결마다 PRAGMA foreign_keys = ON으로 활성화합니다. |
| Python이 DB를 흉내 낸 것인가요? | 실제 SQLite 엔진이 SQL을 실행하고 shop.db에 저장합니다. Python은 실행 도우미입니다. |
| 결과가 실행할 때마다 바뀌지 않나요? | 날짜·데이터가 고정되어 있고 수정/삭제 쿼리는 복원합니다. 사용자 직접 변경 후에는 reset으로 재현합니다. |

마지막으로 `py main.py run all`, `py main.py check`를 실행하여 제출 결과를 현재 상태로 갱신합니다.
