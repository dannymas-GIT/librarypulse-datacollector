import os
import pytest
from typing import Any, Generator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app


@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    test_db_url = settings.TEST_DATABASE_URL or settings.DATABASE_URL
    engine = create_engine(str(test_db_url))
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = TestSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db) -> Generator[TestClient, None, None]:
    """Create a FastAPI TestClient with the test database session."""
    def _get_test_db():
        try:
            yield db
        finally:
            pass
    
    # Override the get_db dependency
    app.dependency_overrides = {}
    from app.core.deps import get_db
    app.dependency_overrides[get_db] = _get_test_db
    
    with TestClient(app) as test_client:
        yield test_client 