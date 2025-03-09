#!/usr/bin/env python
"""
Command-line tool for collecting PLS data.
"""
import argparse
import sys
from typing import List, Optional

from loguru import logger

from app.db.session import SessionLocal
from app.services.collector import PLSDataCollector


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="IMLS Library Pulse Data Collector")
    
    # Create a mutually exclusive group for the different collection modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--year", type=int, help="Collect data for a specific year")
    group.add_argument("--all-years", action="store_true", help="Collect data for all available years")
    group.add_argument("--update", action="store_true", help="Update with latest available data")
    group.add_argument("--discover", action="store_true", help="Discover available years without collecting data")
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the command-line tool.
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create collector
        collector = PLSDataCollector(db)
        
        if args.discover:
            # Discover available years
            years = collector.discover_available_years()
            
            if not years:
                logger.error("No available years discovered")
                return 1
            
            logger.info(f"Available years: {', '.join(str(year) for year in years)}")
            return 0
        
        elif args.year:
            # Collect data for a specific year
            logger.info(f"Collecting data for year {args.year}")
            
            success = collector.collect_data_for_year(args.year)
            
            if not success:
                logger.error(f"Failed to collect data for year {args.year}")
                return 1
            
            logger.info(f"Successfully collected data for year {args.year}")
            return 0
        
        elif args.all_years:
            # Collect data for all available years
            logger.info("Collecting data for all available years")
            
            results = collector.collect_all_available_data()
            
            if not results:
                logger.error("No data collected")
                return 1
            
            success_count = sum(1 for success in results.values() if success)
            failure_count = len(results) - success_count
            
            logger.info(f"Collected data for {success_count} years, {failure_count} failures")
            
            if failure_count > 0:
                logger.warning(f"Failed years: {', '.join(str(year) for year, success in results.items() if not success)}")
                return 1
            
            return 0
        
        elif args.update:
            # Update with latest available data
            logger.info("Updating with latest available data")
            
            latest_year = collector.update_with_latest_data()
            
            if latest_year is None:
                logger.warning("No update performed")
                return 0
            
            logger.info(f"Successfully updated with data for year {latest_year}")
            return 0
        
        else:
            # Should never reach here due to required argument group
            logger.error("No action specified")
            return 1
        
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        return 1
    
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main()) 