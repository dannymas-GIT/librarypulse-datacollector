import psycopg2

try:
    conn = psycopg2.connect(
        dbname="librarypulse",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    print("Database connection successful!")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
    # Close connection
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error connecting to database: {e}") 