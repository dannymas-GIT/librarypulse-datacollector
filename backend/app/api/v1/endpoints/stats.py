from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.session import get_db
from app.services import stats as stats_service

router = APIRouter(tags=["stats"])

@router.get("/summary/{dataset_id}")
async def get_dataset_summary(
    dataset_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get summary statistics for a dataset."""
    summary = await stats_service.get_dataset_summary(db, dataset_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    return summary

@router.get("/trends/{dataset_id}")
async def get_dataset_trends(
    dataset_id: int,
    metric: str,
    start_year: int,
    end_year: int = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get trend analysis for a specific metric over time."""
    trends = await stats_service.get_dataset_trends(
        db, 
        dataset_id, 
        metric, 
        start_year, 
        end_year
    )
    if not trends:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset or metric not found"
        )
    return trends

@router.get("/compare")
async def compare_datasets(
    dataset_ids: List[int],
    metrics: List[str],
    year: int = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Compare multiple datasets across specified metrics."""
    comparison = await stats_service.compare_datasets(
        db,
        dataset_ids,
        metrics,
        year
    )
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more datasets not found"
        )
    return comparison

@router.get("/rankings/{dataset_id}")
async def get_library_rankings(
    dataset_id: int,
    metric: str,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get top/bottom rankings for libraries based on a specific metric."""
    rankings = await stats_service.get_library_rankings(
        db,
        dataset_id,
        metric,
        limit
    )
    if not rankings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset or metric not found"
        )
    return rankings 