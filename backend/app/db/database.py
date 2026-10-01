# TODO: Implement module logic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# `check_same_thread` is specifically required for SQLite in FastAPI
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL, connect_args=connect_args
)

# This creates a database session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All our database models will inherit from this Base class
Base = declarative_base()

# Dependency function to use in our API routes to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()