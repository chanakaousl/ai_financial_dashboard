#!/usr/bin/env python
"""
Script to clean the financial database by deleting all data from tables.

Usage:
    python clean_database.py
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database import db
from backend.models.financial_data import FinancialReport, FinancialMetric, YearlyData

def clean_database():
    """
    Delete all data from the database tables while keeping the schema intact.
    """
    print("Starting database cleanup...")
    
    # Initialize the database 
    db.init_db()
    
    # Create session
    session = db.get_session()
    
    try:
        # Delete all yearly data entries first (due to foreign key constraints)
        yearly_data_count = session.query(YearlyData).delete()
        print(f"Deleted {yearly_data_count} entries from YearlyData table")
        
        # Delete all financial metrics
        metrics_count = session.query(FinancialMetric).delete()
        print(f"Deleted {metrics_count} entries from FinancialMetric table")
        
        # Delete all financial reports
        reports_count = session.query(FinancialReport).delete()
        print(f"Deleted {reports_count} entries from FinancialReport table")
        
        # Commit the changes
        session.commit()
        print("Database cleanup completed successfully")
        
    except Exception as e:
        session.rollback()
        print(f"Error during database cleanup: {e}")
        return 1
    finally:
        db.close_session(session)
    
    return 0

if __name__ == "__main__":
    sys.exit(clean_database()) 