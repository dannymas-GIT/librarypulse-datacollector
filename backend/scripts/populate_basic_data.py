#!/usr/bin/env python3
"""
Script to populate the database with basic sample library data.
"""
import sys
import logging
from sqlalchemy import create_engine
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

def populate_datasets(session):
    """Populate the pls_datasets table with sample data."""
    try:
        # Check if any datasets already exist
        if session.query(PLSDataset).count() > 0:
            logger.info("Datasets already exist in the database, skipping.")
            return
        
        # Create sample datasets
        datasets = [
            PLSDataset(year=2022, status="complete", record_count=9000),
            PLSDataset(year=2021, status="complete", record_count=9002),
            PLSDataset(year=2020, status="complete", record_count=8998)
        ]
        
        for dataset in datasets:
            session.add(dataset)
        
        session.commit()
        logger.info(f"Added {len(datasets)} datasets to the database.")
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding datasets: {e}")

def populate_libraries(session):
    """Populate the libraries table with sample data."""
    try:
        # Check if any libraries already exist
        if session.query(Library).count() > 0:
            logger.info("Libraries already exist in the database, skipping.")
            return
        
        # Get dataset IDs
        datasets = session.query(PLSDataset).all()
        if not datasets:
            logger.error("No datasets found. Please run populate_datasets first.")
            return
        
        # Create sample libraries for each dataset
        libraries = []
        for dataset in datasets:
            # New York Public Library
            libraries.append(
                Library(
                    dataset_id=dataset.id,
                    library_id="NY0001",
                    name="New York Public Library",
                    address="476 5th Ave",
                    city="New York",
                    state="NY",
                    zip_code="10018",
                    county="New York",
                    phone="212-930-0800",
                    locale="Urban",
                    central_library_count=1,
                    branch_library_count=92,
                    bookmobile_count=0,
                    service_area_population=3500000,
                    print_collection=8500000
                )
            )
            
            # Chicago Public Library
            libraries.append(
                Library(
                    dataset_id=dataset.id,
                    library_id="IL0001",
                    name="Chicago Public Library",
                    address="400 S State St",
                    city="Chicago",
                    state="IL",
                    zip_code="60605",
                    county="Cook",
                    phone="312-747-4300",
                    locale="Urban",
                    central_library_count=1,
                    branch_library_count=80,
                    bookmobile_count=1,
                    service_area_population=2700000,
                    print_collection=5400000
                )
            )
            
            # Los Angeles Public Library
            libraries.append(
                Library(
                    dataset_id=dataset.id,
                    library_id="CA0001",
                    name="Los Angeles Public Library",
                    address="630 W 5th St",
                    city="Los Angeles",
                    state="CA",
                    zip_code="90071",
                    county="Los Angeles",
                    phone="213-228-7000",
                    locale="Urban",
                    central_library_count=1,
                    branch_library_count=72,
                    bookmobile_count=2,
                    service_area_population=3900000,
                    print_collection=6200000
                )
            )
            
            # Boston Public Library
            libraries.append(
                Library(
                    dataset_id=dataset.id,
                    library_id="MA0001",
                    name="Boston Public Library",
                    address="700 Boylston St",
                    city="Boston",
                    state="MA",
                    zip_code="02116",
                    county="Suffolk",
                    phone="617-536-5400",
                    locale="Urban",
                    central_library_count=1,
                    branch_library_count=25,
                    bookmobile_count=1,
                    service_area_population=694583,
                    print_collection=1900000
                )
            )
            
            # Seattle Public Library
            libraries.append(
                Library(
                    dataset_id=dataset.id,
                    library_id="WA0001",
                    name="Seattle Public Library",
                    address="1000 4th Ave",
                    city="Seattle",
                    state="WA",
                    zip_code="98104",
                    county="King",
                    phone="206-386-4636",
                    locale="Urban",
                    central_library_count=1,
                    branch_library_count=26,
                    bookmobile_count=0,
                    service_area_population=724745,
                    print_collection=1200000
                )
            )
        
        for library in libraries:
            session.add(library)
        
        session.commit()
        logger.info(f"Added {len(libraries)} libraries to the database.")
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding libraries: {e}")

def populate_outlets(session):
    """Populate the library_outlets table with sample data."""
    try:
        # Check if any outlets already exist
        if session.query(LibraryOutlet).count() > 0:
            logger.info("Library outlets already exist in the database, skipping.")
            return
        
        # Get libraries
        libraries = session.query(Library).all()
        if not libraries:
            logger.error("No libraries found. Please run populate_libraries first.")
            return
        
        # Create sample outlets for each library
        outlets = []
        for library in libraries:
            # Create an outlet ID for the main branch (typically 01)
            main_outlet_id = "01"
            
            # Main branch
            outlets.append(
                LibraryOutlet(
                    dataset_id=library.dataset_id,
                    library_id=library.library_id,
                    outlet_id=main_outlet_id,
                    name=f"{library.name} - Main Branch",
                    address=library.address,
                    city=library.city,
                    state=library.state,
                    zip_code=library.zip_code,
                    county=library.county,
                    phone=library.phone,
                    outlet_type="Central",
                    square_footage=250000,
                    hours_open=70  # Weekly hours
                )
            )
            
            # Branch 1
            outlets.append(
                LibraryOutlet(
                    dataset_id=library.dataset_id,
                    library_id=library.library_id,
                    outlet_id="02",
                    name=f"{library.name} - Downtown Branch",
                    address=f"123 Main St",
                    city=library.city,
                    state=library.state,
                    zip_code=library.zip_code,
                    county=library.county,
                    phone="555-123-4567",
                    outlet_type="Branch",
                    square_footage=15000,
                    hours_open=60  # Weekly hours
                )
            )
            
            # Branch 2
            outlets.append(
                LibraryOutlet(
                    dataset_id=library.dataset_id,
                    library_id=library.library_id,
                    outlet_id="03",
                    name=f"{library.name} - North Branch",
                    address=f"456 Park Ave",
                    city=library.city,
                    state=library.state,
                    zip_code=library.zip_code,
                    county=library.county,
                    phone="555-987-6543",
                    outlet_type="Branch",
                    square_footage=12000,
                    hours_open=56  # Weekly hours
                )
            )
        
        for outlet in outlets:
            session.add(outlet)
        
        session.commit()
        logger.info(f"Added {len(outlets)} library outlets to the database.")
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding library outlets: {e}")

def setup_library_config(session):
    """Set up a basic library configuration."""
    try:
        # Check if a library config already exists
        if session.query(LibraryConfig).count() > 0:
            logger.info("Library configuration already exists, skipping.")
            return
        
        # Get a library to use for configuration
        library = session.query(Library).filter(Library.state == "NY").first()
        if not library:
            logger.error("No libraries found to use for configuration.")
            return
        
        # Create library configuration with default settings
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
            last_update_check=2022
        )
        
        session.add(config)
        session.commit()
        logger.info(f"Created library configuration for {library.name}.")
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error setting up library configuration: {e}")

def main():
    """Main function to populate the database with basic sample data."""
    engine = create_engine_and_connect()
    
    with Session(engine) as session:
        logger.info("Starting database population.")
        
        populate_datasets(session)
        populate_libraries(session)
        populate_outlets(session)
        setup_library_config(session)
        
        logger.info("Database population completed.")

if __name__ == "__main__":
    main() 