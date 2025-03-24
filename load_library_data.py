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
            notes="Imported from CSV file"
        )
        db.add(dataset)
        db.commit()
        print(f"Created dataset for year 2021 with ID {dataset.id}")
    
    # Check if we already have libraries
    library_count = db.query(Library).count()
    print(f"Current library count: {library_count}")
    
    if library_count == 0:
        # Load the CSV file
        csv_path = "/app/data_2021_library.csv"
        if not os.path.exists(csv_path):
            print(f"CSV file not found at {csv_path}")
            csv_path = "/app/extracted_data/data_2021_library.csv"
            if not os.path.exists(csv_path):
                print(f"CSV file not found at {csv_path}")
                return
        
        print(f"Loading library data from {csv_path}")
        try:
            df = pd.read_csv(csv_path)
            print(f"Loaded {len(df)} libraries from CSV")
            
            # Import libraries
            for _, row in df.iterrows():
                library = Library(
                    dataset_id=dataset.id,
                    library_id=str(row.get('FSCSKEY', '')),
                    name=str(row.get('LIBNAME', '')),
                    city=str(row.get('CITY', '')),
                    state=str(row.get('STABR', '')),
                    zip_code=str(row.get('ZIP', '')),
                    county=str(row.get('CNTY', ''))
                )
                db.add(library)
            
            db.commit()
            print(f"Imported {len(df)} libraries")
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