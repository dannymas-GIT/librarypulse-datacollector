import json
import os
from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app import schemas
from app.core.config import settings
from app.db.session import get_db
from app.models.demographic_data import (
    DemographicDataset, PopulationData, EconomicData, 
    EducationData, HousingData
)

router = APIRouter()

# Define the path for processed demographic data (kept for fallback)
PROCESSED_DEMO_DATA_PATH = os.path.join(
    settings.BASE_DIR, "data", "demographics", "processed"
)


@router.get("/", summary="Get demographic data sources")
def get_demographic_sources(db: Session = Depends(get_db)) -> Dict[str, Any]:
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving demographic sources: {str(e)}"
        )


def _build_demographic_data(db: Session, geographic_id: str) -> schemas.SimpleDemographicData:
    """
    Helper function to build demographic data from database records.
    """
    # Get the most recent dataset
    dataset = db.query(DemographicDataset).order_by(DemographicDataset.year.desc()).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No demographic datasets found in database"
        )
    
    # Get population data
    population = db.query(PopulationData).filter(
        and_(
            PopulationData.dataset_id == dataset.id,
            PopulationData.geographic_id == geographic_id
        )
    ).first()
    
    if not population:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demographic data for geographic_id {geographic_id} not found"
        )
    
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
                "under_18": (population.population_under_5 or 0) + 
                           (population.population_5_to_9 or 0) + 
                           (population.population_10_to_14 or 0) + 
                           (population.population_15_to_19 or 0) * 0.75,  # Estimate: 75% of 15-19 are under 18
                "over_65": (population.population_65_to_74 or 0) + 
                          (population.population_75_to_84 or 0) + 
                          (population.population_85_plus or 0)
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
            "high_school_or_higher": (education.population_high_school_graduate / education.population_25_plus * 100) 
                                    if education and education.population_25_plus else None,
            "bachelors_or_higher": (education.population_bachelors_degree / education.population_25_plus * 100)
                                  if education and education.population_25_plus else None
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


@router.get("/west-babylon", response_model=schemas.SimpleDemographicData)
def get_west_babylon_demographics(db: Session = Depends(get_db)) -> schemas.SimpleDemographicData:
    """
    Get demographic data for West Babylon, NY (ZCTA 11704).
    
    Returns comprehensive demographic data including population, economics, education, and housing statistics.
    """
    try:
        # Try to get data from the database
        try:
            return _build_demographic_data(db, "11704")
        except HTTPException as db_error:
            # If database retrieval fails, fall back to the JSON file
            data_file = os.path.join(PROCESSED_DEMO_DATA_PATH, "west_babylon_demographics.json")
            
            if not os.path.exists(data_file):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Demographic data for West Babylon not found"
                )
            
            with open(data_file, 'r') as f:
                demographic_data = json.load(f)
            
            return demographic_data
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving West Babylon demographic data: {str(e)}"
        )


@router.get("/by-zip/{zip_code}", response_model=schemas.SimpleDemographicData)
def get_demographics_by_zip(
    zip_code: str,
    db: Session = Depends(get_db)
) -> schemas.SimpleDemographicData:
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


@router.get("/for-library/{library_id}", response_model=schemas.SimpleDemographicData)
def get_demographics_for_library(
    library_id: str,
    db: Session = Depends(get_db)
) -> schemas.SimpleDemographicData:
    """
    Get demographic data for the area served by a specific library.
    
    Currently hard-coded to return West Babylon demographic data, regardless of library ID.
    Will be extended in the future to match libraries with their service areas.
    """
    # For now, we return West Babylon data for any library ID
    # In a future version, we would look up the library's service area and return the appropriate data
    return get_west_babylon_demographics(db) 