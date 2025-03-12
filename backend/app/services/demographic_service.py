import os
import csv
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from loguru import logger

from app.models.demographic_data import (
    DemographicDataset,
    PopulationData,
    EconomicData,
    EducationData,
    LanguageData,
    HousingData
)


class DemographicDataCollector:
    """Service for collecting and managing demographic data."""
    
    def __init__(self, db: Session):
        """Initialize the demographic data collector.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "demographics")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Census API configuration
        self.census_api_key = os.environ.get("CENSUS_API_KEY", "")
        self.census_api_base_url = "https://api.census.gov/data"
    
    def load_population_data_from_csv(self, file_path: str, source: str, year: int) -> bool:
        """Load population data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            source: Source of the data (e.g., "Census ACS")
            year: Year of the data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create or get the dataset
            dataset = self._get_or_create_dataset(source, year)
            
            # Read the CSV file
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Process each row
                for row in reader:
                    # Extract geographic identifiers
                    geographic_id = row.get('GEOID', '')
                    geographic_type = row.get('GEO_TYPE', '')
                    state = row.get('STATE', '')
                    county = row.get('COUNTY', '')
                    city = row.get('CITY', '')
                    zip_code = row.get('ZIP', '')
                    
                    # Skip if missing required fields
                    if not geographic_id or not state:
                        logger.warning(f"Skipping row with missing required fields: {row}")
                        continue
                    
                    # Create population data object
                    population_data = PopulationData(
                        dataset_id=dataset.id,
                        geographic_id=geographic_id,
                        geographic_type=geographic_type,
                        state=state,
                        county=county,
                        city=city,
                        zip_code=zip_code,
                        
                        # Population data
                        total_population=self._safe_int(row.get('TOTAL_POPULATION')),
                        
                        # Age ranges
                        population_under_5=self._safe_int(row.get('POP_UNDER_5')),
                        population_5_to_9=self._safe_int(row.get('POP_5_TO_9')),
                        population_10_to_14=self._safe_int(row.get('POP_10_TO_14')),
                        population_15_to_19=self._safe_int(row.get('POP_15_TO_19')),
                        population_20_to_24=self._safe_int(row.get('POP_20_TO_24')),
                        population_25_to_34=self._safe_int(row.get('POP_25_TO_34')),
                        population_35_to_44=self._safe_int(row.get('POP_35_TO_44')),
                        population_45_to_54=self._safe_int(row.get('POP_45_TO_54')),
                        population_55_to_59=self._safe_int(row.get('POP_55_TO_59')),
                        population_60_to_64=self._safe_int(row.get('POP_60_TO_64')),
                        population_65_to_74=self._safe_int(row.get('POP_65_TO_74')),
                        population_75_to_84=self._safe_int(row.get('POP_75_TO_84')),
                        population_85_plus=self._safe_int(row.get('POP_85_PLUS')),
                        
                        # Sex
                        population_male=self._safe_int(row.get('POP_MALE')),
                        population_female=self._safe_int(row.get('POP_FEMALE')),
                        
                        # Race/ethnicity
                        population_white=self._safe_int(row.get('POP_WHITE')),
                        population_black=self._safe_int(row.get('POP_BLACK')),
                        population_hispanic=self._safe_int(row.get('POP_HISPANIC')),
                        population_asian=self._safe_int(row.get('POP_ASIAN')),
                        population_native=self._safe_int(row.get('POP_NATIVE')),
                        population_pacific_islander=self._safe_int(row.get('POP_PACIFIC_ISLANDER')),
                        population_other_race=self._safe_int(row.get('POP_OTHER_RACE')),
                        population_two_or_more_races=self._safe_int(row.get('POP_TWO_OR_MORE_RACES')),
                        
                        # Household data
                        total_households=self._safe_int(row.get('TOTAL_HOUSEHOLDS')),
                        avg_household_size=self._safe_float(row.get('AVG_HOUSEHOLD_SIZE')),
                        households_with_children=self._safe_int(row.get('HOUSEHOLDS_WITH_CHILDREN')),
                        family_households=self._safe_int(row.get('FAMILY_HOUSEHOLDS')),
                        nonfamily_households=self._safe_int(row.get('NONFAMILY_HOUSEHOLDS'))
                    )
                    
                    # Add to database
                    self.db.add(population_data)
            
            # Update dataset status and record count
            dataset.status = "complete"
            dataset.record_count = self.db.query(PopulationData).filter(
                PopulationData.dataset_id == dataset.id
            ).count()
            
            # Commit changes
            self.db.commit()
            
            logger.info(f"Successfully loaded population data from {file_path}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Error loading population data: {str(e)}")
            return False
    
    def load_economic_data_from_csv(self, file_path: str, source: str, year: int) -> bool:
        """Load economic data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            source: Source of the data (e.g., "Census ACS")
            year: Year of the data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create or get the dataset
            dataset = self._get_or_create_dataset(source, year)
            
            # Read the CSV file
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Process each row
                for row in reader:
                    # Extract geographic identifiers
                    geographic_id = row.get('GEOID', '')
                    geographic_type = row.get('GEO_TYPE', '')
                    state = row.get('STATE', '')
                    county = row.get('COUNTY', '')
                    city = row.get('CITY', '')
                    zip_code = row.get('ZIP', '')
                    
                    # Skip if missing required fields
                    if not geographic_id or not state:
                        logger.warning(f"Skipping row with missing required fields: {row}")
                        continue
                    
                    # Create economic data object
                    economic_data = EconomicData(
                        dataset_id=dataset.id,
                        geographic_id=geographic_id,
                        geographic_type=geographic_type,
                        state=state,
                        county=county,
                        city=city,
                        zip_code=zip_code,
                        
                        # Income data
                        median_household_income=self._safe_int(row.get('MEDIAN_HOUSEHOLD_INCOME')),
                        mean_household_income=self._safe_int(row.get('MEAN_HOUSEHOLD_INCOME')),
                        per_capita_income=self._safe_int(row.get('PER_CAPITA_INCOME')),
                        
                        # Income ranges
                        households_income_less_10k=self._safe_int(row.get('HOUSEHOLDS_INCOME_LESS_10K')),
                        households_income_10k_15k=self._safe_int(row.get('HOUSEHOLDS_INCOME_10K_15K')),
                        households_income_15k_25k=self._safe_int(row.get('HOUSEHOLDS_INCOME_15K_25K')),
                        households_income_25k_35k=self._safe_int(row.get('HOUSEHOLDS_INCOME_25K_35K')),
                        households_income_35k_50k=self._safe_int(row.get('HOUSEHOLDS_INCOME_35K_50K')),
                        households_income_50k_75k=self._safe_int(row.get('HOUSEHOLDS_INCOME_50K_75K')),
                        households_income_75k_100k=self._safe_int(row.get('HOUSEHOLDS_INCOME_75K_100K')),
                        households_income_100k_150k=self._safe_int(row.get('HOUSEHOLDS_INCOME_100K_150K')),
                        households_income_150k_200k=self._safe_int(row.get('HOUSEHOLDS_INCOME_150K_200K')),
                        households_income_200k_plus=self._safe_int(row.get('HOUSEHOLDS_INCOME_200K_PLUS')),
                        
                        # Employment data
                        population_in_labor_force=self._safe_int(row.get('POPULATION_IN_LABOR_FORCE')),
                        population_employed=self._safe_int(row.get('POPULATION_EMPLOYED')),
                        population_unemployed=self._safe_int(row.get('POPULATION_UNEMPLOYED')),
                        unemployment_rate=self._safe_float(row.get('UNEMPLOYMENT_RATE')),
                        
                        # Poverty data
                        population_below_poverty_level=self._safe_int(row.get('POPULATION_BELOW_POVERTY_LEVEL')),
                        poverty_rate=self._safe_float(row.get('POVERTY_RATE'))
                    )
                    
                    # Add to database
                    self.db.add(economic_data)
            
            # Update dataset status and record count
            dataset.status = "complete"
            dataset.record_count = self.db.query(EconomicData).filter(
                EconomicData.dataset_id == dataset.id
            ).count()
            
            # Commit changes
            self.db.commit()
            
            logger.info(f"Successfully loaded economic data from {file_path}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Error loading economic data: {str(e)}")
            return False
    
    def fetch_population_data_from_census_api(self, state: str, county: Optional[str] = None, year: int = 2022) -> bool:
        """Fetch population data from the Census API.
        
        Args:
            state: State code (e.g., "NY")
            county: County name (optional)
            year: Year of the data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.census_api_key:
            logger.error("Census API key not configured")
            return False
        
        try:
            # Create dataset
            dataset = self._get_or_create_dataset("Census ACS", year)
            
            # Build API URL
            url = f"{self.census_api_base_url}/{year}/acs/acs5"
            
            # Define variables to fetch
            variables = [
                "NAME",  # Geographic name
                "B01001_001E",  # Total population
                "B01001_002E",  # Male population
                "B01001_026E",  # Female population
                "B01001_003E",  # Male under 5 years
                "B01001_027E",  # Female under 5 years
                # Add more variables as needed
            ]
            
            # Build query parameters
            params = {
                "get": ",".join(variables),
                "for": f"county:*" if county is None else f"county:{county}",
                "in": f"state:{state}",
                "key": self.census_api_key
            }
            
            # Make API request
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            headers = data[0]
            rows = data[1:]
            
            # Process each row
            for row in rows:
                # Create a dictionary from headers and row values
                row_dict = dict(zip(headers, row))
                
                # Extract values
                county_name = row_dict.get("NAME", "").split(",")[0].strip()
                state_name = row_dict.get("NAME", "").split(",")[1].strip() if "," in row_dict.get("NAME", "") else ""
                
                # Create geographic ID (FIPS code)
                state_code = row_dict.get("state", "")
                county_code = row_dict.get("county", "")
                geographic_id = f"{state_code}{county_code}"
                
                # Calculate age groups
                male_under_5 = self._safe_int(row_dict.get("B01001_003E", 0))
                female_under_5 = self._safe_int(row_dict.get("B01001_027E", 0))
                population_under_5 = male_under_5 + female_under_5
                
                # Create population data object
                population_data = PopulationData(
                    dataset_id=dataset.id,
                    geographic_id=geographic_id,
                    geographic_type="county",
                    state=state,
                    county=county_name,
                    
                    # Population data
                    total_population=self._safe_int(row_dict.get("B01001_001E")),
                    population_male=self._safe_int(row_dict.get("B01001_002E")),
                    population_female=self._safe_int(row_dict.get("B01001_026E")),
                    
                    # Age data
                    population_under_5=population_under_5,
                    # Add more age groups as needed
                )
                
                # Add to database
                self.db.add(population_data)
            
            # Update dataset status and record count
            dataset.status = "complete"
            dataset.record_count = self.db.query(PopulationData).filter(
                PopulationData.dataset_id == dataset.id
            ).count()
            
            # Commit changes
            self.db.commit()
            
            logger.info(f"Successfully fetched population data for {state}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Error fetching population data: {str(e)}")
            return False
    
    def _get_or_create_dataset(self, source: str, year: int) -> DemographicDataset:
        """Get or create a demographic dataset.
        
        Args:
            source: Source of the data (e.g., "Census ACS")
            year: Year of the data
            
        Returns:
            DemographicDataset: The dataset object
        """
        # Check if dataset already exists
        dataset = self.db.query(DemographicDataset).filter(
            DemographicDataset.source == source,
            DemographicDataset.year == year
        ).first()
        
        # Create new dataset if it doesn't exist
        if dataset is None:
            dataset = DemographicDataset(
                source=source,
                year=year,
                date_collected=datetime.now().date(),
                status="pending"
            )
            self.db.add(dataset)
            self.db.commit()
        
        return dataset
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert a value to an integer.
        
        Args:
            value: Value to convert
            
        Returns:
            int or None: Converted value or None if conversion fails
        """
        if value is None:
            return None
        
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert a value to a float.
        
        Args:
            value: Value to convert
            
        Returns:
            float or None: Converted value or None if conversion fails
        """
        if value is None:
            return None
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


class DemographicService:
    """Service for accessing demographic data."""
    
    def __init__(self, db: Session):
        """Initialize the demographic service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def get_population_data(self, state: str, county: Optional[str] = None, 
                           city: Optional[str] = None, zip_code: Optional[str] = None,
                           year: Optional[int] = None) -> List[Dict]:
        """Get population data for a specific geographic area.
        
        Args:
            state: State code (e.g., "NY")
            county: County name (optional)
            city: City name (optional)
            zip_code: ZIP code (optional)
            year: Year of the data (optional, defaults to most recent)
            
        Returns:
            List[Dict]: List of population data dictionaries
        """
        # Build query
        query = self.db.query(PopulationData).join(
            DemographicDataset, 
            PopulationData.dataset_id == DemographicDataset.id
        ).filter(
            PopulationData.state == state
        )
        
        # Add optional filters
        if county:
            query = query.filter(PopulationData.county == county)
        
        if city:
            query = query.filter(PopulationData.city == city)
        
        if zip_code:
            query = query.filter(PopulationData.zip_code == zip_code)
        
        if year:
            query = query.filter(DemographicDataset.year == year)
        else:
            # Get most recent year
            subquery = self.db.query(DemographicDataset.year).order_by(
                DemographicDataset.year.desc()
            ).limit(1).scalar_subquery()
            
            query = query.filter(DemographicDataset.year == subquery)
        
        # Execute query
        results = query.all()
        
        # Convert to dictionaries
        return [self._population_data_to_dict(result) for result in results]
    
    def get_economic_data(self, state: str, county: Optional[str] = None, 
                         city: Optional[str] = None, zip_code: Optional[str] = None,
                         year: Optional[int] = None) -> List[Dict]:
        """Get economic data for a specific geographic area.
        
        Args:
            state: State code (e.g., "NY")
            county: County name (optional)
            city: City name (optional)
            zip_code: ZIP code (optional)
            year: Year of the data (optional, defaults to most recent)
            
        Returns:
            List[Dict]: List of economic data dictionaries
        """
        # Build query
        query = self.db.query(EconomicData).join(
            DemographicDataset, 
            EconomicData.dataset_id == DemographicDataset.id
        ).filter(
            EconomicData.state == state
        )
        
        # Add optional filters
        if county:
            query = query.filter(EconomicData.county == county)
        
        if city:
            query = query.filter(EconomicData.city == city)
        
        if zip_code:
            query = query.filter(EconomicData.zip_code == zip_code)
        
        if year:
            query = query.filter(DemographicDataset.year == year)
        else:
            # Get most recent year
            subquery = self.db.query(DemographicDataset.year).order_by(
                DemographicDataset.year.desc()
            ).limit(1).scalar_subquery()
            
            query = query.filter(DemographicDataset.year == subquery)
        
        # Execute query
        results = query.all()
        
        # Convert to dictionaries
        return [self._economic_data_to_dict(result) for result in results]
    
    def _population_data_to_dict(self, data: PopulationData) -> Dict:
        """Convert a PopulationData object to a dictionary.
        
        Args:
            data: PopulationData object
            
        Returns:
            Dict: Dictionary representation of the data
        """
        return {
            "geographic_id": data.geographic_id,
            "geographic_type": data.geographic_type,
            "state": data.state,
            "county": data.county,
            "city": data.city,
            "zip_code": data.zip_code,
            "total_population": data.total_population,
            "population_by_age": {
                "under_5": data.population_under_5,
                "5_to_9": data.population_5_to_9,
                "10_to_14": data.population_10_to_14,
                "15_to_19": data.population_15_to_19,
                "20_to_24": data.population_20_to_24,
                "25_to_34": data.population_25_to_34,
                "35_to_44": data.population_35_to_44,
                "45_to_54": data.population_45_to_54,
                "55_to_59": data.population_55_to_59,
                "60_to_64": data.population_60_to_64,
                "65_to_74": data.population_65_to_74,
                "75_to_84": data.population_75_to_84,
                "85_plus": data.population_85_plus
            },
            "population_by_sex": {
                "male": data.population_male,
                "female": data.population_female
            },
            "population_by_race": {
                "white": data.population_white,
                "black": data.population_black,
                "hispanic": data.population_hispanic,
                "asian": data.population_asian,
                "native": data.population_native,
                "pacific_islander": data.population_pacific_islander,
                "other_race": data.population_other_race,
                "two_or_more_races": data.population_two_or_more_races
            },
            "households": {
                "total": data.total_households,
                "avg_size": data.avg_household_size,
                "with_children": data.households_with_children,
                "family": data.family_households,
                "nonfamily": data.nonfamily_households
            }
        }
    
    def _economic_data_to_dict(self, data: EconomicData) -> Dict:
        """Convert an EconomicData object to a dictionary.
        
        Args:
            data: EconomicData object
            
        Returns:
            Dict: Dictionary representation of the data
        """
        return {
            "geographic_id": data.geographic_id,
            "geographic_type": data.geographic_type,
            "state": data.state,
            "county": data.county,
            "city": data.city,
            "zip_code": data.zip_code,
            "income": {
                "median_household": data.median_household_income,
                "mean_household": data.mean_household_income,
                "per_capita": data.per_capita_income
            },
            "income_distribution": {
                "less_than_10k": data.households_income_less_10k,
                "10k_to_15k": data.households_income_10k_15k,
                "15k_to_25k": data.households_income_15k_25k,
                "25k_to_35k": data.households_income_25k_35k,
                "35k_to_50k": data.households_income_35k_50k,
                "50k_to_75k": data.households_income_50k_75k,
                "75k_to_100k": data.households_income_75k_100k,
                "100k_to_150k": data.households_income_100k_150k,
                "150k_to_200k": data.households_income_150k_200k,
                "200k_plus": data.households_income_200k_plus
            },
            "employment": {
                "in_labor_force": data.population_in_labor_force,
                "employed": data.population_employed,
                "unemployed": data.population_unemployed,
                "unemployment_rate": data.unemployment_rate
            },
            "poverty": {
                "below_poverty_level": data.population_below_poverty_level,
                "poverty_rate": data.poverty_rate
            }
        } 