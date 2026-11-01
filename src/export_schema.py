from sqlalchemy.schema import CreateTable
from src.database import engine, Base
from src import models

output_file = "schema/schema.sql"

with open(output_file, "w", encoding="utf-8") as file:

    file.write("-- YottaFlex Database Schema\n")
    file.write("-- Generated from SQLAlchemy ORM Models\n\n")

    for table in Base.metadata.sorted_tables:

        ddl = str(
            CreateTable(table).compile(
                dialect=engine.dialect
            )
        )

        file.write(ddl + ";\n\n")

print("SCHEMA EXPORT COMPLETED")
print(f"Schema file: {output_file}")
print(f"Total tables: {len(Base.metadata.tables)}")