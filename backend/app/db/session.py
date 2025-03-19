from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

def get_db():
    """Dependency for getting a database session.

    Yields:
        Session: A SQLAlchemy session that will be closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 