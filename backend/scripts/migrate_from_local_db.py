#!/usr/bin/env python3
"""
Script to migrate data from a local PostgreSQL database to the container database.
"""
import sys
import logging
import argparse
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.sql import select
from sqlalchemy.dialects.postgresql import insert
from pathlib import Path
from dotenv import load_dotenv
import os

# Add the parent directory to the path so we can import the app modules
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.append(str(backend_dir))

# Load environment variables
load_dotenv(backend_dir / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Migrate data from local PostgreSQL database to container database')
    parser.add_argument('--local-url', type=str, help='Local database URL (source)')
    parser.add_argument('--container-url', type=str, default=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/librarypulse"),
                        help='Container database URL (destination)')
    parser.add_argument('--tables', type=str, nargs='+', help='Tables to migrate (default: all)')
    parser.add_argument('--batch-size', type=int, default=1000, help='Number of rows to process in a batch')
    parser.add_argument('--exclude-tables', type=str, nargs='+', default=['alembic_version'],
                        help='Tables to exclude from migration')
    parser.add_argument('--skip-constraints', action='store_true', help='Skip foreign key constraints during import')
    return parser.parse_args()

def connect_to_database(db_url, purpose="source"):
    """Connect to a database and return engine and metadata."""
    try:
        logger.info(f"Connecting to {purpose} database at {db_url}")
        engine = create_engine(db_url)
        metadata = MetaData()
        metadata.reflect(bind=engine)
        return engine, metadata
    except Exception as e:
        logger.error(f"Error connecting to {purpose} database: {e}")
        sys.exit(1)

def get_tables_to_migrate(source_metadata, target_engine, include_tables=None, exclude_tables=None):
    """Get tables to migrate, ensuring they exist in both source and target."""
    if exclude_tables is None:
        exclude_tables = ['alembic_version']
    
    # Get list of tables in the source database
    source_tables = source_metadata.tables
    
    # Filter tables if include_tables is specified
    if include_tables:
        source_tables = {name: table for name, table in source_tables.items() if name in include_tables}
    
    # Exclude specified tables
    source_tables = {name: table for name, table in source_tables.items() if name not in exclude_tables}
    
    # Check target database for table existence
    inspector = inspect(target_engine)
    target_table_names = inspector.get_table_names()
    
    # Filter source tables to only include those that exist in target
    tables_to_migrate = {}
    for name, table in source_tables.items():
        if name in target_table_names:
            tables_to_migrate[name] = table
        else:
            logger.warning(f"Table '{name}' exists in source but not in target database, skipping")
    
    return tables_to_migrate

def count_rows(engine, table_name):
    """Count the number of rows in a table."""
    try:
        with engine.connect() as conn:
            result = conn.execute(select([Table(table_name, MetaData(), autoload_with=engine).count()]))
            return result.scalar()
    except Exception as e:
        logger.error(f"Error counting rows in {table_name}: {e}")
        return 0

def migrate_table(source_engine, target_engine, table_name, source_table, batch_size=1000, skip_constraints=False):
    """Migrate data from source table to target table."""
    source_row_count = count_rows(source_engine, table_name)
    target_row_count = count_rows(target_engine, table_name)
    
    logger.info(f"Table {table_name}: {source_row_count} rows in source, {target_row_count} rows in target")
    
    if source_row_count == 0:
        logger.info(f"No rows in source table {table_name}, skipping")
        return 0
    
    # If target already has data and the same number of rows, skip migration
    if target_row_count > 0 and target_row_count >= source_row_count:
        logger.info(f"Target table {table_name} already has the same or more rows than source, skipping")
        return 0
    
    # Reflect target table
    target_meta = MetaData(bind=target_engine)
    target_table = Table(table_name, target_meta, autoload=True)
    
    # Get column names that exist in both source and target
    source_columns = [c.name for c in source_table.columns]
    target_columns = [c.name for c in target_table.columns]
    common_columns = [c for c in source_columns if c in target_columns]
    
    if not common_columns:
        logger.warning(f"No common columns between source and target for table {table_name}, skipping")
        return 0
    
    # Column subset for SELECT
    select_columns = [source_table.c[col] for col in common_columns]
    
    rows_migrated = 0
    offset = 0
    
    # Temporarily disable foreign key constraints if requested
    if skip_constraints:
        with target_engine.connect() as conn:
            conn.execute("SET CONSTRAINTS ALL DEFERRED")
    
    # Process in batches
    while True:
        try:
            # Select batch of rows from source
            with source_engine.connect() as source_conn:
                query = select(select_columns).offset(offset).limit(batch_size)
                result = source_conn.execute(query)
                rows = [dict(zip(common_columns, row)) for row in result]
            
            if not rows:
                break
            
            # Insert into target
            with target_engine.connect() as target_conn:
                # Using PostgreSQL's INSERT ON CONFLICT DO NOTHING
                stmt = insert(target_table).values(rows)
                stmt = stmt.on_conflict_do_nothing()
                result = target_conn.execute(stmt)
                target_conn.commit()
            
            batch_count = len(rows)
            rows_migrated += batch_count
            offset += batch_count
            
            logger.info(f"Migrated {rows_migrated}/{source_row_count} rows for table {table_name}")
            
            if batch_count < batch_size:
                break
                
        except Exception as e:
            logger.error(f"Error migrating batch for table {table_name}: {e}")
            if skip_constraints:
                with target_engine.connect() as conn:
                    conn.execute("SET CONSTRAINTS ALL IMMEDIATE")
            return rows_migrated
    
    # Re-enable constraints if they were disabled
    if skip_constraints:
        with target_engine.connect() as conn:
            conn.execute("SET CONSTRAINTS ALL IMMEDIATE")
    
    return rows_migrated

def main():
    """Main function for database migration."""
    args = parse_args()
    
    if not args.local_url:
        logger.error("Local database URL is required. Use --local-url to specify it.")
        sys.exit(1)
    
    # Connect to source and target databases
    source_engine, source_metadata = connect_to_database(args.local_url, "source")
    target_engine, _ = connect_to_database(args.container_url, "target")
    
    # Get tables to migrate
    tables_to_migrate = get_tables_to_migrate(
        source_metadata, 
        target_engine,
        include_tables=args.tables,
        exclude_tables=args.exclude_tables
    )
    
    if not tables_to_migrate:
        logger.error("No tables to migrate. Check that tables exist in both source and target databases.")
        sys.exit(1)
    
    logger.info(f"Found {len(tables_to_migrate)} tables to migrate: {', '.join(tables_to_migrate.keys())}")
    
    # Migrate each table
    total_rows_migrated = 0
    for name, table in tables_to_migrate.items():
        logger.info(f"Migrating table: {name}")
        rows_migrated = migrate_table(
            source_engine, 
            target_engine, 
            name, 
            table, 
            batch_size=args.batch_size,
            skip_constraints=args.skip_constraints
        )
        total_rows_migrated += rows_migrated
        logger.info(f"Completed migration for table {name}: {rows_migrated} rows")
    
    logger.info(f"Migration completed. Total rows migrated: {total_rows_migrated}")

if __name__ == "__main__":
    main() 