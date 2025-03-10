"""
Libraries API endpoints for the Library Pulse API.
"""
import os
import json
import glob
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# Create router
router = APIRouter(prefix="/api/libraries", tags=["libraries"])

# Models
class LibraryLocation(BaseModel):
    """Library location model."""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class LibraryContact(BaseModel):
    """Library contact model."""
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

class LibraryProfile(BaseModel):
    """Library profile model."""
    id: str
    name: str
    location: Optional[LibraryLocation] = None
    contact: Optional[LibraryContact] = None
    service_area: Optional[str] = None
    population_served: Optional[int] = None
    region: Optional[str] = None
    available_years: List[int] = []

class LibrarySearchResult(BaseModel):
    """Library search result model."""
    total: int
    libraries: List[LibraryProfile]

# Helper functions
def load_all_libraries() -> List[Dict[str, Any]]:
    """Load all library data from JSON files."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    library_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    libraries = []
    for library_file in library_files:
        with open(library_file, "r") as f:
            library_data = json.load(f)
            libraries.append(library_data)
    
    return libraries

def determine_region(library_data: Dict[str, Any]) -> str:
    """Determine the region of a library based on its location."""
    # This is a simplified implementation
    # In a real application, this would use more sophisticated logic
    
    # Default to "Unknown"
    region = "Unknown"
    
    # Check if location data exists
    if "location" in library_data and library_data["location"]:
        location = library_data["location"]
        
        # Check if city exists
        if "city" in location and location["city"]:
            city = location["city"].lower()
            
            # Nassau County
            if city in ["hempstead", "levittown", "freeport", "valley stream", "long beach"]:
                region = "Nassau"
            
            # Suffolk County
            elif city in ["brookhaven", "islip", "babylon", "huntington", "smithtown"]:
                region = "Suffolk"
            
            # NYC
            elif city in ["new york", "brooklyn", "queens", "bronx", "staten island"]:
                region = "NYC"
            
            # Upstate
            elif city in ["albany", "buffalo", "rochester", "syracuse", "yonkers"]:
                region = "Upstate"
    
    return region

def create_library_profile(library_data: Dict[str, Any]) -> LibraryProfile:
    """Create a library profile from library data."""
    # Extract available years
    available_years = []
    if "yearly_data" in library_data:
        available_years = sorted([int(year) for year in library_data["yearly_data"].keys()])
    
    # Determine region
    region = determine_region(library_data)
    
    # Create location
    location = None
    if "location" in library_data:
        location = LibraryLocation(**library_data["location"])
    
    # Create contact
    contact = None
    if "contact" in library_data:
        contact = LibraryContact(**library_data["contact"])
    
    # Create profile
    return LibraryProfile(
        id=library_data.get("id", ""),
        name=library_data.get("name", "Unknown Library"),
        location=location,
        contact=contact,
        service_area=library_data.get("service_area", None),
        population_served=library_data.get("population_served", None),
        region=region,
        available_years=available_years
    )

# Endpoints
@router.get("/search", response_model=LibrarySearchResult)
async def search_libraries(
    query: Optional[str] = Query(None, description="Search query"),
    region: Optional[str] = Query(None, description="Region filter (Nassau, Suffolk, NYC, Upstate)"),
    limit: int = Query(10, description="Maximum number of results to return"),
    offset: int = Query(0, description="Number of results to skip")
):
    """Search for libraries."""
    try:
        # Load all libraries
        all_libraries = load_all_libraries()
        
        # Filter libraries
        filtered_libraries = all_libraries
        
        # Filter by query
        if query:
            query = query.lower()
            filtered_libraries = [
                lib for lib in filtered_libraries
                if query in lib.get("name", "").lower() or query in lib.get("id", "").lower()
            ]
        
        # Filter by region
        if region:
            region = region.lower()
            filtered_libraries = [
                lib for lib in filtered_libraries
                if determine_region(lib).lower() == region
            ]
        
        # Create library profiles
        library_profiles = [create_library_profile(lib) for lib in filtered_libraries]
        
        # Apply pagination
        paginated_libraries = library_profiles[offset:offset + limit]
        
        # Return search result
        return LibrarySearchResult(
            total=len(library_profiles),
            libraries=paginated_libraries
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/regions", response_model=Dict[str, List[LibraryProfile]])
async def get_libraries_by_region():
    """Get libraries grouped by region."""
    try:
        # Load all libraries
        all_libraries = load_all_libraries()
        
        # Group libraries by region
        libraries_by_region = {
            "Nassau": [],
            "Suffolk": [],
            "NYC": [],
            "Upstate": [],
            "Unknown": []
        }
        
        # Create library profiles and group by region
        for library_data in all_libraries:
            profile = create_library_profile(library_data)
            region = profile.region or "Unknown"
            
            if region in libraries_by_region:
                libraries_by_region[region].append(profile)
            else:
                libraries_by_region["Unknown"].append(profile)
        
        # Sort libraries by name within each region
        for region in libraries_by_region:
            libraries_by_region[region] = sorted(
                libraries_by_region[region],
                key=lambda lib: lib.name
            )
        
        return libraries_by_region
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{library_id}", response_model=LibraryProfile)
async def get_library(library_id: str):
    """Get a specific library by ID."""
    try:
        # Load library data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        library_file = os.path.join(data_dir, f"{library_id}.json")
        
        if not os.path.exists(library_file):
            raise HTTPException(status_code=404, detail=f"Library with ID {library_id} not found")
        
        with open(library_file, "r") as f:
            library_data = json.load(f)
        
        # Create library profile
        return create_library_profile(library_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[LibraryProfile])
async def get_all_libraries(
    limit: int = Query(100, description="Maximum number of results to return"),
    offset: int = Query(0, description="Number of results to skip")
):
    """Get all libraries."""
    try:
        # Load all libraries
        all_libraries = load_all_libraries()
        
        # Create library profiles
        library_profiles = [create_library_profile(lib) for lib in all_libraries]
        
        # Sort libraries by name
        library_profiles = sorted(library_profiles, key=lambda lib: lib.name)
        
        # Apply pagination
        paginated_libraries = library_profiles[offset:offset + limit]
        
        return paginated_libraries
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 