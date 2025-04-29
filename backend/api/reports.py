"""
API endpoints for financial reports.
"""
from flask import jsonify, request
from api import api_bp
from database import db
from models.financial_data import FinancialReport

# Note: Report endpoints have been moved to routes.py to avoid duplication
