#!/usr/bin/env python3
"""
Script to set up library configuration with real data.
"""
import sys
import logging
from sqlalchemy import create_engine, text, desc
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

def setup_library_config(session, library_id=None, state=None):
    """Set up a library configuration with real data."""
    try:
        # Check if a library config already exists
        existing_config = session.query(LibraryConfig).first()
        if existing_config:
            logger.info(f"Library configuration already exists for {existing_config.library_name}. Skipping.")
            return
        
        # Find the most recent dataset
        dataset = session.query(PLSDataset).order_by(desc(PLSDataset.year)).first()
        if not dataset:
            logger.error("No datasets found in the database.")
            return
            
        logger.info(f"Using dataset from year {dataset.year}")
        
        # Find a library to use for configuration
        library = None
        
        if library_id:
            # Try to find the specific library by ID
            library = session.query(Library).filter(
                Library.dataset_id == dataset.id,
                Library.library_id == library_id
            ).first()
            
        if not library and state:
            # Try to find a large library in the specified state
            library = session.query(Library).filter(
                Library.dataset_id == dataset.id,
                Library.state == state
            ).order_by(desc(Library.service_area_population)).first()
            
        if not library:
            # Default to finding a large, well-known library
            for known_library in ["NY0001", "NY0042", "NY0744", "IL0018", "CA0001"]:
                library = session.query(Library).filter(
                    Library.dataset_id == dataset.id,
                    Library.library_id == known_library
                ).first()
                if library:
                    break
                    
        if not library:
            # Fallback to any large library
            library = session.query(Library).filter(
                Library.dataset_id == dataset.id
            ).order_by(desc(Library.service_area_population)).first()
        
        if not library:
            logger.error("No suitable libraries found to use for configuration.")
            return
            
        logger.info(f"Selected library: {library.name} ({library.library_id}) in {library.state}")
        
        # Get available years
        years = [year[0] for year in session.query(PLSDataset.year).order_by(desc(PLSDataset.year)).all()]
        
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
            last_update_check=dataset.year
        )
        
        session.add(config)
        session.commit()
        logger.info(f"Created library configuration for {library.name}.")
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error setting up library configuration: {e}")
        raise

def main():
    """Main function to set up library configuration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up library configuration with real data")
    parser.add_argument("--library-id", type=str, help="Specific library ID to use")
    parser.add_argument("--state", type=str, help="State code to select a library from")
    
    args = parser.parse_args()
    
    engine = create_engine_and_connect()
    
    with Session(engine) as session:
        logger.info("Starting library configuration setup")
        setup_library_config(session, args.library_id, args.state)
        logger.info("Library configuration setup completed")

if __name__ == "__main__":
    main() 