import pandas as pd
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Direct database connection without ORM
DB_URL = "postgresql://postgres:postgres@db:5432/librarypulse"
engine = create_engine(DB_URL)

# First create dataset record if it doesn't exist
with engine.connect() as conn:
    # Check if dataset exists
    result = conn.execute(text("SELECT id FROM pls_datasets WHERE year = 2021"))
    dataset_id = result.scalar()
    
    if not dataset_id:
        # Create dataset
        result = conn.execute(
            text("INSERT INTO pls_datasets (year, status, notes, created_at, updated_at) "
            "VALUES (2021, 'processing', 'Suffolk County Libraries', NOW(), NOW()) "
            "RETURNING id")
        )
        dataset_id = result.scalar()
        print(f"Created dataset with ID: {dataset_id}")
    else:
        print(f"Using existing dataset with ID: {dataset_id}")
        
    # Read CSV file
    print('Reading CSV file...')
    df = pd.read_csv('/app/data/2021/pls_2021_library.csv', encoding='latin1', low_memory=False)
    
    # Filter for Suffolk County libraries
    print('Filtering for Suffolk County libraries...')
    # The actual county column is 'CNTY' not 'county'
    suffolk_mask = df['CNTY'].str.contains('SUFFOLK', case=False, na=False) & (df['STABR'] == 'NY')
    df_suffolk = df[suffolk_mask]
    print(f'Found {len(df_suffolk)} Suffolk County libraries in CSV')
    
    if len(df_suffolk) == 0:
        print("No Suffolk County libraries found in the CSV file")
        exit(1)
    
    # Add libraries to database
    libraries_added = 0
    for _, row in df_suffolk.iterrows():
        try:
            # Check if library already exists
            check = conn.execute(
                text("SELECT id FROM libraries WHERE dataset_id = :dataset_id AND library_id = :library_id"),
                {"dataset_id": dataset_id, "library_id": row['FSCSKEY']}
            )
            if check.scalar():
                print(f"Library {row['LIBNAME']} already exists, skipping")
                continue
                
            # Insert library
            conn.execute(
                text("""
                INSERT INTO libraries (
                    dataset_id, library_id, name, address, city, state, 
                    zip_code, county, phone, central_library_count,
                    branch_library_count, bookmobile_count, service_area_population,
                    total_staff, librarian_staff, total_circulation,
                    visits, reference_transactions, total_operating_revenue,
                    total_operating_expenditures, created_at, updated_at
                ) VALUES (
                    :dataset_id, :library_id, :name, :address, :city, :state, 
                    :zip_code, :county, :phone, :central_library_count,
                    :branch_library_count, :bookmobile_count, :service_area_population,
                    :total_staff, :librarian_staff, :total_circulation,
                    :visits, :reference_transactions, :total_operating_revenue,
                    :total_operating_expenditures, :created_at, :updated_at
                )
                """),
                {
                    "dataset_id": dataset_id, 
                    "library_id": row['FSCSKEY'], 
                    "name": row['LIBNAME'], 
                    "address": row.get('ADDRESS', ''), 
                    "city": row.get('CITY', ''), 
                    "state": 'NY',
                    "zip_code": str(row.get('ZIP', '')), 
                    "county": row.get('CNTY', ''), 
                    "phone": str(row.get('PHONE', '')),
                    "central_library_count": row.get('CENTLIB', 0), 
                    "branch_library_count": row.get('BRANLIB', 0), 
                    "bookmobile_count": row.get('BKMOB', 0),
                    "service_area_population": row.get('POPU_LSA', 0), 
                    "total_staff": row.get('TOTSTAFF', 0), 
                    "librarian_staff": row.get('LIBRARIA', 0),
                    "total_circulation": row.get('TOTCIR', 0), 
                    "visits": row.get('VISITS', 0), 
                    "reference_transactions": row.get('REFERENC', 0),
                    "total_operating_revenue": row.get('TOTINCM', 0), 
                    "total_operating_expenditures": row.get('TOTEXPCO', 0),
                    "created_at": datetime.now(), 
                    "updated_at": datetime.now()
                }
            )
            libraries_added += 1
            print(f"Added library: {row['LIBNAME']}")
        except Exception as e:
            print(f"Error adding library {row.get('LIBNAME')}: {str(e)}")
    
    # Update dataset status
    if libraries_added > 0:
        conn.execute(
            text("UPDATE pls_datasets SET status = 'complete', record_count = :record_count, updated_at = NOW() WHERE id = :dataset_id"),
            {"record_count": libraries_added, "dataset_id": dataset_id}
        )
    
    print(f'Successfully imported {libraries_added} Suffolk County libraries') 