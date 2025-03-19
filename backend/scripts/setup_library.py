#!/usr/bin/env python3
"""
Script to set up a library directly in the database.
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

def setup_library(state="NY", year=2021):
    """Set up a library in the database directly."""
    engine = create_engine(DB_URL)
    with Session(engine) as session:
        try:
            # Clean up existing data
            session.execute(text("DELETE FROM library_config"))
            session.execute(text("DELETE FROM library_outlets"))
            session.execute(text("DELETE FROM libraries"))
            session.execute(text("DELETE FROM pls_datasets"))
            session.commit()
            logger.info("Cleared existing data")
            
            # Create dataset
            dataset = PLSDataset(
                year=year,
                status="complete",
                record_count=1,
                notes=f"Dataset for {year}"
            )
            session.add(dataset)
            session.flush()
            logger.info(f"Created dataset for year {year} with ID {dataset.id}")
            
            # Create library
            library = Library(
                dataset_id=dataset.id,
                library_id=f"{state}0001",
                name=f"{state} Public Library",
                address="123 Main St",
                city="New York",
                state=state,
                zip_code="10001",
                county="New York",
                phone="555-123-4567",
                locale="Urban",
                central_library_count=1,
                branch_library_count=5,
                bookmobile_count=1,
                service_area_population=1000000,
                print_collection=500000
            )
            session.add(library)
            session.flush()
            logger.info(f"Created library {library.name} with ID {library.id}")
            
            # Create outlet
            outlet = LibraryOutlet(
                dataset_id=dataset.id,
                library_id=library.library_id,
                outlet_id="01",
                name=f"{library.name} - Main Branch",
                outlet_type="Central",
                address=library.address,
                city=library.city,
                state=library.state,
                zip_code=library.zip_code,
                county=library.county,
                phone=library.phone,
                square_footage=100000
            )
            session.add(outlet)
            session.flush()
            logger.info(f"Created outlet {outlet.name} with ID {outlet.id}")
            
            # Create library config
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
                last_update_check=year
            )
            session.add(config)
            session.commit()
            logger.info(f"Created library configuration for {library.name}")
            
            logger.info("Library setup completed successfully")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error setting up library: {e}")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up a library directly in the database")
    parser.add_argument("--state", type=str, default="NY", help="State code (default: NY)")
    parser.add_argument("--year", type=int, default=2021, help="Dataset year (default: 2021)")
    
    args = parser.parse_args()
    
    logger.info(f"Setting up library for state {args.state}, year {args.year}")
    success = setup_library(args.state, args.year)
    
    if success:
        logger.info("Library setup completed")
    else:
        logger.error("Library setup failed")
        sys.exit(1) 