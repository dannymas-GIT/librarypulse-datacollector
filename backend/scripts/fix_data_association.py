#!/usr/bin/env python3
"""
Script to fix the association between datasets and libraries/outlets.
"""
import sys
import logging
from sqlalchemy import create_engine, text, desc, func
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

def check_database_status(session):
    """Check the status of the database tables."""
    try:
        dataset_count = session.query(PLSDataset).count()
        library_count = session.query(Library).count()
        outlet_count = session.query(LibraryOutlet).count()
        config_count = session.query(LibraryConfig).count()
        
        logger.info(f"Database status:")
        logger.info(f"  - Datasets: {dataset_count}")
        logger.info(f"  - Libraries: {library_count}")
        logger.info(f"  - Outlets: {outlet_count}")
        logger.info(f"  - Library configs: {config_count}")
        
        # Check for unassigned libraries and outlets
        unassigned_libraries = session.query(Library).filter(Library.dataset_id.is_(None)).count()
        unassigned_outlets = session.query(LibraryOutlet).filter(LibraryOutlet.dataset_id.is_(None)).count()
        
        logger.info(f"  - Unassigned libraries: {unassigned_libraries}")
        logger.info(f"  - Unassigned outlets: {unassigned_outlets}")
        
        return {
            "dataset_count": dataset_count,
            "library_count": library_count,
            "outlet_count": outlet_count,
            "config_count": config_count,
            "unassigned_libraries": unassigned_libraries,
            "unassigned_outlets": unassigned_outlets
        }
    except Exception as e:
        logger.error(f"Error checking database status: {e}")
        raise

def create_dataset_if_needed(session, year):
    """Create a dataset for the specified year if it doesn't exist."""
    try:
        dataset = session.query(PLSDataset).filter(PLSDataset.year == year).first()
        if dataset:
            logger.info(f"Dataset for year {year} already exists with ID {dataset.id}")
            return dataset
            
        # Count libraries and outlets to get an estimate of record count
        library_count = session.query(func.count(Library.id)).scalar() or 0
        outlet_count = session.query(func.count(LibraryOutlet.id)).scalar() or 0
        
        # Create dataset
        dataset = PLSDataset(
            year=year,
            status="complete",
            record_count=library_count,
            notes=f"Imported real PLS data for fiscal year {year}"
        )
        
        session.add(dataset)
        session.commit()
        
        logger.info(f"Created new dataset for year {year} with ID {dataset.id}")
        return dataset
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating dataset: {e}")
        raise

def associate_libraries_with_dataset(session, dataset_id):
    """Associate all libraries with the specified dataset."""
    try:
        # Count unassigned libraries
        unassigned_count = session.query(Library).filter(Library.dataset_id.is_(None)).count()
        
        if unassigned_count == 0:
            logger.info("No unassigned libraries found")
            return 0
            
        # Update all unassigned libraries
        result = session.execute(
            text(f"UPDATE libraries SET dataset_id = :dataset_id WHERE dataset_id IS NULL"),
            {"dataset_id": dataset_id}
        )
        
        session.commit()
        logger.info(f"Associated {unassigned_count} libraries with dataset ID {dataset_id}")
        return unassigned_count
    except Exception as e:
        session.rollback()
        logger.error(f"Error associating libraries with dataset: {e}")
        raise

def associate_outlets_with_dataset(session, dataset_id):
    """Associate all outlets with the specified dataset."""
    try:
        # Count unassigned outlets
        unassigned_count = session.query(LibraryOutlet).filter(LibraryOutlet.dataset_id.is_(None)).count()
        
        if unassigned_count == 0:
            logger.info("No unassigned outlets found")
            return 0
            
        # Update all unassigned outlets
        result = session.execute(
            text(f"UPDATE library_outlets SET dataset_id = :dataset_id WHERE dataset_id IS NULL"),
            {"dataset_id": dataset_id}
        )
        
        session.commit()
        logger.info(f"Associated {unassigned_count} outlets with dataset ID {dataset_id}")
        return unassigned_count
    except Exception as e:
        session.rollback()
        logger.error(f"Error associating outlets with dataset: {e}")
        raise

def create_library_config_if_needed(session, dataset_id, state_code=None):
    """Create a library configuration if needed."""
    try:
        # Check if a configuration already exists
        config = session.query(LibraryConfig).first()
        if config:
            logger.info(f"Library configuration already exists for {config.library_name}")
            return config
            
        # Find the largest library in the specified state
        query = session.query(Library).filter(Library.dataset_id == dataset_id)
        
        if state_code:
            query = query.filter(Library.state == state_code)
            
        library = query.order_by(desc(Library.service_area_population)).first()
        
        if not library:
            # Try to find any large library
            library = session.query(Library).filter(
                Library.dataset_id == dataset_id
            ).order_by(desc(Library.service_area_population)).first()
            
        if not library:
            logger.error("No suitable library found for configuration")
            return None
            
        logger.info(f"Selected library: {library.name} ({library.library_id}) in {library.state}")
        
        # Create library configuration
        config = LibraryConfig(
            library_id=library.library_id,
            library_name=library.name,
            setup_complete=True,
            collection_stats_enabled=True,
            usage_stats_enabled=True,
            program_stats_enabled=True,
            staff_stats_enabled=True,
            financial_stats_enabled=True,
            collection_metrics={"print_collection": True, "electronic_collection": True},
            usage_metrics={"visits": True, "circulation": True},
            program_metrics={"programs": True, "attendance": True},
            staff_metrics={"total_staff": True, "librarian_staff": True},
            financial_metrics={"revenue": True, "expenditures": True},
            auto_update_enabled=True,
            last_update_check=2021
        )
        
        session.add(config)
        session.commit()
        
        logger.info(f"Created library configuration for {library.name}")
        return config
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating library configuration: {e}")
        raise

def fix_problems(session, year=2021, state=None):
    """Fix all known problems with the database."""
    try:
        # 1. Check current status
        status = check_database_status(session)
        
        # 2. Create dataset if needed
        dataset = create_dataset_if_needed(session, year)
        
        # 3. Associate libraries with dataset
        associate_libraries_with_dataset(session, dataset.id)
        
        # 4. Associate outlets with dataset
        associate_outlets_with_dataset(session, dataset.id)
        
        # 5. Create library configuration if needed
        create_library_config_if_needed(session, dataset.id, state)
        
        # 6. Check status again
        final_status = check_database_status(session)
        
        return final_status
    except Exception as e:
        logger.error(f"Error fixing problems: {e}")
        raise

def main():
    """Main function to fix data associations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix dataset-library-outlet associations")
    parser.add_argument("--year", type=int, default=2021, help="Dataset year (default: 2021)")
    parser.add_argument("--state", type=str, help="State code to select a library from")
    
    args = parser.parse_args()
    
    engine = create_engine_and_connect()
    
    with Session(engine) as session:
        logger.info("Starting database fix operation")
        fix_problems(session, args.year, args.state)
        logger.info("Database fix operation completed")

if __name__ == "__main__":
    main() 