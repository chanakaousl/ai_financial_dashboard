#!/usr/bin/env python
"""
Script to set up the core financial metrics in the database.

Usage:
    python setup_core_metrics.py
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database import db
from backend.models.financial_data import FinancialMetric

def setup_core_metrics():
    """
    Set up only the core metrics as specified in requirements.
    Avoids duplicate metrics by focusing only on essential financial indicators.
    """
    print("Setting up core metrics...")
    
    # Initialize the database 
    db.init_db()
    
    # Create session
    session = db.get_session()
    
    try:
        # Define only the core metrics
        core_metrics = [
            {
                "name": "revenue", 
                "description": "Total Revenue from annual report", 
                "unit": "LKR", 
                "category": "revenue"
            },
            {
                "name": "cost_of_sales", 
                "description": "Cost of Sales from annual report", 
                "unit": "LKR", 
                "category": "cost_of_sales"
            },
            {
                "name": "operating_expenses", 
                "description": "Operating Expenses from annual report", 
                "unit": "LKR", 
                "category": "operating_expenses"
            },
            {
                "name": "gross_profit_margin", 
                "description": "Gross Profit Margin (Revenue - Cost) / Revenue", 
                "unit": "%", 
                "category": "gross_profit_margin"
            },
            {
                "name": "eps", 
                "description": "Earnings Per Share from annual report", 
                "unit": "LKR/share", 
                "category": "eps"
            },
            {
                "name": "net_asset_per_share", 
                "description": "Net Asset Per Share from annual report", 
                "unit": "LKR/share", 
                "category": "net_asset_per_share"
            },
            {
                "name": "right_issues", 
                "description": "Right Issues information", 
                "unit": "LKR", 
                "category": "right_issues"
            },
            {
                "name": "top_20_shareholders", 
                "description": "Top 20 Shareholders information", 
                "unit": "", 
                "category": "shareholders"
            }
        ]
        
        # Add/update each core metric
        for metric_info in core_metrics:
            metric = session.query(FinancialMetric).filter_by(name=metric_info["name"]).first()
            
            if metric:
                # Update existing metric
                metric.description = metric_info["description"]
                metric.unit = metric_info["unit"]
                metric.category = metric_info["category"]
                print(f"Updated metric: {metric_info['name']}")
            else:
                # Create new metric
                metric = FinancialMetric(
                    name=metric_info["name"],
                    description=metric_info["description"],
                    unit=metric_info["unit"],
                    category=metric_info["category"]
                )
                session.add(metric)
                print(f"Created metric: {metric_info['name']}")
        
        # Commit the changes
        session.commit()
        print("Core metrics setup completed successfully")
        
    except Exception as e:
        session.rollback()
        print(f"Error during core metrics setup: {e}")
        return 1
    finally:
        db.close_session(session)
    
    return 0

if __name__ == "__main__":
    sys.exit(setup_core_metrics()) 