# 실제 실행 결과 ✅

query_01.txt부터 query_15.txt는 영어 SQL을 원본 데이터에서 순서대로 실제 실행한 결과입니다.
SQL 식별자·결과 열·상품명은 영어이며, customer_name 값은 한글입니다.
금액 단위는 원이고, 주문 금액은 products 테이블의 price와 order_items 테이블의 quantity를 곱해 계산합니다.
average_quantity는 order_items 한 행당 수량의 평균입니다.
Q13 이후 Pencil 가격은 1200원, Q14 이후 order_items는 11행입니다.
결과 수집 후 배포 DB는 customers 10 / products 10 / orders 10 / order_items 12행과 필수 인덱스로 복원했습니다.
직접 실습한 SQL과 결과는 캡처나 CSV로 내보내 이 폴더에 보관하세요.
