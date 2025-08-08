
"""
database.py - Database configuration and session management for Job Management API.

This module loads environment variables, sets up the SQLAlchemy engine and session, and provides a dependency function for database access in FastAPI routes.
"""
# Import required modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os



# Load environment variables from .env file for database credentials
load_dotenv()



# Retrieve MySQL connection details from environment variables
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


# Construct the database URL for SQLAlchemy
# Construct the SQLAlchemy database URL (using PyMySQL driver)
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}"


# Create SQLAlchemy engine and session factory
# Create SQLAlchemy engine (handles DB connections)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# Create a session factory for DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base class for ORM models (used for table definitions)
Base = declarative_base()


# Dependency function to get a database session
def get_db():
    """
    Dependency function for FastAPI routes.
    Yields a SQLAlchemy database session and ensures it is closed after use.
    Usage: Add as a dependency in route functions to access the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


