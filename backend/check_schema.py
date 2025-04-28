import logging
from database import db
from models.financial_data import Base, FinancialReport, FinancialMetric, YearlyData, ShareholderData
from sqlalchemy import inspect

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_schema():
    """Check if the database schema matches our models"""
    try:
        # Initialize database
        db.init_db()
        
        # Get inspector
        inspector = inspect(db.engine)
        
        # Check tables
        tables = inspector.get_table_names()
        logger.info(f"Database tables: {tables}")
        
        # Expected tables
        expected_tables = [
            'financial_reports',
            'financial_metrics',
            'yearly_data',
            'shareholders_data'
        ]
        
        # Check if all expected tables exist
        for table in expected_tables:
            if table not in tables:
                logger.error(f"Table {table} does not exist in the database")
            else:
                logger.info(f"Table {table} exists")
                
                # Get columns
                columns = [col['name'] for col in inspector.get_columns(table)]
                logger.info(f"Columns for {table}: {columns}")
        
        logger.info("Schema check completed")
        
    except Exception as e:
        logger.error(f"Error checking schema: {e}")
        raise

if __name__ == "__main__":
    check_schema() 