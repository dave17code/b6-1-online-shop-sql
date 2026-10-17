# B6-1 요구사항 대응표

| 미션 요구사항 | 구현·확인 위치 |
|---|---|
| 자유 주제 DB 1개 | 온라인 쇼핑몰 주문 관리, `data/shop.db` |
| 로컬 DB 준비 | Python sqlite3가 사용하는 실제 SQLite 엔진. README 버전 확인 명령 |
| SQL 실행 도구 | `main.py` CLI/SQL 실습 모드. 별도 SQLite CLI로도 SQL 직접 실행 가능 |
| 최소 4개 테이블 | member, product, orders, order_item |
| 모든 테이블 PK | 각 테이블 `id INTEGER PRIMARY KEY` |
| FK 2개 이상 / 1:N 2개 이상 | 회원-주문, 주문-상세, 상품-상세의 FK 3개·1:N 3개 |
| 적절한 컬럼 타입·이름 | 이름/이메일 TEXT, ID/수량/원 단위 금액 INTEGER, ISO 형식 날짜 TEXT |
| NOT NULL 1개 이상 | 이름, 이메일, FK, 수량, 가격, 날짜 등 |
| UNIQUE 1개 이상 | member.email, order_item(order_id, product_id) |
| 없는 값 참조 차단 | 연결마다 PRAGMA ON, 실제 잘못된 참조 입력 시험 |
| 부모 먼저 입력 | 02_seed.sql: member/product → orders → order_item |
| 각 테이블 10행 이상 | 10 / 12 / 20 / 40행. Q14 변경 중에도 상세 39행 |
| 기본 조회 4개 이상 | Q01~Q04. WHERE, ORDER BY, LIMIT 포함 |
| 조인 4개 이상 | Q05~Q08: INNER JOIN 3개 쿼리 + LEFT JOIN 1개 쿼리 |
| 집계 3개 이상 | Q09~Q11: COUNT, SUM, AVG 및 GROUP BY |
| 서브쿼리 1개 이상 | Q12: 평균 현재 가격보다 비싼 상품 |
| 수정 및 삭제 2개 이상 | Q13 UPDATE, Q14 DELETE. 실제 변경 결과를 출력 후 복원 |
| 인덱스 1개와 이유 | Q15 CREATE INDEX + 회원별 주문 검색 목적 주석 |
| 쿼리별 한 줄 설명 | Q01~Q15 번호 주석 |
| DB 전용 문법 주석 | 각 파일의 SQLite PRAGMA, typeof, INTEGER PK, 인덱스/계획 명령 설명 |
| 스키마 SQL 1개 | `sql/01_schema.sql` |
| INSERT SQL 1개 | `sql/02_seed.sql` |
| 핵심 쿼리 SQL 1개 | `sql/03_queries.sql` |
| 결과 자료 폴더 1개 | `results/`: 15개 결과 텍스트 + 환경/검증 기록 |
| 선택 ERD 이미지 | `docs/erd.png` |
| 백엔드 프레임워크 금지 | Python 표준 라이브러리만 사용, API/화면 없음 |
| 뷰·프로시저·트리거 금지 | 사용하지 않음 |
| 학습 및 동료평가 | STUDY_GUIDE.md, PEER_REVIEW.md, VS Code Tasks |

핵심 범주 합계는 **4 + 4 + 3 + 1 + 2 + 1 = 15**입니다.
Q13/Q14의 전후 확인 SELECT와 BEGIN/ROLLBACK, Q15의 인덱스 확인 명령은 결과를 보여주는 보조 문장입니다.
따라서 파일에 포함된 전체 SQL 문장 수는 15보다 많습니다. 핵심 번호는 Q01~Q15입니다.

구조상 1:N 관계의 부모 쪽은 자식이 0개일 수도 있습니다.
자식 FK에는 UNIQUE를 걸지 않아 같은 회원의 여러 주문 등 실제 1:N 데이터를 허용합니다.
주문 상세의 복합 UNIQUE는 한 주문 안에서 같은 상품을 수량으로 합치는 규칙입니다.

학습 범위는 등록 회원의 상품 주문 기록입니다. 각 상품은 별도의 옵션 없는 판매 단위이며,
주문 금액은 `quantity × unit_price`의 합입니다. 결제·배송·할인·재고 처리는 이 데이터 모델의 범위에 포함하지 않습니다.
