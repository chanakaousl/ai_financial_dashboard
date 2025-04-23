# JKH Financial Dashboard Backend

Backend API for the John Keells Holdings Financial Dashboard application.

## Technology Stack

- **Python**: 3.10+
- **Web Framework**: Flask
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Data Processing**: Pandas, NumPy
- **PDF Parsing**: Camelot, PDFMiner, PyMuPDF
- **Machine Learning**: scikit-learn

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Windows Setup

1. Navigate to the backend directory:

   ```
   cd backend
   ```

2. Run the setup script:

   ```
   setup_env.bat
   ```

3. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```

### Unix/MacOS Setup

1. Navigate to the backend directory:

   ```
   cd backend
   ```

2. Make the setup script executable:

   ```
   chmod +x setup_env.sh
   ```

3. Run the setup script:

   ```
   ./setup_env.sh
   ```

4. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

### Running the Application

1. Start the Flask development server:

   ```
   python app.py
   ```

2. The API will be available at http://localhost:5000

## Project Structure

```
backend/
│
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── database.py         # Database utilities
├── requirements.txt    # Python dependencies
│
├── models/             # SQLAlchemy data models
│   ├── __init__.py
│   └── financial_data.py
│
├── utils/              # Utility modules
│   ├── __init__.py
│   └── pdf_parser.py   # PDF parsing utilities
│
└── venv/               # Python virtual environment
```

## API Documentation

### Endpoints

- `GET /api/health`: Health check endpoint
- `GET /api/reports`: Get list of available financial reports

More detailed API documentation will be provided as development progresses.
