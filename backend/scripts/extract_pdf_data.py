#!/usr/bin/env python
"""
Script to extract financial data from PDF reports and populate the database.

Usage:
    python -m backend.scripts.extract_pdf_data
"""
import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config import get_config
from backend.database import db
from backend.utils.pdf_extractor import PDFExtractor

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main function to extract data from PDF files and populate the database.
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
        
        # Create PDF extractor with stream flavor to avoid Ghostscript dependency
        extractor = PDFExtractor(pdf_directory, flavor='stream')
        
        # Process all reports
        logger.info("Starting PDF data extraction...")
        results = extractor.process_all_reports()
        
        # Log results
        logger.info(f"PDF extraction completed. Results: {results}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error in PDF extraction: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 