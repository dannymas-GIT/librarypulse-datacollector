#!/usr/bin/env python3
"""
Script to search for a specific library in the database.
"""
import os
import sys
import logging
import argparse
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

def search_library_by_name(engine, name, state=None, year=None, limit=10):
    """Search for libraries by name."""
    try:
        query = """
            SELECT 
                libname, city, stabr, fscskey, libtype, 
                popu_lsa, totstaff, totincm, totexpco, visits, totcir, year
            FROM pls_libraries
            WHERE libname ILIKE :name
        """
        
        params = {"name": f"%{name}%"}
        
        if state:
            query += " AND stabr = :state"
            params["state"] = state
            
        if year:
            query += " AND year = :year"
            params["year"] = year
            
        query += " ORDER BY year DESC, libname LIMIT :limit"
        params["limit"] = limit
        
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            libraries = []
            for row in result:
                libraries.append({col: val for col, val in row._mapping.items()})
            
        if not libraries:
            logger.info(f"No libraries found matching '{name}'")
            return []
            
        logger.info(f"Found {len(libraries)} libraries matching '{name}'")
        return libraries
        
    except SQLAlchemyError as e:
        logger.error(f"Error searching for libraries: {e}")
        return []

def search_library_by_fscs(engine, fscskey, year=None):
    """Search for a library by FSCS ID."""
    try:
        query = """
            SELECT 
                libname, address, city, zip, phone, county, stabr,
                fscskey, libtype, popu_lsa, centlib, branlib, bkmob,
                totstaff, libraria, totincm, totexpco, visits, referenc, totcir, totcoll, year
            FROM pls_libraries
            WHERE fscskey = :fscskey
        """
        
        params = {"fscskey": fscskey}
        
        if year:
            query += " AND year = :year"
            params["year"] = year
            
        query += " ORDER BY year DESC"
        
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            libraries = []
            for row in result:
                libraries.append({col: val for col, val in row._mapping.items()})
            
        if not libraries:
            logger.info(f"No library found with FSCS ID '{fscskey}'")
            return []
            
        logger.info(f"Found {len(libraries)} records for library with FSCS ID '{fscskey}'")
        return libraries
        
    except SQLAlchemyError as e:
        logger.error(f"Error searching for library: {e}")
        return []

def get_library_outlets(engine, fscskey, year=None):
    """Get outlets for a specific library."""
    try:
        query = """
            SELECT 
                libname, address, city, zip, phone, c_out_ty,
                hours, sq_feet, locale, county, countynm, year
            FROM pls_outlets
            WHERE fscskey = :fscskey
        """
        
        params = {"fscskey": fscskey}
        
        if year:
            query += " AND year = :year"
            params["year"] = year
            
        query += " ORDER BY year DESC, fscs_seq"
        
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            outlets = []
            for row in result:
                outlets.append({col: val for col, val in row._mapping.items()})
            
        if not outlets:
            logger.info(f"No outlets found for library with FSCS ID '{fscskey}'")
            return []
            
        logger.info(f"Found {len(outlets)} outlets for library with FSCS ID '{fscskey}'")
        return outlets
        
    except SQLAlchemyError as e:
        logger.error(f"Error getting library outlets: {e}")
        return []

def display_library_info(library):
    """Display detailed information about a library."""
    print("\n" + "=" * 80)
    print(f"LIBRARY: {library['libname']} (FSCS ID: {library['fscskey']}, Year: {library['year']})")
    print("=" * 80)
    
    # Location information
    print(f"Location: {library['city']}, {library['stabr']}")
    if 'address' in library and library['address']:
        print(f"Address: {library['address']}, {library['zip']}")
    if 'phone' in library and library['phone']:
        print(f"Phone: {library['phone']}")
    
    # Library type and service information
    print(f"Type: {library['libtype']}")
    print(f"Population Served: {library.get('popu_lsa', 'N/A'):,}")
    
    # Facilities
    if 'centlib' in library:
        print(f"Facilities: {library['centlib']} central libraries, "
              f"{library.get('branlib', 0)} branches, "
              f"{library.get('bkmob', 0)} bookmobiles")
    
    # Staff
    if 'totstaff' in library and library['totstaff']:
        print(f"Total Staff: {float(library['totstaff']):,.1f}")
        if 'libraria' in library and library['libraria']:
            print(f"Librarians: {float(library['libraria']):,.1f}")
    
    # Financial information
    if 'totincm' in library and library['totincm']:
        print(f"Total Income: ${float(library['totincm']):,.2f}")
    if 'totexpco' in library and library['totexpco']:
        print(f"Total Expenditures: ${float(library['totexpco']):,.2f}")
    
    # Usage statistics
    if 'visits' in library and library['visits']:
        print(f"Annual Visits: {float(library['visits']):,.0f}")
    if 'referenc' in library and library['referenc']:
        print(f"Reference Transactions: {float(library['referenc']):,.0f}")
    if 'totcir' in library and library['totcir']:
        print(f"Total Circulation: {float(library['totcir']):,.0f}")
    if 'totcoll' in library and library['totcoll']:
        print(f"Total Collection: {float(library['totcoll']):,.0f} items")
    
    print("-" * 80)

def display_outlets(outlets):
    """Display information about library outlets."""
    if not outlets:
        return
        
    print("\nOUTLETS:")
    print("-" * 80)
    
    for outlet in outlets:
        print(f"Name: {outlet['libname']}")
        print(f"Type: {outlet['c_out_ty']}")
        print(f"Address: {outlet['address']}, {outlet['city']}, {outlet.get('zip', '')}")
        if 'phone' in outlet and outlet['phone']:
            print(f"Phone: {outlet['phone']}")
        if 'sq_feet' in outlet and outlet['sq_feet']:
            print(f"Square Footage: {outlet['sq_feet']:,}")
        if 'hours' in outlet and outlet['hours']:
            print(f"Weekly Hours: {outlet['hours']}")
        print("-" * 40)

def main():
    """Main function to search for libraries."""
    parser = argparse.ArgumentParser(description="Search for libraries in the PLS database")
    
    # Define search methods as mutually exclusive group
    search_group = parser.add_mutually_exclusive_group(required=True)
    search_group.add_argument("--name", help="Search by library name")
    search_group.add_argument("--fscs", help="Search by FSCS ID")
    
    # Additional filters
    parser.add_argument("--state", help="Filter by state abbreviation (e.g., CA, NY)")
    parser.add_argument("--year", type=int, help="Filter by year")
    parser.add_argument("--limit", type=int, default=10, help="Limit search results (default: 10)")
    parser.add_argument("--outlets", action="store_true", help="Show outlet information for the library")
    
    args = parser.parse_args()
    
    try:
        # Connect to database
        engine = create_engine_with_retry(DB_URL)
        
        if args.name:
            # Search by name
            libraries = search_library_by_name(engine, args.name, args.state, args.year, args.limit)
            
            if not libraries:
                return
                
            # Display search results
            print(f"\nFound {len(libraries)} libraries matching '{args.name}':")
            for i, lib in enumerate(libraries, 1):
                print(f"{i}. {lib['libname']} - {lib['city']}, {lib['stabr']} (FSCS: {lib['fscskey']}, Year: {lib['year']})")
            
            # If multiple results, ask user to select one
            if len(libraries) > 1:
                try:
                    selection = int(input("\nEnter the number of the library to view details (0 to exit): "))
                    if selection == 0:
                        return
                    if 1 <= selection <= len(libraries):
                        selected_library = libraries[selection - 1]
                        # Get full library details
                        library_details = search_library_by_fscs(engine, selected_library['fscskey'], selected_library['year'])
                        if library_details:
                            display_library_info(library_details[0])
                            
                            # Show outlets if requested
                            if args.outlets:
                                outlets = get_library_outlets(engine, selected_library['fscskey'], selected_library['year'])
                                display_outlets(outlets)
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            elif len(libraries) == 1:
                # Get full library details
                library_details = search_library_by_fscs(engine, libraries[0]['fscskey'], libraries[0]['year'])
                if library_details:
                    display_library_info(library_details[0])
                    
                    # Show outlets if requested
                    if args.outlets:
                        outlets = get_library_outlets(engine, libraries[0]['fscskey'], libraries[0]['year'])
                        display_outlets(outlets)
        
        elif args.fscs:
            # Search by FSCS ID
            libraries = search_library_by_fscs(engine, args.fscs, args.year)
            
            if not libraries:
                return
                
            # If multiple years, show a summary
            if len(libraries) > 1 and not args.year:
                print(f"\nFound data for {len(libraries)} years for library with FSCS ID '{args.fscs}':")
                for lib in libraries:
                    print(f"Year {lib['year']}: {lib['libname']} - {lib['city']}, {lib['stabr']}")
                
                # Ask user to select a year
                try:
                    year = int(input("\nEnter the year to view details (0 to exit): "))
                    if year == 0:
                        return
                    
                    # Find the library record for the selected year
                    selected_library = next((lib for lib in libraries if lib['year'] == year), None)
                    if selected_library:
                        display_library_info(selected_library)
                        
                        # Show outlets if requested
                        if args.outlets:
                            outlets = get_library_outlets(engine, args.fscs, year)
                            display_outlets(outlets)
                    else:
                        print(f"No data available for year {year}.")
                except ValueError:
                    print("Invalid input. Please enter a year.")
            else:
                # Display the first (most recent) library
                display_library_info(libraries[0])
                
                # Show outlets if requested
                if args.outlets:
                    outlets = get_library_outlets(engine, args.fscs, libraries[0]['year'])
                    display_outlets(outlets)
    
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main() 