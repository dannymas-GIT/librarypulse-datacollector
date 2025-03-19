import os
import pytest
from typing import Any, Generator
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings, Settings
from app.db.base import Base
from app.db.session import SessionLocal, engine, get_db
from app.main import app
from app.api.deps import get_db

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

# Test database URL
TEST_DATABASE_URL = settings.TEST_DATABASE_URL

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create tables
Base.metadata.create_all(bind=test_engine)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def async_db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.fixture
def db_session():
    """Fixture that provides a test database session."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Return the session to the test
    yield session
    
    # Clean up after the test
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Fixture that provides a test client with overridden dependencies."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up after the test
    app.dependency_overrides.clear()

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
    app.dependency_overrides[get_db] = _get_test_db
    
    with TestClient(app) as test_client:
        yield test_client 