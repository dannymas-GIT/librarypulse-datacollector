from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Base schemas
class PLSDatasetBase(BaseModel):
    year: int
    status: str = "pending"
    record_count: Optional[int] = None
    notes: Optional[str] = None


class LibraryBase(BaseModel):
    library_id: str
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    county: Optional[str] = None
    phone: Optional[str] = None
    
    # Library classification
    locale: Optional[str] = None
    central_library_count: Optional[int] = None
    branch_library_count: Optional[int] = None
    bookmobile_count: Optional[int] = None
    service_area_population: Optional[int] = None
    
    # Collection statistics
    print_collection: Optional[int] = None
    electronic_collection: Optional[int] = None
    audio_collection: Optional[int] = None
    video_collection: Optional[int] = None
    
    # Usage statistics
    total_circulation: Optional[int] = None
    electronic_circulation: Optional[int] = None
    physical_circulation: Optional[int] = None
    visits: Optional[int] = None
    reference_transactions: Optional[int] = None
    registered_users: Optional[int] = None
    public_internet_computers: Optional[int] = None
    public_wifi_sessions: Optional[int] = None
    website_visits: Optional[int] = None
    
    # Program statistics
    total_programs: Optional[int] = None
    total_program_attendance: Optional[int] = None
    children_programs: Optional[int] = None
    children_program_attendance: Optional[int] = None
    ya_programs: Optional[int] = None
    ya_program_attendance: Optional[int] = None
    adult_programs: Optional[int] = None
    adult_program_attendance: Optional[int] = None
    
    # Staff statistics
    total_staff: Optional[float] = None
    librarian_staff: Optional[float] = None
    mls_librarian_staff: Optional[float] = None
    other_staff: Optional[float] = None
    
    # Financial statistics
    total_operating_revenue: Optional[int] = None
    local_operating_revenue: Optional[int] = None
    state_operating_revenue: Optional[int] = None
    federal_operating_revenue: Optional[int] = None
    other_operating_revenue: Optional[int] = None
    
    total_operating_expenditures: Optional[int] = None
    staff_expenditures: Optional[int] = None
    collection_expenditures: Optional[int] = None
    print_collection_expenditures: Optional[int] = None
    electronic_collection_expenditures: Optional[int] = None
    other_collection_expenditures: Optional[int] = None
    other_operating_expenditures: Optional[int] = None
    
    capital_revenue: Optional[int] = None
    capital_expenditures: Optional[int] = None
    
    # Operation info
    hours_open: Optional[int] = None
    weeks_open: Optional[int] = None


class LibraryOutletBase(BaseModel):
    library_id: str
    outlet_id: str
    name: str
    
    # Outlet info
    outlet_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    county: Optional[str] = None
    phone: Optional[str] = None
    
    # Geolocation
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Metropolitan status
    metro_status: Optional[str] = None
    
    # Operation info
    hours_open: Optional[int] = None
    weeks_open: Optional[int] = None
    
    # Outlet statistics
    square_footage: Optional[int] = None


# Create schemas
class PLSDatasetCreate(PLSDatasetBase):
    pass


class LibraryCreate(LibraryBase):
    dataset_id: int


class LibraryOutletCreate(LibraryOutletBase):
    dataset_id: int


# Read schemas
class PLSDataset(PLSDatasetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LibraryOutlet(LibraryOutletBase):
    id: int
    dataset_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Library(LibraryBase):
    id: int
    dataset_id: int
    created_at: datetime
    updated_at: datetime
    outlets: List[LibraryOutlet] = []
    
    class Config:
        from_attributes = True


class PLSDatasetWithRelations(PLSDataset):
    libraries: List[Library] = []
    outlets: List[LibraryOutlet] = []
    
    class Config:
        from_attributes = True


# Update schemas
class PLSDatasetUpdate(BaseModel):
    status: Optional[str] = None
    record_count: Optional[int] = None
    notes: Optional[str] = None


class LibraryUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    county: Optional[str] = None
    phone: Optional[str] = None
    
    # Other fields omitted for brevity - in real implementation, include all optional fields


class LibraryOutletUpdate(BaseModel):
    name: Optional[str] = None
    outlet_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    county: Optional[str] = None
    phone: Optional[str] = None
    
    # Other fields omitted for brevity - in real implementation, include all optional fields 