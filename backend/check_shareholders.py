import sqlite3

conn = sqlite3.connect('jkh_financial.db')
cursor = conn.cursor()

# Check if shareholder_data table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shareholder_data';")
table_exists = cursor.fetchone()

if table_exists:
    print("Shareholder data table exists.")
    
    # Get schema for shareholder_data table
    cursor.execute("PRAGMA table_info(shareholder_data);")
    columns = cursor.fetchall()
    print("Columns in shareholder_data:")
    for column in columns:
        print(f"  {column[1]} ({column[2]})")
    
    # Get sample data
    cursor.execute("SELECT * FROM shareholder_data LIMIT 5;")
    data = cursor.fetchall()
    print("\nSample data (first 5 rows):")
    for row in data:
        print(row)
else:
    print("Shareholder data table does not exist in the database.")
    print("The table is defined in the models but hasn't been created in the database.")

conn.close() 