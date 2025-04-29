"""
API routes for the JKH Financial Dashboard.
This package organizes all API endpoints for the application.
"""

from flask import Blueprint

# Create a blueprint for the API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import routes to register them with the blueprint
# Only import routes.py since it contains all the endpoints
from .routes import *