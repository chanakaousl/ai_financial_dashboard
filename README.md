# AI-Powered Financial Dashboard for John Keells Holdings

An interactive AI-powered dashboard to visualize key financial metrics from John Keells Holdings PLC's annual reports (2019-2024).

## Project Overview

This application provides insightful visualizations and analysis of financial data extracted from John Keells Holdings' annual reports. The system uses AI/ML techniques to process PDF reports, extract key financial metrics, and present them in an interactive dashboard.

## Features

- PDF data extraction from financial reports
- Interactive data visualizations
- Financial trend analysis
- Predictive analytics for future projections
- Comparison of year-over-year performance
- Custom filtering and data selection

## Tech Stack

### Backend

- **Python**: Processing and API server
- **Flask**: Web framework
- **Pandas/NumPy**: Data manipulation
- **SQLite**: Database storage
- **Camelot/PDFMiner**: PDF data extraction
- **scikit-learn**: ML forecasting

### Frontend

- **React**: UI Framework
- **Chart.js/D3.js**: Data visualization
- **Tailwind CSS**: Styling

## Project Structure

```
ai_financial_dashboard/
├── backend/              # Python Flask API
│   ├── app.py            # Main application
│   ├── models/           # Database models
│   ├── utils/            # Utilities for PDF parsing, etc.
│   └── requirements.txt  # Python dependencies
│
├── frontend/             # React frontend application
│   ├── public/           # Static files
│   ├── src/              # React source code
│   └── package.json      # Node.js dependencies
│
└── data-pdf/             # PDF financial reports
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory
2. Run the setup script:
   - Windows: `setup_env.bat`
   - Unix/Mac: `./setup_env.sh`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/Mac: `source venv/bin/activate`
4. Start the Flask server: `python run.py`

### Frontend Setup

(Instructions will be added once frontend development is complete)

## Development Roadmap

1. ✅ Backend setup and environment configuration
2. ⬜ PDF data extraction and processing
3. ⬜ Database schema and data storage
4. ⬜ API endpoint development
5. ⬜ Frontend setup and component structure
6. ⬜ Dashboard UI development
7. ⬜ Data visualization implementation
8. ⬜ AI/ML model integration
9. ⬜ Testing and quality assurance
10. ⬜ Deployment and documentation

## License

This project is proprietary and confidential.
