import os
import sys
from pathlib import Path
import pandas as pd
from loguru import logger

# Set up logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("sample_data_test.log", level="DEBUG", rotation="10 MB")

# Sample data paths
SAMPLE_DATA_DIR = Path("data/sample")

def test_sample_data_processing():
    """Test processing of sample library data."""
    
    # Verify sample data exists
    library_csv = list(SAMPLE_DATA_DIR.glob("*library*.csv"))
    outlet_csv = list(SAMPLE_DATA_DIR.glob("*outlet*.csv"))
    
    if not library_csv:
        logger.error("❌ Sample library data not found")
        return False
    
    library_file = library_csv[0]
    logger.info(f"✅ Found sample library data at {library_file}")
    
    # Attempt to read the data
    try:
        library_df = pd.read_csv(library_file, encoding='latin1', low_memory=False)
        logger.info(f"✅ Successfully read library data: {len(library_df)} rows")
        
        # Preview columns and data
        logger.info(f"Columns in library data: {', '.join(library_df.columns[:10])}...")
        
        # Sample a random library
        sample_library = library_df.iloc[0]
        logger.info(f"Sample library: {sample_library.get('LIBNAME', 'Unknown')} (ID: {sample_library.get('FSCSKEY', 'Unknown')})")
        
        # Check some key metrics
        metrics = [
            'VISITS', 'TOTCIR', 'TOTSTAFF', 'TOTINCM', 'TOTEXPD',
            'BKVOL', 'EBOOK', 'AUDIO_PH', 'VIDEO_PH'
        ]
        
        for metric in metrics:
            if metric in library_df.columns:
                logger.info(f"  - {metric}: {sample_library.get(metric, 'Not available')}")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error processing library data: {str(e)}")
        return False


def print_summary(library_file, outlet_file=None):
    """Print a summary of the data files."""
    
    try:
        library_df = pd.read_csv(library_file, encoding='latin1', low_memory=False)
        
        print("\n===== LIBRARY DATA SUMMARY =====")
        print(f"File: {library_file.name}")
        print(f"Number of libraries: {len(library_df)}")
        print(f"Columns: {len(library_df.columns)}")
        print("\nSample library data:")
        sample = library_df.iloc[0]
        print(f"  Name: {sample.get('LIBNAME', 'Unknown')}")
        print(f"  ID: {sample.get('FSCSKEY', 'Unknown')}")
        print(f"  City: {sample.get('CITY', 'Unknown')}")
        print(f"  State: {sample.get('STABR', 'Unknown')}")
        
        if outlet_file:
            outlet_df = pd.read_csv(outlet_file, encoding='latin1', low_memory=False)
            print("\n===== OUTLET DATA SUMMARY =====")
            print(f"File: {outlet_file.name}")
            print(f"Number of outlets: {len(outlet_df)}")
            print(f"Columns: {len(outlet_df.columns)}")
            
            if len(outlet_df) > 0:
                sample = outlet_df.iloc[0]
                print("\nSample outlet data:")
                print(f"  Name: {sample.get('LIBNAME', 'Unknown')}")
                print(f"  ID: {sample.get('FSCSKEY', 'Unknown')}-{sample.get('FSCS_SEQ', 'Unknown')}")
                print(f"  City: {sample.get('CITY', 'Unknown')}")
                print(f"  Type: {sample.get('STATDESC', 'Unknown')}")
    
    except Exception as e:
        print(f"Error generating summary: {str(e)}")


if __name__ == "__main__":
    print("Testing sample data processing...")
    
    if not SAMPLE_DATA_DIR.exists():
        print(f"❌ Sample data directory not found at {SAMPLE_DATA_DIR}")
        sys.exit(1)
    
    # Find sample data files
    library_files = list(SAMPLE_DATA_DIR.glob("*library*.csv"))
    outlet_files = list(SAMPLE_DATA_DIR.glob("*outlet*.csv"))
    
    if not library_files:
        print("❌ No library data files found in sample directory")
        sys.exit(1)
    
    print(f"✅ Found {len(library_files)} library data files and {len(outlet_files)} outlet data files")
    
    # Process the first file
    success = test_sample_data_processing()
    
    if success:
        print("\n✅ Sample data processing test completed successfully")
        
        # Print summary of all files
        for library_file in library_files:
            matching_outlet = None
            if outlet_files:
                # Try to find matching outlet file (same year pattern)
                year_match = None
                for year in range(1992, 2030):  # Look for year patterns
                    if str(year) in library_file.name:
                        year_match = str(year)
                        break
                
                if year_match:
                    matching_outlets = [f for f in outlet_files if year_match in f.name]
                    if matching_outlets:
                        matching_outlet = matching_outlets[0]
            
            print_summary(library_file, matching_outlet)
    else:
        print("\n❌ Sample data processing test failed")
    
    print("\nFinished testing.") 