"""
Database Configuration and Connection Management

This module handles database connectivity, session management, and provides
the base declarative class for SQLAlchemy ORM models.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
import os
from typing import Generator
import logging

# Configure logging for database operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Database connection parameters from environment variables
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# Validate required environment variables
required_env_vars = {
    "MYSQL_USER": MYSQL_USER,
    "MYSQL_PASSWORD": MYSQL_PASSWORD,
    "MYSQL_DATABASE": MYSQL_DATABASE
}

missing_vars = [var for var, value in required_env_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Construct database URL for MySQL with PyMySQL driver
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Create database engine with connection pooling and health checks
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Validate connections before use
    poolclass=QueuePool,  # Use connection pooling
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Additional connections beyond pool_size
    pool_recycle=3600,  # Recycle connections every hour
    echo=False  # Set to True for SQL query debugging
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,  # Explicit transaction control
    autoflush=False,   # Manual flush control
    bind=engine
)

# Base class for all ORM models
Base = declarative_base()

def get_db() -> Generator:
    """
    Database dependency for FastAPI endpoints.
    
    This function creates a database session, yields it to the calling function,
    and ensures proper cleanup by closing the session after use.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        logger.debug("Closing database session")
        db.close()

def create_tables():
    """
    Create all database tables based on defined models.
    
    This function should be called during application startup
    to ensure all required tables exist in the database.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_engine():
    """
    Get the database engine instance.
    
    Returns:
        Engine: SQLAlchemy database engine
    """
    return engine


