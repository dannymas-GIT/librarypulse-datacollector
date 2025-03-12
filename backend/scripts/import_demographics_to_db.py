#!/usr/bin/env python3
"""
Script to import demographic data for West Babylon into the database.
"""
import json
import logging
import os
import sys
from datetime import date, datetime
from pathlib import Path

# Add the parent directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
project_dir = os.path.dirname(backend_dir)  # This is the datacollector root
sys.path.insert(0, backend_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to data directory
DATA_DIR = Path(project_dir) / "data" / "demographics" / "processed"

# Direct database connection (avoid environment dependency)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use the same connection string as in the other scripts
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/librarypulse"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import database models
# Need to import this after setting up database connection
sys.path.insert(0, os.path.join(backend_dir))
from app.models.demographic_data import (
    DemographicDataset, PopulationData, EconomicData, 
    EducationData, HousingData
)


def import_west_babylon_demographics():
    """
    Import West Babylon demographic data from the processed JSON file into the database.
    """
    # Path to the processed demographic data
    json_file_path = DATA_DIR / "west_babylon_demographics.json"
    
    # Check if file exists
    if not os.path.exists(json_file_path):
        logger.error(f"Error: File {json_file_path} not found.")
        return
    
    # Load JSON data
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    logger.info(f"Loaded demographic data for {data['geography']['name']}")
    
    # Create database session
    db = SessionLocal()
    try:
        # Check if dataset already exists
        existing_dataset = db.query(DemographicDataset).filter(
            DemographicDataset.source == data["data_source"]["name"],
            DemographicDataset.year == int(data["data_source"]["year"].split("-")[1])  # Extract end year
        ).first()
        
        if existing_dataset:
            logger.info(f"Dataset {data['data_source']['name']} for year {data['data_source']['year']} already exists. Skipping import.")
            return
        
        # Create demographic dataset
        dataset = DemographicDataset(
            source=data["data_source"]["name"],
            year=int(data["data_source"]["year"].split("-")[1]),  # Extract end year (2021)
            date_collected=date.today(),
            status="complete",
            record_count=1,  # Just one geographic area for now
            notes=f"Imported from processed data file on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        db.add(dataset)
        db.flush()  # Get the ID without committing
        
        # Calculate some derived values for age groups
        under_18 = data["population"]["by_age"]["under_18"]
        over_65 = data["population"]["by_age"]["over_65"]
        
        # Create population data - use fields that match the model
        population = PopulationData(
            dataset_id=dataset.id,
            geographic_id=data["geography"]["zcta"],
            geographic_type="ZCTA",
            state=data["geography"]["state"],
            county=data["geography"]["county"],
            city=data["geography"]["name"],
            zip_code=data["geography"]["zcta"],
            total_population=data["population"]["total"],
            # We don't have an exact mapping for median_age, so we'll skip it
            # For age groups, we'll distribute the under 18 and over 65 populations evenly
            population_under_5=int(under_18 / 4) if under_18 else None,
            population_5_to_9=int(under_18 / 4) if under_18 else None,
            population_10_to_14=int(under_18 / 4) if under_18 else None,
            population_15_to_19=int(under_18 / 4) if under_18 else None,
            # Adult population distributed evenly for now
            population_65_to_74=int(over_65 / 3) if over_65 else None,
            population_75_to_84=int(over_65 / 3) if over_65 else None,
            population_85_plus=int(over_65 / 3) if over_65 else None,
            # Racial demographics
            population_white=data["population"]["by_race"]["white"],
            population_black=data["population"]["by_race"]["black"],
            population_hispanic=data["population"]["by_race"]["hispanic"]
        )
        db.add(population)
        
        # Create economic data
        economic = EconomicData(
            dataset_id=dataset.id,
            geographic_id=data["geography"]["zcta"],
            geographic_type="ZCTA",
            state=data["geography"]["state"],
            county=data["geography"]["county"],
            city=data["geography"]["name"],
            zip_code=data["geography"]["zcta"],
            median_household_income=data["economics"]["median_household_income"],
            poverty_rate=data["economics"]["poverty_rate"]
        )
        db.add(economic)
        
        # Calculate values for education fields
        high_school_pop = int(data["education"]["high_school_or_higher"] / 100 * data["population"]["total"])
        bachelors_pop = int(data["education"]["bachelors_or_higher"] / 100 * data["population"]["total"])
        
        # Create education data - map to correct field names
        education = EducationData(
            dataset_id=dataset.id,
            geographic_id=data["geography"]["zcta"],
            geographic_type="ZCTA",
            state=data["geography"]["state"],
            county=data["geography"]["county"],
            city=data["geography"]["name"],
            zip_code=data["geography"]["zcta"],
            population_25_plus=int(data["population"]["total"] * 0.75),  # Estimate: 75% of population is 25+
            population_high_school_graduate=high_school_pop,
            population_bachelors_degree=bachelors_pop
        )
        db.add(education)
        
        # Create housing data - map to correct field names
        housing = HousingData(
            dataset_id=dataset.id,
            geographic_id=data["geography"]["zcta"],
            geographic_type="ZCTA",
            state=data["geography"]["state"],
            county=data["geography"]["county"],
            city=data["geography"]["name"],
            zip_code=data["geography"]["zcta"],
            total_housing_units=data["housing"]["total_units"],
            housing_owner_occupied=data["housing"]["owner_occupied"],
            housing_units_occupied=data["housing"]["total_units"]  # Assuming all units are occupied for now
        )
        db.add(housing)
        
        # Commit all changes
        db.commit()
        logger.info(f"Successfully imported demographic data for {data['geography']['name']} ({data['geography']['zcta']}).")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error importing demographic data: {str(e)}")
        # Print the full stack trace for debugging
        import traceback
        logger.error(traceback.format_exc())
    finally:
        db.close()


if __name__ == "__main__":
    # Make sure the data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Print the path to debug
    logger.info(f"Looking for data file at: {DATA_DIR / 'west_babylon_demographics.json'}")
    
    import_west_babylon_demographics()
    logger.info("Import process completed.") 