from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_db
from app.models.pls_data import Library, LibraryOutlet
from app.schemas.pls_data import Library as LibrarySchema
from app.schemas.pls_data import LibraryOutlet as LibraryOutletSchema

router = APIRouter()


@router.get("/", response_model=List[LibrarySchema])
def get_libraries(
    year: Optional[int] = None,
    state: Optional[str] = None,
    county: Optional[str] = None,
    name: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve libraries with optional filtering by year, state, county, and name.
    """
    query = db.query(Library)
    
    # Apply filters
    if year is not None:
        query = query.join(Library.dataset).filter(Library.dataset.has(year=year))
    
    if state is not None:
        query = query.filter(Library.state == state.upper())
    
    if county is not None:
        query = query.filter(Library.county.ilike(f"%{county}%"))
    
    if name is not None:
        query = query.filter(Library.name.ilike(f"%{name}%"))
    
    # Execute query with pagination
    libraries = query.options(joinedload(Library.outlets)).offset(skip).limit(limit).all()
    
    return libraries


@router.get("/{library_id}", response_model=LibrarySchema)
def get_library(
    library_id: str,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific library by ID, optionally filtered by year.
    """
    query = db.query(Library).filter(Library.library_id == library_id)
    
    if year is not None:
        query = query.join(Library.dataset).filter(Library.dataset.has(year=year))
    else:
        # Get the most recent year if not specified
        query = query.join(Library.dataset).order_by(Library.dataset.year.desc())
    
    library = query.options(joinedload(Library.outlets)).first()
    
    if not library:
        raise HTTPException(status_code=404, detail=f"Library with ID {library_id} not found")
    
    return library


@router.get("/{library_id}/outlets", response_model=List[LibraryOutletSchema])
def get_library_outlets(
    library_id: str,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all outlets for a specific library, optionally filtered by year.
    """
    query = db.query(LibraryOutlet).filter(LibraryOutlet.library_id == library_id)
    
    if year is not None:
        query = query.join(LibraryOutlet.dataset).filter(LibraryOutlet.dataset.has(year=year))
    else:
        # Get the most recent year if not specified
        query = query.join(LibraryOutlet.dataset).order_by(LibraryOutlet.dataset.year.desc())
    
    outlets = query.all()
    
    if not outlets:
        raise HTTPException(status_code=404, detail=f"No outlets found for library with ID {library_id}")
    
    return outlets


@router.get("/states/list", response_model=List[str])
def get_states(
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all states with libraries.
    """
    query = db.query(Library.state).distinct()
    
    if year is not None:
        query = query.join(Library.dataset).filter(Library.dataset.has(year=year))
    
    states = [state[0] for state in query.all() if state[0] is not None]
    return sorted(states)


@router.get("/counties/list", response_model=List[str])
def get_counties(
    state: str,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all counties in a state with libraries.
    """
    query = db.query(Library.county).distinct().filter(Library.state == state.upper())
    
    if year is not None:
        query = query.join(Library.dataset).filter(Library.dataset.has(year=year))
    
    counties = [county[0] for county in query.all() if county[0] is not None]
    return sorted(counties) 