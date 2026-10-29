import sqlite3
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "shop.db"


def width(text):
    return sum(
        2 if unicodedata.east_asian_width(c) in "WF" else 1
        for c in text
    )


def show(cursor):
    if cursor.description is None:
        if cursor.rowcount >= 0:
            print(f"{cursor.rowcount} row(s) affected")
        return

    headers = [column[0] for column in cursor.description]
    rows = [
        ["NULL" if value is None else str(value) for value in row]
        for row in cursor.fetchall()
    ]
    grid = [headers] + rows
    widths = [
        max(width(row[i]) for row in grid)
        for i in range(len(headers))
    ]

    for index, row in enumerate(grid):
        print(" | ".join(
            value + " " * (widths[i] - width(value))
            for i, value in enumerate(row)
        ))
        if index == 0:
            print("-+-".join("-" * size for size in widths))
    print(f"({len(rows)} rows)")


def run_sql(connection, script):
    buffer = ""

    for character in script:
        buffer += character
        if character == ";" and sqlite3.complete_statement(buffer):
            show(connection.execute(buffer))
            buffer = ""

    if buffer.strip():
        show(connection.execute(buffer))


def shell():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, isolation_level=None)
    connection.execute("PRAGMA foreign_keys = ON")
    buffer = ""

    print("Database: data/shop.db | Foreign keys: ON")
    print("Type SQL ending with ; | .read FILE | .quit")

    try:
        while True:
            try:
                line = input("sql> " if not buffer else "...> ")

                if line.strip() == ".quit":
                    break

                if not buffer and line.startswith(".read "):
                    path = ROOT / line[6:].strip()
                    run_sql(
                        connection,
                        path.read_text(encoding="utf-8-sig"),
                    )
                    print(f"File executed: {path.name}")
                    continue

                if not buffer and not line.strip():
                    continue

                buffer += line + "\n"

                if sqlite3.complete_statement(buffer):
                    script, buffer = buffer, ""
                    run_sql(connection, script)

            except EOFError:
                break
            except KeyboardInterrupt:
                buffer = ""
                print("\nInput cancelled.")
            except (sqlite3.Error, OSError) as error:
                buffer = ""
                print(f"Error: {error}")
    finally:
        connection.close()


if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["shell"]):
        raise SystemExit("Usage: python main.py shell")
    shell()
