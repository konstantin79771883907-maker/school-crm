"""
Database configuration and session management.

This module handles database connection setup, session creation,
and table initialization for the School Support CRM system.
Uses SQLite for simplicity, but can be easily switched to PostgreSQL.
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# Database URL - using SQLite for simplicity
# For PostgreSQL, change to: "postgresql://user:password@localhost/dbname"
DATABASE_URL = "sqlite:///./school_crm.db"

# Engine configuration
# connect_args needed only for SQLite
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    connect_args={"check_same_thread": False}
)


def create_db_and_tables() -> None:
    """
    Create all database tables defined in SQLModel models.
    
    This function should be called on application startup
    to ensure all tables exist before handling requests.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        Session: SQLModel database session
        
    Usage:
        @app.get("/items/")
        def get_items(session: Session = Depends(get_session)):
            ...
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
