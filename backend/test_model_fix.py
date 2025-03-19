#!/usr/bin/env python3
"""
Simple script to test the database model fix for PLSDataset.outlets relationship.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.pls_data import PLSDataset, Library, LibraryOutlet
from app.db.base import Base

# Create a test in-memory database
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Create a test session
db = SessionLocal()

def test_model_relationships():
    """Test that we can create and query PLSDataset, Library, and LibraryOutlet models."""
    try:
        # Create a test dataset
        dataset = PLSDataset(year=2023, status="complete", record_count=100)
        db.add(dataset)
        db.commit()
        
        # Create a test library
        library = Library(
            dataset_id=dataset.id, 
            library_id="LIB123", 
            name="Test Library"
        )
        db.add(library)
        db.commit()
        
        # Create a test outlet
        outlet = LibraryOutlet(
            dataset_id=dataset.id,
            library_id="LIB123",
            outlet_id="OUT1",
            name="Test Outlet"
        )
        db.add(outlet)
        db.commit()
        
        # Test relationship queries
        db.refresh(dataset)
        db.refresh(library)
        db.refresh(outlet)
        
        print("Dataset created successfully:", dataset.id, dataset.year)
        print("Library created successfully:", library.id, library.name)
        print("Outlet created successfully:", outlet.id, outlet.name)
        
        # Test outlet -> dataset relationship
        assert outlet.dataset_id == dataset.id
        print("Outlet.dataset_id matches Dataset.id")
        
        # Test dataset -> outlets relationship
        dataset_outlets = dataset.outlets
        assert len(dataset_outlets) == 1
        assert dataset_outlets[0].id == outlet.id
        print("Dataset.outlets contains the outlet we created")
        
        print("All tests passed! The relationship fix worked.")
        return True
    except Exception as e:
        print(f"Error testing relationships: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_model_relationships() 