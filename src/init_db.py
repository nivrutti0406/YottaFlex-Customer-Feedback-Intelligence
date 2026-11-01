
from src.database import Base, engine
from src import models

def initialize_database():
    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully!")
    print("All tables created successfully!")

if __name__ == "__main__":
    initialize_database()
