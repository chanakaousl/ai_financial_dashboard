#!/usr/bin/env python
"""
Enhanced script to extract financial data from PDF reports with a focus on the core metrics.

Usage:
    python enhanced_extraction.py
"""
import os
import sys
import logging
import re
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config import get_config
from backend.database import db
from backend.utils.pdf_extractor import PDFExtractor
from backend.models.financial_data import FinancialReport, FinancialMetric, YearlyData

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_core_metrics_exist(session):
    """
    Ensure that core metric definitions exist in the database.
    Focus only on the essential metrics requested.
    """
    core_metrics = [
        {"name": "revenue", "description": "Total Revenue from annual report", "unit": "LKR", "category": "revenue"},
        {"name": "cost_of_sales", "description": "Cost of Sales from annual report", "unit": "LKR", "category": "cost_of_sales"},
        {"name": "operating_expenses", "description": "Operating Expenses from annual report", "unit": "LKR", "category": "operating_expenses"},
        {"name": "gross_profit_margin", "description": "Gross Profit Margin (Revenue - Cost) / Revenue", "unit": "%", "category": "gross_profit_margin"},
        {"name": "eps", "description": "Earnings Per Share from annual report", "unit": "LKR/share", "category": "eps"},
        {"name": "net_asset_per_share", "description": "Net Asset Per Share from annual report", "unit": "LKR/share", "category": "net_asset_per_share"},
        {"name": "right_issues", "description": "Right Issues information", "unit": "LKR", "category": "right_issues"},
        {"name": "top_20_shareholders", "description": "Top 20 Shareholders information", "unit": "", "category": "shareholders"}
    ]
    
    # Ensure all core metrics exist
    for metric_info in core_metrics:
        metric = session.query(FinancialMetric).filter_by(name=metric_info["name"]).first()
        if not metric:
            metric = FinancialMetric(
                name=metric_info["name"],
                description=metric_info["description"],
                unit=metric_info["unit"],
                category=metric_info["category"]
            )
            db.add_and_commit(session, metric)
            logger.info(f"Created metric: {metric_info['name']}")

def extract_with_focus_on_core_metrics():
    """
    Extract data with a focus on ensuring core metrics are captured.
    We only extract actual values from PDFs, not calculate them.
    """
    try:
        # Get configuration
        config = get_config()
        pdf_directory = config.PDF_DIRECTORY
        
        if not os.path.exists(pdf_directory):
            logger.error(f"PDF directory {pdf_directory} does not exist")
            sys.exit(1)
        
        # Initialize the database
        db.init_db()
        
        # Create session
        session = db.get_session()
        
        # Ensure core metrics exist
        ensure_core_metrics_exist(session)
        
        # Create PDF extractor with stream flavor to avoid Ghostscript dependency
        # Configure it to focus on the core metrics only
        extractor = PDFExtractor(pdf_directory, flavor='stream', focus_metrics=[
            'revenue', 'cost_of_sales', 'operating_expenses', 
            'eps', 'net_asset_per_share', 'right_issues', 'top_20_shareholders'
        ])
        
        # Process all reports
        logger.info("Starting enhanced PDF data extraction...")
        results = extractor.process_all_reports()
        
        # Log results
        logger.info(f"PDF extraction completed. Results: {results}")
        
        # Verify we have the core metrics
        verify_core_metrics_coverage(session)
        
        db.close_session(session)
        return 0
    
    except Exception as e:
        logger.error(f"Error in enhanced PDF extraction: {e}")
        return 1

def verify_core_metrics_coverage(session):
    """
    Verify that we have extracted core metrics for each year and log any missing metrics.
    """
    core_categories = ['revenue', 'cost_of_sales', 'operating_expenses', 
                      'gross_profit_margin', 'eps', 'net_asset_per_share', 
                      'right_issues', 'shareholders']
    
    reports = session.query(FinancialReport).all()
    
    for report in reports:
        logger.info(f"Checking core metrics coverage for year {report.year}:")
        
        for category in core_categories:
            metrics = session.query(FinancialMetric).filter_by(category=category).all()
            metric_ids = [m.id for m in metrics]
            
            if not metric_ids:
                logger.warning(f"  - No metrics defined for category {category}")
                continue
                
            data = session.query(YearlyData).filter(
                YearlyData.report_id == report.id,
                YearlyData.metric_id.in_(metric_ids)
            ).first()
            
            if data:
                logger.info(f"  - {category}: ✓")
            else:
                logger.warning(f"  - {category}: Missing data")

if __name__ == "__main__":
    sys.exit(extract_with_focus_on_core_metrics()) 