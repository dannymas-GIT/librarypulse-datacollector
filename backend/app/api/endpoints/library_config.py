from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.services.library_config_service import LibraryConfigService
from app.services.collector import PLSDataCollector
from app.schemas.library_config import (
    LibraryConfigCreate,
    LibraryConfigResponse,
    LibraryConfigUpdate,
    LibrarySearchResponse,
    MetricsConfigResponse
)

router = APIRouter()


@router.get("/config", response_model=LibraryConfigResponse)
def get_library_config(db: Session = Depends(get_db)):
    """
    Get the current library configuration.
    """
    config = LibraryConfigService.get_library_config(db)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library configuration not found. Please complete the setup."
        )
    return config


@router.post("/config", response_model=LibraryConfigResponse)
def create_library_config(config_data: LibraryConfigCreate, db: Session = Depends(get_db)):
    """
    Create or update the library configuration.
    """
    config = LibraryConfigService.create_or_update_config(
        db=db,
        library_id=config_data.library_id,
        library_name=config_data.library_name,
        collection_stats_enabled=config_data.collection_stats_enabled,
        usage_stats_enabled=config_data.usage_stats_enabled,
        program_stats_enabled=config_data.program_stats_enabled,
        staff_stats_enabled=config_data.staff_stats_enabled,
        financial_stats_enabled=config_data.financial_stats_enabled,
        collection_metrics=config_data.collection_metrics,
        usage_metrics=config_data.usage_metrics,
        program_metrics=config_data.program_metrics,
        staff_metrics=config_data.staff_metrics,
        financial_metrics=config_data.financial_metrics,
        setup_complete=config_data.setup_complete,
        auto_update_enabled=config_data.auto_update_enabled
    )
    return config


@router.patch("/config", response_model=LibraryConfigResponse)
def update_library_config(config_data: LibraryConfigUpdate, db: Session = Depends(get_db)):
    """
    Update the library configuration.
    """
    config = LibraryConfigService.get_library_config(db)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library configuration not found. Please complete the setup first."
        )
    
    updated_config = LibraryConfigService.create_or_update_config(
        db=db,
        library_id=config.library_id,
        library_name=config.library_name,
        collection_stats_enabled=config_data.collection_stats_enabled or config.collection_stats_enabled,
        usage_stats_enabled=config_data.usage_stats_enabled or config.usage_stats_enabled,
        program_stats_enabled=config_data.program_stats_enabled or config.program_stats_enabled,
        staff_stats_enabled=config_data.staff_stats_enabled or config.staff_stats_enabled,
        financial_stats_enabled=config_data.financial_stats_enabled or config.financial_stats_enabled,
        collection_metrics=config_data.collection_metrics,
        usage_metrics=config_data.usage_metrics,
        program_metrics=config_data.program_metrics,
        staff_metrics=config_data.staff_metrics,
        financial_metrics=config_data.financial_metrics,
        setup_complete=config_data.setup_complete or config.setup_complete,
        auto_update_enabled=config_data.auto_update_enabled or config.auto_update_enabled
    )
    return updated_config


@router.get("/libraries/search", response_model=List[LibrarySearchResponse])
def search_libraries(query: str, limit: int = 10, db: Session = Depends(get_db)):
    """
    Search for libraries by name or ID.
    """
    # Check if we have any data in the database
    collector = PLSDataCollector(db)
    available_years = collector.discover_available_years()
    
    if not available_years:
        # If no data, collect the latest year first
        collector.update_with_latest_data()
    
    # Search for libraries
    libraries = LibraryConfigService.search_libraries(db, query, limit)
    return libraries


@router.get("/metrics", response_model=MetricsConfigResponse)
def get_available_metrics():
    """
    Get available metrics for configuration.
    """
    return {
        "categories": LibraryConfigService.get_metric_categories()
    }


@router.get("/setup-status")
def get_setup_status(db: Session = Depends(get_db)):
    """
    Check if the application has been set up.
    """
    setup_complete = LibraryConfigService.is_setup_complete(db)
    return {"setup_complete": setup_complete} 