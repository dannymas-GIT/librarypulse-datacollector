"""
Script to initialize the database.
"""
import logging
import os
from pathlib import Path

from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import ProgrammingError
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define database URL
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/librarypulse"

# Create SQLAlchemy Base
Base = declarative_base()

# Define models directly here to avoid import issues
class PLSDataset(Base):
    __tablename__ = "pls_datasets"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)
    record_count = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    libraries = relationship("Library", back_populates="dataset", cascade="all, delete-orphan")
    outlets = relationship("LibraryOutlet", back_populates="dataset", cascade="all, delete-orphan")


class Library(Base):
    __tablename__ = "libraries"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("pls_datasets.id"), nullable=False)
    library_id = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(20), nullable=True)
    county = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Library classification
    locale = Column(String(50), nullable=True)
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
    total_staff = Column(Float, nullable=True)
    librarian_staff = Column(Float, nullable=True)
    mls_librarian_staff = Column(Float, nullable=True)
    other_staff = Column(Float, nullable=True)
    
    # Financial statistics
    total_operating_revenue = Column(Float, nullable=True)
    local_operating_revenue = Column(Float, nullable=True)
    state_operating_revenue = Column(Float, nullable=True)
    federal_operating_revenue = Column(Float, nullable=True)
    other_operating_revenue = Column(Float, nullable=True)
    total_operating_expenditures = Column(Float, nullable=True)
    staff_expenditures = Column(Float, nullable=True)
    collection_expenditures = Column(Float, nullable=True)
    
    # Relationships
    dataset = relationship("PLSDataset", back_populates="libraries")
    outlets = relationship("LibraryOutlet", back_populates="library", cascade="all, delete-orphan")
    
    # Add a unique constraint to library_id to make it a valid foreign key target
    __table_args__ = (UniqueConstraint('library_id', name='uix_library_id'),)


class LibraryOutlet(Base):
    __tablename__ = "library_outlets"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("pls_datasets.id"), nullable=False)
    library_id = Column(String(50), ForeignKey("libraries.library_id"), nullable=False)
    outlet_id = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(20), nullable=True)
    county = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    hours = Column(Float, nullable=True)
    square_feet = Column(Integer, nullable=True)
    locale = Column(String(50), nullable=True)
    
    # Relationships
    dataset = relationship("PLSDataset", back_populates="outlets")
    library = relationship("Library", back_populates="outlets")


class LibraryConfig(Base):
    __tablename__ = "library_config"

    id = Column(Integer, primary_key=True, index=True)
    library_id = Column(String(50), nullable=False, unique=True, index=True)
    library_name = Column(String(255), nullable=False)
    state = Column(String(2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


def init_db() -> None:
    """
    Initialize the database with tables and initial data.
    """
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Drop existing tables if they exist
        logger.info("Dropping existing tables if they exist...")
        Base.metadata.drop_all(bind=engine)
        
        # Create tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if we need to add initial data
        if db.query(PLSDataset).count() == 0:
            logger.info("Adding initial data...")
            # Add a placeholder dataset for testing
            dataset = PLSDataset(
                year=2022,
                status="pending",
                record_count=0,
                notes="Initial placeholder dataset"
            )
            db.add(dataset)
            db.commit()
            logger.info(f"Added placeholder dataset for year {dataset.year}")
        
        db.close()
        logger.info("Database initialization complete")
        
    except ProgrammingError as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db() 