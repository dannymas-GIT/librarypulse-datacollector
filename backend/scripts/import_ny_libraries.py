import pandas as pd
from app.db.session import SessionLocal
from app.models.pls_data import PLSDataset, Library
from sqlalchemy.exc import SQLAlchemyError

def main():
    # Connect to database
    db = SessionLocal()

    # Get the dataset
    dataset = db.query(PLSDataset).filter(PLSDataset.year == 2021).first()
    if not dataset:
        print('Dataset for 2021 not found')
        exit(1)

    # Read the CSV file
    print('Reading CSV file...')
    df = pd.read_csv('/app/data/2021/pls_2021_library.csv', encoding='latin1', low_memory=False)

    # Filter for Suffolk County libraries
    print('Filtering for Suffolk County libraries...')
    df_suffolk = df[(df['stabr'] == 'NY') & (df['county'].str.contains('SUFFOLK', case=False, na=False))]
    print(f'Found {len(df_suffolk)} Suffolk County libraries')

    # Add libraries to database
    libraries_added = 0
    for _, row in df_suffolk.iterrows():
        try:
            library = Library(
                dataset_id=dataset.id,
                library_id=row['fscskey'],
                name=row['libname'],
                address=row.get('address', ''),
                city=row.get('city', ''),
                state='NY',
                zip_code=str(row.get('zip', '')),
                county=row.get('county', ''),
                phone=str(row.get('phone', '')),
                central_library_count=row.get('centlib', 0),
                branch_library_count=row.get('branlib', 0),
                bookmobile_count=row.get('bkmob', 0),
                service_area_population=row.get('popu_lsa', 0),
                total_staff=row.get('totstaff', 0),
                librarian_staff=row.get('libraria', 0),
                total_circulation=row.get('totcir', 0),
                visits=row.get('visits', 0),
                reference_transactions=row.get('referenc', 0),
                total_operating_revenue=row.get('totincm', 0),
                total_operating_expenditures=row.get('totexpco', 0)
            )
            db.add(library)
            libraries_added += 1
            if libraries_added % 5 == 0:
                db.commit()
                print(f'Committed {libraries_added} libraries')
        except Exception as e:
            print(f'Error adding library {row.get("libname")}: {str(e)}')

    # Commit any remaining libraries
    db.commit()

    # Update dataset
    dataset.record_count = libraries_added
    dataset.status = 'complete'
    db.commit()

    print(f'Successfully imported {libraries_added} Suffolk County libraries')

if __name__ == "__main__":
    main() 