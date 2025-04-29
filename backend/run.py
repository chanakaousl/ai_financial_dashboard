#!/usr/bin/env python
"""
Entry point for the JKH Financial Dashboard Flask application.
"""
from flask import Flask
from flask_cors import CORS
from app import app

# Enable CORS for all routes with additional headers
CORS(app, resources={r"/api/*": {
    "origins": ["http://localhost:5173", "http://localhost:5174"], # Added frontend dev server port 5174
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "expose_headers": ["Content-Range", "X-Content-Range"]
}})

if __name__ == '__main__':
    # Run the Flask development server
    # Debug mode enables auto-reloading and provides detailed error pages
    # Host '0.0.0.0' makes the server accessible externally if needed
    # Port 5000 is the default Flask port
    app.run(debug=True, host='0.0.0.0', port=5000)
