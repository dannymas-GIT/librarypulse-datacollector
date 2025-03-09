import os
import re
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
import shutil
from typing import List, Dict, Optional, Any

import pandas as pd
from loguru import logger
import sys

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stderr, format="{time} | {level} | {message}", level="INFO")
logger.add("standalone_collector_test.log", rotation="10 MB", level="DEBUG")

# Constants
DATA_DIR = Path("data")
SAMPLE_DIR = DATA_DIR / "sample"
TEST_YEAR = 2021
TEST_LIBRARY_ID = "MN00001"  # Sample library ID to test


class StandaloneCollector:
    """
    Standalone version of PLSDataCollector for testing without database dependencies
    """
    
    def __init__(self):
        # Set up data directories
        self.data_dir = DATA_DIR
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_data_dir = self.data_dir / "processed"
        self.base_url = "https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey"
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)
        os.makedirs(SAMPLE_DIR, exist_ok=True)
        
        # Library ID to filter for (if any)
        self.library_id = None
        
        logger.info("Initialized StandaloneCollector")
    
    def discover_available_years(self) -> List[int]:
        """
        Discover available years from sample data
        """
        logger.info("Discovering available years from sample data")
        
        # In our simplified version, we'll just check for sample data years
        years = []
        try:
            for file in SAMPLE_DIR.glob("*_library.csv"):
                match = re.search(r'_(\d{4})_', file.name)
                if match:
                    year = int(match.group(1))
                    years.append(year)
                    logger.info(f"Found year {year} in sample data")
        except Exception as e:
            logger.error(f"Error discovering years: {e}")
        
        # If we didn't find any years, return a default list
        if not years:
            logger.info(f"No years found in sample data, using default year {TEST_YEAR}")
            return [TEST_YEAR]
            
        return sorted(years)
    
    def download_data_for_year(self, year: int) -> Optional[Path]:
        """
        Create a sample data ZIP file for a specific year
        """
        logger.info(f"Creating sample data for year {year}")
        
        # Create directory for this year
        year_dir = self.raw_data_dir / str(year)
        os.makedirs(year_dir, exist_ok=True)
        
        # Define expected file paths
        csv_zip_path = year_dir / f"pls_fy{year}_csv.zip"
        
        # Check if we already have created the data
        if csv_zip_path.exists():
            logger.info(f"Using previously created data for year {year}")
            return csv_zip_path
        
        # Create the sample data zip
        return self._use_sample_data(year, year_dir)
    
    def _use_sample_data(self, year: int, target_dir: Path) -> Optional[Path]:
        """
        Use sample data to create a ZIP file
        """
        # Check if we have sample data
        if not SAMPLE_DIR.exists():
            logger.error(f"Sample data directory not found: {SAMPLE_DIR}")
            return None
        
        # Look for library and outlet CSV files
        library_sample = next(SAMPLE_DIR.glob("*_library.csv"), None)
        outlet_sample = next(SAMPLE_DIR.glob("*_outlet.csv"), None)
        
        if not library_sample or not outlet_sample:
            logger.error("Sample library and outlet CSV files not found")
            return None
        
        # Create a ZIP file with the sample data
        zip_path = target_dir / f"pls_fy{year}_csv.zip"
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                # Add the sample files to the ZIP
                zipf.write(library_sample, f"pls_fy{year}_library.csv")
                zipf.write(outlet_sample, f"pls_fy{year}_outlet.csv")
            
            logger.info(f"Created sample data ZIP file for year {year}")
            return zip_path
        except Exception as e:
            logger.error(f"Error creating sample data ZIP: {e}")
            return None
    
    def process_data_for_year(self, year: int, data_path: Path) -> Dict[str, Any]:
        """
        Process data from a ZIP file
        """
        logger.info(f"Processing data for year {year} from {data_path}")
        
        if not data_path or not os.path.exists(data_path):
            logger.error(f"Data file does not exist: {data_path}")
            return {}
        
        try:
            # Extract ZIP file
            extract_dir = self.processed_data_dir / str(year)
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(data_path, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            # Find CSV files
            library_files = list(extract_dir.glob("*library*.csv"))
            outlet_files = list(extract_dir.glob("*outlet*.csv"))
            
            if not library_files:
                logger.error("No library CSV file found in ZIP")
                return {}
            
            # Read data
            library_data = pd.read_csv(library_files[0], dtype=str)
            outlet_data = pd.read_csv(outlet_files[0], dtype=str) if outlet_files else pd.DataFrame()
            
            # Display column names for debugging
            logger.debug(f"Library data columns: {library_data.columns.tolist()}")
            logger.debug(f"Outlet data columns: {outlet_data.columns.tolist()}")
            
            # Filter data if we have a library ID
            if self.library_id:
                logger.info(f"Filtering data for library ID: {self.library_id}")
                
                # The sample data uses lowercase 'fscskey' instead of 'FSCSKEY'
                if 'fscskey' in library_data.columns:
                    logger.info("Using 'fscskey' column for filtering")
                    library_data = library_data[library_data['fscskey'] == self.library_id]
                    
                    if not library_data.empty and 'fscskey' in outlet_data.columns:
                        outlet_data = outlet_data[outlet_data['fscskey'] == self.library_id]
                else:
                    logger.error("Column 'fscskey' not found in library data")
                    return {}
            
            # Convert to dictionaries
            libraries = library_data.to_dict('records')
            outlets = outlet_data.to_dict('records') if not outlet_data.empty else []
            
            logger.info(f"Processed {len(libraries)} libraries and {len(outlets)} outlets")
            
            return {
                'libraries': libraries,
                'outlets': outlets
            }
            
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            logger.exception(e)
            return {}
    
    def get_library_stats(self, library_id: str, year: int) -> Optional[Dict[str, Any]]:
        """
        Get library statistics for a specific library and year
        """
        logger.info(f"Getting stats for library {library_id} for year {year}")
        
        # Set the library ID for filtering
        self.library_id = library_id
        
        # Download/create data
        data_path = self.download_data_for_year(year)
        if not data_path:
            logger.error(f"Failed to get data for year {year}")
            return None
        
        # Process data
        processed_data = self.process_data_for_year(year, data_path)
        
        # Check if we have library data
        libraries = processed_data.get('libraries', [])
        if not libraries:
            logger.error(f"No library data found for {library_id}")
            return None
        
        # Get the first (and should be only) library
        library = libraries[0]
        
        # Extract statistics
        def safe_convert(value, convert_func, default=None):
            """Safely convert a value"""
            if value is None or pd.isna(value):
                return default
            try:
                return convert_func(value)
            except (ValueError, TypeError):
                return default
        
        # Build statistics dictionary - using sample data column names (lowercase)
        stats = {
            'name': library.get('libname', 'Unknown'),
            'city': library.get('city', 'Unknown'),
            'state': library.get('stabr', 'Unknown'),
            'visits': safe_convert(library.get('visits'), int, 0),
            'circulation': safe_convert(library.get('totcir'), int, 0),
            'electronic_resources': safe_convert(library.get('eleccir', None), int),
            'programs': safe_convert(library.get('totpro', None), int),
            'program_attendance': safe_convert(library.get('totatten', None), int),
            'staff': safe_convert(library.get('totstaff'), float, 0),
            'revenue': safe_convert(library.get('totincm'), float, 0),
        }
        
        # Format currency values
        if stats['revenue'] is not None:
            stats['revenue_formatted'] = f"${stats['revenue']:,.2f}"
        
        return stats


def test_standalone_collector():
    """Test the standalone collector"""
    try:
        # Initialize collector
        logger.info("Initializing standalone collector")
        collector = StandaloneCollector()
        
        # Test year discovery
        logger.info("Testing year discovery")
        years = collector.discover_available_years()
        if years:
            logger.info(f"Discovered {len(years)} years: {years}")
        else:
            logger.warning("No years discovered")
            years = [TEST_YEAR]
        
        # Test data creation for the first year
        test_year = years[0]
        logger.info(f"Testing data creation for year {test_year}")
        data_path = collector.download_data_for_year(test_year)
        
        if data_path and os.path.exists(data_path):
            logger.info(f"Successfully created data file: {data_path}")
        else:
            logger.error(f"Failed to create data file for year {test_year}")
            return False
        
        # Test data processing
        logger.info("Testing data processing")
        processed_data = collector.process_data_for_year(test_year, data_path)
        
        if processed_data and 'libraries' in processed_data:
            libraries_count = len(processed_data['libraries'])
            outlets_count = len(processed_data.get('outlets', []))
            logger.info(f"Successfully processed data: {libraries_count} libraries, {outlets_count} outlets")
        else:
            logger.error("Failed to process data")
            return False
        
        # Test getting stats for a specific library
        logger.info(f"Testing getting stats for library {TEST_LIBRARY_ID}")
        library_stats = collector.get_library_stats(TEST_LIBRARY_ID, test_year)
        
        if library_stats:
            logger.info(f"Successfully retrieved stats for library {TEST_LIBRARY_ID}")
            logger.info(f"Library name: {library_stats['name']}")
            logger.info(f"City, State: {library_stats['city']}, {library_stats['state']}")
            logger.info(f"Visits: {library_stats['visits']}")
            logger.info(f"Circulation: {library_stats['circulation']}")
            if 'revenue_formatted' in library_stats:
                logger.info(f"Revenue: {library_stats['revenue_formatted']}")
        else:
            logger.error(f"Failed to get stats for library {TEST_LIBRARY_ID}")
            return False
        
        logger.info("All tests passed successfully!")
        return True
        
    except Exception as e:
        logger.exception(f"Error during test: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting standalone collector test")
    
    success = test_standalone_collector()
    
    if success:
        logger.info("✅ Standalone collector test completed successfully")
    else:
        logger.error("❌ Standalone collector test failed")
        sys.exit(1) 