from app.db.session import SessionLocal
from app.models.pls_data import Library

# Connect to database
db = SessionLocal()

# Count Suffolk libraries
suffolk_count = db.query(Library).filter(Library.county.ilike('%suffolk%')).count()
print(f"Found {suffolk_count} Suffolk County libraries")

# If any found, list them
if suffolk_count > 0:
    suffolk_libs = db.query(Library).filter(Library.county.ilike('%suffolk%')).limit(10).all()
    print("\nSample Suffolk County libraries:")
    for lib in suffolk_libs:
        print(f"{lib.library_id}: {lib.name} in {lib.city}")
else:
    print("No Suffolk County libraries found") 