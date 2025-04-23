from flask import Flask, jsonify
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({
        'status': 'success',
        'message': 'API is running'
    })

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Endpoint to retrieve a list of available financial reports."""
    return jsonify({
        'status': 'success',
        'data': [
            {'id': '2019', 'name': 'Annual Report 2019'},
            {'id': '2020', 'name': 'Annual Report 2020'},
            {'id': '2021', 'name': 'Annual Report 2021'},
            {'id': '2022', 'name': 'Annual Report 2022'},
            {'id': '2023', 'name': 'Annual Report 2023'},
            {'id': '2024', 'name': 'Annual Report 2024'}
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 