"""
Database connection and session management.

Read DATABASE_URL from environment variable.
Create SQLAlchemy engine and session.
Provide a dependency for FastAPI to get a DB session.
"""

# TODO: Implement database connection here

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()