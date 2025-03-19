import os
import pytest
from typing import Any, Generator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings, Settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app

# Test settings
test_settings = Settings(
    DATABASE_URL="postgresql://postgres:postgres@localhost:5432/librarypulse_test",
    TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/librarypulse_test",
    SECRET_KEY="test_secret_key",
    ACCESS_TOKEN_EXPIRE_MINUTES=5,
    EMAILS_ENABLED=False,
    CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"],
    DEBUG=True,
    ENVIRONMENT="test",
    REDIS_URL="redis://localhost:6379/1"
)

# Override settings in app
app.state.settings = test_settings

# Create test database engine
engine = create_engine(str(test_settings.TEST_DATABASE_URL))
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


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