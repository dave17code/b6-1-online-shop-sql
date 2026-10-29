# B6-1 · Online Shop SQL 🛒

**테이블·컬럼·조회 결과의 열 이름·상품명은 영어, 고객 이름 값은 한글로 구성했습니다.**
SQL을 직접 입력하고 실행하는 프로젝트입니다. 설명 문서는 한글로 제공합니다.

## 1. VS Code에서 시작하기 🔎

기존 한글 테이블 버전과 섞이지 않도록 **새 폴더에 압축을 풀고 이 README가 있는 프로젝트 폴더를 엽니다.**
실습 DB는 **data/shop.db 하나**이고 샘플 데이터와 필수 인덱스가 준비되어 있습니다.

1. 실행용 확장 `@id:alexcvzz.vscode-sqlite`와 뷰어 `@id:qwtel.sqlite-viewer`를 설치합니다.
2. **명령 실행 전에 data/shop.db를 SQLite Viewer로 엽니다.** 필요하면 우클릭 → Open With… → SQLite Viewer를 선택합니다.
3. Ctrl+Shift+P → **SQLite: Open Database** → data/shop.db를 선택합니다.
4. practice.sql을 열고 **SQLite: Use Database**에서 같은 DB를 선택합니다.
5. SQL을 직접 입력하고 저장한 뒤, 실행할 블록 전체를 드래그 → **SQLite: Run Selected Query**를 실행합니다.

새 SQL 파일마다 DB를 지정합니다. UPDATE·DELETE는 뒤의 확인용 SELECT까지 선택합니다.
뷰어는 캐시를 사용하므로 변경 후 **새로고침하거나 DB 탭을 닫았다 다시 여세요.** SELECT 결과는 실행 결과 표에서 봅니다.
Python 실행 명령이나 백엔드 서버는 필요하지 않습니다.
Windows·macOS에서는 실행용 확장에 포함된 SQLite CLI를 사용하며, Linux에서는 필요한 경우 sqlite3 CLI를 준비합니다.
프로젝트 설정은 연결마다 `PRAGMA foreign_keys = ON;`을 실행합니다. 다른 도구로 접속할 때도 FK 검사를 켭니다.

## 2. 파일 구성 📂

| 파일 | 역할 |
|---|---|
| practice.sql | SQL을 직접 타이핑하는 작업 파일 |
| sql/01_schema.sql | 현재 실습 테이블을 지우고 빈 테이블 4개 생성 |
| sql/02_seed.sql | 부모부터 샘플 INSERT |
| sql/03_queries.sql | 설명이 붙은 필수 쿼리 Q01~Q15 |
| sql/04_reset.sql | 원본 테이블·데이터·필수 인덱스 복원 |
| results/query_01.txt ~ query_15.txt | 실제 SQL 실행 결과 15개 |
| results/validation.txt | 필수 조건·제약조건·수정·삭제·복원 검증 기록 |

필수 제출 SQL은 **01·02·03**입니다. 04는 반복 실습을 돕는 보조 파일입니다.

## 3. 테이블과 컬럼 🧩

| 테이블 | 의미 | 컬럼 |
|---|---|---|
| customers | 고객 | customer_id, customer_name, email |
| products | 상품 | product_id, product_name, price |
| orders | 주문 | order_id, customer_id, order_date |
| order_items | 주문에 담긴 상품과 수량 | order_item_id, order_id, product_id, quantity, unit_price |

- **PK:** customer_id, product_id, order_id, order_item_id는 각각 자기 테이블의 행을 구분합니다.
- **FK:** orders.customer_id → customers.customer_id, order_items.order_id → orders.order_id, order_items.product_id → products.product_id.
- **1:N:** 고객 한 명은 여러 주문을, 주문 한 건은 여러 주문상품을 가집니다. 상품 하나도 여러 주문상품에서 판매될 수 있습니다.
- **NOT NULL:** 필요한 값이 NULL인 상태를 막습니다. **UNIQUE:** email 중복을 막습니다.
- **자료형:** 번호·금액·수량은 INTEGER, 이름·이메일·날짜는 TEXT입니다. 날짜는 YYYY-MM-DD, 금액은 원 단위입니다.
- **price:** 상품의 현재 가격. **unit_price:** 주문 당시 상품 한 개의 가격. 과거 주문 금액은 `quantity * unit_price`로 계산합니다.
- **USING (customer_id):** 양쪽 테이블의 customer_id가 같은 행을 연결합니다. 테이블 별칭 없이 짧게 작성했습니다.

고객 이름은 김가람·이나래 등 한글입니다. 상품 이름은 Pencil·Notebook 등 영어입니다.
Pen Case는 필통, Colored Pencil은 색연필입니다.

## 4. 직접 실습하기 ✍️

**SQL을 읽고 결과를 예상한 뒤 실행하고, 결과가 나온 이유를 자신의 말로 설명하세요.**

### ① 테이블 생성

01_schema.sql을 참고해 practice.sql에 직접 작성합니다. 현재 실습 테이블과 데이터를 지우고 빈 테이블 4개를 만듭니다.
🎯 PK·FK·NOT NULL·UNIQUE를 정의하는 이유와 부모·자식 관계를 이해합니다.
✅ 뷰어의 customers·products·orders·order_items가 각각 0행입니다.

### ② 데이터 입력

02_seed.sql의 INSERT를 **customers → products → orders → order_items** 순서로 직접 입력하고 블록별로 실행합니다.
🎯 참조할 부모가 먼저 있어야 하며, INSERT 컬럼 순서와 VALUES 값 순서가 대응합니다.
✅ 최종 행 수는 **10 / 10 / 10 / 12**입니다. 고객 9·10은 주문이 없고, 상품 9·10은 판매되지 않았습니다.
이미 입력한 INSERT를 중복 실행하지 않습니다. 다시 시작할 때는 01부터 실행하거나 04로 복원합니다.

### ③ 필수 쿼리 15개

03_queries.sql을 참고해 Q01부터 Q15까지 하나씩 직접 타이핑하고 **해당 블록만** 선택 실행합니다.

| 번호 | 실습 내용 | 학습 포인트 | 확인 결과 |
|---|---|---|---|
| Q01 | 2000원 이상 상품 | WHERE·ORDER BY | Notebook → Tape → Scissors → Colored Pencil → Pen Case |
| Q02 | 1000~2000원 상품 | BETWEEN은 양끝 포함 | Pencil·Notebook·Pen·Ruler·Glue |
| Q03 | Pencil이 포함된 이름 | LIKE·% | Pencil·Colored Pencil |
| Q04 | 최근 주문 5건 | DESC·LIMIT | order_id 10·9·8·7·6 |
| Q05 | 주문과 고객 이름 | INNER JOIN·USING | 주문 10건에 한글 고객 이름 |
| Q06 | 주문 1번 상품 금액 | JOIN·quantity×unit_price | Pencil 2000원·Notebook 2000원, 합계 4000원 |
| Q07 | 고객 1번 구매 내역 | 네 테이블 연결 | 김가람의 주문 2건, 주문상품 3행 |
| Q08 | 주문 없는 고객 포함 | LEFT JOIN·NULL | 12행, 고객 9·10의 order_id NULL |
| Q09 | 고객별 주문 횟수 | COUNT·GROUP BY | 김가람·이나래 2건, 한이든·오하늘 0건 |
| Q10 | 상품별 판매 합계 | SUM·GROUP BY | Notebook 3개·6000원, 판매된 상품 8종 |
| Q11 | 한 행당 평균 수량 | AVG·GROUP BY | Pencil 1.5개, Notebook 1.5개, Glue 2개 |
| Q12 | 평균보다 비싼 상품 | 서브쿼리 | 평균 2150원, Pen Case·Colored Pencil·Scissors·Tape |
| Q13 | Pencil 가격 수정 | UPDATE·WHERE | price 1000 → 1200원 |
| Q14 | 주문상품 4번 삭제 | DELETE·WHERE | order_item_id 4번 삭제, 12 → 11행 |
| Q15 | 고객별 주문 검색 인덱스 | CREATE INDEX·이유 | orders_customer_id_index |

Q01~Q12는 조회이므로 원본 데이터를 바꾸지 않습니다.
Q07은 한 주문에 여러 상품이 있어 주문 2건이 3행으로 나옵니다.
Q09의 COUNT(order_id)는 NULL을 세지 않아 주문 없는 고객이 0건입니다. 고객을 구분할 때 이름뿐 아니라 customer_id로 그룹을 묶습니다.
Q10·Q11은 판매 내역만 INNER JOIN하므로 판매되지 않은 상품은 결과에 없습니다. Q11의 평균 기준은 **order_items 한 행당 수량**입니다.

### ④ 실제 변경 확인

Q13·Q14의 변경은 **실제 저장되며 자동으로 취소되지 않습니다.** 실행 후 뷰어를 다시 열어 확인합니다.

- **Q13:** products의 Pencil 가격은 1200원으로 바뀌지만, order_items의 기존 unit_price는 1000원 그대로입니다.
- **Q14:** order_items에서 4번 Pen 행만 사라집니다. 주문 2번의 Eraser 행과 orders의 주문 2번은 남습니다.
- **Q15:** 결과의 index_name과 table_name을 확인합니다. 인덱스는 데이터 값 자체를 바꾸지 않습니다.

🎯 현재 가격과 과거 단가를 분리하는 이유, WHERE로 수정·삭제 대상을 정하는 방법, 검색 컬럼에 인덱스를 두는 이유를 설명해 보세요.

### ⑤ 결과 저장과 복원 🔄

각 번호의 SQL과 실행 결과를 캡처하거나 CSV로 내보내 results에 저장합니다. 제공된 텍스트는 실제 실행한 기준 결과입니다.
실습이 끝나면 **04_reset.sql 전체를 한 번에 선택 실행**하고 뷰어를 다시 엽니다.

✅ **customers 10 / products 10 / orders 10 / order_items 12행**, Pencil 가격 1000원, 삭제했던 order_item_id 4번으로 돌아옵니다.
필수 인덱스도 복원합니다. Q15의 IF NOT EXISTS는 같은 이름의 인덱스가 있으면 중복 생성하지 않습니다.
01 → 02부터 실습하면 기존 인덱스가 제거되고 Q15에서 실제 새로 생성됩니다. practice.sql과 결과 파일은 복원 대상이 아닙니다.

## 5. 미션 필수 구현 ✅

| 요구사항 | 구현 |
|---|---|
| 로컬 DB와 실행 도구 | SQLite 파일 DB·VS Code 확장 |
| 테이블 4개와 PK | customers·products·orders·order_items |
| FK 2개 이상과 1:N | customer_id·order_id·product_id로 FK 3개 |
| NOT NULL·UNIQUE·실제 FK 동작 | 필수값·email 중복·없는 부모 참조 차단 |
| 각 테이블 10행 이상 | 10 / 10 / 10 / 12행, 부모부터 INSERT |
| 기본 조회 4개 | Q01~Q04 |
| JOIN 4개 | Q05~Q08, INNER 3개·LEFT 1개 |
| GROUP BY 집계 3개 | Q09~Q11, COUNT·SUM·AVG |
| 서브쿼리 | Q12 |
| UPDATE·DELETE | Q13·Q14 |
| 인덱스와 이유 | Q15와 주석 |
| SQL 3개와 실제 결과 | 01·02·03, results 폴더 |
| 고급 기능·프레임워크 미사용 | 뷰·프로시저·트리거·백엔드 프레임워크 없음 |

SQLite 전용 문법은 해당 SQL에 주석으로 표시했습니다. 실행 결과는 원본에서 Q01~Q15 순서로 수집했으며 배포 DB는 원본 상태입니다.

공식 도구 설명: [SQLite 확장](https://marketplace.visualstudio.com/items?itemName=alexcvzz.vscode-sqlite), [SQLite Viewer](https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer), [SQLite SELECT](https://www.sqlite.org/lang_select.html), [FK 활성화](https://www.sqlite.org/foreignkeys.html).
