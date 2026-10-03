# TODO: Implement module logic
from sqlalchemy import create_engine, inspect, text
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


def migrate_sqlite_schema():
    """Apply small additive migrations needed by the local SQLite database."""
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "tickets" not in inspector.get_table_names():
        return

    ticket_columns = {column["name"] for column in inspector.get_columns("tickets")}
    missing_columns = {
        "assigned_group": "VARCHAR",
        "agent_reply": "TEXT",
        "email_delivery_status": "VARCHAR",
        "email_delivery_detail": "TEXT",
        "requires_escalation": "BOOLEAN NOT NULL DEFAULT 0",
        "escalation_reason": "TEXT",
        "ai_summary": "TEXT",
        "knowledge_sources": "JSON",
    }
    for column_name, column_type in missing_columns.items():
        if column_name in ticket_columns:
            continue
        with engine.begin() as connection:
            connection.execute(text(f"ALTER TABLE tickets ADD COLUMN {column_name} {column_type}"))

# Dependency function to use in our API routes to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
