from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, Text, Enum, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import and_

from app.db.base import Base, IDMixin, TimestampMixin


class PLSDataset(Base, IDMixin, TimestampMixin):
    """Model representing a Public Libraries Survey dataset for a specific year."""
    
    __tablename__ = "pls_datasets"
    
    __table_args__ = {'extend_existing': True}
    
    year = Column(Integer, nullable=False, index=True, unique=True)
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, complete, error
    record_count = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships - these will be defined after the other classes


class Library(Base, IDMixin, TimestampMixin):
    """Model representing a library administrative entity from the PLS data."""
    
    __tablename__ = "libraries"
    
    dataset_id = Column(Integer, ForeignKey("pls_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    library_id = Column(String(20), nullable=False, index=True)  # FSCSKEY
    
    __table_args__ = (
        UniqueConstraint('dataset_id', 'library_id', name='uix_library_dataset_library_id'),
        {'extend_existing': True}
    )
    
    # Library info
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True, index=True)
    zip_code = Column(String(10), nullable=True)
    county = Column(String(100), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    
    # Library classification
    locale = Column(String(50), nullable=True, index=True)  # Urban/rural classification
    central_library_count = Column(Integer, nullable=True)
    branch_library_count = Column(Integer, nullable=True)
    bookmobile_count = Column(Integer, nullable=True)
    service_area_population = Column(Integer, nullable=True)
    
    # Collection statistics
    print_collection = Column(Integer, nullable=True)
    electronic_collection = Column(Integer, nullable=True)
    audio_collection = Column(Integer, nullable=True)
    video_collection = Column(Integer, nullable=True)
    
    # Usage statistics
    total_circulation = Column(Integer, nullable=True)
    electronic_circulation = Column(Integer, nullable=True)
    physical_circulation = Column(Integer, nullable=True)
    visits = Column(Integer, nullable=True)
    reference_transactions = Column(Integer, nullable=True)
    registered_users = Column(Integer, nullable=True)
    public_internet_computers = Column(Integer, nullable=True)
    public_wifi_sessions = Column(Integer, nullable=True)
    website_visits = Column(Integer, nullable=True)
    
    # Program statistics
    total_programs = Column(Integer, nullable=True)
    total_program_attendance = Column(Integer, nullable=True)
    children_programs = Column(Integer, nullable=True)
    children_program_attendance = Column(Integer, nullable=True)
    ya_programs = Column(Integer, nullable=True)
    ya_program_attendance = Column(Integer, nullable=True)
    adult_programs = Column(Integer, nullable=True)
    adult_program_attendance = Column(Integer, nullable=True)
    
    # Staff statistics
    total_staff = Column(Float, nullable=True)  # FTE
    librarian_staff = Column(Float, nullable=True)  # FTE
    mls_librarian_staff = Column(Float, nullable=True)  # FTE with MLS
    other_staff = Column(Float, nullable=True)  # FTE
    
    # Financial statistics
    total_operating_revenue = Column(Integer, nullable=True)
    local_operating_revenue = Column(Integer, nullable=True)
    state_operating_revenue = Column(Integer, nullable=True)
    federal_operating_revenue = Column(Integer, nullable=True)
    other_operating_revenue = Column(Integer, nullable=True)
    
    total_operating_expenditures = Column(Integer, nullable=True)
    staff_expenditures = Column(Integer, nullable=True)
    collection_expenditures = Column(Integer, nullable=True)
    print_collection_expenditures = Column(Integer, nullable=True)
    electronic_collection_expenditures = Column(Integer, nullable=True)
    other_collection_expenditures = Column(Integer, nullable=True)
    other_operating_expenditures = Column(Integer, nullable=True)
    
    capital_revenue = Column(Integer, nullable=True)
    capital_expenditures = Column(Integer, nullable=True)
    
    # Operation info
    hours_open = Column(Integer, nullable=True)  # Annual
    weeks_open = Column(Integer, nullable=True)  # Annual
    
    # Relationships - these will be defined after the LibraryOutlet class


class LibraryOutlet(Base, IDMixin, TimestampMixin):
    """Model representing a library outlet/branch from the PLS data."""
    
    __tablename__ = "library_outlets"
    
    dataset_id = Column(Integer, ForeignKey("pls_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    library_id = Column(String(20), nullable=False, index=True)
    outlet_id = Column(String(20), nullable=False, index=True)  # FSCS_SEQ
    
    __table_args__ = (
        ForeignKeyConstraint(
            ['dataset_id', 'library_id'],
            ['libraries.dataset_id', 'libraries.library_id'],
            ondelete="CASCADE"
        ),
        {'extend_existing': True}
    )
    
    # Outlet info
    name = Column(String(255), nullable=False)
    outlet_type = Column(String(50), nullable=True)  # Central, Branch, Bookmobile, etc.
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True, index=True)
    zip_code = Column(String(10), nullable=True)
    county = Column(String(100), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    
    # Geolocation
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Metropolitan status
    metro_status = Column(String(50), nullable=True)
    
    # Operation info
    hours_open = Column(Integer, nullable=True)  # Weekly
    weeks_open = Column(Integer, nullable=True)  # Annual
    
    # Outlet statistics (if available separately)
    square_footage = Column(Integer, nullable=True)


# Define relationships after all classes are defined
PLSDataset.libraries = relationship("Library", back_populates="dataset", cascade="all, delete-orphan")
PLSDataset.outlets = relationship("LibraryOutlet", back_populates="dataset", cascade="all, delete-orphan")

Library.dataset = relationship("PLSDataset", back_populates="libraries")
Library.outlets = relationship("LibraryOutlet", back_populates="library", cascade="all, delete-orphan")
Library.users = relationship("User", back_populates="library")

LibraryOutlet.dataset = relationship("PLSDataset", back_populates="outlets")
LibraryOutlet.library = relationship("Library", back_populates="outlets") 