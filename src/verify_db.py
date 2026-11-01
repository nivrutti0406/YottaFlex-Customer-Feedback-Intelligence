
from sqlalchemy import inspect
from src.database import engine

inspector = inspect(engine)

tables = inspector.get_table_names()

print("\nYottaFlex Database Tables")
print("-" * 35)

for table in tables:
    print(table)

print("-" * 35)
print("Total tables:", len(tables))

if len(tables) == 13:
    print("Database verification successful!")
else:
    print("Please check the database schema.")
