"""
Database engine and session management.
Supports SQLite (dev) and PostgreSQL (production).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from loguru import logger
from dotenv import load_dotenv

from backend.database.schema import Base
from backend.utils.config import get_secret

load_dotenv()

DATABASE_URL = get_secret("DATABASE_URL", "sqlite:///./placement_copilot.db")

# SQLite needs connect_args; PostgreSQL does not
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=get_secret("DEBUG", "False").lower() == "true",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables on startup. Falls back to in-memory if write fails."""
    global engine, SessionLocal
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.warning(f"Failed to initialize physical database: {e}. Falling back to in-memory database...")
        try:
            engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
            SessionLocal.configure(bind=engine)
            Base.metadata.create_all(bind=engine)
            logger.info("In-memory database tables initialized successfully.")
        except Exception as ex:
            logger.error(f"Failed to initialize in-memory database fallback: {ex}")


# Auto-initialize database schema on import
init_db()


def get_db():
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for use outside of dependency injection."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
