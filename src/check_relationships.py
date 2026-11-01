
from sqlalchemy import inspect
from src.database import engine

inspector = inspect(engine)

print("\nDATABASE RELATIONSHIP REPORT")
print("=" * 45)

for table_name in inspector.get_table_names():
    foreign_keys = inspector.get_foreign_keys(table_name)

    print(f"\nTable: {table_name}")

    if foreign_keys:
        for fk in foreign_keys:
            print(
                f"  {fk['constrained_columns']} "
                f"-> {fk['referred_table']}"
                f".{fk['referred_columns']}"
            )
    else:
        print("  No foreign keys")

print("\nRELATIONSHIP CHECK COMPLETED")
