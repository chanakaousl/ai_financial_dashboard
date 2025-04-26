import sqlite3

conn = sqlite3.connect('jkh_financial.db')
cursor = conn.cursor()

# Get sample data from financial_reports
print("Sample data from financial_reports (first 5 rows):")
cursor.execute("SELECT * FROM financial_reports LIMIT 5;")
reports = cursor.fetchall()
for report in reports:
    print(report)
print()

# Get sample data from financial_metrics
print("Sample data from financial_metrics (first 10 rows):")
cursor.execute("SELECT * FROM financial_metrics LIMIT 10;")
metrics = cursor.fetchall()
for metric in metrics:
    print(metric)
print()

# Get sample data from yearly_data with joined metric names
print("Sample yearly_data with metric names (first 10 rows):")
cursor.execute("""
    SELECT y.id, r.year, m.name, y.value 
    FROM yearly_data y
    JOIN financial_reports r ON y.report_id = r.id
    JOIN financial_metrics m ON y.metric_id = m.id
    LIMIT 10;
""")
data = cursor.fetchall()
for row in data:
    print(row)

conn.close() 