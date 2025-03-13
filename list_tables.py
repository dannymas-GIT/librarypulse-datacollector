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
    
    # Get list of tables
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    
    print("\nTables in the database:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Close connection
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error connecting to database: {e}") 