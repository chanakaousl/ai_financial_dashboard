"""
API routes for the JKH Financial Dashboard.
This package organizes all API endpoints for the application.
"""

from flask import Blueprint

# Create a blueprint for the API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import all routes
from .reports import *
from .metrics import *
from .analysis import *

# Register routes with the blueprint
# Note: The imports above automatically register routes to the blueprint 