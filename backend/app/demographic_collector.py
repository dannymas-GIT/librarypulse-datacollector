#!/usr/bin/env python
"""
Command-line tool for collecting demographic data.
"""
import argparse
import os
import sys
from typing import List, Optional

from loguru import logger

from app.db.session import SessionLocal
from app.services.demographic_service import DemographicDataCollector


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Library Pulse Demographic Data Collector")
    
    # Create a mutually exclusive group for the different collection modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--load-csv", type=str, help="Load data from a CSV file")
    group.add_argument("--fetch-api", action="store_true", help="Fetch data from the Census API")
    group.add_argument("--create-sample", action="store_true", help="Create sample data files")
    
    # Common arguments
    parser.add_argument("--source", type=str, default="Census ACS", help="Source of the data")
    parser.add_argument("--year", type=int, required=True, help="Year of the data")
    parser.add_argument("--state", type=str, help="State code (e.g., 'NY')")
    parser.add_argument("--data-type", type=str, choices=["population", "economic", "education", "language", "housing"], 
                        default="population", help="Type of data to collect")
    
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
        collector = DemographicDataCollector(db)
        
        if args.load_csv:
            # Load data from a CSV file
            file_path = args.load_csv
            
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return 1
            
            logger.info(f"Loading {args.data_type} data from {file_path}")
            
            if args.data_type == "population":
                success = collector.load_population_data_from_csv(file_path, args.source, args.year)
            elif args.data_type == "economic":
                success = collector.load_economic_data_from_csv(file_path, args.source, args.year)
            else:
                logger.error(f"Loading {args.data_type} data from CSV is not implemented yet")
                return 1
            
            if not success:
                logger.error(f"Failed to load data from {file_path}")
                return 1
            
            logger.info(f"Successfully loaded data from {file_path}")
            return 0
        
        elif args.fetch_api:
            # Fetch data from the Census API
            if not args.state:
                logger.error("State code is required for API fetching")
                return 1
            
            logger.info(f"Fetching {args.data_type} data for {args.state} from Census API")
            
            if args.data_type == "population":
                success = collector.fetch_population_data_from_census_api(args.state, year=args.year)
            else:
                logger.error(f"Fetching {args.data_type} data from API is not implemented yet")
                return 1
            
            if not success:
                logger.error(f"Failed to fetch data from Census API")
                return 1
            
            logger.info(f"Successfully fetched data from Census API")
            return 0
        
        elif args.create_sample:
            # Create sample data files
            logger.info(f"Creating sample {args.data_type} data files")
            
            # Create sample directory
            sample_dir = os.path.join(collector.data_dir, "sample")
            os.makedirs(sample_dir, exist_ok=True)
            
            if args.data_type == "population":
                # Create sample population data file
                file_path = os.path.join(sample_dir, f"population_{args.year}.csv")
                
                with open(file_path, 'w', encoding='utf-8') as f:
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
                
                logger.info(f"Created sample population data file: {file_path}")
            
            elif args.data_type == "economic":
                # Create sample economic data file
                file_path = os.path.join(sample_dir, f"economic_{args.year}.csv")
                
                with open(file_path, 'w', encoding='utf-8') as f:
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
                
                logger.info(f"Created sample economic data file: {file_path}")
            
            else:
                logger.error(f"Creating sample {args.data_type} data is not implemented yet")
                return 1
            
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