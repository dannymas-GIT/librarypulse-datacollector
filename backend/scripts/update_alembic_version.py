#!/usr/bin/env python
"""
Script to update the Alembic version in the database.
"""
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

def main():
    """Update the Alembic version in the database."""
    try:
        # Create engine - convert PostgresDsn to string
        db_url = str(settings.DATABASE_URL)
        engine = create_engine(db_url)
        
        # Update the version
        with engine.connect() as conn:
            conn.execute(text("UPDATE alembic_version SET version_num = '002_add_demographic_data_models' WHERE version_num = '9f8a7b6c5d4e'"))
            conn.commit()
            
        print("Successfully updated Alembic version")
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 