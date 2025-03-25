from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.dataset import Dataset, DatasetCreate, DatasetUpdate
from app.services import dataset as dataset_service

router = APIRouter(tags=["datasets"])

@router.get("/", response_model=List[Dataset])
async def get_datasets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all datasets."""
    return await dataset_service.get_datasets(db, skip=skip, limit=limit)

@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific dataset by ID."""
    dataset = await dataset_service.get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    return dataset

@router.post("/", response_model=Dataset)
async def create_dataset(
    dataset: DatasetCreate,
    db: Session = Depends(get_db)
):
    """Create a new dataset."""
    return await dataset_service.create_dataset(db, dataset)

@router.put("/{dataset_id}", response_model=Dataset)
async def update_dataset(
    dataset_id: int,
    dataset: DatasetUpdate,
    db: Session = Depends(get_db)
):
    """Update a dataset."""
    updated_dataset = await dataset_service.update_dataset(db, dataset_id, dataset)
    if not updated_dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    return updated_dataset

@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    """Delete a dataset."""
    success = await dataset_service.delete_dataset(db, dataset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    return {"message": "Dataset deleted successfully"} 