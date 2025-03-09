from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting a database session.
    Yields a SQLAlchemy Session that is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 