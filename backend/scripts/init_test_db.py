from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.models import *  # noqa

def init_test_db():
    """Initialize test database with schema."""
    engine = create_engine(settings.TEST_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Add any initial test data here if needed
        pass
    finally:
        db.close()

if __name__ == "__main__":
    init_test_db() 