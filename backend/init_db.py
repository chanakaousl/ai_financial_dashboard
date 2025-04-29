import logging
import os
from database import db
from models.financial_data import Base, FinancialReport, FinancialMetric, YearlyData, ShareholderData
# import populate_sample_data # Removed sample data import

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database schema"""
    try:
        # # Check if database file exists and delete if it does # Deletion moved to separate command
        # db_file = 'jkh_financial.db'
        # if os.path.exists(db_file):
        #     logger.info(f"Removing existing database file: {db_file}")
        #     os.remove(db_file)
            
        # Initialize database
        logger.info("Initializing database connection...")
        db.init_db()
        
        # Create tables
        Base.metadata.create_all(db.engine)
        logger.info("Database schema created successfully")
        
        # # Populate with sample data # Removed sample data population
        # logger.info("Populating database with sample data...")
        # populate_sample_data.populate_sample_data()
        logger.info("Database initialization complete (without sample data)")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_database()
