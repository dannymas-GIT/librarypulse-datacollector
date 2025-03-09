"""
Script to initialize the database.
"""
import logging
import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.models.pls_data import PLSDataset, Library, LibraryOutlet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Initialize the database with tables and initial data.
    """
    try:
        # Create engine
        engine = create_engine(str(settings.DATABASE_URL))
        
        # Create tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Run Alembic migrations
        logger.info("Running Alembic migrations...")
        alembic_cfg = Config(os.path.join(Path(__file__).parent, "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))
        command.upgrade(alembic_cfg, "head")
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if we need to add initial data
        if db.query(PLSDataset).count() == 0:
            logger.info("Adding initial data...")
            # Add a placeholder dataset for testing
            dataset = PLSDataset(
                year=2022,
                status="pending",
                record_count=0,
                notes="Initial placeholder dataset"
            )
            db.add(dataset)
            db.commit()
            logger.info(f"Added placeholder dataset for year {dataset.year}")
        
        db.close()
        logger.info("Database initialization complete")
        
    except ProgrammingError as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db() 