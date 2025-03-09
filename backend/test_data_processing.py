import os
import sys
from pathlib import Path
import zipfile
import pandas as pd
import tempfile
import re
import shutil
from loguru import logger

# Set up logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("processing_test.log", level="DEBUG", rotation="10 MB")

# Define paths
SAMPLE_DATA_DIR = Path("data/sample")
PROCESSED_DIR = Path("data/processed_test")
YEAR_TO_TEST = 2021

def create_test_zip():
    """Create a test ZIP file from sample data."""
    # Find sample data files
    library_file = next(SAMPLE_DATA_DIR.glob("*library*.csv"), None)
    outlet_file = next(SAMPLE_DATA_DIR.glob("*outlet*.csv"), None)
    
    if not library_file or not outlet_file:
        raise FileNotFoundError("Sample library and outlet files not found")
    
    # Create output directory
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Create ZIP file
    zip_path = PROCESSED_DIR / f"pls_fy{YEAR_TO_TEST}_csv.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(library_file, f"pls_fy{YEAR_TO_TEST}_library.csv")
        zipf.write(outlet_file, f"pls_fy{YEAR_TO_TEST}_outlet.csv")
    
    logger.info(f"Created test ZIP file at {zip_path}")
    return zip_path


def process_data(data_path, focus_library_id=None):
    """Process library data similar to the collector's process_data_for_year method."""
    logger.info(f"Processing data from {data_path}")
    
    extract_dir = PROCESSED_DIR / "extracted"
    os.makedirs(extract_dir, exist_ok=True)
    
    # Extract if zip file
    if data_path.suffix.lower() == '.zip':
        with zipfile.ZipFile(data_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        # Find CSV files in extracted directory
        csv_files = list(extract_dir.glob('*.csv'))
        
        if not csv_files:
            logger.error(f"No CSV files found in ZIP")
            return None
        
        # Use pattern matching to identify files
        library_pattern = re.compile(r'(pupld|pupldf|library)', re.IGNORECASE)
        outlet_pattern = re.compile(r'(puout|outlet)', re.IGNORECASE)
        
        library_files = [f for f in csv_files if library_pattern.search(f.name)]
        outlet_files = [f for f in csv_files if outlet_pattern.search(f.name)]
        
        # If pattern matching didn't work, try a fallback approach
        if not library_files:
            # Try to find library data by looking for files with 'FSCSKEY' and not 'FSCS_SEQ'
            for file in csv_files:
                try:
                    with open(file, 'r', encoding='latin1') as f:
                        header = f.readline().upper()
                        if 'FSCSKEY' in header and 'FSCS_SEQ' not in header:
                            library_files.append(file)
                except Exception as e:
                    logger.warning(f"Error reading file {file}: {str(e)}")
        
        if not outlet_files:
            # Try to find outlet data by looking for files with both 'FSCSKEY' and 'FSCS_SEQ'
            for file in csv_files:
                try:
                    with open(file, 'r', encoding='latin1') as f:
                        header = f.readline().upper()
                        if 'FSCSKEY' in header and 'FSCS_SEQ' in header:
                            outlet_files.append(file)
                except Exception as e:
                    logger.warning(f"Error reading file {file}: {str(e)}")
        
        # If we still don't have both files, use file size approach
        if not library_files and not outlet_files and len(csv_files) >= 2:
            # Sort by file size (ascending)
            csv_files.sort(key=lambda f: f.stat().st_size)
            library_files = [csv_files[0]]
            outlet_files = [csv_files[1]]
        
        library_file = library_files[0] if library_files else None
        outlet_file = outlet_files[0] if outlet_files else None
        
        if not library_file:
            logger.error(f"Library data file not found")
            return None
    else:
        # Direct CSV file
        library_file = data_path
        outlet_file = None
    
    # Load library data
    try:
        library_df = pd.read_csv(library_file, encoding='latin1', low_memory=False)
        
        # Standardize column names to uppercase
        library_df.columns = map(str.upper, library_df.columns)
        
        # Make sure we have the FSCSKEY column
        if 'FSCSKEY' not in library_df.columns:
            logger.error(f"FSCSKEY column not found in library data")
            return None
        
        # Filter to just the selected library if specified
        if focus_library_id:
            logger.info(f"Filtering data for library ID: {focus_library_id}")
            library_df = library_df[library_df['FSCSKEY'] == focus_library_id]
            
            if library_df.empty:
                logger.warning(f"No data found for library ID {focus_library_id}")
                return None
    
    except Exception as e:
        logger.error(f"Error processing library data: {str(e)}")
        return None
    
    # Load outlet data if available
    outlet_df = None
    if outlet_file:
        try:
            outlet_df = pd.read_csv(outlet_file, encoding='latin1', low_memory=False)
            
            # Standardize column names to uppercase
            outlet_df.columns = map(str.upper, outlet_df.columns)
            
            # Make sure we have the FSCSKEY and FSCS_SEQ columns
            required_columns = ['FSCSKEY', 'FSCS_SEQ']
            if not all(col in outlet_df.columns for col in required_columns):
                logger.error(f"Required columns not found in outlet data")
                outlet_df = None
            else:
                # Filter outlets to just the selected library
                if focus_library_id:
                    outlet_df = outlet_df[outlet_df['FSCSKEY'] == focus_library_id]
        
        except Exception as e:
            logger.error(f"Error processing outlet data: {str(e)}")
            outlet_df = None
    
    results = {
        'libraries': library_df,
        'outlets': outlet_df
    }
    
    # Print some stats
    logger.info(f"Processed library data: {len(library_df)} libraries")
    if outlet_df is not None:
        logger.info(f"Processed outlet data: {len(outlet_df)} outlets")
    
    return results


def get_info_for_library(data, library_id):
    """Get information for a specific library from processed data."""
    library_df = data['libraries']
    outlet_df = data['outlets']
    
    # Find the library
    library = library_df[library_df['FSCSKEY'] == library_id]
    
    if library.empty:
        logger.error(f"Library ID {library_id} not found in data")
        return None
    
    # Get the first (and should be only) row for this library
    library_data = library.iloc[0]
    
    # Get outlets for this library
    outlets = []
    if outlet_df is not None:
        library_outlets = outlet_df[outlet_df['FSCSKEY'] == library_id]
        for _, outlet in library_outlets.iterrows():
            outlets.append({
                'id': f"{outlet['FSCSKEY']}-{outlet['FSCS_SEQ']}",
                'name': outlet.get('LIBNAME', 'Unknown'),
                'type': outlet.get('STATDESC', 'Unknown'),
                'address': outlet.get('ADDRESS', 'Unknown'),
                'city': outlet.get('CITY', 'Unknown'),
                'state': outlet.get('STABR', 'Unknown')
            })
    
    # Build library info dictionary
    def get_value(field_names):
        for field in field_names:
            if field in library_data and pd.notna(library_data[field]):
                return library_data[field]
        return None
    
    library_info = {
        'id': library_data['FSCSKEY'],
        'name': get_value(['LIBNAME', 'NAME']),
        'address': get_value(['ADDRESS']),
        'city': get_value(['CITY']),
        'state': get_value(['STABR', 'STATE']),
        'statistics': {
            'visits': get_value(['VISITS']),
            'circulation': {
                'total': get_value(['TOTCIR']),
                'electronic': get_value(['ELECCIR']),
                'physical': get_value(['PHYSCIR'])
            },
            'collection': {
                'print': get_value(['BKVOL']),
                'electronic': get_value(['EBOOK']),
                'audio': get_value(['AUDIO_PH']),
                'video': get_value(['VIDEO_PH'])
            },
            'programs': {
                'total': get_value(['PROGAM']),
                'attendance': get_value(['ATTPRG'])
            },
            'staff': get_value(['TOTSTAFF']),
            'revenue': get_value(['TOTINCM']),
            'expenditures': get_value(['TOTEXPD'])
        },
        'outlets': outlets
    }
    
    return library_info


if __name__ == "__main__":
    print(f"Testing data processing for IMLS Library Pulse")
    print(f"Processing sample data for year {YEAR_TO_TEST}")
    
    # Clean up previous outputs
    if PROCESSED_DIR.exists():
        shutil.rmtree(PROCESSED_DIR)
    
    try:
        # 1. Create test ZIP from sample data
        zip_path = create_test_zip()
        print(f"✅ Created test data ZIP at {zip_path}")
        
        # 2. Process the data (without filtering)
        processed_data = process_data(zip_path)
        
        if not processed_data:
            print("❌ Failed to process data")
            sys.exit(1)
        
        print(f"✅ Successfully processed data:")
        print(f"  - Libraries: {len(processed_data['libraries'])}")
        if processed_data['outlets'] is not None:
            print(f"  - Outlets: {len(processed_data['outlets'])}")
        
        # 3. Pick a sample library and process its data
        if len(processed_data['libraries']) > 0:
            sample_library_id = processed_data['libraries']['FSCSKEY'].iloc[0]
            print(f"\nTesting filtering for library ID: {sample_library_id}")
            
            # Process data again with filtering
            filtered_data = process_data(zip_path, sample_library_id)
            
            if filtered_data and len(filtered_data['libraries']) > 0:
                print(f"✅ Successfully filtered data for library {sample_library_id}")
                
                # Get detailed information for this library
                library_info = get_info_for_library(filtered_data, sample_library_id)
                
                if library_info:
                    print("\n===== LIBRARY INFORMATION =====")
                    print(f"ID: {library_info['id']}")
                    print(f"Name: {library_info['name']}")
                    print(f"Location: {library_info['city']}, {library_info['state']}")
                    print("\nSTATISTICS:")
                    print(f"Visits: {library_info['statistics']['visits']}")
                    print(f"Total Circulation: {library_info['statistics']['circulation']['total']}")
                    print(f"Electronic Resources: {library_info['statistics']['collection']['electronic']}")
                    print(f"Total Programs: {library_info['statistics']['programs']['total']}")
                    print(f"Program Attendance: {library_info['statistics']['programs']['attendance']}")
                    print(f"Total Staff: {library_info['statistics']['staff']}")
                    print(f"Total Revenue: ${library_info['statistics']['revenue']:,.2f}")
                    print(f"Total Expenditures: ${library_info['statistics']['expenditures']:,.2f}")
                    
                    if library_info['outlets']:
                        print(f"\nOUTLETS ({len(library_info['outlets'])}):")
                        for outlet in library_info['outlets']:
                            print(f"  - {outlet['name']} ({outlet['type']}): {outlet['city']}, {outlet['state']}")
            else:
                print(f"❌ Failed to filter data for library {sample_library_id}")
    
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
    
    print("\nFinished testing.") 