# 실행 결과 자료

- `query_01.txt`~`query_15.txt`: 한 줄 목적, 실제 실행 SQL, 실제 결과와 성공 여부.
- `environment.txt`: 생성 시각, OS, Python/SQLite 버전, 연결의 FK 설정, 현재 행 수.
- `validation.txt`: 현재 DB의 구조/제약조건과 기준 SQL 실행 결과에 대한 검증 보고서.

동봉된 결과는 제작 환경의 실제 실행 기록입니다. 자신의 컴퓨터에서 다음 명령으로 갱신할 수 있습니다.

```bash
py main.py run all
py main.py check
```

macOS에서는 `py` 대신 `python3`를 사용합니다. 명령은 프로젝트 최상위에서 실행하세요.
쿼리 하나만 실행하면 그 결과 파일만 갱신되므로, 제출 전에는 `run all`로 같은 상태의 전체 결과를 만드세요.
SQL/실습 데이터를 직접 수정했다면 원본과 결과가 달라질 수 있습니다.

Q13/Q14의 `after`는 실제 변경 후 결과이고 `restored`는 ROLLBACK 후의 결과입니다.
Q15의 PRAGMA와 실행 계획은 SQLite 버전에 따라 표시 문구가 다를 수 있습니다.
미션은 결과 텍스트를 허용하므로 이 폴더를 실행 결과 자료로 사용할 수 있습니다.
