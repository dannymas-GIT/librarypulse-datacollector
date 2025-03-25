from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.library import Library, LibraryCreate, LibraryUpdate
from app.services import library as library_service

router = APIRouter(tags=["libraries"])

@router.get("/", response_model=List[Library])
async def get_libraries(
    dataset_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all libraries for a dataset."""
    return await library_service.get_libraries(db, dataset_id, skip=skip, limit=limit)

@router.get("/{library_id}", response_model=Library)
async def get_library(
    dataset_id: int,
    library_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific library by ID."""
    library = await library_service.get_library(db, dataset_id, library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return library

@router.post("/", response_model=Library)
async def create_library(
    library: LibraryCreate,
    db: Session = Depends(get_db)
):
    """Create a new library."""
    return await library_service.create_library(db, library)

@router.put("/{library_id}", response_model=Library)
async def update_library(
    dataset_id: int,
    library_id: str,
    library: LibraryUpdate,
    db: Session = Depends(get_db)
):
    """Update a library."""
    updated_library = await library_service.update_library(db, dataset_id, library_id, library)
    if not updated_library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return updated_library

@router.delete("/{library_id}")
async def delete_library(
    dataset_id: int,
    library_id: str,
    db: Session = Depends(get_db)
):
    """Delete a library."""
    success = await library_service.delete_library(db, dataset_id, library_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return {"message": "Library deleted successfully"} 