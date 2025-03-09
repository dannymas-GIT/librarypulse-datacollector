from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base, IDMixin, TimestampMixin


class LibraryConfig(Base, IDMixin, TimestampMixin):
    """Model representing the library configuration for the application."""
    
    __tablename__ = "library_config"
    
    # There should only be one row in this table
    # The library_id representing the FSCSKEY of the selected library
    library_id = Column(String(20), nullable=False, index=True)
    library_name = Column(String(255), nullable=False)
    
    # Configuration for statistics collection
    setup_complete = Column(Boolean, default=False, nullable=False)
    
    # Track which statistics are of interest
    # Statistics categories (JSON format to store selected metrics)
    collection_stats_enabled = Column(Boolean, default=True, nullable=False)
    usage_stats_enabled = Column(Boolean, default=True, nullable=False) 
    program_stats_enabled = Column(Boolean, default=True, nullable=False)
    staff_stats_enabled = Column(Boolean, default=True, nullable=False)
    financial_stats_enabled = Column(Boolean, default=True, nullable=False)
    
    # Detailed selected metrics within each category
    collection_metrics = Column(JSON, nullable=True)
    usage_metrics = Column(JSON, nullable=True)
    program_metrics = Column(JSON, nullable=True)
    staff_metrics = Column(JSON, nullable=True)
    financial_metrics = Column(JSON, nullable=True)
    
    # Automatic update settings
    auto_update_enabled = Column(Boolean, default=False, nullable=False)
    last_update_check = Column(Integer, nullable=True)  # Year of last update check 