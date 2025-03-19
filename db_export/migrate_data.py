#!/usr/bin/env python3
"""
Script to migrate data from a local database to the container database.
"""
import os
import sys
import logging
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text, MetaData, Table, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Database connection variables
DEFAULT_LOCAL_DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/librarypulse")
LOCAL_DB_URL = input(f"Enter your local database URL (default: {DEFAULT_LOCAL_DB_URL}): ") or DEFAULT_LOCAL_DB_URL
CONTAINER_DB_URL = "postgresql://postgres:postgres@localhost:5433/librarypulse"  # Container DB exposed on port 5433

logger.info(f"Using local database: {LOCAL_DB_URL}")
logger.info(f"Using container database: {CONTAINER_DB_URL}")

print("\nThis script will migrate data from your local database to the container database.")
print("Make sure both databases are running before proceeding.")
confirmation = input("Do you want to continue? (y/n): ")
if confirmation.lower() != "y":
    print("Migration cancelled.")
    sys.exit(0)

def create_engine_with_retry(db_url, max_retries=3, name="Database"):
    """Create a database engine with retry logic."""
    for attempt in range(max_retries):
        try:
            logger.info(f"Connecting to {name}...")
            engine = create_engine(db_url)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Successfully connected to {name}")
            return engine
        except SQLAlchemyError as e:
            logger.error(f"{name} connection attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
    
    raise Exception(f"Failed to connect to {name} after multiple attempts")

def get_tables(engine):
    """Get a list of all tables in the database."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return tables
    except SQLAlchemyError as e:
        logger.error(f"Error getting tables: {e}")
        return []

def migrate_table(local_engine, container_engine, table_name, batch_size=1000):
    """Migrate data from a table in the local database to the container database."""
    try:
        # Check if table exists in container database
        container_tables = get_tables(container_engine)
        if table_name not in container_tables:
            logger.warning(f"Table {table_name} does not exist in container database. Skipping.")
            return False
        
        # Get total count
        with local_engine.connect() as conn:
            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            total_count = count_result.scalar()
        
        logger.info(f"Migrating {total_count} records from table {table_name}")
        
        # Migrate in batches
        for offset in range(0, total_count, batch_size):
            logger.info(f"Processing batch {offset//batch_size + 1} of {(total_count + batch_size - 1)//batch_size} for table {table_name}")
            
            # Read batch from local database
            query = f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
            df = pd.read_sql(query, local_engine)
            
            if df.empty:
                logger.info(f"No more data to migrate for table {table_name}")
                break
            
            # Insert into container database
            df.to_sql(table_name, container_engine, if_exists='append', index=False)
        
        logger.info(f"Successfully migrated {total_count} records from table {table_name}")
        return True
    
    except Exception as e:
        logger.error(f"Error migrating table {table_name}: {e}")
        return False

def main():
    """Main function to migrate data from local database to container database."""
    try:
        # Connect to databases
        local_engine = create_engine_with_retry(LOCAL_DB_URL, name="Local Database")
        container_engine = create_engine_with_retry(CONTAINER_DB_URL, name="Container Database")
        
        # Get tables from local database
        local_tables = get_tables(local_engine)
        logger.info(f"Found {len(local_tables)} tables in local database:")
        for i, table in enumerate(local_tables, 1):
            logger.info(f"{i}. {table}")
        
        # Ask user which tables to migrate
        print("\nWhich tables would you like to migrate?")
        print("0. All tables")
        for i, table in enumerate(local_tables, 1):
            print(f"{i}. {table}")
        
        choice = input("\nEnter your choice (comma-separated for multiple tables): ")
        
        tables_to_migrate = []
        if choice == "0":
            tables_to_migrate = local_tables
        else:
            choices = [int(c.strip()) for c in choice.split(",")]
            tables_to_migrate = [local_tables[i-1] for i in choices if 1 <= i <= len(local_tables)]
        
        logger.info(f"Will migrate the following tables: {', '.join(tables_to_migrate)}")
        
        # Confirm
        confirm = input(f"Are you sure you want to migrate {len(tables_to_migrate)} tables? (y/n): ")
        if confirm.lower() != "y":
            logger.info("Migration cancelled by user.")
            return
        
        # Migrate tables
        success_count = 0
        for table in tables_to_migrate:
            if migrate_table(local_engine, container_engine, table):
                success_count += 1
        
        logger.info(f"Migration completed. Successfully migrated {success_count} out of {len(tables_to_migrate)} tables.")
    
    except Exception as e:
        logger.error(f"Error during migration process: {e}")

if __name__ == "__main__":
    main() 