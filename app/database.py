import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()



# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# PostgreSQL SQLAlchemy Configuration (for ORM)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not SUPABASE_URL or not SUPABASE_KEY or not DATABASE_URL:
    raise EnvironmentError("Missing one or more required environment variables: SUPABASE_URL, SUPABASE_KEY, DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)


# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create Base class for models
Base = declarative_base()
# print(engine)
# print(Base)
# print(SessionLocal)
logging.basicConfig(level=logging.INFO)

def get_db():
    db = SessionLocal()
    try:
        logging.info("Database session created successfully")
        yield db
    finally:
        db.close()
        logging.info("Database session closed")

# Optional: Supabase direct query method
def supabase_query(table, method='select', **kwargs):
    try:
        table_query = supabase.table(table)
        if method == 'select':
            response = table_query.select('*', **kwargs).execute()
        elif method == 'insert':
            response = table_query.insert(kwargs).execute()
        elif method == 'update':
            response = table_query.update(kwargs).execute()
        elif method == 'delete':
            response = table_query.delete(**kwargs).execute()
        else:
            raise ValueError(f"Invalid method: {method}")

        if response.get("error"):
            raise Exception(f"Supabase Error: {response['error']}")

        return response
    except Exception as e:
        print(f"Error in Supabase Query: {e}")
        return None
