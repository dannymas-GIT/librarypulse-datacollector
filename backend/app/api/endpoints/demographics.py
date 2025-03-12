from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.services.demographic_service import DemographicService

router = APIRouter()


@router.get("/population")
async def get_population_data(
    state: str = Query(..., description="State code (e.g., 'NY')"),
    county: Optional[str] = Query(None, description="County name"),
    city: Optional[str] = Query(None, description="City name"),
    zip_code: Optional[str] = Query(None, description="ZIP code"),
    year: Optional[int] = Query(None, description="Year of the data"),
    db: Session = Depends(get_db)
):
    """
    Get population data for a specific geographic area.
    """
    try:
        service = DemographicService(db)
        data = service.get_population_data(state, county, city, zip_code, year)
        
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No population data found for the specified criteria"
            )
        
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/economics")
async def get_economic_data(
    state: str = Query(..., description="State code (e.g., 'NY')"),
    county: Optional[str] = Query(None, description="County name"),
    city: Optional[str] = Query(None, description="City name"),
    zip_code: Optional[str] = Query(None, description="ZIP code"),
    year: Optional[int] = Query(None, description="Year of the data"),
    db: Session = Depends(get_db)
):
    """
    Get economic data for a specific geographic area.
    """
    try:
        service = DemographicService(db)
        data = service.get_economic_data(state, county, city, zip_code, year)
        
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No economic data found for the specified criteria"
            )
        
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/education")
async def get_education_data(
    state: str = Query(..., description="State code (e.g., 'NY')"),
    county: Optional[str] = Query(None, description="County name"),
    city: Optional[str] = Query(None, description="City name"),
    zip_code: Optional[str] = Query(None, description="ZIP code"),
    year: Optional[int] = Query(None, description="Year of the data"),
    db: Session = Depends(get_db)
):
    """
    Get education data for a specific geographic area.
    """
    # This is a placeholder until we implement the education data service
    raise HTTPException(
        status_code=501,
        detail="Education data endpoint not implemented yet"
    )


@router.get("/languages")
async def get_language_data(
    state: str = Query(..., description="State code (e.g., 'NY')"),
    county: Optional[str] = Query(None, description="County name"),
    city: Optional[str] = Query(None, description="City name"),
    zip_code: Optional[str] = Query(None, description="ZIP code"),
    year: Optional[int] = Query(None, description="Year of the data"),
    db: Session = Depends(get_db)
):
    """
    Get language data for a specific geographic area.
    """
    # This is a placeholder until we implement the language data service
    raise HTTPException(
        status_code=501,
        detail="Language data endpoint not implemented yet"
    )


@router.get("/housing")
async def get_housing_data(
    state: str = Query(..., description="State code (e.g., 'NY')"),
    county: Optional[str] = Query(None, description="County name"),
    city: Optional[str] = Query(None, description="City name"),
    zip_code: Optional[str] = Query(None, description="ZIP code"),
    year: Optional[int] = Query(None, description="Year of the data"),
    db: Session = Depends(get_db)
):
    """
    Get housing data for a specific geographic area.
    """
    # This is a placeholder until we implement the housing data service
    raise HTTPException(
        status_code=501,
        detail="Housing data endpoint not implemented yet"
    )


@router.get("/library/{library_id}")
async def get_demographic_data_for_library(
    library_id: str,
    year: Optional[int] = Query(None, description="Year of the data"),
    db: Session = Depends(get_db)
):
    """
    Get all demographic data for a specific library's service area.
    """
    try:
        # This is a placeholder until we implement the library-to-demographic mapping
        # In a real implementation, we would:
        # 1. Look up the library's service area (county, city, zip)
        # 2. Fetch demographic data for that area
        # 3. Return a comprehensive set of demographic data
        
        raise HTTPException(
            status_code=501,
            detail="Library demographic data endpoint not implemented yet"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 