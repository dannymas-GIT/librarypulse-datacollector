from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from fastapi import status

from app.core.deps import get_db
from app.models.pls_data import Library, LibraryOutlet, PLSDataset

router = APIRouter()


@router.get("/summary")
def get_summary_stats(
    year: Optional[int] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for libraries, optionally filtered by year and state.
    """
    # If year is not specified, use the most recent year
    if year is None:
        latest_year = db.query(func.max(PLSDataset.year)).scalar()
        if not latest_year:
            raise HTTPException(status_code=404, detail="No data available")
        year = latest_year
    
    # Build the base query
    query = db.query(Library).join(Library.dataset).filter(PLSDataset.year == year)
    
    # Apply state filter if provided
    if state:
        query = query.filter(Library.state == state.upper())
    
    # Get total count
    library_count = query.count()
    
    if library_count == 0:
        raise HTTPException(status_code=404, detail=f"No libraries found for year {year}{' in state ' + state if state else ''}")
    
    # Calculate summary statistics
    stats = {
        "year": year,
        "state": state.upper() if state else "All States",
        "library_count": library_count,
        "total_visits": query.with_entities(func.sum(Library.visits)).scalar() or 0,
        "total_circulation": query.with_entities(func.sum(Library.total_circulation)).scalar() or 0,
        "total_programs": query.with_entities(func.sum(Library.total_programs)).scalar() or 0,
        "total_program_attendance": query.with_entities(func.sum(Library.total_program_attendance)).scalar() or 0,
        "total_operating_revenue": query.with_entities(func.sum(Library.total_operating_revenue)).scalar() or 0,
        "total_operating_expenditures": query.with_entities(func.sum(Library.total_operating_expenditures)).scalar() or 0,
        "total_staff": query.with_entities(func.sum(Library.total_staff)).scalar() or 0,
        "outlet_count": db.query(LibraryOutlet).join(LibraryOutlet.dataset).filter(
            PLSDataset.year == year,
            *([LibraryOutlet.state == state.upper()] if state else [])
        ).count(),
    }
    
    # Calculate per-library averages
    if library_count > 0:
        stats.update({
            "avg_visits_per_library": stats["total_visits"] / library_count,
            "avg_circulation_per_library": stats["total_circulation"] / library_count,
            "avg_programs_per_library": stats["total_programs"] / library_count,
            "avg_operating_revenue_per_library": stats["total_operating_revenue"] / library_count,
            "avg_operating_expenditures_per_library": stats["total_operating_expenditures"] / library_count,
            "avg_staff_per_library": stats["total_staff"] / library_count,
        })
    
    return stats


@router.get("/trends")
def get_trend_stats(
    metrics: List[str] = Query(..., description="Metrics to include in trend data"),
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get trend statistics for specified metrics over time, optionally filtered by year range and state.
    """
    # Validate and map metric names to model attributes
    valid_metrics = {
        "visits": Library.visits,
        "total_circulation": Library.total_circulation,
        "electronic_circulation": Library.electronic_circulation,
        "physical_circulation": Library.physical_circulation,
        "total_programs": Library.total_programs,
        "total_program_attendance": Library.total_program_attendance,
        "total_operating_revenue": Library.total_operating_revenue,
        "local_operating_revenue": Library.local_operating_revenue,
        "state_operating_revenue": Library.state_operating_revenue,
        "federal_operating_revenue": Library.federal_operating_revenue,
        "total_operating_expenditures": Library.total_operating_expenditures,
        "staff_expenditures": Library.staff_expenditures,
        "collection_expenditures": Library.collection_expenditures,
        "print_collection": Library.print_collection,
        "electronic_collection": Library.electronic_collection,
        "total_staff": Library.total_staff,
    }
    
    # Check for invalid metrics
    invalid_metrics = [m for m in metrics if m not in valid_metrics]
    if invalid_metrics:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid metrics: {', '.join(invalid_metrics)}. Valid options are: {', '.join(valid_metrics.keys())}"
        )
    
    # Get available years
    available_years = [year[0] for year in db.query(PLSDataset.year).order_by(PLSDataset.year).all()]
    
    if not available_years:
        raise HTTPException(status_code=404, detail="No data available")
    
    # If start_year is not specified, use the earliest available year
    if start_year is None:
        start_year = min(available_years)
    
    # If end_year is not specified, use the latest available year
    if end_year is None:
        end_year = max(available_years)
    
    # Filter years to the requested range
    years_in_range = [year for year in available_years if start_year <= year <= end_year]
    
    if not years_in_range:
        raise HTTPException(
            status_code=404, 
            detail=f"No data available for years between {start_year} and {end_year}"
        )
    
    # Initialize results dictionary
    trends = {metric: [] for metric in metrics}
    trends["years"] = years_in_range
    
    # For each year, calculate metrics
    for year in years_in_range:
        # Build the base query for this year
        query = db.query(Library).join(Library.dataset).filter(PLSDataset.year == year)
        
        # Apply state filter if provided
        if state:
            query = query.filter(Library.state == state.upper())
        
        # Calculate each requested metric for this year
        for metric in metrics:
            value = query.with_entities(func.sum(valid_metrics[metric])).scalar() or 0
            trends[metric].append(value)
    
    return trends


@router.get("/comparison")
def compare_libraries(
    library_ids: List[str] = Query(..., description="List of library IDs to compare"),
    year: Optional[int] = None,
    metrics: List[str] = Query(None, description="Specific metrics to compare"),
    db: Session = Depends(get_db)
):
    """
    Compare specific libraries across selected metrics.
    """
    # If year is not specified, use the most recent year
    if year is None:
        latest_year = db.query(func.max(PLSDataset.year)).scalar()
        if not latest_year:
            raise HTTPException(status_code=404, detail="No data available")
        year = latest_year
    
    # Define valid metrics for comparison
    all_metrics = {
        "visits": "Visits",
        "total_circulation": "Total Circulation",
        "electronic_circulation": "E-Circulation",
        "physical_circulation": "Physical Circulation",
        "total_programs": "Programs",
        "total_program_attendance": "Program Attendance",
        "total_operating_revenue": "Operating Revenue",
        "total_operating_expenditures": "Operating Expenditures",
        "staff_expenditures": "Staff Expenditures",
        "collection_expenditures": "Collection Expenditures",
        "print_collection": "Print Materials",
        "electronic_collection": "E-Materials",
        "total_staff": "Staff (FTE)",
        "service_area_population": "Service Population",
    }
    
    # If specific metrics are requested, filter the all_metrics dictionary
    if metrics:
        invalid_metrics = [m for m in metrics if m not in all_metrics]
        if invalid_metrics:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid metrics: {', '.join(invalid_metrics)}"
            )
        comparison_metrics = {k: v for k, v in all_metrics.items() if k in metrics}
    else:
        comparison_metrics = all_metrics
    
    # Get libraries data
    libraries_data = []
    
    for library_id in library_ids:
        library = db.query(Library).join(Library.dataset).filter(
            Library.library_id == library_id,
            PLSDataset.year == year
        ).first()
        
        if not library:
            raise HTTPException(
                status_code=404, 
                detail=f"Library with ID {library_id} not found for year {year}"
            )
        
        library_data = {
            "library_id": library.library_id,
            "name": library.name,
            "state": library.state,
            "metrics": {}
        }
        
        # Add metrics data
        for metric_key, metric_name in comparison_metrics.items():
            value = getattr(library, metric_key)
            library_data["metrics"][metric_key] = {
                "name": metric_name,
                "value": value if value is not None else 0
            }
        
        libraries_data.append(library_data)
    
    return {
        "year": year,
        "libraries": libraries_data,
        "metric_definitions": comparison_metrics
    }


@router.get("/library/{library_id}/dashboard")
async def get_library_dashboard(
    library_id: str,
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics for a specific library.
    """
    try:
        # Check if the library exists
        library = db.query(Library).filter(Library.library_id == library_id).order_by(Library.dataset_id.desc()).first()
        
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Library with ID {library_id} not found"
            )
        
        # Get all years of data for this library
        library_data = db.query(Library)\
            .join(PLSDataset, Library.dataset_id == PLSDataset.id)\
            .filter(Library.library_id == library_id)\
            .order_by(PLSDataset.year.desc())\
            .all()
        
        if not library_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data available for library {library_id}"
            )
        
        # Most recent data is the first item
        recent_data = library_data[0]
        recent_year = db.query(PLSDataset).filter(PLSDataset.id == recent_data.dataset_id).first().year
        
        # Build trend data
        visits_trend = []
        circulation_trend = []
        programs_trend = []
        revenue_trend = []
        
        for lib in library_data:
            year = db.query(PLSDataset).filter(PLSDataset.id == lib.dataset_id).first().year
            
            # Add trend data points
            if lib.visits is not None:
                visits_trend.append({"year": year, "value": lib.visits})
            
            if lib.total_circulation is not None:
                circulation_trend.append({"year": year, "value": lib.total_circulation})
            
            if lib.total_programs is not None:
                programs_trend.append({"year": year, "value": lib.total_programs})
            
            if lib.total_operating_revenue is not None:
                revenue_trend.append({"year": year, "value": lib.total_operating_revenue})
        
        # Sort trend data by year
        visits_trend.sort(key=lambda x: x["year"])
        circulation_trend.sort(key=lambda x: x["year"])
        programs_trend.sort(key=lambda x: x["year"])
        revenue_trend.sort(key=lambda x: x["year"])
        
        # Build response
        response = {
            "name": recent_data.name,
            "city": recent_data.city,
            "state": recent_data.state,
            "recent_data": {
                "year": recent_year,
                "visits": recent_data.visits or 0,
                "circulation": {
                    "total": recent_data.total_circulation or 0,
                    "electronic": recent_data.electronic_circulation or 0,
                    "physical": recent_data.physical_circulation or 0
                },
                "collections": {
                    "print": recent_data.print_collection or 0,
                    "electronic": recent_data.electronic_collection or 0,
                    "audio": recent_data.audio_collection or 0,
                    "video": recent_data.video_collection or 0
                },
                "programs": {
                    "total": recent_data.total_programs or 0,
                    "attendance": recent_data.total_program_attendance or 0
                },
                "revenue": recent_data.total_operating_revenue or 0,
                "expenditures": recent_data.total_operating_expenditures or 0,
                "staff": recent_data.total_staff or 0
            },
            "trends": {
                "visits": visits_trend,
                "circulation": circulation_trend,
                "programs": programs_trend,
                "revenue": revenue_trend
            }
        }
        
        return response
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard data: {str(e)}"
        ) 