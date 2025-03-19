#!/usr/bin/env python3
"""
Simplified script to migrate libraries from local PostgreSQL to container database.
"""
import os
import sys
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "database": "librarypulse",
    "user": "postgres",
    "password": "postgres"
}

CONTAINER_DB = {
    "host": "localhost",
    "port": 5433,
    "database": "librarypulse",
    "user": "postgres",
    "password": "postgres"
}

# Fields to exclude when migrating libraries
EXCLUDE_LIBRARY_FIELDS = {'id', 'county_id', 'fscs_id', 'county_name', 'latitude', 'longitude', 'year'}

# Field name mappings for library_outlets
OUTLET_FIELD_MAPPINGS = {
    'type': 'outlet_type',
    'hours': 'hours_open',
    'square_feet': 'square_footage'
}

# Valid fields for library_outlets in container database
VALID_OUTLET_FIELDS = {
    'dataset_id', 'library_id', 'outlet_id', 'name', 'outlet_type', 'address', 'city', 'state',
    'zip_code', 'county', 'phone', 'latitude', 'longitude', 'metro_status', 'hours_open',
    'weeks_open', 'square_footage', 'created_at', 'updated_at'
}

# Valid fields for library_config in container database
VALID_CONFIG_FIELDS = {
    'library_id', 'library_name', 'setup_complete', 'collection_stats_enabled', 'usage_stats_enabled',
    'program_stats_enabled', 'staff_stats_enabled', 'financial_stats_enabled', 'collection_metrics',
    'usage_metrics', 'program_metrics', 'staff_metrics', 'financial_metrics', 'auto_update_enabled',
    'last_update_check', 'created_at', 'updated_at'
}

def truncate_string(value, max_length):
    """Truncate string to max_length if needed"""
    if value and isinstance(value, str) and len(value) > max_length:
        return value[:max_length]
    return value

def migrate_data():
    try:
        # Connect to both databases
        local_conn = psycopg2.connect(**LOCAL_DB)
        container_conn = psycopg2.connect(**CONTAINER_DB)
        
        local_cur = local_conn.cursor(cursor_factory=RealDictCursor)
        container_cur = container_conn.cursor()
        
        # First, get all datasets from local database
        local_cur.execute("SELECT * FROM pls_datasets ORDER BY year")
        datasets = local_cur.fetchall()
        
        # Create a mapping of local dataset IDs to container dataset IDs
        dataset_id_map = {}
        now = datetime.now(timezone.utc)
        
        for dataset in datasets:
            # Check if dataset exists in container
            container_cur.execute(
                "SELECT id FROM pls_datasets WHERE year = %s",
                (dataset['year'],)
            )
            result = container_cur.fetchone()
            
            if result:
                dataset_id_map[dataset['id']] = result[0]
            else:
                # Create new dataset
                columns = ['year', 'status', 'record_count', 'notes', 'created_at', 'updated_at']
                values = [
                    dataset['year'],
                    dataset.get('status', 'complete'),  # Default to 'complete' if not set
                    dataset.get('record_count', 0),     # Default to 0 if not set
                    dataset.get('notes', ''),           # Default to empty string if not set
                    now,
                    now
                ]
                
                container_cur.execute(
                    f"INSERT INTO pls_datasets ({','.join(columns)}) VALUES ({','.join(['%s']*len(columns))}) RETURNING id",
                    values
                )
                new_dataset_id = container_cur.fetchone()[0]
                dataset_id_map[dataset['id']] = new_dataset_id
                container_conn.commit()
                logger.info(f"Created dataset for year {dataset['year']} with ID {new_dataset_id}")
        
        # Get total library count
        local_cur.execute("SELECT COUNT(*) FROM libraries")
        total_libraries = local_cur.fetchone()['count']
        logger.info(f"Found {total_libraries} libraries to migrate")
        
        # Get all libraries
        local_cur.execute("""
            SELECT l.*, d.year 
            FROM libraries l 
            JOIN pls_datasets d ON l.dataset_id = d.id 
            ORDER BY d.year, l.library_id
        """)
        libraries = local_cur.fetchall()
        
        current_year = None
        library_count = 0
        outlet_count = 0
        
        for library in libraries:
            if current_year != library['year']:
                if current_year is not None:
                    logger.info(f"Year {current_year}: Migrated {library_count} libraries and {outlet_count} outlets")
                current_year = library['year']
                library_count = 0
                outlet_count = 0
            
            # Map the dataset ID
            new_dataset_id = dataset_id_map[library['dataset_id']]
            
            # Check if library already exists
            container_cur.execute(
                "SELECT id FROM libraries WHERE library_id = %s AND dataset_id = %s",
                (truncate_string(library['library_id'], 20), new_dataset_id)
            )
            
            if not container_cur.fetchone():
                # Insert library
                columns = [k for k in library.keys() if k not in EXCLUDE_LIBRARY_FIELDS]
                values = []
                
                for col in columns:
                    val = library[col]
                    if col == 'dataset_id':
                        val = new_dataset_id
                    elif col == 'library_id':
                        val = truncate_string(val, 20)
                    elif col == 'zip_code':
                        val = truncate_string(val, 10)
                    values.append(val)
                
                # Update timestamps
                if 'created_at' in columns:
                    idx = columns.index('created_at')
                    values[idx] = now
                if 'updated_at' in columns:
                    idx = columns.index('updated_at')
                    values[idx] = now
                
                try:
                    container_cur.execute(
                        f"INSERT INTO libraries ({','.join(columns)}) VALUES ({','.join(['%s']*len(values))})",
                        values
                    )
                    library_count += 1
                    
                    # Get and insert outlets
                    local_cur.execute(
                        "SELECT * FROM library_outlets WHERE library_id = %s AND dataset_id = %s",
                        (library['library_id'], library['dataset_id'])
                    )
                    outlets = local_cur.fetchall()
                    
                    for outlet in outlets:
                        # Map field names and prepare values
                        outlet_data = {}
                        for k, v in outlet.items():
                            if k == 'id':
                                continue
                            
                            # Map the field name if needed
                            mapped_key = OUTLET_FIELD_MAPPINGS.get(k, k)
                            
                            # Only include fields that exist in the container database
                            if mapped_key not in VALID_OUTLET_FIELDS:
                                continue
                            
                            if mapped_key == 'dataset_id':
                                outlet_data[mapped_key] = new_dataset_id
                            elif mapped_key == 'library_id':
                                outlet_data[mapped_key] = truncate_string(v, 20)
                            elif mapped_key == 'outlet_id':
                                outlet_data[mapped_key] = truncate_string(v, 20)
                            elif mapped_key == 'zip_code':
                                outlet_data[mapped_key] = truncate_string(v, 10)
                            else:
                                outlet_data[mapped_key] = v
                        
                        # Add timestamps
                        outlet_data['created_at'] = now
                        outlet_data['updated_at'] = now
                        
                        columns = list(outlet_data.keys())
                        values = [outlet_data[k] for k in columns]
                        
                        try:
                            container_cur.execute(
                                f"INSERT INTO library_outlets ({','.join(columns)}) VALUES ({','.join(['%s']*len(values))})",
                                values
                            )
                            outlet_count += 1
                        except Exception as e:
                            logger.warning(f"Error inserting outlet for library {library['library_id']}: {e}")
                            continue
                    
                    # Get and insert config if not exists
                    container_cur.execute(
                        "SELECT id FROM library_config WHERE library_id = %s",
                        (truncate_string(library['library_id'], 20),)
                    )
                    
                    if not container_cur.fetchone():
                        local_cur.execute(
                            "SELECT * FROM library_config WHERE library_id = %s",
                            (library['library_id'],)
                        )
                        config = local_cur.fetchone()
                        
                        if config:
                            # Create config data with default values
                            config_data = {
                                'library_id': truncate_string(config['library_id'], 20),
                                'library_name': config['library_name'],
                                'setup_complete': config.get('setup_complete', False),
                                'collection_stats_enabled': config.get('collection_stats_enabled', True),
                                'usage_stats_enabled': config.get('usage_stats_enabled', True),
                                'program_stats_enabled': config.get('program_stats_enabled', True),
                                'staff_stats_enabled': config.get('staff_stats_enabled', True),
                                'financial_stats_enabled': config.get('financial_stats_enabled', True),
                                'collection_metrics': config.get('collection_metrics', {}),
                                'usage_metrics': config.get('usage_metrics', {}),
                                'program_metrics': config.get('program_metrics', {}),
                                'staff_metrics': config.get('staff_metrics', {}),
                                'financial_metrics': config.get('financial_metrics', {}),
                                'auto_update_enabled': config.get('auto_update_enabled', False),
                                'last_update_check': config.get('last_update_check', None),
                                'created_at': now,
                                'updated_at': now
                            }
                            
                            columns = list(config_data.keys())
                            values = [config_data[k] for k in columns]
                            
                            try:
                                container_cur.execute(
                                    f"INSERT INTO library_config ({','.join(columns)}) VALUES ({','.join(['%s']*len(values))})",
                                    values
                                )
                            except Exception as e:
                                logger.warning(f"Error inserting config for library {library['library_id']}: {e}")
                except Exception as e:
                    logger.warning(f"Error inserting library {library['library_id']}: {e}")
                    continue
            
            # Commit every 10 libraries
            if library_count % 10 == 0 and library_count > 0:
                container_conn.commit()
                logger.info(f"Progress: {library_count}/{total_libraries} libraries migrated")
        
        # Final commit
        container_conn.commit()
        logger.info(f"Year {current_year}: Migrated {library_count} libraries and {outlet_count} outlets")
        logger.info("Migration completed successfully")
        
        local_cur.close()
        container_cur.close()
        local_conn.close()
        container_conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        if 'container_conn' in locals():
            container_conn.rollback()
        return False

if __name__ == "__main__":
    success = migrate_data()
    sys.exit(0 if success else 1) 