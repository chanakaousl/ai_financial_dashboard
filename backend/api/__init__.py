"""
API routes for the JKH Financial Dashboard.
This package organizes all API endpoints for the application.
"""

from flask import Blueprint

# Create a blueprint for the API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import routes to register them with the blueprint
from .routes import *

# Import all routes
from api.reports import *
from api.metrics import *
from api.analysis import *

# Register routes with the blueprint
# Note: The imports above automatically register routes to the blueprint 