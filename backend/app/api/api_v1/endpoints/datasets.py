from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.pls_data import PLSDataset
from app.schemas.pls_data import PLSDataset as PLSDatasetSchema
from app.schemas.pls_data import PLSDatasetWithRelations

router = APIRouter()


@router.get("/", response_model=List[PLSDatasetSchema])
def get_datasets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all PLS datasets.
    """
    datasets = db.query(PLSDataset).offset(skip).limit(limit).all()
    return datasets


@router.get("/{year}", response_model=PLSDatasetWithRelations)
def get_dataset(
    year: int,
    include_libraries: bool = False,
    include_outlets: bool = False,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific PLS dataset by year.
    """
    dataset = db.query(PLSDataset).filter(PLSDataset.year == year).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset for year {year} not found")
    
    return dataset


@router.get("/years/available", response_model=List[int])
def get_available_years(
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of years for which datasets are available.
    """
    years = [year[0] for year in db.query(PLSDataset.year).order_by(PLSDataset.year).all()]
    return years 