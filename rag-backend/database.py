"""
Database configuration and session management for Neon Postgres
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Use pg8000 driver (pure Python, works on Windows)
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)
    # Remove sslmode parameter as pg8000 doesn't support it
    if "?sslmode=" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.split("?sslmode=")[0]

# Create engine with NullPool for serverless (Neon)
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Best for serverless Postgres
    echo=False,  # Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
