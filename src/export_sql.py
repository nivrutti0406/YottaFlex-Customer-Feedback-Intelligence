
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "data" / "yottaflex.db"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

SQL_FILE = OUTPUT_DIR / "yottaflex_full_dump.sql"


def export_sql():
    connection = sqlite3.connect(DB_FILE)

    try:
        with open(SQL_FILE, "w", encoding="utf-8") as file:
            for line in connection.iterdump():
                file.write(line + "\n")

        print("SQL EXPORT COMPLETED")
        print("SQL file:", SQL_FILE)

    finally:
        connection.close()


if __name__ == "__main__":
    export_sql()
