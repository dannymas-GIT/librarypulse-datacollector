#!/usr/bin/env python3
"""
Script to migrate libraries from the local PostgreSQL database to the container database.
"""
import os
import sys
import logging
import time
from pathlib import Path
from sqlalchemy import create_engine, text, MetaData, Table, select, insert, and_
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Database connection strings
LOCAL_DB_URL = "postgresql://postgres:postgres@localhost:5432/librarypulse"
CONTAINER_DB_URL = "postgresql://postgres:postgres@localhost:5433/librarypulse"

def create_engine_with_retry(db_url, max_retries=5, name="Database"):
    """Create a database engine with retry logic for connection issues."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            engine = create_engine(db_url)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Successfully connected to {name}")
            return engine
        except OperationalError as e:
            retry_count += 1
            wait_time = retry_count * 2
            logger.warning(f"Failed to connect to {name} (attempt {retry_count}/{max_retries}): {e}")
            logger.info(f"Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)
    
    logger.error(f"Failed to connect to {name} after {max_retries} attempts")
    raise ConnectionError(f"Could not connect to {name}")

def get_table_names(engine):
    """Get all table names from database"""
    with engine.connect() as conn:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        return metadata.tables.keys()

def migrate_libraries(local_engine, container_engine, batch_size=100):
    """Migrate libraries data from local database to container database"""
    try:
        # Get table objects
        local_metadata = MetaData()
        local_metadata.reflect(bind=local_engine)
        
        container_metadata = MetaData()
        container_metadata.reflect(bind=container_engine)
        
        # Get tables
        local_libraries = local_metadata.tables.get('libraries')
        local_outlets = local_metadata.tables.get('library_outlets')
        local_datasets = local_metadata.tables.get('pls_datasets')
        local_configs = local_metadata.tables.get('library_config')
        
        container_libraries = container_metadata.tables.get('libraries')
        container_outlets = container_metadata.tables.get('library_outlets')
        container_datasets = container_metadata.tables.get('pls_datasets')
        container_configs = container_metadata.tables.get('library_config')
        
        if not all([local_libraries, local_outlets, local_datasets, local_configs,
                  container_libraries, container_outlets, container_datasets, container_configs]):
            logger.error("Some required tables not found")
            return False
        
        # Create sessions
        local_session = Session(local_engine)
        container_session = Session(container_engine)
        
        # Get dataset years from local database
        local_dataset_years = []
        with local_session.begin():
            local_dataset_result = local_session.execute(
                select(local_datasets.c.year).distinct()
            ).fetchall()
            local_dataset_years = [row[0] for row in local_dataset_result]
        
        logger.info(f"Found datasets for years: {local_dataset_years}")
        
        # Migrate each dataset
        for year in local_dataset_years:
            logger.info(f"Migrating dataset for year {year}")
            
            # Get dataset data
            with local_session.begin():
                dataset_data = local_session.execute(
                    select(local_datasets).where(local_datasets.c.year == year)
                ).fetchone()
                
                if not dataset_data:
                    logger.warning(f"No dataset found for year {year}")
                    continue
                
                # Create dataset in container
                dataset_id = None
                with container_session.begin():
                    # Check if dataset already exists
                    existing_dataset = container_session.execute(
                        select(container_datasets.c.id).where(container_datasets.c.year == year)
                    ).fetchone()
                    
                    if existing_dataset:
                        dataset_id = existing_dataset[0]
                        logger.info(f"Dataset for year {year} already exists with ID {dataset_id}")
                    else:
                        # Create new dataset
                        dataset_dict = {c.name: getattr(dataset_data, c.name) 
                                       for c in local_datasets.columns 
                                       if c.name != 'id'}
                        
                        result = container_session.execute(
                            insert(container_datasets).values(**dataset_dict)
                        )
                        container_session.flush()
                        
                        # Get the new dataset ID
                        new_dataset = container_session.execute(
                            select(container_datasets.c.id).where(container_datasets.c.year == year)
                        ).fetchone()
                        
                        if new_dataset:
                            dataset_id = new_dataset[0]
                            logger.info(f"Created new dataset for year {year} with ID {dataset_id}")
                        else:
                            logger.error(f"Failed to create dataset for year {year}")
                            continue
                
                # Migrate libraries for this dataset
                count = 0
                total_libraries = local_session.execute(
                    select(text("COUNT(*)")).select_from(local_libraries).where(
                        local_libraries.c.dataset_id == dataset_data.id
                    )
                ).scalar()
                
                logger.info(f"Found {total_libraries} libraries to migrate for year {year}")
                
                # Get all libraries for this dataset
                libraries_query = select(local_libraries).where(
                    local_libraries.c.dataset_id == dataset_data.id
                )
                
                for batch_offset in range(0, total_libraries, batch_size):
                    batch_libraries = local_session.execute(
                        libraries_query.limit(batch_size).offset(batch_offset)
                    ).fetchall()
                    
                    for library in batch_libraries:
                        # Check if library already exists in container
                        existing_library = container_session.execute(
                            select(container_libraries.c.id).where(
                                and_(
                                    container_libraries.c.dataset_id == dataset_id,
                                    container_libraries.c.library_id == library.library_id
                                )
                            )
                        ).fetchone()
                        
                        if existing_library:
                            logger.debug(f"Library {library.library_id} already exists for year {year}")
                            continue
                        
                        # Create library dict with updated dataset_id
                        library_dict = {c.name: getattr(library, c.name) 
                                      for c in local_libraries.columns 
                                      if c.name not in ['id', 'dataset_id']}
                        library_dict['dataset_id'] = dataset_id
                        
                        # Insert library
                        try:
                            with container_session.begin_nested():
                                container_session.execute(
                                    insert(container_libraries).values(**library_dict)
                                )
                                count += 1
                        except SQLAlchemyError as e:
                            logger.error(f"Error inserting library {library.library_id}: {e}")
                            continue
                        
                        # Get outlets for this library
                        outlets = local_session.execute(
                            select(local_outlets).where(
                                and_(
                                    local_outlets.c.library_id == library.library_id,
                                    local_outlets.c.dataset_id == dataset_data.id
                                )
                            )
                        ).fetchall()
                        
                        for outlet in outlets:
                            # Create outlet dict with updated dataset_id
                            outlet_dict = {c.name: getattr(outlet, c.name) 
                                         for c in local_outlets.columns 
                                         if c.name not in ['id', 'dataset_id']}
                            outlet_dict['dataset_id'] = dataset_id
                            
                            # Insert outlet
                            try:
                                with container_session.begin_nested():
                                    container_session.execute(
                                        insert(container_outlets).values(**outlet_dict)
                                    )
                            except SQLAlchemyError as e:
                                logger.error(f"Error inserting outlet {outlet.outlet_id} for library {library.library_id}: {e}")
                    
                    # Commit batch
                    container_session.commit()
                    logger.info(f"Migrated batch of libraries: {batch_offset+len(batch_libraries)}/{total_libraries}")
                
                # Migrate library configs
                configs = local_session.execute(
                    select(local_configs).where(
                        local_configs.c.library_id.in_(
                            select(local_libraries.c.library_id).where(
                                local_libraries.c.dataset_id == dataset_data.id
                            )
                        )
                    )
                ).fetchall()
                
                config_count = 0
                for config in configs:
                    # Check if config already exists
                    existing_config = container_session.execute(
                        select(container_configs.c.id).where(
                            container_configs.c.library_id == config.library_id
                        )
                    ).fetchone()
                    
                    if existing_config:
                        logger.debug(f"Config for library {config.library_id} already exists")
                        continue
                    
                    # Create config dict
                    config_dict = {c.name: getattr(config, c.name) 
                                  for c in local_configs.columns 
                                  if c.name != 'id'}
                    
                    # Insert config
                    try:
                        with container_session.begin_nested():
                            container_session.execute(
                                insert(container_configs).values(**config_dict)
                            )
                            config_count += 1
                    except SQLAlchemyError as e:
                        logger.error(f"Error inserting config for library {config.library_id}: {e}")
                
                logger.info(f"Migrated {config_count} library configurations")
                logger.info(f"Successfully migrated {count} libraries for year {year}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False

def main():
    """Main function"""
    try:
        logger.info("Starting migration of libraries from local database to container database")
        logger.info(f"Using local database: {LOCAL_DB_URL}")
        logger.info(f"Using container database: {CONTAINER_DB_URL}")
        
        # Create database connections
        local_engine = create_engine_with_retry(LOCAL_DB_URL, name="Local Database")
        container_engine = create_engine_with_retry(CONTAINER_DB_URL, name="Container Database")
        
        # Verify tables exist
        local_tables = get_table_names(local_engine)
        container_tables = get_table_names(container_engine)
        
        logger.info(f"Local database tables: {', '.join(local_tables)}")
        logger.info(f"Container database tables: {', '.join(container_tables)}")
        
        required_tables = ['libraries', 'library_outlets', 'pls_datasets', 'library_config']
        
        # Check if required tables exist in both databases
        missing_local = [table for table in required_tables if table not in local_tables]
        missing_container = [table for table in required_tables if table not in container_tables]
        
        if missing_local:
            logger.error(f"Missing required tables in local database: {', '.join(missing_local)}")
            return False
        
        if missing_container:
            logger.error(f"Missing required tables in container database: {', '.join(missing_container)}")
            return False
        
        # Perform migration
        success = migrate_libraries(local_engine, container_engine)
        
        if success:
            logger.info("Migration completed successfully")
            return True
        else:
            logger.error("Migration failed")
            return False
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate libraries from local database to container database")
    parser.add_argument("--local-db", type=str, help="Local database URL",
                        default=LOCAL_DB_URL)
    parser.add_argument("--container-db", type=str, help="Container database URL",
                        default=CONTAINER_DB_URL)
    parser.add_argument("--batch-size", type=int, default=50,
                        help="Number of libraries to migrate in a single batch")
    
    args = parser.parse_args()
    
    if args.local_db != LOCAL_DB_URL:
        LOCAL_DB_URL = args.local_db
    
    if args.container_db != CONTAINER_DB_URL:
        CONTAINER_DB_URL = args.container_db
    
    success = main()
    sys.exit(0 if success else 1) 