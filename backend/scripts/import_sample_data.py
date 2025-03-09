#!/usr/bin/env python3
"""
Script to import sample PLS data into the database.
"""
import os
import sys
import logging
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Database connection
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/librarypulse")

def create_engine_with_retry(db_url, max_retries=3):
    """Create a database engine with retry logic."""
    for attempt in range(max_retries):
        try:
            engine = create_engine(db_url)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except SQLAlchemyError as e:
            logger.error(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
    
    raise Exception("Failed to connect to database after multiple attempts")

def import_library_data(engine, csv_file, year):
    """Import library data from CSV file into the database."""
    logger.info(f"Importing library data from {csv_file}")
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)
        
        # Clean column names
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Add year column if not present
        if 'year' not in df.columns:
            df['year'] = year
        
        # Insert into database
        df.to_sql('pls_libraries', engine, if_exists='append', index=False)
        
        logger.info(f"Successfully imported {len(df)} library records")
        return True
    
    except Exception as e:
        logger.error(f"Error importing library data: {e}")
        return False

def import_outlet_data(engine, csv_file, year):
    """Import outlet data from CSV file into the database."""
    logger.info(f"Importing outlet data from {csv_file}")
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)
        
        # Clean column names
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Add year column if not present
        if 'year' not in df.columns:
            df['year'] = year
        
        # Insert into database
        df.to_sql('pls_outlets', engine, if_exists='append', index=False)
        
        logger.info(f"Successfully imported {len(df)} outlet records")
        return True
    
    except Exception as e:
        logger.error(f"Error importing outlet data: {e}")
        return False

def create_tables_if_not_exist(engine):
    """Create necessary tables if they don't exist."""
    try:
        # Create pls_libraries table
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS pls_libraries (
                    id SERIAL PRIMARY KEY,
                    libid VARCHAR(20),
                    libname VARCHAR(255),
                    address VARCHAR(255),
                    city VARCHAR(100),
                    zip VARCHAR(20),
                    phone VARCHAR(20),
                    county VARCHAR(100),
                    state VARCHAR(100),
                    stabr VARCHAR(2),
                    fscskey VARCHAR(20),
                    fscs_seq VARCHAR(20),
                    libtype VARCHAR(20),
                    c_admin VARCHAR(20),
                    c_fscs VARCHAR(20),
                    geocode VARCHAR(20),
                    lsabound VARCHAR(20),
                    startdat VARCHAR(20),
                    enddate VARCHAR(20),
                    popu_lsa INTEGER,
                    centlib INTEGER,
                    branlib INTEGER,
                    bkmob INTEGER,
                    totstaff NUMERIC,
                    libraria NUMERIC,
                    totincm NUMERIC,
                    totexpco NUMERIC,
                    visits NUMERIC,
                    referenc NUMERIC,
                    totcir NUMERIC,
                    totcoll NUMERIC,
                    year INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create pls_outlets table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS pls_outlets (
                    id SERIAL PRIMARY KEY,
                    libid VARCHAR(20),
                    libname VARCHAR(255),
                    fscskey VARCHAR(20),
                    fscs_seq VARCHAR(20),
                    stabr VARCHAR(2),
                    statname VARCHAR(100),
                    address VARCHAR(255),
                    city VARCHAR(100),
                    zip VARCHAR(20),
                    phone VARCHAR(20),
                    c_out_ty VARCHAR(20),
                    c_fscs VARCHAR(20),
                    hours NUMERIC,
                    sq_feet INTEGER,
                    locale VARCHAR(20),
                    county VARCHAR(100),
                    countynm VARCHAR(100),
                    year INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create indexes for faster queries
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_libraries_fscskey ON pls_libraries(fscskey)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_libraries_year ON pls_libraries(year)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_outlets_fscskey ON pls_outlets(fscskey)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_outlets_year ON pls_outlets(year)"))
            
            logger.info("Database tables created or already exist")
            return True
    
    except SQLAlchemyError as e:
        logger.error(f"Error creating tables: {e}")
        return False

def main():
    """Main function to import sample PLS data."""
    # Get year from command line or use default
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2021
    
    # Path to sample data directory
    data_dir = Path(__file__).parent.parent / "data" / "sample"
    
    if not data_dir.exists():
        logger.error(f"Sample data directory {data_dir} does not exist. Please generate sample data first.")
        return
    
    try:
        # Connect to database
        engine = create_engine_with_retry(DB_URL)
        
        # Create tables if they don't exist
        if not create_tables_if_not_exist(engine):
            return
        
        # Import library data
        library_file = data_dir / f"pls_sample_{year}_library.csv"
        if library_file.exists():
            import_library_data(engine, library_file, year)
        else:
            logger.error(f"Library data file {library_file} not found")
        
        # Import outlet data
        outlet_file = data_dir / f"pls_sample_{year}_outlet.csv"
        if outlet_file.exists():
            import_outlet_data(engine, outlet_file, year)
        else:
            logger.error(f"Outlet data file {outlet_file} not found")
        
        logger.info(f"Import process completed for year {year}")
    
    except Exception as e:
        logger.error(f"Error during import process: {e}")

if __name__ == "__main__":
    main() 