
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

from sqlalchemy import inspect, text
from src.database import engine

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

SEED = 20261022


def generate_manifest():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    table_counts = {}

    with engine.connect() as connection:
        for table in table_names:
            count = connection.execute(
                text(f'SELECT COUNT(*) FROM "{table}"')
            ).scalar()

            table_counts[table] = count

    manifest = {
        "project_name": "YottaFlex Feedback Intelligence",
        "description": "Synthetic customer feedback intelligence dataset",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "random_seed": SEED,
        "python_version": sys.version,
        "data_source": {
            "type": "synthetic",
            "description": "Generated using Python and Faker",
            "real_customer_data_used": False
        },
        "generation_scripts": [
            "src/generate_master.py",
            "src/generate_feedback.py",
            "src/generate_support.py",
            "src/inject_anomalies.py"
        ],
        "database": {
            "file": "data/yottaflex.db",
            "total_tables": len(table_names),
            "table_record_counts": table_counts
        },
        "exports": {
            "directory": "outputs",
            "formats": ["CSV", "JSON", "SQL"]
        },
        "privacy": {
            "synthetic_data_only": True,
            "real_personal_information": False
        },
        "reproducibility": {
            "fixed_random_seed": SEED,
            "database_file": "data/yottaflex.db"
        }
    }

    manifest_file = OUTPUT_DIR / "source_manifest.json"

    with open(manifest_file, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)

    print("SOURCE MANIFEST GENERATED SUCCESSFULLY!")
    print("Total tables:", len(table_names))
    print("Manifest file:", manifest_file)


if __name__ == "__main__":
    generate_manifest()
