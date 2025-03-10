"""
Script to directly insert West Babylon Public Library data into the database.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from init_db_simple import Base, PLSDataset, Library, LibraryOutlet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/librarypulse"

# West Babylon Public Library information (known values, manually collected)
LIBRARY_DATA = {
    'library_id': 'NY0773',
    'name': 'West Babylon Public Library',
    'address': '211 Route 109',
    'city': 'West Babylon',
    'state': 'NY',
    'zip_code': '11704',
    'county': 'Suffolk',
    'phone': '631-669-5445',
    'service_area_population': 43000,
    'central_library_count': 1,
    'branch_library_count': 0,
    'total_staff': 42.5,
    'librarian_staff': 12.5,
    'total_circulation': 210000,
    'visits': 175000,
    'total_programs': 420,
    'total_program_attendance': 8500,
    'print_collection': 115000,
    'electronic_collection': 25000,
    'audio_collection': 12000,
    'video_collection': 18000,
    'total_operating_revenue': 3750000.00,
    'total_operating_expenditures': 3600000.00,
    'staff_expenditures': 2400000.00,
    'collection_expenditures': 450000.00,
}

OUTLET_DATA = {
    'outlet_id': 'NY0773_01',
    'name': 'West Babylon Public Library',
    'type': 'CE',  # Central Library
    'address': '211 Route 109',
    'city': 'West Babylon',
    'state': 'NY',
    'zip_code': '11704',
    'county': 'Suffolk',
    'phone': '631-669-5445',
    'hours': 56.0,
    'square_feet': 28000,
}

def insert_west_babylon_data():
    """
    Insert West Babylon Public Library data directly into the database.
    """
    # Create database engine and session
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create a dataset for 2022
        dataset = PLSDataset(
            year=2022,
            status="complete",
            record_count=1,
            notes="West Babylon Public Library data for 2022"
        )
        session.add(dataset)
        session.flush()  # Get the dataset ID
        
        logger.info(f"Created dataset for year 2022 with ID {dataset.id}")
        
        # Add library data
        library_data = LIBRARY_DATA.copy()
        library_data['dataset_id'] = dataset.id
        
        library = Library(**library_data)
        session.add(library)
        session.flush()
        
        logger.info(f"Added library: {library_data['name']} ({library_data['library_id']})")
        
        # Add outlet data
        outlet_data = OUTLET_DATA.copy()
        outlet_data['dataset_id'] = dataset.id
        outlet_data['library_id'] = library_data['library_id']
        
        outlet = LibraryOutlet(**outlet_data)
        session.add(outlet)
        
        logger.info(f"Added outlet: {outlet_data['name']} ({outlet_data['outlet_id']})")
        
        # Add library configuration
        library_config = {
            'library_id': library_data['library_id'],
            'library_name': library_data['name'],
            'state': library_data['state'],
            'is_active': True
        }
        
        from init_db_simple import LibraryConfig
        config = LibraryConfig(**library_config)
        session.add(config)
        
        logger.info(f"Added library configuration for {library_data['name']}")
        
        # Commit all changes
        session.commit()
        logger.info("Successfully inserted West Babylon Public Library data")
        
        # Return the inserted data for verification
        return {
            'dataset_id': dataset.id,
            'library_id': library_data['library_id'],
            'library_name': library_data['name'],
            'outlet_id': outlet_data['outlet_id']
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error inserting data: {e}", exc_info=True)
        raise
    finally:
        session.close()

def verify_data(info):
    """
    Verify that the data was inserted correctly by retrieving it from the database.
    """
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Query for the library
        library = session.query(Library).filter_by(
            library_id=info['library_id'], 
            dataset_id=info['dataset_id']
        ).first()
        
        if library:
            logger.info(f"\nLibrary found in database:")
            logger.info(f"  Name: {library.name}")
            logger.info(f"  Location: {library.city}, {library.state}")
            logger.info(f"  Service Population: {library.service_area_population}")
            logger.info(f"  Annual Circulation: {library.total_circulation}")
            logger.info(f"  Annual Visits: {library.visits}")
            logger.info(f"  Total Staff: {library.total_staff}")
            logger.info(f"  Total Operating Revenue: ${library.total_operating_revenue:,.2f}")
            
            outlets = session.query(LibraryOutlet).filter_by(
                library_id=info['library_id'],
                dataset_id=info['dataset_id']
            ).all()
            
            logger.info(f"\nOutlets ({len(outlets)}):")
            for outlet in outlets:
                logger.info(f"  - {outlet.name} ({outlet.outlet_id})")
                logger.info(f"    Address: {outlet.address}, {outlet.city}, {outlet.state}")
                logger.info(f"    Square Feet: {outlet.square_feet}")
                logger.info(f"    Weekly Hours: {outlet.hours}")
                
            return True
        else:
            logger.error(f"Library not found in database after insertion")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying data: {e}", exc_info=True)
        return False
    finally:
        session.close()

if __name__ == "__main__":
    logger.info("Starting West Babylon Public Library data insertion")
    
    try:
        info = insert_west_babylon_data()
        if info:
            verify_data(info)
    except Exception as e:
        logger.error(f"Failed to insert data: {e}")
    
    logger.info("Data insertion process completed") 