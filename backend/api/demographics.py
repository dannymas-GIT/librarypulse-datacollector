"""
Demographics API for accessing demographic data for library service areas.
"""
import json
import os
import sys
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import Session, sessionmaker

# Add the backend directory to the path so we can import modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Import models directly - instead of using app module imports
# Define the models here
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, Text, Enum, UniqueConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

# Create the Base 
Base = declarative_base()

# Database URL - should match what's in the other scripts
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/librarypulse"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/demographics",
    tags=["demographics"],
    responses={404: {"description": "Not found"}},
)

# Define the path for processed demographic data (kept for fallback)
PROCESSED_DEMO_DATA_PATH = os.path.join(
    os.path.dirname(backend_dir), "data", "demographics", "processed"
)

# Dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database models we need for our demographics API
class IDMixin(object):
    """Mixin for common ID field."""
    id = Column(Integer, primary_key=True, index=True)

class TimestampMixin(object):
    """Mixin for created_at and updated_at fields."""
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class DemographicDataset(Base):
    """Model representing a demographic dataset from the Census or other sources."""
    
    __tablename__ = "demographic_datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    source = Column(String(100), nullable=False, index=True)  # "Census ACS", "Census Decennial", etc.
    year = Column(Integer, nullable=False, index=True)
    date_collected = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, complete, error
    record_count = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Creates a unique constraint on source and year
    __table_args__ = (UniqueConstraint('source', 'year', name='uix_demographic_source_year'),)
    
    # Relationships
    population_data = relationship("PopulationData", back_populates="dataset", cascade="all, delete-orphan")
    economic_data = relationship("EconomicData", back_populates="dataset", cascade="all, delete-orphan")
    education_data = relationship("EducationData", back_populates="dataset", cascade="all, delete-orphan")
    housing_data = relationship("HousingData", back_populates="dataset", cascade="all, delete-orphan")

class PopulationData(Base):
    """Model representing population statistics for a specific geographic area."""
    
    __tablename__ = "population_data"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    dataset_id = Column(Integer, ForeignKey("demographic_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    geographic_id = Column(String(20), nullable=False, index=True)  # FIPS code or other geographic identifier
    geographic_type = Column(String(50), nullable=False, index=True)  # "County", "ZIP", "Census Tract", etc.
    
    # Geographic identifiers
    state = Column(String(2), nullable=False, index=True)
    county = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    zip_code = Column(String(10), nullable=True, index=True)
    
    # Total population
    total_population = Column(Integer, nullable=True)
    
    # Population by age ranges
    population_under_5 = Column(Integer, nullable=True)
    population_5_to_9 = Column(Integer, nullable=True)
    population_10_to_14 = Column(Integer, nullable=True)
    population_15_to_19 = Column(Integer, nullable=True)
    population_65_to_74 = Column(Integer, nullable=True)
    population_75_to_84 = Column(Integer, nullable=True)
    population_85_plus = Column(Integer, nullable=True)
    
    # Population by sex
    population_male = Column(Integer, nullable=True)
    population_female = Column(Integer, nullable=True)
    
    # Population by race/ethnicity
    population_white = Column(Integer, nullable=True)
    population_black = Column(Integer, nullable=True)
    population_hispanic = Column(Integer, nullable=True)
    
    # Relationship
    dataset = relationship("DemographicDataset", back_populates="population_data")

class EconomicData(Base):
    """Model representing economic statistics for a specific geographic area."""
    
    __tablename__ = "economic_data"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    dataset_id = Column(Integer, ForeignKey("demographic_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    geographic_id = Column(String(20), nullable=False, index=True)  # FIPS code or other geographic identifier
    geographic_type = Column(String(50), nullable=False, index=True)  # "County", "ZIP", "Census Tract", etc.
    
    # Geographic identifiers
    state = Column(String(2), nullable=False, index=True)
    county = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    zip_code = Column(String(10), nullable=True, index=True)
    
    # Income data
    median_household_income = Column(Integer, nullable=True)
    mean_household_income = Column(Integer, nullable=True)
    per_capita_income = Column(Integer, nullable=True)
    
    # Poverty data
    population_below_poverty_level = Column(Integer, nullable=True)
    poverty_rate = Column(Float, nullable=True)
    
    # Relationship
    dataset = relationship("DemographicDataset", back_populates="economic_data")

class EducationData(Base):
    """Model representing education statistics for a specific geographic area."""
    
    __tablename__ = "education_data"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    dataset_id = Column(Integer, ForeignKey("demographic_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    geographic_id = Column(String(20), nullable=False, index=True)  # FIPS code or other geographic identifier
    geographic_type = Column(String(50), nullable=False, index=True)  # "County", "ZIP", "Census Tract", etc.
    
    # Geographic identifiers
    state = Column(String(2), nullable=False, index=True)
    county = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    zip_code = Column(String(10), nullable=True, index=True)
    
    # Population 25 years and over
    population_25_plus = Column(Integer, nullable=True)
    
    # Educational attainment
    population_high_school_graduate = Column(Integer, nullable=True)
    population_bachelors_degree = Column(Integer, nullable=True)
    
    # Relationship
    dataset = relationship("DemographicDataset", back_populates="education_data")

class HousingData(Base):
    """Model representing housing statistics for a specific geographic area."""
    
    __tablename__ = "housing_data"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    dataset_id = Column(Integer, ForeignKey("demographic_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    geographic_id = Column(String(20), nullable=False, index=True)  # FIPS code or other geographic identifier
    geographic_type = Column(String(50), nullable=False, index=True)  # "County", "ZIP", "Census Tract", etc.
    
    # Geographic identifiers
    state = Column(String(2), nullable=False, index=True)
    county = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    zip_code = Column(String(10), nullable=True, index=True)
    
    # Housing units
    total_housing_units = Column(Integer, nullable=True)
    housing_units_occupied = Column(Integer, nullable=True)
    housing_units_vacant = Column(Integer, nullable=True)
    
    # Occupancy
    housing_owner_occupied = Column(Integer, nullable=True)
    housing_renter_occupied = Column(Integer, nullable=True)
    
    # Relationship
    dataset = relationship("DemographicDataset", back_populates="housing_data")


@router.get("/", summary="Get demographic data sources")
async def get_demographic_sources(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get a list of available demographic data sources.
    
    Returns a list of available demographic data sources and years.
    """
    try:
        # Check for sources in the database
        datasets = db.query(DemographicDataset).all()
        
        if datasets:
            sources = []
            for dataset in datasets:
                # Get the unique geographies for this dataset
                geographies = set()
                
                # Get all population records for this dataset and extract their geographic types
                population_records = db.query(PopulationData).filter(
                    PopulationData.dataset_id == dataset.id
                ).all()
                
                for record in population_records:
                    geo_name = f"{record.city} ({record.geographic_type} {record.geographic_id})"
                    geographies.add(geo_name)
                
                sources.append({
                    "name": dataset.source,
                    "years": [str(dataset.year)],
                    "geographies": list(geographies)
                })
            
            return {
                "sources": sources,
                "count": len(sources)
            }
        else:
            # Fallback to static list if no database records
            sources = [{
                "name": "American Community Survey 5-Year Estimates",
                "years": ["2017-2021"],
                "geographies": ["ZCTA 11704"]
            }]
            
            return {
                "sources": sources,
                "count": len(sources)
            }
    except Exception as e:
        logger.error(f"Error retrieving demographic sources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving demographic sources: {str(e)}"
        )


def _build_demographic_data(db: Session, geographic_id: str) -> Dict[str, Any]:
    """
    Helper function to build demographic data from database records.
    """
    # First, find a dataset that contains data for this geographic_id
    population_record = db.query(PopulationData).filter(
        PopulationData.geographic_id == geographic_id
    ).first()
    
    if not population_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demographic data for geographic_id {geographic_id} not found in any dataset"
        )
    
    # Use the dataset_id from the found population record
    dataset_id = population_record.dataset_id
    
    # Now get the dataset
    dataset = db.query(DemographicDataset).filter(
        DemographicDataset.id == dataset_id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} not found in database"
        )
    
    logger.info(f"Found dataset for geographic_id {geographic_id}: id={dataset.id}, source={dataset.source}, year={dataset.year}")
    
    # Get population data (we already have it but query to be consistent)
    population = db.query(PopulationData).filter(
        and_(
            PopulationData.dataset_id == dataset.id,
            PopulationData.geographic_id == geographic_id
        )
    ).first()
    
    # Get economic data
    economic = db.query(EconomicData).filter(
        and_(
            EconomicData.dataset_id == dataset.id,
            EconomicData.geographic_id == geographic_id
        )
    ).first()
    
    # Get education data
    education = db.query(EducationData).filter(
        and_(
            EducationData.dataset_id == dataset.id,
            EducationData.geographic_id == geographic_id
        )
    ).first()
    
    # Get housing data
    housing = db.query(HousingData).filter(
        and_(
            HousingData.dataset_id == dataset.id,
            HousingData.geographic_id == geographic_id
        )
    ).first()
    
    # Calculate derived values
    under_18 = 0
    if population.population_under_5:
        under_18 += population.population_under_5
    if population.population_5_to_9:
        under_18 += population.population_5_to_9
    if population.population_10_to_14:
        under_18 += population.population_10_to_14
    if population.population_15_to_19:
        # Assume 75% of 15-19 are under 18
        under_18 += int(population.population_15_to_19 * 0.75) if population.population_15_to_19 else 0
    
    over_65 = 0
    if population.population_65_to_74:
        over_65 += population.population_65_to_74
    if population.population_75_to_84:
        over_65 += population.population_75_to_84
    if population.population_85_plus:
        over_65 += population.population_85_plus
    
    # Build the response object
    demographic_data = {
        "geography": {
            "name": population.city,
            "zcta": population.zip_code,
            "state": population.state,
            "county": population.county
        },
        "population": {
            "total": population.total_population,
            "median_age": 43.4,  # Hard-coded for now as it's not in our model
            "by_age": {
                "under_18": under_18,
                "over_65": over_65
            },
            "by_race": {
                "white": population.population_white,
                "black": population.population_black,
                "hispanic": population.population_hispanic
            }
        },
        "economics": {
            "median_household_income": economic.median_household_income if economic else None,
            "poverty_rate": economic.poverty_rate if economic else None
        },
        "education": {
            "high_school_or_higher": min(100.0, (education.population_high_school_graduate / education.population_25_plus * 100) 
                                    if education and education.population_25_plus else None),
            "bachelors_or_higher": min(100.0, (education.population_bachelors_degree / education.population_25_plus * 100)
                                  if education and education.population_25_plus else None)
        },
        "housing": {
            "total_units": housing.total_housing_units if housing else None,
            "owner_occupied": housing.housing_owner_occupied if housing else None,
            "median_home_value": 395200  # Hard-coded for now as it's not in our model
        },
        "data_source": {
            "name": dataset.source,
            "year": f"{dataset.year - 4}-{dataset.year}"  # 5-year range
        }
    }
    
    return demographic_data


@router.get("/west-babylon", summary="Get demographic data for West Babylon")
async def get_west_babylon_demographics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get demographic data for West Babylon, NY (ZCTA 11704).
    
    Returns comprehensive demographic data including population, economics, education, and housing statistics.
    """
    try:
        # Try to get data from the database
        try:
            logger.info("Attempting to retrieve West Babylon demographic data from database")
            
            # Use the _build_demographic_data helper to get demographic data
            # This will find the correct dataset that contains West Babylon data (geographic_id 11704)
            demographic_data = _build_demographic_data(db, "11704")
            logger.info("Successfully retrieved West Babylon demographic data from database")
            return demographic_data
            
        except HTTPException as db_error:
            logger.warning(f"Database retrieval failed: {str(db_error)}, falling back to JSON file")
            # If database retrieval fails, fall back to the JSON file
            data_file = os.path.join(PROCESSED_DEMO_DATA_PATH, "west_babylon_demographics.json")
            
            if not os.path.exists(data_file):
                logger.error(f"JSON fallback file not found at {data_file}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Demographic data for West Babylon not found"
                )
            
            logger.info(f"Loading data from JSON file: {data_file}")
            with open(data_file, 'r') as f:
                demographic_data = json.load(f)
            
            return demographic_data
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving West Babylon demographic data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving West Babylon demographic data: {str(e)}"
        )


@router.get("/by-zip/{zip_code}", summary="Get demographic data by ZIP code")
async def get_demographics_by_zip(
    zip_code: str = Path(..., description="The ZIP code to retrieve demographic data for"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get demographic data for a specific ZIP code.
    
    Currently only supports ZCTA 11704 (West Babylon, NY).
    """
    try:
        # Try to get data from the database for this ZIP code
        return _build_demographic_data(db, zip_code)
    except HTTPException as e:
        # If we don't have data for this ZIP, return a 404
        if e.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Demographic data for ZIP code {zip_code} not available"
            )
        raise e


@router.get("/for-library/{library_id}", summary="Get demographic data for a library")
async def get_demographics_for_library(
    library_id: str = Path(..., description="The ID of the library"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get demographic data for the area served by a specific library.
    
    Currently hard-coded to return West Babylon demographic data, regardless of library ID.
    Will be extended in the future to match libraries with their service areas.
    """
    # For now, we return West Babylon data for any library ID
    # In a future version, we would look up the library's service area and return the appropriate data
    return await get_west_babylon_demographics(db)


@router.get("/test-db", summary="Test database connection")
async def test_db_connection(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Test database connection by querying for demographic datasets.
    """
    try:
        # Check connection by trying to query the demographic_datasets table
        datasets = db.query(DemographicDataset).all()
        
        # If we get here, connection works
        return {
            "status": "success",
            "message": "Database connection successful",
            "num_datasets": len(datasets),
            "datasets": [
                {
                    "id": dataset.id,
                    "source": dataset.source,
                    "year": dataset.year,
                    "status": dataset.status
                }
                for dataset in datasets
            ]
        }
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        } 