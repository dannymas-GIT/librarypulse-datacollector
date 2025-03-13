import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(
        dbname="librarypulse",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    print("Database connection successful!")
    
    # Get libraries
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT id, fscs_id, name, city, state, county
        FROM libraries
        LIMIT 10;
    """)
    
    libraries = cursor.fetchall()
    
    print("\nLibraries in the database (first 10):")
    for library in libraries:
        print(f"- {library['fscs_id']} | {library['name']} | {library['city']}, {library['state']} | {library['county']} County")
    
    # Count libraries
    cursor.execute("SELECT COUNT(*) FROM libraries;")
    count = cursor.fetchone()
    print(f"\nTotal libraries: {count['count']}")
    
    # Close connection
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error connecting to database: {e}") 