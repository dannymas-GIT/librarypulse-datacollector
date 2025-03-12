#!/usr/bin/env python3
import sys
import os

# Add backend to the path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

# Import models directly
from api.demographics import DemographicDataset, PopulationData, EconomicData, EducationData, HousingData

# Database connection
DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/librarypulse'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Get datasets and check for population data
    print('\nDatasets in database:')
    datasets = db.query(DemographicDataset).all()
    for ds in datasets:
        print(f'ID: {ds.id}, Source: {ds.source}, Year: {ds.year}, Status: {ds.status}')
        
        # Check for West Babylon population data
        pop_west_babylon = db.query(PopulationData).filter(
            and_(
                PopulationData.dataset_id == ds.id,
                PopulationData.geographic_id == "11704"
            )
        ).first()
        
        if pop_west_babylon:
            print(f'  FOUND West Babylon data for dataset {ds.id}')
            print(f'    Geographic ID: {pop_west_babylon.geographic_id}')
            print(f'    City: {pop_west_babylon.city}')
            print(f'    Total Population: {pop_west_babylon.total_population}')
        else:
            print(f'  NO West Babylon data for dataset {ds.id}')
        
        # Check all population records
        pop_records = db.query(PopulationData).filter(PopulationData.dataset_id == ds.id).all()
        print(f'  All population records for dataset {ds.id}: {len(pop_records)}')
        for i, p in enumerate(pop_records):
            print(f'    {i+1}. Geographic ID: {p.geographic_id}, City: {p.city}, ZIP: {p.zip_code}')
finally:
    db.close() 