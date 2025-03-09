#!/usr/bin/env python3
"""
Script to generate sample library data for testing.
"""
import os
import sys
import logging
import csv
import random
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Sample library data
LIBRARY_TYPES = ["CE", "CR", "CO", "LD", "FS", "SO"]
ADMIN_TYPES = ["MA", "MO", "MC", "SO", "CC", "NL", "NP", "NA"]
STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

def generate_fscs_id(state, index):
    """Generate a unique FSCS ID for a library."""
    return f"{state}{index:05d}"

def generate_library_data(num_libraries=100, year=2021):
    """Generate sample library data."""
    libraries = []
    
    for i in range(1, num_libraries + 1):
        state = random.choice(STATES)
        fscs_id = generate_fscs_id(state, i)
        
        library = {
            "libid": i,
            "libname": f"Sample Library {i}",
            "address": f"{random.randint(100, 9999)} Main St",
            "city": f"City {i}",
            "zip": f"{random.randint(10000, 99999)}",
            "phone": f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "county": f"County {i}",
            "state": f"State {state}",
            "stabr": state,
            "fscskey": fscs_id,
            "fscs_seq": "1",
            "libtype": random.choice(LIBRARY_TYPES),
            "c_admin": random.choice(ADMIN_TYPES),
            "c_fscs": "1",
            "geocode": f"{random.randint(1000, 9999)}",
            "lsabound": "CI",
            "startdat": "01/01/2021",
            "enddate": "12/31/2021",
            "popu_lsa": random.randint(1000, 100000),
            "centlib": random.randint(0, 1),
            "branlib": random.randint(0, 5),
            "bkmob": random.randint(0, 2),
            "totstaff": round(random.uniform(1, 50), 2),
            "libraria": round(random.uniform(1, 10), 2),
            "totincm": round(random.uniform(10000, 1000000), 2),
            "totexpco": round(random.uniform(10000, 900000), 2),
            "visits": random.randint(1000, 100000),
            "referenc": random.randint(100, 10000),
            "totcir": random.randint(1000, 100000),
            "totcoll": random.randint(5000, 500000),
            "year": year
        }
        
        libraries.append(library)
    
    return libraries

def generate_outlet_data(libraries, year=2021):
    """Generate sample outlet data based on libraries."""
    outlets = []
    
    for library in libraries:
        # Main outlet (central library)
        if library["centlib"] > 0:
            outlet = {
                "libid": library["libid"],
                "libname": library["libname"],
                "fscskey": library["fscskey"],
                "fscs_seq": "1",
                "stabr": library["stabr"],
                "statname": f"State {library['stabr']}",
                "address": library["address"],
                "city": library["city"],
                "zip": library["zip"],
                "phone": library["phone"],
                "c_out_ty": "CE",
                "c_fscs": "1",
                "hours": random.randint(20, 70),
                "sq_feet": random.randint(1000, 50000),
                "locale": f"{random.randint(1, 4)}{random.randint(1, 3)}",
                "county": library["county"],
                "countynm": f"County {library['county']}",
                "year": year
            }
            outlets.append(outlet)
        
        # Branch libraries
        for j in range(1, library["branlib"] + 1):
            outlet = {
                "libid": library["libid"],
                "libname": f"{library['libname']} - Branch {j}",
                "fscskey": library["fscskey"],
                "fscs_seq": f"{j+1}",
                "stabr": library["stabr"],
                "statname": f"State {library['stabr']}",
                "address": f"{random.randint(100, 9999)} Branch St",
                "city": library["city"],
                "zip": library["zip"],
                "phone": f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "c_out_ty": "BR",
                "c_fscs": "1",
                "hours": random.randint(20, 60),
                "sq_feet": random.randint(500, 20000),
                "locale": f"{random.randint(1, 4)}{random.randint(1, 3)}",
                "county": library["county"],
                "countynm": f"County {library['county']}",
                "year": year
            }
            outlets.append(outlet)
    
    return outlets

def write_csv(data, filename):
    """Write data to a CSV file."""
    if not data:
        logger.error(f"No data to write to {filename}")
        return False
    
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Successfully wrote {len(data)} records to {filename}")
        return True
    
    except Exception as e:
        logger.error(f"Error writing to {filename}: {e}")
        return False

def main():
    """Main function to generate sample data."""
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / "data" / "sample"
    data_dir.mkdir(exist_ok=True, parents=True)
    
    # Get parameters from command line
    num_libraries = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2021
    
    logger.info(f"Generating sample data for {num_libraries} libraries for year {year}")
    
    # Generate library data
    libraries = generate_library_data(num_libraries, year)
    
    # Generate outlet data
    outlets = generate_outlet_data(libraries, year)
    
    # Write data to CSV files
    library_file = data_dir / f"pls_sample_{year}_library.csv"
    outlet_file = data_dir / f"pls_sample_{year}_outlet.csv"
    
    write_csv(libraries, library_file)
    write_csv(outlets, outlet_file)
    
    logger.info(f"Sample data generation completed")
    logger.info(f"Library data: {library_file}")
    logger.info(f"Outlet data: {outlet_file}")

if __name__ == "__main__":
    main() 