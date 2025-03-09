from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.pls_data import PLSDataset
from app.services.collector import PLSDataCollector

router = APIRouter()


@router.post("/collect/{year}", status_code=202)
def collect_data_for_year(
    year: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start a data collection job for a specific year.
    """
    # Check if year is valid
    if year < 1992 or year > 2100:  # Arbitrary upper limit
        raise HTTPException(status_code=400, detail="Invalid year. Must be between 1992 and present year.")
    
    # Check if data for this year already exists
    existing_dataset = db.query(PLSDataset).filter(PLSDataset.year == year).first()
    
    if existing_dataset and existing_dataset.status == "complete":
        raise HTTPException(status_code=400, detail=f"Data for year {year} already exists and is complete.")
    
    # If dataset exists but is not complete, update its status
    if existing_dataset:
        existing_dataset.status = "pending"
        db.commit()
    else:
        # Create a new dataset record
        dataset = PLSDataset(year=year, status="pending")
        db.add(dataset)
        db.commit()
    
    # Start data collection in the background
    background_tasks.add_task(collect_data_background, year, db)
    
    return {"message": f"Data collection for year {year} started", "status": "pending"}


@router.post("/collect-all", status_code=202)
def collect_all_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start a data collection job for all available years.
    """
    # Create collector instance to discover years
    collector = PLSDataCollector(db)
    available_years = collector.discover_available_years()
    
    if not available_years:
        raise HTTPException(status_code=404, detail="No available years discovered")
    
    # Start data collection in the background
    background_tasks.add_task(collect_all_data_background, db)
    
    return {
        "message": "Data collection for all available years started",
        "available_years": available_years,
        "status": "pending"
    }


@router.post("/update", status_code=202)
def update_with_latest_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Update the database with the latest available PLS data.
    """
    # Create collector instance to discover years
    collector = PLSDataCollector(db)
    available_years = collector.discover_available_years()
    
    if not available_years:
        raise HTTPException(status_code=404, detail="No available years discovered")
    
    latest_year = max(available_years)
    
    # Check if we already have this year's data
    existing_dataset = db.query(PLSDataset).filter(PLSDataset.year == latest_year).first()
    
    if existing_dataset and existing_dataset.status == "complete":
        return {
            "message": f"Already have complete data for latest year {latest_year}",
            "status": "complete",
            "year": latest_year
        }
    
    # Start data collection in the background
    background_tasks.add_task(collect_data_background, latest_year, db)
    
    return {
        "message": f"Update with latest data (year {latest_year}) started",
        "status": "pending",
        "year": latest_year
    }


@router.get("/status")
def get_collection_status(
    db: Session = Depends(get_db)
):
    """
    Get the status of all data collection jobs.
    """
    datasets = db.query(PLSDataset).order_by(PLSDataset.year).all()
    
    status_by_year = {
        dataset.year: {
            "status": dataset.status,
            "record_count": dataset.record_count,
            "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
            "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None,
        }
        for dataset in datasets
    }
    
    return status_by_year


# Background task functions
def collect_data_background(year: int, db: Session):
    """
    Background task for collecting data for a specific year.
    """
    collector = PLSDataCollector(db)
    
    # Update dataset status
    dataset = db.query(PLSDataset).filter(PLSDataset.year == year).first()
    dataset.status = "processing"
    db.commit()
    
    try:
        success = collector.collect_data_for_year(year)
        
        # Update dataset status based on success
        dataset = db.query(PLSDataset).filter(PLSDataset.year == year).first()
        dataset.status = "complete" if success else "error"
        db.commit()
        
    except Exception as e:
        # Update dataset status on error
        dataset = db.query(PLSDataset).filter(PLSDataset.year == year).first()
        dataset.status = "error"
        dataset.notes = str(e)
        db.commit()


def collect_all_data_background(db: Session):
    """
    Background task for collecting data for all available years.
    """
    collector = PLSDataCollector(db)
    
    # Discover available years
    available_years = collector.discover_available_years()
    
    for year in available_years:
        # Check if we already have complete data for this year
        existing_dataset = db.query(PLSDataset).filter(PLSDataset.year == year).first()
        
        if existing_dataset and existing_dataset.status == "complete":
            continue
        
        # Create or update dataset record
        if existing_dataset:
            existing_dataset.status = "processing"
            db.commit()
        else:
            dataset = PLSDataset(year=year, status="processing")
            db.add(dataset)
            db.commit()
        
        try:
            success = collector.collect_data_for_year(year)
            
            # Update dataset status based on success
            dataset = db.query(PLSDataset).filter(PLSDataset.year == year).first()
            dataset.status = "complete" if success else "error"
            db.commit()
            
        except Exception as e:
            # Update dataset status on error
            dataset = db.query(PLSDataset).filter(PLSDataset.year == year).first()
            dataset.status = "error"
            dataset.notes = str(e)
            db.commit() 