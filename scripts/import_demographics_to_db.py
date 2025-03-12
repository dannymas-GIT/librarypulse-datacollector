#!/usr/bin/env python3
import json
import os
import sys
from datetime import date, datetime

# Add parent directory to path so we can import modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.insert(0, project_dir)

# Import database models - use direct imports from backend
try:
    from backend.app.models.demographic_data import (
        DemographicDataset, PopulationData, EconomicData, 
        EducationData, HousingData
    )
    from backend.app.db.session import SessionLocal
    
    print("Successfully imported backend modules")
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


def import_west_babylon_demographics():
    """
    Import West Babylon demographic data from the processed JSON file into the database.
    """
    # Path to the processed demographic data
    json_file_path = os.path.join(
        project_dir, "data", "demographics", "processed", "west_babylon_demographics.json"
    )
    
    # Check if file exists
    if not os.path.exists(json_file_path):
        print(f"Error: File {json_file_path} not found.")
        return
    
    # Load JSON data
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    print(f"Loaded demographic data for {data['geography']['name']}")
    
    # Create database session
    db = SessionLocal()
    try:
        # Check if dataset already exists
        existing_dataset = db.query(DemographicDataset).filter(
            DemographicDataset.source == data["data_source"]["name"],
            DemographicDataset.year == int(data["data_source"]["year"].split("-")[1])  # Extract end year
        ).first()
        
        if existing_dataset:
            print(f"Dataset {data['data_source']['name']} for year {data['data_source']['year']} already exists. Skipping import.")
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
        
        # Create population data
        population = PopulationData(
            dataset_id=dataset.id,
            geographic_id=data["geography"]["zcta"],
            geographic_type="ZCTA",
            state=data["geography"]["state"],
            county=data["geography"]["county"],
            city=data["geography"]["name"],
            zip_code=data["geography"]["zcta"],
            total_population=data["population"]["total"],
            median_age=data["population"]["median_age"],
            population_under_18=data["population"]["by_age"]["under_18"],
            population_65_plus=data["population"]["by_age"]["over_65"],
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
        
        # Create education data
        education = EducationData(
            dataset_id=dataset.id,
            geographic_id=data["geography"]["zcta"],
            geographic_type="ZCTA",
            state=data["geography"]["state"],
            county=data["geography"]["county"],
            city=data["geography"]["name"],
            zip_code=data["geography"]["zcta"],
            high_school_or_higher_percent=data["education"]["high_school_or_higher"],
            bachelors_or_higher_percent=data["education"]["bachelors_or_higher"]
        )
        db.add(education)
        
        # Create housing data
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
            housing_median_value=data["housing"]["median_home_value"]
        )
        db.add(housing)
        
        # Commit all changes
        db.commit()
        print(f"Successfully imported demographic data for {data['geography']['name']} ({data['geography']['zcta']}).")
        
    except Exception as e:
        db.rollback()
        print(f"Error importing demographic data: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    import_west_babylon_demographics()
    print("Import process completed.") 