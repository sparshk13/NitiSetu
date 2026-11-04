import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import settings

logger = logging.getLogger("nitisetu.db")

Base = declarative_base()

def get_engine():
    db_url = settings.database_url
    if not db_url:
        # Fallback to local SQLite for immediate offline execution or unit tests
        db_url = "sqlite:///./nitisetu.db"
        logger.info(f"DATABASE_URL not set. Defaulting to local storage: {db_url}")
        return create_engine(db_url, connect_args={"check_same_thread": False})
    
    # Handle postgres protocol alias if needed
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    return create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800
    )

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """FastAPI dependency to yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

