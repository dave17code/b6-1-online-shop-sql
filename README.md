# B6-1 · 온라인 쇼핑몰 주문 관리 SQL

회원·상품·주문·주문 상세를 직접 설계하고 SQL로 조회·조인·집계·수정·삭제하는 프로젝트입니다.
**학습할 핵심 코드는 `sql/`의 세 파일입니다.** Python은 이 SQL을 실행하고 결과를 저장하는 도우미입니다.

| 항목 | 구성 |
|---|---|
| DB | 로컬 SQLite, `data/shop.db` |
| 실행 환경 | Python 3.10 이상 + `sqlite3` 기본 모듈, VS Code 터미널 |
| 추가 패키지 / 서버 | 없음. `pip install` 및 별도 DB 서버 실행 불필요 |
| 테이블 / 데이터 | 회원 10명, 상품 12개, 주문 20건, 주문 상세 40행 |
| 핵심 SQL | Q01~Q15, 범주별 필수 개수 충족 |
| 결과 | `results/query_01.txt` ~ `query_15.txt`, 환경 및 검증 보고서 |

웹사이트/API·뷰·프로시저·트리거를 사용하지 않습니다. 모든 이름과 이메일은 실습용 가상 정보입니다.

## 1. VS Code에서 시작하기 🚀

1. 압축을 풀고 VS Code에서 **파일 → 폴더 열기**로 `b6-1-online-shop-sql` 폴더를 여세요.
2. 왼쪽 탐색기에 `main.py`, `sql`, `docs`, `results`가 바로 보이는지 확인하세요.
3. **터미널 → 새 터미널**을 여세요. Windows PowerShell 또는 Git Bash 모두 사용할 수 있습니다.
4. 아래 명령을 한 줄씩 실행하세요.

**Windows**

```bash
py --version
py -c "import sqlite3; print(sqlite3.sqlite_version)"
py main.py init
py main.py run all
py main.py check
```

**macOS / Linux**

```bash
python3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
python3 main.py init
python3 main.py run all
python3 main.py check
```

기준 프로젝트의 검증 결과는 **45개 중 45개 통과**입니다.
Python/SQLite 버전 숫자는 컴퓨터에 따라 달라도 됩니다.

압축에는 바로 열 수 있는 `data/shop.db`와 제작 환경에서 실제 생성한 결과 텍스트가 들어 있습니다.
`init`은 기존 DB를 보존합니다. `run all`, `check`를 실행하면 결과 파일을 **본인 컴퓨터의 실행 결과로 갱신**합니다.
본인 환경은 `results/environment.txt`에서 확인하세요.

`py`가 없다면 설치된 Python의 `python` 명령을 사용하거나 [Python 공식 설치 안내](https://www.python.org/downloads/)를 확인하세요.
macOS에서는 `python3`를 사용합니다. Python에서 `import sqlite3`가 성공하면 이 프로젝트의 SQLite 환경 준비가 된 것입니다.
Python의 `sqlite3` 모듈과 별도 `sqlite3` CLI 실행 파일은 다릅니다. 이 도우미를 사용할 때 별도 CLI 설치는 필요 없습니다.

## 2. 반복 실습 명령

아래는 Windows 기준이며 macOS에서는 `py`를 `python3`로 바꾸세요.

| 명령 | 동작 |
|---|---|
| `py main.py init` | DB가 없을 때만 스키마·데이터 생성 |
| `py main.py run all` | 15개 쿼리 실행 + 쿼리별 결과 텍스트 저장 |
| `py main.py run 8` | Q08만 실행 + 해당 결과 파일 갱신 |
| `py main.py check` | 현재 DB 및 SQL 기준 동작 검증 + `validation.txt` 저장 |
| `py main.py shell` | SQL을 직접 입력하는 실습 모드 |
| `py main.py sql "SELECT * FROM product;"` | SQL 한 문장을 실행 |
| `py main.py reset --yes` | 현재 `data/shop.db`를 지우고 스키마·샘플 데이터로 다시 생성 |

**처음 상태에서 다시 시연하기**

```bash
py main.py reset --yes
py main.py run all
py main.py check
```

`reset`은 직접 추가하거나 수정한 실습 데이터를 초기화합니다. SQL 소스 파일은 삭제하지 않습니다.
SQL을 고친 경우에는 **현재 저장된 SQL 파일**을 기준으로 다시 만듭니다. 원본 SQL로 돌아가려면 Git 변경을 확인하거나 원본 압축을 다시 풀어 사용하세요.
결과 파일은 `run all`과 `check`로 다시 생성하세요.

**VS Code 작업 메뉴도 사용할 수 있습니다.**

- `Ctrl+Shift+B`(macOS `Cmd+Shift+B`): DB 준비 → 전체 쿼리 → 검증을 순서대로 실행합니다.
- **터미널 → 작업 실행**: 한 쿼리 실행, SQL 직접 입력, DB 초기화를 선택할 수 있습니다.
- Windows 작업 명령은 `py`, macOS/Linux는 `python3`입니다. Windows에서 `python`만 사용하는 경우 `.vscode/tasks.json`의 Windows `command` 값을 `python`으로 바꾸세요.
- 별도 VS Code 확장 설치는 필수가 아닙니다. Markdown은 미리 보기로, 결과 `.txt`는 편집기로 확인할 수 있습니다.

## 3. 꼭 알아야 할 실행 동작 💡

**Q13 UPDATE, Q14 DELETE**는 실제 변경 전후를 출력한 다음 `ROLLBACK`합니다.
원본 SQL에서는 반복 실행해도 상품 가격과 주문 상세가 원래 상태로 유지됩니다.
Q15 인덱스는 생성 후 유지되며, 다시 실행해도 중복 생성되지 않습니다.

**`shell`과 `sql`에서 직접 입력한 UPDATE/DELETE는 기본적으로 저장됩니다.**
되돌리면서 실습하려면 `BEGIN;`으로 시작하고 `ROLLBACK;`으로 끝내세요. 저장하려면 `COMMIT;`을 사용하세요.

`check`의 검사 대상은 두 가지입니다.

1. **현재 DB:** 행 수, PK/FK, 인덱스, 무결성 및 제약조건. 오류 입력은 메모리 복사본에서만 시험합니다.
2. **원본 SQL의 기준 동작:** 매번 별도 메모리 DB에 SQL 파일을 실행하여 15개 결과를 검사합니다.

따라서 현재 DB를 실습으로 바꿔도 기준 쿼리 검사는 원래 샘플을 기준으로 합니다.
샘플 데이터나 쿼리의 의도 자체를 바꾸면 `checks.py`의 기준 기대값도 검토해야 합니다.
제출·동료평가 직전에는 원본 SQL로 `reset → run all → check`를 실행하는 것을 권장합니다.

## 4. 어디부터 공부할까요?

| 순서 | 파일 | 볼 내용 |
|---|---|---|
| 1 | [STUDY_GUIDE.md](docs/STUDY_GUIDE.md) | 관계·키·집계와 반복 실습 |
| 2 | [01_schema.sql](sql/01_schema.sql) | 한 행의 의미, PK/FK, 제약조건 |
| 3 | [02_seed.sql](sql/02_seed.sql) | 부모부터 입력하는 순서와 데이터 사례 |
| 4 | [03_queries.sql](sql/03_queries.sql) | Q01~Q15의 실제 SQL |
| 5 | [PEER_REVIEW.md](docs/PEER_REVIEW.md) | 동료평가 시연 순서·기대 결과 |
| 6 | [REQUIREMENTS.md](docs/REQUIREMENTS.md) | 미션 요구사항과 구현 위치 |

관계도: [erd.png](docs/erd.png)

## 5. SQL 파일만 직접 실행하는 방법 — 선택

별도 SQLite CLI가 준비되어 있으면 Python 도우미 없이 세 SQL 파일을 실행할 수 있습니다.
다음은 **아직 존재하지 않는 새 DB 파일** `data/shop-cli.db`로 처음 실행하는 예입니다.

```bash
sqlite3 data/shop-cli.db
```

SQLite CLI 안에서:

```text
.bail on
.headers on
.mode column
.read sql/01_schema.sql
.read sql/02_seed.sql
.read sql/03_queries.sql
.quit
```

다시 접속할 때는 기존 테이블/샘플을 중복 생성하지 말고 `03_queries.sql`만 실행하세요.
각 SQL 파일은 SQLite 전용 설정/문법을 주석으로 표시합니다.
공식 CLI의 `.read`는 `main.py shell`의 명령이 아닙니다.
`shop-cli.db`는 `shop.db`와 별개 파일이므로 도우미로 검사/실습하는 대상은 계속 `shop.db`입니다.

## 6. 자주 만나는 메시지

| 메시지 | 확인할 것 |
|---|---|
| `can't open file ... main.py` | VS Code에서 압축을 푼 프로젝트 폴더를 열었는지 확인 |
| `DB가 없습니다` | `init`부터 실행 |
| 인덱스 검사 FAIL | `run 15` 또는 `run all`을 먼저 실행 |
| `UNIQUE constraint failed` | 이미 존재하는 PK/이메일/주문-상품 조합인지 확인 |
| `FOREIGN KEY constraint failed` | 부모 ID가 존재하는지, 참조 중인 부모를 삭제하려는지 확인 |
| `CHECK constraint failed` | 수량은 양의 정수, 금액은 0 이상의 정수인지 확인 |
| `...>` 프롬프트가 계속 표시 | 문장 끝 `;`, 따옴표를 확인. `Ctrl+C`로 현재 입력 취소 |
| `database is locked` | 다른 도구의 미완료 트랜잭션을 COMMIT/ROLLBACK하고 다시 실행 |
| 기준 쿼리 결과 FAIL | SQL/샘플을 변경했는지 확인하고 보고서의 해당 항목 비교 |

참고 문서: [Python sqlite3](https://docs.python.org/3/library/sqlite3.html),
[SQLite FK](https://www.sqlite.org/foreignkeys.html),
[SQLite CLI](https://www.sqlite.org/cli.html),
[VS Code Tasks](https://code.visualstudio.com/docs/debugtest/tasks).
