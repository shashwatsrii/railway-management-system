from app.db.base import Base
from app.db.session import engine

def init_database():
    """
    Initialize the database by creating all tables
    """
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")

