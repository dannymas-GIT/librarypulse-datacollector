"""
Dashboard API endpoints for the Library Pulse API.
"""
import os
import json
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# Create router
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Models
class KPI(BaseModel):
    """Key Performance Indicator model."""
    name: str
    value: float
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", or "stable"
    unit: Optional[str] = None

class DashboardSummary(BaseModel):
    """Dashboard summary model."""
    library_id: str
    library_name: str
    year: int
    kpis: List[KPI]
    
# Helper functions
def load_library_data(library_id: str) -> Dict[str, Any]:
    """Load library data from JSON file."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    library_file = os.path.join(data_dir, f"{library_id}.json")
    
    if not os.path.exists(library_file):
        raise HTTPException(status_code=404, detail=f"Library with ID {library_id} not found")
    
    with open(library_file, "r") as f:
        return json.load(f)

def calculate_trend(current: float, previous: float) -> str:
    """Calculate trend based on current and previous values."""
    if current > previous:
        return "up"
    elif current < previous:
        return "down"
    else:
        return "stable"

def calculate_change_percent(current: float, previous: float) -> float:
    """Calculate percent change between current and previous values."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - previous) / previous) * 100.0

# Endpoints
@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    library_id: str = Query("NY0773", description="Library ID"),
    year: int = Query(2006, description="Year for dashboard data")
):
    """Get dashboard summary for a library."""
    try:
        # Load library data
        library_data = load_library_data(library_id)
        
        # Get library name
        library_name = library_data.get("name", "Unknown Library")
        
        # Get data for the specified year and previous year
        yearly_data = library_data.get("yearly_data", {})
        current_year_data = yearly_data.get(str(year), {})
        previous_year_data = yearly_data.get(str(year - 1), {})
        
        if not current_year_data:
            raise HTTPException(status_code=404, detail=f"Data for year {year} not found")
        
        # Calculate KPIs
        kpis = []
        
        # Total circulation
        total_circulation = current_year_data.get("total_circulation", 0)
        prev_total_circulation = previous_year_data.get("total_circulation", 0)
        kpis.append(KPI(
            name="Total Circulation",
            value=total_circulation,
            previous_value=prev_total_circulation,
            change_percent=calculate_change_percent(total_circulation, prev_total_circulation),
            trend=calculate_trend(total_circulation, prev_total_circulation),
            unit="items"
        ))
        
        # Visits
        visits = current_year_data.get("visits", 0)
        prev_visits = previous_year_data.get("visits", 0)
        kpis.append(KPI(
            name="Visits",
            value=visits,
            previous_value=prev_visits,
            change_percent=calculate_change_percent(visits, prev_visits),
            trend=calculate_trend(visits, prev_visits),
            unit="visits"
        ))
        
        # Total programs
        total_programs = current_year_data.get("total_programs", 0)
        prev_total_programs = previous_year_data.get("total_programs", 0)
        kpis.append(KPI(
            name="Total Programs",
            value=total_programs,
            previous_value=prev_total_programs,
            change_percent=calculate_change_percent(total_programs, prev_total_programs),
            trend=calculate_trend(total_programs, prev_total_programs),
            unit="programs"
        ))
        
        # Program attendance
        program_attendance = current_year_data.get("total_program_attendance", 0)
        prev_program_attendance = previous_year_data.get("total_program_attendance", 0)
        kpis.append(KPI(
            name="Program Attendance",
            value=program_attendance,
            previous_value=prev_program_attendance,
            change_percent=calculate_change_percent(program_attendance, prev_program_attendance),
            trend=calculate_trend(program_attendance, prev_program_attendance),
            unit="attendees"
        ))
        
        # Return dashboard summary
        return DashboardSummary(
            library_id=library_id,
            library_name=library_name,
            year=year,
            kpis=kpis
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kpis", response_model=List[KPI])
async def get_kpis(
    library_id: str = Query("NY0773", description="Library ID"),
    year: int = Query(2006, description="Year for KPI data"),
    metrics: List[str] = Query(["total_circulation", "visits", "total_programs", "total_program_attendance"], description="Metrics to include in KPIs")
):
    """Get KPIs for a library."""
    try:
        # Load library data
        library_data = load_library_data(library_id)
        
        # Get data for the specified year and previous year
        yearly_data = library_data.get("yearly_data", {})
        current_year_data = yearly_data.get(str(year), {})
        previous_year_data = yearly_data.get(str(year - 1), {})
        
        if not current_year_data:
            raise HTTPException(status_code=404, detail=f"Data for year {year} not found")
        
        # Calculate KPIs for requested metrics
        kpis = []
        
        # Map of metric names to display names
        metric_names = {
            "total_circulation": "Total Circulation",
            "visits": "Visits",
            "total_programs": "Total Programs",
            "total_program_attendance": "Program Attendance",
            "reference_transactions": "Reference Transactions",
            "registered_users": "Registered Users",
            "print_collection": "Print Collection",
            "electronic_collection": "Electronic Collection",
            "audio_collection": "Audio Collection",
            "video_collection": "Video Collection"
        }
        
        # Map of metrics to units
        metric_units = {
            "total_circulation": "items",
            "visits": "visits",
            "total_programs": "programs",
            "total_program_attendance": "attendees",
            "reference_transactions": "transactions",
            "registered_users": "users",
            "print_collection": "items",
            "electronic_collection": "items",
            "audio_collection": "items",
            "video_collection": "items"
        }
        
        for metric in metrics:
            if metric in current_year_data:
                current_value = current_year_data.get(metric, 0)
                previous_value = previous_year_data.get(metric, 0)
                
                kpis.append(KPI(
                    name=metric_names.get(metric, metric),
                    value=current_value,
                    previous_value=previous_value,
                    change_percent=calculate_change_percent(current_value, previous_value),
                    trend=calculate_trend(current_value, previous_value),
                    unit=metric_units.get(metric, "")
                ))
        
        return kpis
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/library/{library_id}/dashboard", response_model=DashboardSummary)
async def get_library_dashboard(
    library_id: str,
    year: int = Query(2006, description="Year for dashboard data")
):
    """Get dashboard for a specific library."""
    return await get_dashboard_summary(library_id=library_id, year=year) 