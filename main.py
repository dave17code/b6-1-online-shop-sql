"""SQL 파일을 그대로 실행하는 B6-1 학습 도우미. 외부 패키지는 사용하지 않습니다."""

import argparse
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import platform
import re
import sqlite3
import sys
import tempfile
import unicodedata


ROOT = Path(__file__).resolve().parent
SQL_DIR = ROOT / "sql"
DB_PATH = ROOT / "data" / "shop.db"
RESULT_DIR = ROOT / "results"
TABLES = ("member", "product", "orders", "order_item")


@dataclass
class Query:
    number: int
    category: str
    title: str
    sql: str


def connect_db(path):
    """연결할 때마다 FK 검사를 켭니다. 직접 입력한 변경은 기본적으로 즉시 저장됩니다."""
    connection = sqlite3.connect(path, isolation_level=None)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def open_practice_db():
    if not DB_PATH.is_file():
        raise ValueError("DB가 없습니다. 먼저 'py main.py init'을 실행하세요. macOS: python3")
    return connect_db(DB_PATH)


def load_queries():
    """Q01~Q15 주석을 기준으로 나눕니다. SQL 문장 자체를 다시 작성하지 않습니다."""
    text = (SQL_DIR / "03_queries.sql").read_text(encoding="utf-8-sig")
    pattern = re.compile(r"^-- Q(\d{2}) \| ([A-Z]+) \| (.+)$", re.MULTILINE)
    markers = list(pattern.finditer(text))
    queries = []
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        queries.append(Query(int(marker[1]), marker[2], marker[3], text[marker.end():end].strip()))
    if [query.number for query in queries] != list(range(1, 16)):
        raise ValueError("03_queries.sql의 '-- Q01 | ...'부터 Q15까지 번호 주석을 유지하세요.")
    return queries


def split_statements(script):
    """문자열 안의 세미콜론은 나누지 않고, SQLite가 완성된 문장인지 판단하게 합니다."""
    buffer = ""
    for character in script:
        buffer += character
        if character == ";" and sqlite3.complete_statement(buffer):
            yield buffer.strip()
            buffer = ""
    # 마지막 문장 뒤의 주석만 남는 것은 허용합니다.
    remainder = re.sub(r"/\*.*?\*/|--[^\n]*", "", buffer, flags=re.DOTALL).strip()
    if remainder:
        raise ValueError("완성되지 않은 SQL이 있습니다. 세미콜론(;)과 따옴표를 확인하세요.")


def cell_text(value):
    if value is None:
        return "NULL"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value).replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


def text_width(text):
    # 한국어가 포함된 결과도 VS Code 터미널에서 열을 맞춰 표시합니다.
    return sum(0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in "WF" else 1
               for c in text)


def format_table(columns, rows):
    values = [[cell_text(value) for value in row] for row in rows]
    widths = [max([text_width(name)] + [text_width(row[i]) for row in values])
              for i, name in enumerate(columns)]

    def line(row):
        return " | ".join(value + " " * (widths[i] - text_width(value))
                          for i, value in enumerate(row))

    output = [line(columns), "-+-".join("-" * width for width in widths)]
    output.extend(line(row) for row in values)
    output.append(f"({len(rows)}행)")
    return "\n".join(output)


def execute_and_format(connection, statement):
    cursor = connection.execute(statement)
    if cursor.description:
        return format_table([column[0] for column in cursor.description], cursor.fetchall())
    if cursor.rowcount >= 0:
        return f"영향받은 행: {cursor.rowcount}"
    return "실행 완료"


def initialize(reset=False):
    if DB_PATH.exists() and not reset:
        print("기존 DB를 그대로 사용합니다: data/shop.db")
        print("처음 상태로 복원하려면: py main.py reset --yes (macOS: python3)")
        return
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    # 스키마/샘플 입력이 모두 성공한 DB만 최종 위치로 옮깁니다.
    handle, temporary_name = tempfile.mkstemp(prefix="shop_build_", suffix=".db", dir=DB_PATH.parent)
    os.close(handle)
    temporary = Path(temporary_name)
    connection = None
    try:
        connection = connect_db(temporary)
        for filename in ("01_schema.sql", "02_seed.sql"):
            connection.executescript((SQL_DIR / filename).read_text(encoding="utf-8-sig"))
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("샘플 데이터의 FK 연결을 확인하세요.")
        connection.close()
        connection = None
        os.replace(temporary, DB_PATH)
    finally:
        if connection is not None:
            connection.close()
        temporary.unlink(missing_ok=True)
        Path(str(temporary) + "-journal").unlink(missing_ok=True)
    print("DB 준비 완료: data/shop.db")
    connection = open_practice_db()
    try:
        for table in TABLES:
            count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table}: {count}행")
    finally:
        connection.close()


def environment_text(connection):
    return "\n".join([
        "B6-1 실행 환경", f"기록 시각: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"운영체제: {platform.system()} {platform.release()}",
        f"Python: {platform.python_version()}", f"SQLite: {sqlite3.sqlite_version}",
        "DB: data/shop.db", f"현재 연결의 foreign_keys: {connection.execute('PRAGMA foreign_keys').fetchone()[0]}",
        *[f"{table}: {connection.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]}행" for table in TABLES],
    ]) + "\n"


def save_environment(connection):
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    (RESULT_DIR / "environment.txt").write_text(environment_text(connection), encoding="utf-8")


def run_queries(selection):
    queries = load_queries()
    if selection != "all":
        try:
            number = int(selection)
        except ValueError as exc:
            raise ValueError("쿼리는 1~15 또는 all로 지정하세요.") from exc
        if not 1 <= number <= 15:
            raise ValueError("쿼리 번호는 1~15입니다.")
        queries = [query for query in queries if query.number == number]

    connection = open_practice_db()
    try:
        save_environment(connection)
        for query in queries:
            path = RESULT_DIR / f"query_{query.number:02d}.txt"
            parts = [f"Q{query.number:02d} | {query.category} | {query.title}",
                     f"실행 시각: {datetime.now().astimezone().isoformat(timespec='seconds')}",
                     f"SQLite: {sqlite3.sqlite_version}", "원본: sql/03_queries.sql", "DB: data/shop.db"]
            try:
                for statement in split_statements(query.sql):
                    parts.extend(["\n[실행 SQL]", statement, "[실제 결과]",
                                  execute_and_format(connection, statement)])
                if connection.in_transaction:
                    raise ValueError("트랜잭션이 끝나지 않았습니다. COMMIT 또는 ROLLBACK을 확인하세요.")
                parts.append("\n상태: 성공")
            except (sqlite3.Error, ValueError) as exc:
                if connection.in_transaction:
                    connection.rollback()
                parts.append(f"\n상태: 실패 — {exc}")
                path.write_text("\n".join(parts) + "\n", encoding="utf-8")
                raise ValueError(f"Q{query.number:02d} 실패: {exc}. {path.name}을 확인하세요.") from exc
            path.write_text("\n".join(parts) + "\n", encoding="utf-8")
            print("\n".join(parts))
            print(f"결과 저장: results/{path.name}\n")
    finally:
        connection.close()


def check_project():
    from checks import run_checks

    connection = open_practice_db()
    try:
        save_environment(connection)
        checks = run_checks(connection, load_queries(),
                            (SQL_DIR / "01_schema.sql").read_text(encoding="utf-8-sig"),
                            (SQL_DIR / "02_seed.sql").read_text(encoding="utf-8-sig"),
                            split_statements)
        lines = [environment_text(connection),
                 "검사 범위: 현재 DB의 구조/무결성 + SQL 파일로 새로 만든 기준 데이터의 쿼리 결과",
                 "현재 DB의 제약조건 오류 입력은 메모리 복사본에서 시험합니다.", ""]
        for name, passed, detail in checks:
            lines.append(f"[{'PASS' if passed else 'FAIL'}] {name} — {detail}")
        successes = sum(passed for _, passed, _ in checks)
        lines.append(f"\n총 {len(checks)}개 중 {successes}개 통과")
        report = "\n".join(lines) + "\n"
        (RESULT_DIR / "validation.txt").write_text(report, encoding="utf-8")
        print(report)
        print("결과 저장: results/validation.txt")
        return 0 if successes == len(checks) else 1
    finally:
        connection.close()


def execute_one(sql):
    connection = open_practice_db()
    try:
        print(execute_and_format(connection, sql))
    finally:
        connection.close()


def interactive_shell():
    connection = open_practice_db()
    print("B6-1 SQL 실습 | data/shop.db | FK 검사 ON")
    print("SQL 끝에 ;을 입력하세요. .tables: 테이블 목록 / .quit: 종료")
    print("직접 실행한 UPDATE/DELETE는 저장됩니다. 되돌리기 실습은 BEGIN; ... ROLLBACK;을 사용하세요.")
    buffer = ""
    try:
        while True:
            try:
                line = input("sql> " if not buffer else "...> ")
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n입력을 취소했습니다.")
                buffer = ""
                continue
            if line.strip() == ".quit":
                break
            if not buffer and not line.strip():
                continue
            if not buffer and line.lstrip().startswith("."):
                if line.strip() == ".tables":
                    print(execute_and_format(connection,
                          "SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"))
                else:
                    print("이 도우미의 명령은 .tables와 .quit입니다. SQL 파일 실행에는 main.py run을 사용하세요.")
                continue
            buffer += line + "\n"
            if not sqlite3.complete_statement(buffer):
                continue
            try:
                for statement in split_statements(buffer):
                    print(execute_and_format(connection, statement))
            except (sqlite3.Error, ValueError) as exc:
                print(f"SQL 오류: {exc}")
            buffer = ""
    finally:
        if connection.in_transaction:
            connection.rollback()
            print("확정하지 않은 트랜잭션은 되돌렸습니다.")
        connection.close()


def main():
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="B6-1 온라인 쇼핑몰 SQL 실습 (Python 3.10 이상)")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("init", help="DB가 없을 때 스키마와 샘플 데이터를 준비")
    reset = commands.add_parser("reset", help="data/shop.db를 초기 샘플 데이터로 복원")
    reset.add_argument("--yes", action="store_true", help="현재 DB의 실습 변경을 지우고 복원")
    run = commands.add_parser("run", help="쿼리 실행과 결과 텍스트 저장")
    run.add_argument("number", nargs="?", default="all", help="1~15 또는 all (기본: all)")
    commands.add_parser("check", help="미션 조건, 제약조건과 기준 쿼리 결과 검사")
    commands.add_parser("shell", help="SQL을 직접 입력하며 실습")
    sql = commands.add_parser("sql", help="SQL 한 문장을 실행")
    sql.add_argument("statement", help="큰따옴표로 감싼 SQL")
    args = parser.parse_args()
    try:
        if args.command == "init":
            initialize()
        elif args.command == "reset":
            if not args.yes:
                raise ValueError("현재 실습 DB를 초기화합니다. 실행하려면 reset --yes를 사용하세요.")
            initialize(reset=True)
        elif args.command == "run":
            run_queries(args.number)
        elif args.command == "check":
            return check_project()
        elif args.command == "shell":
            interactive_shell()
        elif args.command == "sql":
            execute_one(args.statement)
        else:
            parser.print_help()
    except (sqlite3.Error, OSError, ValueError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
