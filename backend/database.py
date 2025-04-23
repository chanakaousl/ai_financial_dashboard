from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from .models.financial_data import Base
import logging
from .config import get_config

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Database:
    """Database utility for managing SQLAlchemy sessions and operations."""
    
    def __init__(self, config=None):
        """
        Initialize the database utility.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        self.engine = None
        self.session_factory = None
        self.Session = None
        
    def init_db(self):
        """Initialize the database engine and session factory."""
        try:
            self.engine = create_engine(self.config.SQLALCHEMY_DATABASE_URI)
            self.session_factory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(self.session_factory)
            
            # Create all tables
            Base.metadata.create_all(self.engine)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def get_session(self):
        """
        Get a database session.
        
        Returns:
            SQLAlchemy session object
        """
        if not self.Session:
            self.init_db()
        return self.Session()
    
    def close_session(self, session):
        """
        Close a database session.
        
        Args:
            session: SQLAlchemy session object
        """
        try:
            session.close()
        except Exception as e:
            logger.error(f"Error closing database session: {e}")
    
    def add_and_commit(self, session, obj):
        """
        Add an object to the session and commit.
        
        Args:
            session: SQLAlchemy session object
            obj: SQLAlchemy model object
            
        Returns:
            Added object
        """
        try:
            session.add(obj)
            session.commit()
            return obj
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding object to database: {e}")
            raise
    
    def bulk_add_and_commit(self, session, objects):
        """
        Add multiple objects to the session and commit.
        
        Args:
            session: SQLAlchemy session object
            objects: List of SQLAlchemy model objects
            
        Returns:
            List of added objects
        """
        try:
            session.add_all(objects)
            session.commit()
            return objects
        except Exception as e:
            session.rollback()
            logger.error(f"Error bulk adding objects to database: {e}")
            raise

# Create a database instance
db = Database() 