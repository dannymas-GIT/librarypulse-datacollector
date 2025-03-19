#!/usr/bin/env python3
"""
Script to remove all sample data from the database.
"""
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from pathlib import Path
from dotenv import load_dotenv
import os

# Add the parent directory to the path so we can import the app modules
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.append(str(backend_dir))

# Load environment variables
load_dotenv(backend_dir / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import models after adding to path
from app.db.base import Base
from app.models.pls_data import PLSDataset, Library, LibraryOutlet
from app.models.library_config import LibraryConfig

# Database connection - use the environment variable or docker-compose service name
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/librarypulse")

def create_engine_and_connect():
    """Create a database engine and connect."""
    try:
        logger.info(f"Connecting to database at {DB_URL}")
        engine = create_engine(DB_URL)
        return engine
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        sys.exit(1)

def remove_all_sample_data(session):
    """Remove all sample data from the database."""
    try:
        # Remove library configuration
        library_config_count = session.query(LibraryConfig).delete()
        logger.info(f"Removed {library_config_count} library configuration records")
        
        # Remove library outlets - this should cascade delete due to foreign key constraints
        outlet_count = session.query(LibraryOutlet).delete()
        logger.info(f"Removed {outlet_count} library outlet records")
        
        # Remove libraries - this should cascade delete due to foreign key constraints
        library_count = session.query(Library).delete()
        logger.info(f"Removed {library_count} library records")
        
        # Remove datasets - this should cascade delete due to foreign key constraints
        dataset_count = session.query(PLSDataset).delete()
        logger.info(f"Removed {dataset_count} dataset records")
        
        # Commit the transaction
        session.commit()
        
        logger.info("Successfully removed all sample data from the database")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error removing sample data: {e}")
        sys.exit(1)

def main():
    """Main function to remove all sample data from the database."""
    engine = create_engine_and_connect()
    
    with Session(engine) as session:
        logger.info("Starting removal of all sample data from the database")
        remove_all_sample_data(session)
        logger.info("Database cleanup completed")

if __name__ == "__main__":
    main() 