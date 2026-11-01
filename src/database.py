
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# SQLite database path
DATABASE_URL = f"sqlite:///{(DATA_DIR / 'yottaflex.db').as_posix()}"

# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create base class for database models
Base = declarative_base()

# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database():
    from src import models

    Base.metadata.create_all(bind=engine)
    print("Database connection successful!")
    print("All database tables created successfully!")


if __name__ == "__main__":
    create_database()