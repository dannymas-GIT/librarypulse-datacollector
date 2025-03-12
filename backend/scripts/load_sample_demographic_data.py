#!/usr/bin/env python
"""
Script to load sample demographic data for development and testing purposes.
"""
import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.services.demographic_service import DemographicDataCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Create and load sample demographic data."""
    # Create database session
    db = SessionLocal()
    
    try:
        # Create collector
        collector = DemographicDataCollector(db)
        
        # Create sample directory
        sample_dir = os.path.join(collector.data_dir, "sample")
        os.makedirs(sample_dir, exist_ok=True)
        
        # Create sample population data
        logger.info("Creating sample population data file")
        population_file = os.path.join(sample_dir, "population_2022.csv")
        
        with open(population_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("GEOID,GEO_TYPE,STATE,COUNTY,CITY,ZIP,TOTAL_POPULATION,POP_MALE,POP_FEMALE,")
            f.write("POP_UNDER_5,POP_5_TO_9,POP_10_TO_14,POP_15_TO_19,POP_20_TO_24,")
            f.write("POP_25_TO_34,POP_35_TO_44,POP_45_TO_54,POP_55_TO_59,POP_60_TO_64,")
            f.write("POP_65_TO_74,POP_75_TO_84,POP_85_PLUS,")
            f.write("POP_WHITE,POP_BLACK,POP_HISPANIC,POP_ASIAN,POP_NATIVE,")
            f.write("POP_PACIFIC_ISLANDER,POP_OTHER_RACE,POP_TWO_OR_MORE_RACES,")
            f.write("TOTAL_HOUSEHOLDS,AVG_HOUSEHOLD_SIZE,HOUSEHOLDS_WITH_CHILDREN,")
            f.write("FAMILY_HOUSEHOLDS,NONFAMILY_HOUSEHOLDS\n")
            
            # Write sample data for New York counties
            f.write("36001,county,NY,Albany,,12203,307117,149064,158053,")
            f.write("15356,15356,15356,24569,30712,")
            f.write("46068,39925,39925,15356,15356,")
            f.write("30712,15356,7678,")
            f.write("214982,30712,30712,15356,3071,")
            f.write("1536,7678,3071,")
            f.write("125000,2.4,37500,")
            f.write("75000,50000\n")
            
            f.write("36047,county,NY,Kings,,11201,2559903,1228752,1331151,")
            f.write("179193,153594,127995,153594,204792,")
            f.write("460783,332787,281589,102396,102396,")
            f.write("179193,102396,51198,")
            f.write("1023961,639976,383985,255990,25599,")
            f.write("5120,153594,71677,")
            f.write("1000000,2.6,400000,")
            f.write("600000,400000\n")
            
            f.write("36059,county,NY,Nassau,,11530,1395774,677990,717784,")
            f.write("69789,83746,97704,97704,69789,")
            f.write("167493,181451,195409,69789,69789,")
            f.write("139577,97704,55831,")
            f.write("976042,139577,139577,139577,13958,")
            f.write("2792,41873,41873,")
            f.write("450000,2.9,180000,")
            f.write("337500,112500\n")
        
        # Create sample economic data
        logger.info("Creating sample economic data file")
        economic_file = os.path.join(sample_dir, "economic_2022.csv")
        
        with open(economic_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("GEOID,GEO_TYPE,STATE,COUNTY,CITY,ZIP,")
            f.write("MEDIAN_HOUSEHOLD_INCOME,MEAN_HOUSEHOLD_INCOME,PER_CAPITA_INCOME,")
            f.write("HOUSEHOLDS_INCOME_LESS_10K,HOUSEHOLDS_INCOME_10K_15K,HOUSEHOLDS_INCOME_15K_25K,")
            f.write("HOUSEHOLDS_INCOME_25K_35K,HOUSEHOLDS_INCOME_35K_50K,HOUSEHOLDS_INCOME_50K_75K,")
            f.write("HOUSEHOLDS_INCOME_75K_100K,HOUSEHOLDS_INCOME_100K_150K,HOUSEHOLDS_INCOME_150K_200K,")
            f.write("HOUSEHOLDS_INCOME_200K_PLUS,")
            f.write("POPULATION_IN_LABOR_FORCE,POPULATION_EMPLOYED,POPULATION_UNEMPLOYED,")
            f.write("UNEMPLOYMENT_RATE,POPULATION_BELOW_POVERTY_LEVEL,POVERTY_RATE\n")
            
            # Write sample data for New York counties
            f.write("36001,county,NY,Albany,,12203,")
            f.write("68000,82000,35000,")
            f.write("6250,3750,8750,")
            f.write("10000,15000,25000,")
            f.write("18750,22500,8750,")
            f.write("6250,")
            f.write("160000,152000,8000,")
            f.write("5.0,30712,10.0\n")
            
            f.write("36047,county,NY,Kings,,11201,")
            f.write("60000,75000,32000,")
            f.write("70000,40000,90000,")
            f.write("100000,120000,180000,")
            f.write("150000,150000,60000,")
            f.write("40000,")
            f.write("1300000,1200000,100000,")
            f.write("7.7,383985,15.0\n")
            
            f.write("36059,county,NY,Nassau,,11530,")
            f.write("116000,140000,50000,")
            f.write("13500,9000,22500,")
            f.write("27000,45000,67500,")
            f.write("76500,94500,49500,")
            f.write("45000,")
            f.write("700000,665000,35000,")
            f.write("5.0,83746,6.0\n")
        
        # Load the data
        logger.info("Loading population data from CSV")
        success = collector.load_population_data_from_csv(
            population_file, 
            source="Census ACS Sample", 
            year=2022
        )
        
        if success:
            logger.info("Successfully loaded population data")
        else:
            logger.error("Failed to load population data")
            return 1
        
        logger.info("Loading economic data from CSV")
        success = collector.load_economic_data_from_csv(
            economic_file, 
            source="Census ACS Sample", 
            year=2022
        )
        
        if success:
            logger.info("Successfully loaded economic data")
        else:
            logger.error("Failed to load economic data")
            return 1
        
        logger.info("Sample demographic data loaded successfully")
        return 0
    
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        return 1
    
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main()) 