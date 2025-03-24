from app.services.collector import PLSDataCollector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def main():
    # Create engine and session
    engine = create_engine(str(settings.DATABASE_URL))
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    
    # Create collector
    collector = PLSDataCollector(db)
    
    # Check available years
    available_years = collector.discover_available_years()
    print(f"Available years: {available_years}")
    
    # Update with latest data
    print("Updating with latest data...")
    collector.update_with_latest_data()
    
    # Close the session
    db.close()
    print("Done!")

if __name__ == "__main__":
    main() 