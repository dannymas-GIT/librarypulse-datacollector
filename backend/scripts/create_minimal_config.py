#!/usr/bin/env python3
"""
Script to create a minimal working configuration.
"""
import sys
import logging
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import Session
from pathlib import Path
from dotenv import load_dotenv
import os
import pandas as pd

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
        
        return {
            "dataset_count": dataset_count,
            "library_count": library_count,
            "outlet_count": outlet_count,
            "config_count": config_count
        }
    except Exception as e:
        logger.error(f"Error checking database status: {e}")
        raise

def import_library_from_csv(session, csv_file, state_code):
    """Import a single library from CSV file for the specified state."""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Filter for the specified state and get the largest library by population
        state_libraries = df[df['STABR'] == state_code].sort_values(by='POPU_LSA', ascending=False)
        
        if state_libraries.empty:
            logger.error(f"No libraries found for state {state_code} in {csv_file}")
            return None
            
        # Get the first (largest) library
        library_data = state_libraries.iloc[0]
        
        # Extract library ID
        library_id = library_data.get('FSCSKEY')
        
        # Get or create dataset for 2021
        dataset = session.query(PLSDataset).filter(PLSDataset.year == 2021).first()
        if not dataset:
            dataset = PLSDataset(
                year=2021,
                status="complete",
                record_count=1,
                notes="Imported single library for minimal configuration"
            )
            session.add(dataset)
            session.flush()
            logger.info(f"Created dataset for year 2021 with ID {dataset.id}")
        
        # Check if library already exists
        existing_library = session.query(Library).filter(
            Library.dataset_id == dataset.id,
            Library.library_id == library_id
        ).first()
        
        if existing_library:
            logger.info(f"Library {library_id} already exists with ID {existing_library.id}")
            return existing_library
            
        # Create the library record
        library = Library(
            dataset_id=dataset.id,
            library_id=library_id,
            name=library_data.get('LIBNAME'),
            address=library_data.get('ADDRESS'),
            city=library_data.get('CITY'),
            state=library_data.get('STABR'),
            zip_code=library_data.get('ZIP'),
            county=library_data.get('CNTY'),
            phone=library_data.get('PHONE'),
            service_area_population=library_data.get('POPU_LSA'),
            central_library_count=library_data.get('CENTLIB'),
            branch_library_count=library_data.get('BRANLIB'),
            bookmobile_count=library_data.get('BKMOB')
        )
        
        session.add(library)
        session.commit()
        
        logger.info(f"Created library record for {library.name} ({library.library_id})")
        return library
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error importing library from CSV: {e}")
        raise

def import_outlets_for_library(session, csv_file, library):
    """Import outlets for a specific library from CSV file."""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Filter for the specified library
        library_outlets = df[df['FSCSKEY'] == library.library_id]
        
        if library_outlets.empty:
            logger.error(f"No outlets found for library {library.library_id} in {csv_file}")
            return []
            
        # Get dataset
        dataset = session.query(PLSDataset).get(library.dataset_id)
        if not dataset:
            logger.error(f"Dataset with ID {library.dataset_id} not found")
            return []
            
        outlets_created = []
        
        # Process each outlet
        for _, outlet_data in library_outlets.iterrows():
            # Extract outlet ID
            outlet_id = outlet_data.get('FSCS_SEQ')
            
            # Check if outlet already exists
            existing_outlet = session.query(LibraryOutlet).filter(
                LibraryOutlet.dataset_id == dataset.id,
                LibraryOutlet.library_id == library.library_id,
                LibraryOutlet.outlet_id == outlet_id
            ).first()
            
            if existing_outlet:
                logger.info(f"Outlet {outlet_id} already exists with ID {existing_outlet.id}")
                outlets_created.append(existing_outlet)
                continue
                
            # Create the outlet record
            outlet = LibraryOutlet(
                dataset_id=dataset.id,
                library_id=library.library_id,
                outlet_id=outlet_id,
                name=outlet_data.get('LIBNAME'),
                outlet_type=outlet_data.get('STATSTRU'),
                address=outlet_data.get('ADDRESS'),
                city=outlet_data.get('CITY'),
                state=outlet_data.get('STABR'),
                zip_code=outlet_data.get('ZIP'),
                county=outlet_data.get('CNTY'),
                phone=outlet_data.get('PHONE'),
                square_footage=outlet_data.get('SQ_FEET')
            )
            
            session.add(outlet)
            outlets_created.append(outlet)
            
        session.commit()
        
        logger.info(f"Created {len(outlets_created)} outlet records for library {library.library_id}")
        return outlets_created
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error importing outlets from CSV: {e}")
        raise

def create_library_config(session, library):
    """Create a library configuration for the specified library."""
    try:
        # Check if a configuration already exists
        existing_config = session.query(LibraryConfig).first()
        if existing_config:
            logger.info(f"Library configuration already exists for {existing_config.library_name}. Skipping.")
            return existing_config
            
        # Get dataset
        dataset = session.query(PLSDataset).get(library.dataset_id)
        if not dataset:
            logger.error(f"Dataset with ID {library.dataset_id} not found")
            return None
            
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
            last_update_check=dataset.year
        )
        
        session.add(config)
        session.commit()
        
        logger.info(f"Created library configuration for {library.name}")
        return config
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating library configuration: {e}")
        raise

def create_minimal_configuration(session, year=2021, state="NY"):
    """Create a minimal working configuration."""
    try:
        # 1. Check current status
        check_database_status(session)
        
        # 2. Clear all existing data
        if session.query(LibraryConfig).count() > 0:
            session.execute(text("DELETE FROM library_config"))
            logger.info("Cleared existing library configuration")
            
        if session.query(LibraryOutlet).count() > 0:
            session.execute(text("DELETE FROM library_outlets"))
            logger.info("Cleared existing library outlets")
            
        if session.query(Library).count() > 0:
            session.execute(text("DELETE FROM libraries"))
            logger.info("Cleared existing libraries")
            
        if session.query(PLSDataset).count() > 0:
            session.execute(text("DELETE FROM pls_datasets"))
            logger.info("Cleared existing datasets")
            
        session.commit()
        
        # 3. Set up paths to data files
        library_csv = f"/app/data/{year}/pls_{year}_library.csv"
        outlet_csv = f"/app/data/{year}/pls_{year}_outlet.csv"
        
        if not os.path.exists(library_csv):
            logger.error(f"Library CSV file not found: {library_csv}")
            return None
            
        if not os.path.exists(outlet_csv):
            logger.error(f"Outlet CSV file not found: {outlet_csv}")
            return None
            
        # 4. Import single library
        library = import_library_from_csv(session, library_csv, state)
        if not library:
            logger.error(f"Failed to import library for state {state}")
            return None
            
        # 5. Import outlets for the library
        outlets = import_outlets_for_library(session, outlet_csv, library)
        
        # 6. Create library configuration
        config = create_library_config(session, library)
        
        # 7. Check final status
        check_database_status(session)
        
        return {
            "library": library,
            "outlets": outlets,
            "config": config
        }
        
    except Exception as e:
        logger.error(f"Error creating minimal configuration: {e}")
        raise

def main():
    """Main function to create a minimal working configuration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create a minimal working configuration")
    parser.add_argument("--year", type=int, default=2021, help="Dataset year (default: 2021)")
    parser.add_argument("--state", type=str, default="NY", help="State code (default: NY)")
    
    args = parser.parse_args()
    
    engine = create_engine_and_connect()
    
    with Session(engine) as session:
        logger.info(f"Creating minimal configuration for year {args.year}, state {args.state}")
        create_minimal_configuration(session, args.year, args.state)
        logger.info("Minimal configuration creation completed")

if __name__ == "__main__":
    main() 