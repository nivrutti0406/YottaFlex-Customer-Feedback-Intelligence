from sqlalchemy import inspect
from src.database import engine

inspector = inspect(engine)

tables = [
    "customers",
    "products",
    "channels",
    "sentiment_labels",
    "survey_responses",
    "reviews",
    "support_messages",
    "themes",
    "anomaly_cases"
]

print("\nYOTTAFLEX DATABASE COLUMN REPORT")
print("=" * 50)

for table in tables:
    print(f"\nTABLE: {table}")

    columns = inspector.get_columns(table)

    for column in columns:
        print(
            f"  {column['name']} "
            f"({column['type']})"
        )

print("\nCOLUMN INSPECTION COMPLETED")