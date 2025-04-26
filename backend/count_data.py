import sqlite3

conn = sqlite3.connect('jkh_financial.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables found:", [table[0] for table in tables])

# Count records in each table
for table in tables:
    table_name = table[0]
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"Table {table_name}: {count} records")
    except Exception as e:
        print(f"Error counting records in {table_name}: {e}")

# Check yearly data by year
try:
    cursor.execute("""
        SELECT r.year, COUNT(*) 
        FROM yearly_data y
        JOIN financial_reports r ON y.report_id = r.id
        GROUP BY r.year;
    """)
    yearly_counts = cursor.fetchall()
    print("\nYearly data counts by year:")
    for year_count in yearly_counts:
        print(f"Year {year_count[0]}: {year_count[1]} metrics")
except Exception as e:
    print(f"Error getting yearly data counts: {e}")

# Check shareholder data by year if it exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shareholder_data';")
if cursor.fetchone():
    try:
        cursor.execute("""
            SELECT r.year, COUNT(*) 
            FROM shareholder_data s
            JOIN financial_reports r ON s.report_id = r.id
            GROUP BY r.year;
        """)
        shareholder_counts = cursor.fetchall()
        print("\nShareholder data counts by year:")
        for year_count in shareholder_counts:
            print(f"Year {year_count[0]}: {year_count[1]} shareholders")
    except Exception as e:
        print(f"Error getting shareholder data counts: {e}")

conn.close() 