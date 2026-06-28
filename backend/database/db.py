"""
Database engine and session management.
Supports SQLite (dev) and PostgreSQL (production).
"""
import os
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from loguru import logger
from dotenv import load_dotenv

from backend.database.schema import Base
from backend.utils.config import get_secret

load_dotenv()

DATABASE_URL = get_secret("DATABASE_URL", "sqlite:///./placement_copilot.db")

_db_lock = threading.Lock()
engine = None
SessionLocal = None

def _get_engine_and_sessionmaker():
    """Thread-safe lazy initialization of engine and sessionmaker."""
    global engine, SessionLocal
    if engine is None or SessionLocal is None:
        with _db_lock:
            if engine is None or SessionLocal is None:
                connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
                engine = create_engine(
                    DATABASE_URL,
                    connect_args=connect_args,
                    echo=get_secret("DEBUG", "False").lower() == "true",
                )
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


def init_db() -> None:
    """Create all tables on startup. Falls back to in-memory if write fails."""
    global engine, SessionLocal
    _, sessionmaker_local = _get_engine_and_sessionmaker()
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.warning(f"Failed to initialize physical database: {e}. Falling back to in-memory database...")
        with _db_lock:
            try:
                engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                Base.metadata.create_all(bind=engine)
                logger.info("In-memory database tables initialized successfully.")
            except Exception as ex:
                logger.error(f"Failed to initialize in-memory database fallback: {ex}")


def get_db():
    """Dependency that yields a database session."""
    _, sessionmaker_local = _get_engine_and_sessionmaker()
    db = sessionmaker_local()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for use outside of dependency injection."""
    _, sessionmaker_local = _get_engine_and_sessionmaker()
    db = sessionmaker_local()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
