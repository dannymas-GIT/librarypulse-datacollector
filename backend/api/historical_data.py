"""
API endpoints for accessing historical library data.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from pydantic import BaseModel

# Create router
router = APIRouter(prefix="/api/historical", tags=["historical"])

# Constants
WEST_BABYLON_ID = "NY0773"
DB_PARAMS = {
    "dbname": "librarypulse",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

# Models
class LibraryHistoricalData(BaseModel):
    id: int
    library_id: str
    year: int
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    county: Optional[str] = None
    phone: Optional[str] = None
    locale: Optional[str] = None
    central_library_count: Optional[int] = None
    branch_library_count: Optional[int] = None
    bookmobile_count: Optional[int] = None
    service_area_population: Optional[int] = None
    print_collection: Optional[int] = None
    electronic_collection: Optional[int] = None
    audio_collection: Optional[int] = None
    video_collection: Optional[int] = None
    total_circulation: Optional[int] = None
    electronic_circulation: Optional[int] = None
    physical_circulation: Optional[int] = None
    visits: Optional[int] = None
    reference_transactions: Optional[int] = None
    registered_users: Optional[int] = None
    public_internet_computers: Optional[int] = None
    public_wifi_sessions: Optional[int] = None
    website_visits: Optional[int] = None
    total_programs: Optional[int] = None
    total_program_attendance: Optional[int] = None
    children_programs: Optional[int] = None
    children_program_attendance: Optional[int] = None
    ya_programs: Optional[int] = None
    ya_program_attendance: Optional[int] = None
    adult_programs: Optional[int] = None
    adult_program_attendance: Optional[int] = None
    total_staff: Optional[float] = None
    librarian_staff: Optional[float] = None
    mls_librarian_staff: Optional[float] = None
    other_staff: Optional[float] = None
    total_operating_revenue: Optional[float] = None
    local_operating_revenue: Optional[float] = None
    state_operating_revenue: Optional[float] = None
    federal_operating_revenue: Optional[float] = None
    other_operating_revenue: Optional[float] = None
    total_operating_expenditures: Optional[float] = None
    staff_expenditures: Optional[float] = None
    collection_expenditures: Optional[float] = None

class TrendData(BaseModel):
    metric: str
    years: List[int]
    values: List[Optional[float]]
    growth_rates: Optional[Dict[str, Any]] = None

class HistoricalSummary(BaseModel):
    library_id: str
    name: str
    years_available: List[int]
    earliest_year: int
    latest_year: int
    total_years: int
    metrics_available: List[str]

# Helper functions
def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        conn.autocommit = False
        return conn
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

def get_available_years(conn, library_id=WEST_BABYLON_ID):
    """Get a list of available years for the library."""
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT year FROM library_historical_data WHERE library_id = %s ORDER BY year",
            (library_id,)
        )
        years = [row[0] for row in cursor.fetchall()]
        return years
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        cursor.close()

def get_library_data_for_year(conn, year, library_id=WEST_BABYLON_ID):
    """Get library data for a specific year."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            "SELECT * FROM library_historical_data WHERE library_id = %s AND year = %s",
            (library_id, year)
        )
        data = cursor.fetchone()
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for library {library_id} in year {year}")
        return dict(data)
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        cursor.close()

def get_all_library_data(conn, library_id=WEST_BABYLON_ID):
    """Get all historical data for the library."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            "SELECT * FROM library_historical_data WHERE library_id = %s ORDER BY year",
            (library_id,)
        )
        data = cursor.fetchall()
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for library {library_id}")
        return [dict(row) for row in data]
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        cursor.close()

def calculate_trend_data(data, metric):
    """Calculate trend data for a specific metric."""
    if not data:
        return None
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(data)
    
    # Check if metric exists in data
    if metric not in df.columns:
        return None
    
    # Extract years and values
    years = df['year'].tolist()
    
    # Convert values to float where possible
    try:
        values = [float(v) if v is not None else None for v in df[metric].tolist()]
    except (ValueError, TypeError):
        # If conversion fails, use original values
        values = df[metric].tolist()
    
    # Calculate growth rates if numeric
    growth_rates = None
    if pd.api.types.is_numeric_dtype(df[metric]):
        try:
            # Calculate year-over-year growth rates
            df['growth_rate'] = df[metric].pct_change() * 100
            
            # Convert to dictionary
            growth_rates = {
                'yearly': {str(year): float(rate) if not pd.isna(rate) else None 
                          for year, rate in zip(df['year'][1:], df['growth_rate'][1:].tolist())},
                'average': float(df['growth_rate'].mean()) if not pd.isna(df['growth_rate'].mean()) else None,
                'total': float((df[metric].iloc[-1] - df[metric].iloc[0]) / df[metric].iloc[0] * 100) 
                        if df[metric].iloc[0] and df[metric].iloc[0] != 0 else None
            }
        except Exception as e:
            # If growth rate calculation fails, return None for growth_rates
            growth_rates = None
    
    return TrendData(
        metric=metric,
        years=years,
        values=values,
        growth_rates=growth_rates
    )

# API Endpoints
@router.get("/summary", response_model=HistoricalSummary)
async def get_summary(library_id: str = WEST_BABYLON_ID):
    """Get a summary of available historical data."""
    conn = get_db_connection()
    
    try:
        # Get available years
        years = get_available_years(conn, library_id)
        if not years:
            raise HTTPException(status_code=404, detail=f"No historical data found for library {library_id}")
        
        # Get a sample record to determine available metrics
        sample_data = get_library_data_for_year(conn, years[-1], library_id)
        
        # Filter out non-null metrics
        metrics_available = [key for key, value in sample_data.items() 
                            if key not in ['id', 'library_id', 'year'] and value is not None]
        
        return HistoricalSummary(
            library_id=library_id,
            name=sample_data['name'],
            years_available=years,
            earliest_year=years[0],
            latest_year=years[-1],
            total_years=len(years),
            metrics_available=metrics_available
        )
    finally:
        conn.close()

@router.get("/years", response_model=List[int])
async def get_years(library_id: str = WEST_BABYLON_ID):
    """Get a list of available years for the library."""
    conn = get_db_connection()
    
    try:
        years = get_available_years(conn, library_id)
        if not years:
            raise HTTPException(status_code=404, detail=f"No historical data found for library {library_id}")
        return years
    finally:
        conn.close()

@router.get("/data/{year}", response_model=LibraryHistoricalData)
async def get_data_for_year(year: int, library_id: str = WEST_BABYLON_ID):
    """Get library data for a specific year."""
    conn = get_db_connection()
    
    try:
        data = get_library_data_for_year(conn, year, library_id)
        return data
    finally:
        conn.close()

@router.get("/data", response_model=List[LibraryHistoricalData])
async def get_all_data(library_id: str = WEST_BABYLON_ID):
    """Get all historical data for the library."""
    conn = get_db_connection()
    
    try:
        data = get_all_library_data(conn, library_id)
        return data
    finally:
        conn.close()

@router.get("/trends/{metric}", response_model=TrendData)
async def get_trend_data(metric: str, library_id: str = WEST_BABYLON_ID):
    """Get trend data for a specific metric."""
    conn = get_db_connection()
    
    try:
        data = get_all_library_data(conn, library_id)
        trend_data = calculate_trend_data(data, metric)
        if not trend_data:
            raise HTTPException(status_code=404, detail=f"No trend data available for metric '{metric}'")
        return trend_data
    finally:
        conn.close()

@router.get("/trends", response_model=List[TrendData])
async def get_multiple_trends(
    metrics: List[str] = Query(..., description="List of metrics to analyze"),
    library_id: str = WEST_BABYLON_ID
):
    """Get trend data for multiple metrics."""
    conn = get_db_connection()
    
    try:
        data = get_all_library_data(conn, library_id)
        
        trend_data_list = []
        for metric in metrics:
            trend_data = calculate_trend_data(data, metric)
            if trend_data:
                trend_data_list.append(trend_data)
        
        if not trend_data_list:
            raise HTTPException(status_code=404, detail=f"No trend data available for any of the requested metrics")
        
        return trend_data_list
    finally:
        conn.close() 