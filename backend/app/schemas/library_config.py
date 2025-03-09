from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from pydantic import BaseModel, Field


class LibrarySearchResponse(BaseModel):
    """Schema for library search results."""
    id: str
    name: str
    city: Optional[str] = None
    state: Optional[str] = None


class MetricsConfigResponse(BaseModel):
    """Schema for available metrics configuration."""
    categories: Dict[str, Dict[str, str]]


class LibraryConfigBase(BaseModel):
    """Base schema for library configuration."""
    library_id: str
    library_name: str
    collection_stats_enabled: bool = True
    usage_stats_enabled: bool = True
    program_stats_enabled: bool = True
    staff_stats_enabled: bool = True
    financial_stats_enabled: bool = True
    collection_metrics: Optional[Dict[str, bool]] = None
    usage_metrics: Optional[Dict[str, bool]] = None
    program_metrics: Optional[Dict[str, bool]] = None
    staff_metrics: Optional[Dict[str, bool]] = None
    financial_metrics: Optional[Dict[str, bool]] = None
    setup_complete: bool = True
    auto_update_enabled: bool = False


class LibraryConfigCreate(LibraryConfigBase):
    """Schema for creating a library configuration."""
    pass


class LibraryConfigUpdate(BaseModel):
    """Schema for updating a library configuration."""
    collection_stats_enabled: Optional[bool] = None
    usage_stats_enabled: Optional[bool] = None
    program_stats_enabled: Optional[bool] = None
    staff_stats_enabled: Optional[bool] = None
    financial_stats_enabled: Optional[bool] = None
    collection_metrics: Optional[Dict[str, bool]] = None
    usage_metrics: Optional[Dict[str, bool]] = None
    program_metrics: Optional[Dict[str, bool]] = None
    staff_metrics: Optional[Dict[str, bool]] = None
    financial_metrics: Optional[Dict[str, bool]] = None
    setup_complete: Optional[bool] = None
    auto_update_enabled: Optional[bool] = None


class LibraryConfigResponse(LibraryConfigBase):
    """Schema for library configuration response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 