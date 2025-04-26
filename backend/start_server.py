#!/usr/bin/env python
"""
Special startup script that ensures proper imports for the JKH Financial Dashboard.
"""
import os
import sys

# Add the current directory to the Python path to allow absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now we can import our app
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True) 