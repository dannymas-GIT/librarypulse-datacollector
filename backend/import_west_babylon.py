"""
Script to import data for West Babylon Public Library.
"""
import logging
import os
import pandas as pd
import zipfile
import tempfile
import requests
from pathlib import Path
import re
from sqlalchemy import create_engine, exists, and_, inspect
from sqlalchemy.orm import sessionmaker

# Import our models
from init_db_simple import Base, PLSDataset, Library, LibraryOutlet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/librarypulse"

# IMLS Data URL - we'll download directly for demonstration
PLS_DATA_URL = "https://www.imls.gov/sites/default/files/2023-10/pls_fy2021_csv.zip"
SAMPLE_DATA_DIR = Path("data/sample")

# Target library information
TARGET_LIBRARY_NAME = "West Babylon Public Library"
TARGET_LIBRARY_CITY = "West Babylon"
TARGET_LIBRARY_STATE = "NY"


def ensure_database_initialized():
    """Ensure the database is initialized before importing data."""
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    if not inspector.has_table("pls_datasets"):
        logger.info("Database tables not found. Initializing database...")
        from init_db_simple import init_db
        init_db()
    return engine


def download_or_use_sample_data(year=2021):
    """Download data or use sample data if available."""
    # Check if we already have the data
    output_dir = Path(f"data/raw/{year}")
    os.makedirs(output_dir, exist_ok=True)
    zip_path = output_dir / f"pls_fy{year}_csv.zip"
    
    if zip_path.exists():
        logger.info(f"Using existing data file: {zip_path}")
        return zip_path
    
    # Check for sample data
    sample_zip = next(SAMPLE_DATA_DIR.glob(f"*{year}*.zip"), None)
    if sample_zip:
        logger.info(f"Using sample data: {sample_zip}")
        return sample_zip
    
    try:
        # Try to download the data
        logger.info(f"Downloading data from {PLS_DATA_URL}")
        response = requests.get(PLS_DATA_URL, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Downloaded data to {zip_path}")
        return zip_path
    except Exception as e:
        logger.error(f"Error downloading data: {e}")
        
        # Create from sample files as fallback
        logger.info("Using sample data as fallback")
        library_sample = next(SAMPLE_DATA_DIR.glob("*_library.csv"), None)
        outlet_sample = next(SAMPLE_DATA_DIR.glob("*_outlet.csv"), None)
        
        if library_sample and outlet_sample:
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(library_sample, f"pls_fy{year}_library.csv")
                zipf.write(outlet_sample, f"pls_fy{year}_outlet.csv")
            
            logger.info(f"Created sample data ZIP at {zip_path}")
            return zip_path
        
        return None


def extract_data(zip_path):
    """Extract data from ZIP file and load into pandas DataFrames."""
    logger.info(f"Extracting data from {zip_path}")
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # Find CSV files
        temp_path = Path(temp_dir)
        library_files = list(temp_path.glob("*library*.csv"))
        outlet_files = list(temp_path.glob("*outlet*.csv"))
        
        if not library_files:
            logger.error("No library data files found in ZIP")
            return None, None
        
        # Load data
        library_data = pd.read_csv(library_files[0], dtype=str, encoding='latin1')
        outlet_data = pd.read_csv(outlet_files[0], dtype=str, encoding='latin1') if outlet_files else None
        
        logger.info(f"Loaded {len(library_data)} library records and {len(outlet_data) if outlet_data is not None else 0} outlet records")
        return library_data, outlet_data


def find_west_babylon_library(library_data):
    """Find West Babylon Public Library in the data."""
    logger.info(f"Searching for {TARGET_LIBRARY_NAME} in {TARGET_LIBRARY_CITY}, {TARGET_LIBRARY_STATE}")
    
    # Normalize columns
    library_data.columns = [col.lower() for col in library_data.columns]
    
    # Look for columns that might contain the library name, city, and state
    name_cols = [col for col in library_data.columns if 'name' in col or 'libname' in col]
    city_cols = [col for col in library_data.columns if 'city' in col]
    state_cols = [col for col in library_data.columns if 'state' in col or 'stabr' in col]
    
    # First try exact match on name
    for name_col in name_cols:
        mask = library_data[name_col].str.contains(TARGET_LIBRARY_NAME, case=False, na=False)
        if mask.any():
            matches = library_data[mask]
            logger.info(f"Found {len(matches)} possible matches by name")
            
            # Further filter by city and state if columns exist
            if city_cols and state_cols:
                for city_col in city_cols:
                    for state_col in state_cols:
                        city_state_mask = (
                            matches[city_col].str.contains(TARGET_LIBRARY_CITY, case=False, na=False) & 
                            matches[state_col].str.contains(TARGET_LIBRARY_STATE, case=False, na=False)
                        )
                        if city_state_mask.any():
                            final_matches = matches[city_state_mask]
                            logger.info(f"Found {len(final_matches)} matches with city and state")
                            return final_matches
            
            # If we couldn't filter by city and state, return name matches
            return matches
    
    # If we get here, try a more flexible search
    logger.info("No exact matches found. Trying more flexible search...")
    
    # Try searching for parts of the name and location
    for name_col in name_cols:
        mask = library_data[name_col].str.contains("Babylon", case=False, na=False)
        if mask.any():
            matches = library_data[mask]
            logger.info(f"Found {len(matches)} possible matches containing 'Babylon'")
            
            # Further filter by state
            if state_cols:
                for state_col in state_cols:
                    state_mask = matches[state_col].str.contains(TARGET_LIBRARY_STATE, case=False, na=False)
                    if state_mask.any():
                        state_matches = matches[state_mask]
                        logger.info(f"Found {len(state_matches)} matches in {TARGET_LIBRARY_STATE}")
                        return state_matches
            
            return matches
    
    logger.warning(f"No matches found for {TARGET_LIBRARY_NAME}")
    return pd.DataFrame()


def get_matching_outlets(library_records, outlet_data):
    """Get outlet records for the library."""
    if outlet_data is None or library_records.empty:
        return pd.DataFrame()
    
    # Normalize columns
    outlet_data.columns = [col.lower() for col in outlet_data.columns]
    
    # Get library IDs
    id_cols = [col for col in library_records.columns if 'fscs' in col or 'libid' in col]
    if not id_cols:
        logger.warning("No library ID columns found")
        return pd.DataFrame()
    
    # Get all outlets matching any of our libraries
    matching_outlets = pd.DataFrame()
    for id_col in id_cols:
        library_ids = library_records[id_col].tolist()
        
        # Find matching columns in outlet data
        outlet_id_cols = [col for col in outlet_data.columns if 'fscs' in col or 'libid' in col]
        
        for outlet_id_col in outlet_id_cols:
            mask = outlet_data[outlet_id_col].isin(library_ids)
            if mask.any():
                new_matches = outlet_data[mask]
                matching_outlets = pd.concat([matching_outlets, new_matches])
                logger.info(f"Found {len(new_matches)} matching outlets")
    
    # Remove duplicates
    matching_outlets = matching_outlets.drop_duplicates()
    logger.info(f"Total of {len(matching_outlets)} unique matching outlets")
    return matching_outlets


def import_to_database(library_records, outlet_records, year=2021):
    """Import the data to the database."""
    if library_records.empty:
        logger.error("No library records to import")
        return
    
    # Create database session
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if we already have a dataset for this year
        dataset = session.query(PLSDataset).filter(PLSDataset.year == year).first()
        if not dataset:
            # Create a new dataset
            dataset = PLSDataset(
                year=year,
                status="complete",
                record_count=len(library_records),
                notes=f"Imported West Babylon Public Library data for {year}"
            )
            session.add(dataset)
            session.flush()  # Get the dataset ID
            logger.info(f"Created new dataset for year {year}")
        else:
            logger.info(f"Using existing dataset for year {year}")
        
        # Normalize column names
        library_records.columns = [col.lower() for col in library_records.columns]
        if not outlet_records.empty:
            outlet_records.columns = [col.lower() for col in outlet_records.columns]
        
        # Map standard column names to model fields
        library_col_map = {
            'fscskey': 'library_id',
            'libid': 'library_id',
            'libname': 'name',
            'name': 'name',
            'address': 'address',
            'city': 'city',
            'stabr': 'state',
            'zip': 'zip_code',
            'cnty': 'county',
            'county': 'county',
            'phone': 'phone',
            'locale': 'locale',
            'centlib': 'central_library_count',
            'branlib': 'branch_library_count',
            'bkmob': 'bookmobile_count',
            'popu_lsa': 'service_area_population',
            'popu': 'service_area_population',
            'bkvol': 'print_collection',
            'ebook': 'electronic_collection',
            'audio_ph': 'audio_collection',
            'video_ph': 'video_collection',
            'totcir': 'total_circulation',
            'eleccir': 'electronic_circulation',
            'physcir': 'physical_circulation',
            'visits': 'visits',
            'referenc': 'reference_transactions',
            'regbor': 'registered_users',
            'totstaff': 'total_staff',
            'libraria': 'librarian_staff',
            'totincm': 'total_operating_revenue',
            'totexpd': 'total_operating_expenditures',
            'staffexp': 'staff_expenditures',
            'libmatex': 'collection_expenditures',
        }
        
        outlet_col_map = {
            'fscskey': 'library_id',
            'libid': 'library_id',
            'fscs_seq': 'outlet_id',
            'libname': 'name',
            'name': 'name',
            'address': 'address',
            'city': 'city',
            'stabr': 'state',
            'zip': 'zip_code',
            'cnty': 'county',
            'county': 'county',
            'phone': 'phone',
            'c_out_ty': 'type',
            'hours': 'hours',
            'sq_feet': 'square_feet',
            'locale': 'locale',
        }
        
        # Import library records
        for _, row in library_records.iterrows():
            # Check if this library already exists in this dataset
            library_id = row.get('fscskey', row.get('libid'))
            if not library_id:
                logger.warning(f"Skipping library record without ID: {row}")
                continue
            
            existing = session.query(exists().where(
                and_(Library.dataset_id == dataset.id, Library.library_id == library_id)
            )).scalar()
            
            if existing:
                logger.info(f"Library {library_id} already exists in dataset {dataset.id}")
                continue
            
            # Create library record
            library_data = {'dataset_id': dataset.id, 'library_id': library_id}
            
            # Map all available columns
            for col in row.index:
                if col in library_col_map and not pd.isna(row[col]):
                    model_field = library_col_map[col]
                    library_data[model_field] = row[col]
            
            # Ensure required fields
            if 'name' not in library_data or not library_data['name']:
                library_data['name'] = f"Library {library_id}"
            
            library = Library(**library_data)
            session.add(library)
            logger.info(f"Added library: {library_data['name']} ({library_id})")
        
        session.flush()
        
        # Import outlet records
        if not outlet_records.empty:
            for _, row in outlet_records.iterrows():
                # Get library ID and outlet ID
                library_id = row.get('fscskey', row.get('libid'))
                outlet_seq = row.get('fscs_seq', '')
                outlet_id = f"{library_id}_{outlet_seq}"
                
                if not library_id:
                    logger.warning(f"Skipping outlet record without library ID: {row}")
                    continue
                
                # Check if this outlet already exists in this dataset
                existing = session.query(exists().where(
                    and_(LibraryOutlet.dataset_id == dataset.id, LibraryOutlet.outlet_id == outlet_id)
                )).scalar()
                
                if existing:
                    logger.info(f"Outlet {outlet_id} already exists in dataset {dataset.id}")
                    continue
                
                # Create outlet record
                outlet_data = {
                    'dataset_id': dataset.id,
                    'library_id': library_id,
                    'outlet_id': outlet_id
                }
                
                # Map all available columns
                for col in row.index:
                    if col in outlet_col_map and not pd.isna(row[col]):
                        model_field = outlet_col_map[col]
                        outlet_data[model_field] = row[col]
                
                # Ensure required fields
                if 'name' not in outlet_data or not outlet_data['name']:
                    outlet_data['name'] = f"Outlet {outlet_id}"
                
                outlet = LibraryOutlet(**outlet_data)
                session.add(outlet)
                logger.info(f"Added outlet: {outlet_data['name']} ({outlet_id})")
        
        # Commit all changes
        session.commit()
        logger.info("Database import complete")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error importing to database: {e}", exc_info=True)
    finally:
        session.close()


def main():
    """Main function to import West Babylon Public Library data."""
    try:
        # Ensure database is initialized
        ensure_database_initialized()
        
        # Download or use sample data
        zip_path = download_or_use_sample_data()
        if not zip_path:
            logger.error("Failed to get data file")
            return
        
        # Extract data
        library_data, outlet_data = extract_data(zip_path)
        if library_data is None:
            logger.error("Failed to extract data")
            return
        
        # Find West Babylon Public Library
        target_libraries = find_west_babylon_library(library_data)
        if target_libraries.empty:
            logger.error(f"Could not find {TARGET_LIBRARY_NAME}")
            return
        
        # Display found libraries
        logger.info("\nFound libraries:")
        for _, row in target_libraries.iterrows():
            name_col = next((col for col in row.index if 'name' in col.lower()), None)
            city_col = next((col for col in row.index if 'city' in col.lower()), None)
            state_col = next((col for col in row.index if 'state' in col.lower() or 'stabr' in col.lower()), None)
            id_col = next((col for col in row.index if 'fscs' in col.lower() or 'libid' in col.lower()), None)
            
            name = row[name_col] if name_col else "Unknown"
            city = row[city_col] if city_col else "Unknown"
            state = row[state_col] if state_col else "Unknown"
            lib_id = row[id_col] if id_col else "Unknown"
            
            logger.info(f"  - {name} ({lib_id}) in {city}, {state}")
        
        # Get outlet information
        matching_outlets = get_matching_outlets(target_libraries, outlet_data)
        if not matching_outlets.empty:
            logger.info("\nMatching outlets:")
            for _, row in matching_outlets.iterrows():
                name_col = next((col for col in row.index if 'name' in col.lower()), None)
                city_col = next((col for col in row.index if 'city' in col.lower()), None)
                id_col = next((col for col in row.index if 'fscs' in col.lower() or 'libid' in col.lower()), None)
                seq_col = next((col for col in row.index if 'seq' in col.lower()), None)
                
                name = row[name_col] if name_col else "Unknown"
                city = row[city_col] if city_col else "Unknown"
                lib_id = row[id_col] if id_col else "Unknown"
                seq = row[seq_col] if seq_col else "Unknown"
                
                logger.info(f"  - {name} ({lib_id}_{seq}) in {city}")
        
        # Import to database
        import_to_database(target_libraries, matching_outlets)
        
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("Starting West Babylon Public Library data import")
    main()
    logger.info("Import process completed") 