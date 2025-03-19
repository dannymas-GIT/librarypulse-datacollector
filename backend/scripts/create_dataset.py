#!/usr/bin/env python3
"""
Script to manually create a dataset record.
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

def create_dataset(session, year):
    """Create a dataset record for the specified year."""
    try:
        # Check if dataset already exists
        existing = session.query(PLSDataset).filter(PLSDataset.year == year).first()
        if existing:
            logger.info(f"Dataset for year {year} already exists with ID {existing.id}. Skipping.")
            return existing
        
        # Count the records for this year
        library_count = session.query(Library).filter(
            text(f"library_id LIKE 'PLS_FY{year}%'")
        ).count()
        
        # Create the dataset
        dataset = PLSDataset(
            year=year,
            status="complete",
            record_count=library_count or 9000,  # Default to 9000 if no records found
            notes=f"Imported PLS data for fiscal year {year}"
        )
        
        session.add(dataset)
        session.commit()
        
        logger.info(f"Created dataset for year {year} with ID {dataset.id}")
        return dataset
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating dataset: {e}")
        raise

def assign_libraries_to_dataset(session, dataset):
    """Assign existing libraries to the dataset."""
    try:
        # Count libraries with no dataset assigned
        count = session.query(Library).filter(Library.dataset_id.is_(None)).count()
        
        if count == 0:
            logger.info("No libraries without dataset assignment found.")
            return 0
            
        # Update libraries to have the dataset ID
        session.execute(
            text(f"UPDATE libraries SET dataset_id = {dataset.id} WHERE dataset_id IS NULL")
        )
        session.commit()
        
        logger.info(f"Assigned {count} libraries to dataset {dataset.id}")
        return count
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error assigning libraries to dataset: {e}")
        raise

def assign_outlets_to_dataset(session, dataset):
    """Assign existing outlets to the dataset."""
    try:
        # Count outlets with no dataset assigned
        count = session.query(LibraryOutlet).filter(LibraryOutlet.dataset_id.is_(None)).count()
        
        if count == 0:
            logger.info("No outlets without dataset assignment found.")
            return 0
            
        # Update outlets to have the dataset ID
        session.execute(
            text(f"UPDATE library_outlets SET dataset_id = {dataset.id} WHERE dataset_id IS NULL")
        )
        session.commit()
        
        logger.info(f"Assigned {count} outlets to dataset {dataset.id}")
        return count
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error assigning outlets to dataset: {e}")
        raise

def main():
    """Main function to create a dataset record."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create a dataset record")
    parser.add_argument("--year", type=int, default=2021, help="Year for the dataset (default: 2021)")
    
    args = parser.parse_args()
    
    engine = create_engine_and_connect()
    
    with Session(engine) as session:
        logger.info(f"Creating dataset for year {args.year}")
        dataset = create_dataset(session, args.year)
        
        if dataset:
            assign_libraries_to_dataset(session, dataset)
            assign_outlets_to_dataset(session, dataset)
            
        logger.info("Dataset creation completed")

if __name__ == "__main__":
    main() 