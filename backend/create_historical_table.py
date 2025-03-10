"""
Script to create a historical data table for West Babylon Public Library.
This script creates a new table specifically for historical data and populates it
with synthetic data from 1988 to present.
"""
import logging
import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("historical_import.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
WEST_BABYLON_ID = "NY0773"
START_YEAR = 1988
END_YEAR = datetime.now().year - 1  # Last year
DATA_DIR = Path("data/historical")
DB_PARAMS = {
    "dbname": "librarypulse",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

# Base data for West Babylon Library in recent years (2022)
BASE_LIBRARY_DATA = {
    "name": "West Babylon Public Library",
    "address": "211 Route 109",
    "city": "West Babylon",
    "state": "NY",
    "zip_code": "11704",
    "county": "Suffolk",
    "phone": "631-669-5445",
    "central_library_count": 1,
    "branch_library_count": 0, 
    "bookmobile_count": 0,
    "service_area_population": 43000,
    "print_collection": 115000,
    "electronic_collection": 25000,
    "audio_collection": 12000,
    "video_collection": 18000,
    "total_circulation": 210000,
    "electronic_circulation": 75000,
    "physical_circulation": 135000,
    "visits": 175000,
    "reference_transactions": 15000,
    "registered_users": 25000,
    "public_internet_computers": 40,
    "public_wifi_sessions": 50000,
    "website_visits": 180000,
    "total_programs": 420,
    "total_program_attendance": 8500,
    "children_programs": 200,
    "children_program_attendance": 4000,
    "ya_programs": 80,
    "ya_program_attendance": 1500,
    "adult_programs": 140, 
    "adult_program_attendance": 3000,
    "total_staff": 42.5,
    "librarian_staff": 12.5,
    "mls_librarian_staff": 10.0,
    "other_staff": 30.0,
    "total_operating_revenue": 3750000,
    "local_operating_revenue": 3400000,
    "state_operating_revenue": 300000,
    "federal_operating_revenue": 20000,
    "other_operating_revenue": 30000,
    "total_operating_expenditures": 3600000,
    "staff_expenditures": 2400000,
    "collection_expenditures": 500000
}

def ensure_dirs():
    """Ensure data directories exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return True

def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        conn.autocommit = False
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def generate_synthetic_data(year):
    """
    Generate synthetic data for West Babylon Public Library for a specific year.
    Uses base data with realistic growth trends.
    """
    logger.info(f"Generating synthetic data for {year}")
    
    # Copy base data
    library_data = BASE_LIBRARY_DATA.copy()
    
    # Calculate year difference from 2022 (our base year)
    year_diff = 2022 - year
    
    # Skip if we're trying to generate data for the future
    if year_diff < 0:
        library_data = adjust_future_data(library_data, abs(year_diff))
    else:
        # Adjust data based on historical trends
        library_data = adjust_historical_data(library_data, year_diff, year)
    
    # Add consistent identifiers and year
    library_data["library_id"] = WEST_BABYLON_ID
    library_data["year"] = year
    
    # Add random noise to make data look natural (±3%)
    for key in library_data:
        if isinstance(library_data[key], (int, float)) and library_data[key] > 0:
            if key not in ['central_library_count', 'branch_library_count', 'bookmobile_count', 'year']:
                noise = random.uniform(0.97, 1.03)
                library_data[key] = int(library_data[key] * noise) if isinstance(library_data[key], int) else round(library_data[key] * noise, 1)
    
    # Ensure consistency in derived values
    if 'electronic_circulation' in library_data and 'physical_circulation' in library_data:
        if 'total_circulation' in library_data:
            # Make sure elec_circ + phys_circ = total_circ
            library_data['total_circulation'] = library_data['electronic_circulation'] + library_data['physical_circulation']
    
    if 'children_program_attendance' in library_data and 'ya_program_attendance' in library_data and 'adult_program_attendance' in library_data:
        if 'total_program_attendance' in library_data:
            # Make sure program attendance adds up
            library_data['total_program_attendance'] = (
                library_data['children_program_attendance'] + 
                library_data['ya_program_attendance'] + 
                library_data['adult_program_attendance']
            )
    
    if 'children_programs' in library_data and 'ya_programs' in library_data and 'adult_programs' in library_data:
        if 'total_programs' in library_data:
            # Make sure program counts add up
            library_data['total_programs'] = (
                library_data['children_programs'] + 
                library_data['ya_programs'] + 
                library_data['adult_programs']
            )
    
    logger.info(f"Generated synthetic data for {year}")
    
    return library_data

def adjust_historical_data(data, year_diff, actual_year):
    """Adjust data for historical trends based on years before 2022."""
    # Make a copy to avoid modifying the input
    result = data.copy()
    
    # Population change (slight growth over time)
    if 'service_area_population' in result:
        if actual_year < 2000:
            result['service_area_population'] = int(result['service_area_population'] * (0.9 - (year_diff - 22) * 0.005))
        elif actual_year < 2010:
            result['service_area_population'] = int(result['service_area_population'] * (0.9 + (actual_year - 2000) * 0.01))
        else:
            result['service_area_population'] = int(result['service_area_population'] * (1.0 - (year_diff) * 0.005))
    
    # Electronic collection - non-existent before 2000, then growing rapidly
    if 'electronic_collection' in result:
        if actual_year < 1995:
            result['electronic_collection'] = 0
        elif actual_year < 2000:
            result['electronic_collection'] = int((actual_year - 1995) * 100)  # Very minimal
        elif actual_year < 2010:
            result['electronic_collection'] = int((actual_year - 2000) * 1000)  # Growing
        else:
            result['electronic_collection'] = int(result['electronic_collection'] * (0.4 - (year_diff - 12) * 0.03))  # Rapid recent growth
    
    # Electronic circulation - follows similar pattern to collection
    if 'electronic_circulation' in result:
        if actual_year < 2000:
            result['electronic_circulation'] = 0
        elif actual_year < 2010:
            result['electronic_circulation'] = int(result['electronic_circulation'] * 0.1 * (actual_year - 2000) / 10)
        else:
            result['electronic_circulation'] = int(result['electronic_circulation'] * (0.4 - (year_diff - 12) * 0.03))
    
    # Physical circulation changes
    if 'physical_circulation' in result:
        if actual_year < 2000:
            result['physical_circulation'] = int(result['total_circulation'] * (0.8 + (actual_year - 1988) * 0.01))
        elif actual_year < 2010:
            result['physical_circulation'] = int(result['total_circulation'] * (0.95 - (actual_year - 2000) * 0.005))
        elif actual_year < 2019:
            result['physical_circulation'] = int(result['physical_circulation'] * (1.1 + (year_diff - 12) * 0.01))
        else:  # COVID impact
            result['physical_circulation'] = int(result['physical_circulation'] * 0.7)
    
    # Print collection changes - growing until 2010, then slight decline
    if 'print_collection' in result:
        if actual_year < 2000:
            result['print_collection'] = int(result['print_collection'] * (0.7 + (actual_year - 1988) * 0.015))
        elif actual_year < 2010:
            result['print_collection'] = int(result['print_collection'] * (0.85 + (actual_year - 2000) * 0.015))
        else:
            result['print_collection'] = int(result['print_collection'] * (1.0 + (year_diff - 12) * 0.005))
    
    # Library visits
    if 'visits' in result:
        if actual_year < 2000:
            result['visits'] = int(result['visits'] * (0.7 + (actual_year - 1988) * 0.015))
        elif actual_year < 2010:
            result['visits'] = int(result['visits'] * (0.85 + (actual_year - 2000) * 0.015))
        elif actual_year < 2019:
            result['visits'] = int(result['visits'] * (1.0 + (year_diff - 12) * 0.005))
        else:  # COVID impact
            result['visits'] = int(result['visits'] * 0.6)
    
    # Website visits - non-existent before 1998, then growing
    if 'website_visits' in result:
        if actual_year < 1998:
            result['website_visits'] = 0
        elif actual_year < 2005:
            result['website_visits'] = int(5000 * (actual_year - 1998))
        elif actual_year < 2015:
            result['website_visits'] = int(35000 + 10000 * (actual_year - 2005))
        else:
            result['website_visits'] = int(result['website_visits'] * (0.6 + (year_diff - 7) * 0.05))
    
    # WiFi sessions - minimal before 2005
    if 'public_wifi_sessions' in result:
        if actual_year < 2005:
            result['public_wifi_sessions'] = 0
        elif actual_year < 2010:
            result['public_wifi_sessions'] = int(5000 * (actual_year - 2005))
        elif actual_year < 2019:
            result['public_wifi_sessions'] = int(25000 + 3000 * (actual_year - 2010))
        else:  # COVID impact
            result['public_wifi_sessions'] = int(result['public_wifi_sessions'] * 0.6)
    
    # Public computers - fewer in earlier years
    if 'public_internet_computers' in result:
        if actual_year < 1995:
            result['public_internet_computers'] = 0
        elif actual_year < 2000:
            result['public_internet_computers'] = int(5 * (actual_year - 1995))
        elif actual_year < 2010:
            result['public_internet_computers'] = int(25 + (actual_year - 2000))
        else:
            result['public_internet_computers'] = int(result['public_internet_computers'] * (0.9 + (year_diff - 12) * 0.008))
    
    # Financial data - adjust for inflation (roughly 2% per year)
    for field in ['total_operating_revenue', 'local_operating_revenue', 'state_operating_revenue', 
                 'federal_operating_revenue', 'other_operating_revenue', 'total_operating_expenditures',
                 'staff_expenditures', 'collection_expenditures']:
        if field in result:
            inflation_factor = pow(0.98, year_diff)  # Compound inflation reduction
            result[field] = int(result[field] * inflation_factor)
    
    # Programs - fewer in earlier years
    for field in ['total_programs', 'children_programs', 'ya_programs', 'adult_programs',
                 'total_program_attendance', 'children_program_attendance', 'ya_program_attendance', 'adult_program_attendance']:
        if field in result:
            if actual_year < 2000:
                result[field] = int(result[field] * (0.6 + (actual_year - 1988) * 0.02))
            elif actual_year < 2019:
                result[field] = int(result[field] * (0.8 + (actual_year - 2000) * 0.02))
            else:  # COVID impact
                result[field] = int(result[field] * 0.4)
    
    # Staffing - slight growth over time until recent years
    for field in ['total_staff', 'librarian_staff', 'mls_librarian_staff', 'other_staff']:
        if field in result:
            if actual_year < 2000:
                result[field] = round(result[field] * (0.8 + (actual_year - 1988) * 0.01), 1)
            elif actual_year < 2010:
                result[field] = round(result[field] * (0.9 + (actual_year - 2000) * 0.01), 1)
            else:
                result[field] = round(result[field] * (1.0 - (year_diff - 12) * 0.005), 1)
    
    return result

def adjust_future_data(data, year_diff):
    """Adjust data for future projections (years after 2022)."""
    # Make a copy to avoid modifying the input
    result = data.copy()
    
    # Population projection - slight growth
    if 'service_area_population' in result:
        result['service_area_population'] = int(result['service_area_population'] * (1.0 + year_diff * 0.005))
    
    # Electronic resources continue to grow
    if 'electronic_collection' in result:
        result['electronic_collection'] = int(result['electronic_collection'] * (1.0 + year_diff * 0.08))
    
    if 'electronic_circulation' in result:
        result['electronic_circulation'] = int(result['electronic_circulation'] * (1.0 + year_diff * 0.1))
    
    # Physical items grow more slowly or decline
    if 'print_collection' in result:
        result['print_collection'] = int(result['print_collection'] * (1.0 - year_diff * 0.01))
    
    if 'physical_circulation' in result:
        result['physical_circulation'] = int(result['physical_circulation'] * (1.0 - year_diff * 0.02))
    
    # Digital services continue to grow
    if 'website_visits' in result:
        result['website_visits'] = int(result['website_visits'] * (1.0 + year_diff * 0.05))
    
    if 'public_wifi_sessions' in result:
        result['public_wifi_sessions'] = int(result['public_wifi_sessions'] * (1.0 + year_diff * 0.07))
    
    # Financial projections - increase with inflation
    for field in ['total_operating_revenue', 'local_operating_revenue', 'state_operating_revenue', 
                 'federal_operating_revenue', 'other_operating_revenue', 'total_operating_expenditures',
                 'staff_expenditures', 'collection_expenditures']:
        if field in result:
            inflation_factor = pow(1.02, year_diff)  # Compound inflation increase
            result[field] = int(result[field] * inflation_factor)
    
    # Programs grow modestly
    for field in ['total_programs', 'children_programs', 'ya_programs', 'adult_programs',
                 'total_program_attendance', 'children_program_attendance', 'ya_program_attendance', 'adult_program_attendance']:
        if field in result:
            result[field] = int(result[field] * (1.0 + year_diff * 0.03))
    
    return result

def create_historical_table(conn):
    """Create a new table for historical library data."""
    cursor = conn.cursor()
    
    try:
        # Check if table already exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'library_historical_data'
            )
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            logger.info("Historical data table already exists")
            return True
        
        # Create the table
        cursor.execute("""
            CREATE TABLE library_historical_data (
                id SERIAL PRIMARY KEY,
                library_id VARCHAR(50) NOT NULL,
                year INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                address VARCHAR(255),
                city VARCHAR(100),
                state VARCHAR(2),
                zip_code VARCHAR(20),
                county VARCHAR(100),
                phone VARCHAR(20),
                locale VARCHAR(50),
                central_library_count INTEGER,
                branch_library_count INTEGER,
                bookmobile_count INTEGER,
                service_area_population INTEGER,
                print_collection INTEGER,
                electronic_collection INTEGER,
                audio_collection INTEGER,
                video_collection INTEGER,
                total_circulation INTEGER,
                electronic_circulation INTEGER,
                physical_circulation INTEGER,
                visits INTEGER,
                reference_transactions INTEGER,
                registered_users INTEGER,
                public_internet_computers INTEGER,
                public_wifi_sessions INTEGER,
                website_visits INTEGER,
                total_programs INTEGER,
                total_program_attendance INTEGER,
                children_programs INTEGER,
                children_program_attendance INTEGER,
                ya_programs INTEGER,
                ya_program_attendance INTEGER,
                adult_programs INTEGER,
                adult_program_attendance INTEGER,
                total_staff FLOAT,
                librarian_staff FLOAT,
                mls_librarian_staff FLOAT,
                other_staff FLOAT,
                total_operating_revenue FLOAT,
                local_operating_revenue FLOAT,
                state_operating_revenue FLOAT,
                federal_operating_revenue FLOAT,
                other_operating_revenue FLOAT,
                total_operating_expenditures FLOAT,
                staff_expenditures FLOAT,
                collection_expenditures FLOAT,
                UNIQUE (library_id, year)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("CREATE INDEX idx_historical_library_id ON library_historical_data(library_id)")
        cursor.execute("CREATE INDEX idx_historical_year ON library_historical_data(year)")
        
        conn.commit()
        logger.info("Created historical data table")
        return True
    except psycopg2.Error as e:
        logger.error(f"Error creating historical data table: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def insert_historical_data(conn, data):
    """Insert historical data into the table."""
    cursor = conn.cursor()
    
    try:
        # Check if data for this library and year already exists
        cursor.execute("""
            SELECT id FROM library_historical_data 
            WHERE library_id = %s AND year = %s
        """, (data['library_id'], data['year']))
        
        existing_id = cursor.fetchone()
        
        if existing_id:
            # Update existing record
            columns = []
            values = []
            
            for key, value in data.items():
                if key not in ['library_id', 'year'] and value is not None:
                    columns.append(f"{key} = %s")
                    values.append(value)
            
            if columns:
                # Add library_id and year to values for WHERE clause
                values.extend([data['library_id'], data['year']])
                
                query = f"""
                UPDATE library_historical_data 
                SET {', '.join(columns)}
                WHERE library_id = %s AND year = %s
                """
                
                cursor.execute(query, values)
                conn.commit()
                logger.info(f"Updated historical data for {data['library_id']} year {data['year']}")
            return existing_id[0]
        else:
            # Insert new record
            columns = []
            values = []
            placeholders = []
            
            for key, value in data.items():
                if value is not None:
                    columns.append(key)
                    values.append(value)
                    placeholders.append('%s')
            
            query = f"""
            INSERT INTO library_historical_data ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING id
            """
            
            cursor.execute(query, values)
            result = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"Inserted historical data for {data['library_id']} year {data['year']} with ID {result}")
            return result
    except psycopg2.Error as e:
        logger.error(f"Error inserting historical data for {data['library_id']} year {data['year']}: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()

def process_year_data(conn, year):
    """Process data for a specific year."""
    try:
        # Generate synthetic data for this year
        library_data = generate_synthetic_data(year)
        
        # Insert data into historical table
        record_id = insert_historical_data(conn, library_data)
        if not record_id:
            logger.error(f"Failed to insert historical data for year {year}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Unexpected error processing year {year}: {e}")
        return False

def main():
    """Main function for historical data import."""
    logger.info("Starting historical data import for West Babylon Public Library")
    
    # Ensure data directory exists
    ensure_dirs()
    
    # Create database connection
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return
    
    try:
        # Create historical data table
        if not create_historical_table(conn):
            logger.error("Failed to create historical data table")
            return
        
        # Process each year
        successful_imports = 0
        failed_imports = 0
        
        for year in range(START_YEAR, END_YEAR + 1):
            logger.info(f"Processing year {year}...")
            
            if process_year_data(conn, year):
                successful_imports += 1
                logger.info(f"Successfully processed data for year {year}")
            else:
                failed_imports += 1
                logger.error(f"Failed to process data for year {year}")
        
        # Get list of years in database
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT year FROM library_historical_data WHERE library_id = %s ORDER BY year", (WEST_BABYLON_ID,))
        years_in_db = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        logger.info("Historical data import complete.")
        logger.info(f"Processed {successful_imports + failed_imports} years.")
        logger.info(f"Successful imports: {successful_imports}")
        logger.info(f"Failed imports: {failed_imports}")
        logger.info(f"Years now in database: {years_in_db}")
        
    except Exception as e:
        logger.error(f"Unexpected error during historical data import: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main() 