import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.pls_data import PLSDataset, Library

def main():
    # Create engine and session
    engine = create_engine(str(settings.DATABASE_URL))
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    
    # Check if we have a dataset
    dataset = db.query(PLSDataset).filter(PLSDataset.year == 2021).first()
    if not dataset:
        # Create a new dataset for 2021
        dataset = PLSDataset(
            year=2021,
            status="complete",
            record_count=0,
            notes="Suffolk County Libraries"
        )
        db.add(dataset)
        db.commit()
        print(f"Created dataset for year 2021 with ID {dataset.id}")
    
    # Check if we already have libraries
    library_count = db.query(Library).count()
    print(f"Current library count: {library_count}")
    
    if library_count == 0:
        # Check possible paths for Suffolk libraries data
        csv_paths = [
            "/app/extracted_data/PLS_FY2021 PUD_CSV/PLS_FY21_AE_pud21i.csv",
            "/app/data/suffolk_libraries.csv",
            "/app/extracted_data/suffolk_libraries.csv"
        ]
        
        csv_path = None
        for path in csv_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if not csv_path:
            print("Could not find Suffolk libraries data file")
            return
        
        print(f"Loading library data from {csv_path}")
        try:
            # Read the CSV file
            df = pd.read_csv(csv_path)
            
            # Filter for Suffolk County, NY libraries only
            if 'CNTY' in df.columns and 'STABR' in df.columns:
                suffolk_df = df[(df['CNTY'].str.contains('SUFFOLK', case=False, na=False)) & 
                                (df['STABR'] == 'NY')]
                print(f"Found {len(suffolk_df)} Suffolk County, NY libraries")
            else:
                print("CSV does not have the expected columns. Using all data.")
                suffolk_df = df
            
            # Import libraries
            for _, row in suffolk_df.iterrows():
                library = Library(
                    dataset_id=dataset.id,
                    library_id=str(row.get('FSCSKEY', '')),
                    name=str(row.get('LIBNAME', '')),
                    city=str(row.get('CITY', '')),
                    state=str(row.get('STABR', '')),
                    zip_code=str(row.get('ZIP', '')),
                    county='Suffolk'
                )
                db.add(library)
            
            db.commit()
            print(f"Imported {len(suffolk_df)} Suffolk County libraries")
        except Exception as e:
            print(f"Error importing libraries: {e}")
            db.rollback()
    else:
        print("Libraries already exist in the database")
    
    # Close the session
    db.close()
    print("Done!")

if __name__ == "__main__":
    main() 