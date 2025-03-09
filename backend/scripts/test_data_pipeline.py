#!/usr/bin/env python
"""
Test script for the IMLS Library Pulse data pipeline.

This script tests the data collection pipeline by:
1. Discovering available years
2. Downloading data for the most recent year
3. Processing the data
4. Loading it into the database
"""
import argparse
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the app modules
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from loguru import logger
from app.db.session import SessionLocal
from app.services.collector import PLSDataCollector
from app.models.library_config import LibraryConfig
from app.services.library_config_service import LibraryConfigService


def test_data_discovery():
    """Test discovering available years from IMLS website."""
    db = SessionLocal()
    
    try:
        collector = PLSDataCollector(db)
        years = collector.discover_available_years()
        
        if not years:
            logger.error("❌ Failed to discover any available years")
            return False
        
        logger.info(f"✅ Successfully discovered {len(years)} available years: {', '.join(str(y) for y in years)}")
        return True
    
    except Exception as e:
        logger.exception(f"❌ Error during data discovery: {str(e)}")
        return False
    
    finally:
        db.close()


def test_data_download(year=None):
    """Test downloading data for a specific year or the most recent year."""
    db = SessionLocal()
    
    try:
        collector = PLSDataCollector(db)
        
        # If year not specified, get the most recent year
        if year is None:
            years = collector.discover_available_years()
            if not years:
                logger.error("❌ Failed to discover available years")
                return False
            
            year = max(years)
        
        logger.info(f"Testing data download for year {year}")
        
        # Download data
        data_path = collector.download_data_for_year(year)
        
        if data_path.exists():
            logger.info(f"✅ Successfully downloaded data for year {year} to {data_path}")
            return True, data_path, year
        else:
            logger.error(f"❌ Failed to download data for year {year}")
            return False, None, year
    
    except Exception as e:
        logger.exception(f"❌ Error during data download: {str(e)}")
        return False, None, year
    
    finally:
        db.close()


def test_data_processing(data_path, year):
    """Test processing downloaded data."""
    db = SessionLocal()
    
    try:
        collector = PLSDataCollector(db)
        
        # Process data
        processed_data = collector.process_data_for_year(year, data_path)
        
        if not processed_data or not processed_data.get('libraries') is not None:
            logger.error(f"❌ Failed to process data for year {year}")
            return False, None
        
        library_count = len(processed_data.get('libraries', []))
        outlet_count = len(processed_data.get('outlets', [])) if processed_data.get('outlets') is not None else 0
        
        logger.info(f"✅ Successfully processed data for year {year}: {library_count} libraries, {outlet_count} outlets")
        return True, processed_data
    
    except Exception as e:
        logger.exception(f"❌ Error during data processing: {str(e)}")
        return False, None
    
    finally:
        db.close()


def test_data_loading(processed_data, year):
    """Test loading processed data into the database."""
    db = SessionLocal()
    
    try:
        collector = PLSDataCollector(db)
        
        # Load data into database
        collector.load_data_into_db(year, processed_data)
        
        logger.info(f"✅ Successfully loaded data for year {year} into database")
        return True
    
    except Exception as e:
        logger.exception(f"❌ Error during data loading: {str(e)}")
        return False
    
    finally:
        db.close()


def test_library_specific_data(library_id):
    """Test collecting data for a specific library."""
    db = SessionLocal()
    
    try:
        # Create a test library configuration if it doesn't exist
        config = LibraryConfigService.get_library_config(db)
        if not config:
            logger.info(f"Creating test library configuration for library ID: {library_id}")
            LibraryConfigService.create_or_update_config(
                db=db,
                library_id=library_id,
                library_name=f"Test Library {library_id}",
                setup_complete=True
            )
        elif config.library_id != library_id:
            logger.info(f"Updating library configuration from {config.library_id} to {library_id}")
            LibraryConfigService.create_or_update_config(
                db=db,
                library_id=library_id,
                library_name=f"Test Library {library_id}",
                setup_complete=True
            )
        
        collector = PLSDataCollector(db)
        years = collector.discover_available_years()
        
        if not years:
            logger.error("❌ Failed to discover available years")
            return False
        
        # Just test the most recent year
        year = max(years)
        
        success = collector.collect_data_for_year(year)
        
        if success:
            logger.info(f"✅ Successfully collected data for library {library_id} for year {year}")
            return True
        else:
            logger.error(f"❌ Failed to collect data for library {library_id} for year {year}")
            return False
    
    except Exception as e:
        logger.exception(f"❌ Error during library-specific data collection: {str(e)}")
        return False
    
    finally:
        db.close()


def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test the IMLS Library Pulse data pipeline")
    parser.add_argument("--year", type=int, help="Specific year to test")
    parser.add_argument("--library", type=str, help="Specific library ID to test")
    parser.add_argument("--full", action="store_true", help="Run a full test including database loading")
    parser.add_argument("--discovery-only", action="store_true", help="Only test data discovery")
    
    args = parser.parse_args()
    
    logger.info("Starting data pipeline test")
    
    # If a specific library ID is provided, test that
    if args.library:
        logger.info(f"Testing data collection for library ID: {args.library}")
        success = test_library_specific_data(args.library)
        sys.exit(0 if success else 1)
    
    # If only testing discovery
    if args.discovery_only:
        success = test_data_discovery()
        sys.exit(0 if success else 1)
    
    # Test data discovery
    discovery_success = test_data_discovery()
    if not discovery_success:
        logger.error("Data discovery test failed, aborting further tests")
        sys.exit(1)
    
    # Test data download
    download_success, data_path, year = test_data_download(args.year)
    if not download_success:
        logger.error("Data download test failed, aborting further tests")
        sys.exit(1)
    
    # Test data processing
    processing_success, processed_data = test_data_processing(data_path, year)
    if not processing_success:
        logger.error("Data processing test failed, aborting further tests")
        sys.exit(1)
    
    # If full test, also test loading into database
    if args.full:
        loading_success = test_data_loading(processed_data, year)
        if not loading_success:
            logger.error("Data loading test failed")
            sys.exit(1)
    
    logger.info("All tests completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main() 