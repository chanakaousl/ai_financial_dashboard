"""
Command-line interface for the JKH Financial Dashboard application.
"""
import click
import logging
from .database import db
from .scripts.financial_data_extractor import FinancialDataExtractor
from .config import get_config

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Command-line interface for the JKH Financial Dashboard."""
    pass

@cli.command()
def init_db():
    """Initialize the database and create tables."""
    db.init_db()
    logger.info("Database initialized successfully")

@cli.command()
def process_pdfs():
    """Extract data from PDFs and populate the database."""
    try:
        # Get configuration
        config = get_config()
        pdf_directory = config.PDF_DIRECTORY
        
        # Initialize the database
        db.init_db()
        
        # Create financial data extractor
        extractor = FinancialDataExtractor(pdf_directory)
        
        # Process all reports
        logger.info("Starting financial data extraction...")
        results = extractor.process_all_reports()
        
        # Log results
        logger.info(f"Extraction completed. Results: {results}")
        
    except Exception as e:
        logger.error(f"Error in financial data extraction: {e}")
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli() 