#!/usr/bin/env python
"""
Clean Database Script

This script cleans all data from the database to allow for fresh data extraction.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database import db
from backend.models.financial_data import FinancialReport, FinancialMetric, YearlyData

def clean_database():
    """Delete all existing data from the database."""
    print("Cleaning database...")
    session = db.get_session()
    
    try:
        # Delete all yearly data entries first (due to foreign key constraints)
        yearly_data_count = session.query(YearlyData).delete()
        print(f"Deleted {yearly_data_count} entries from YearlyData table")
        
        # Delete all financial reports
        reports_count = session.query(FinancialReport).delete()
        print(f"Deleted {reports_count} entries from FinancialReport table")
        
        # Delete all financial metrics
        metrics_count = session.query(FinancialMetric).delete()
        print(f"Deleted {metrics_count} entries from FinancialMetric table")
        
        # Commit the changes
        session.commit()
        print("Database cleanup completed successfully")
        
    except Exception as e:
        session.rollback()
        print(f"Error during database cleanup: {e}")
    finally:
        db.close_session(session)

if __name__ == "__main__":
    # Initialize the database
    db.init_db()
    
    # Clean the database
    clean_database() 