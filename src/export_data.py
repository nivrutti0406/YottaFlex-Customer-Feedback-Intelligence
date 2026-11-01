
import json
import csv
from pathlib import Path
from sqlalchemy import inspect

from src.database import engine

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)


def export_data():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    for table_name in table_names:
        with engine.connect() as connection:
            result = connection.exec_driver_sql(
                f'SELECT * FROM "{table_name}"'
            )

            columns = list(result.keys())
            rows = [dict(row._mapping) for row in result.fetchall()]

        # Export CSV
        csv_file = OUTPUT_DIR / f"{table_name}.csv"

        with open(csv_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

        # Export JSON
        json_file = OUTPUT_DIR / f"{table_name}.json"

        with open(json_file, "w", encoding="utf-8") as file:
            json.dump(rows, file, indent=4, default=str)

        print(f"Exported: {table_name}")

    print("\nDATA EXPORT COMPLETED")
    print("Total tables exported:", len(table_names))
    print("Output folder:", OUTPUT_DIR)


if __name__ == "__main__":
    export_data()
