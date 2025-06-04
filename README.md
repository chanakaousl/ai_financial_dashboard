# AI-Powered Financial Dashboard 

An interactive AI-powered dashboard to visualize and analyze key financial metrics from John Keells Holdings PLC's annual reports (2020-2024). The dashboard provides dynamic analysis with user-friendly filters and enhanced insights.

## Features

- **Total Revenue**: 5-year trend analysis with annotations for key events
- **Cost of Sales vs. Operating Expenses**: Comparative analysis over 5 years
- **Gross Profit Margin**: Trend visualization with annotations
- **Earnings Per Share (EPS)**: 5-year curve with detailed tooltips
- **Net Asset Per Share**: 5-year trend with industry benchmarks
- **Top 20 Shareholders**: Interactive table/pie chart with year filters

## Tech Stack

- **Backend**: Python (Flask API, Pandas for data processing)
- **Frontend**: React with TypeScript (Chart.js for visualizations)
- **AI/ML**: Python (scikit-learn for forecasting)
- **Data Extraction**: Camelot and PDFMiner for PDF parsing
- **Database**: SQLite with SQLAlchemy ORM

## Project Structure

```
/
├── frontend/               # React frontend
│   ├── src/                # Source code
│   │   ├── components/     # Reusable components
│   │   ├── views/          # Page components
│   │   ├── api/            # API services
│   │   ├── contexts/       # React contexts
│   │   ├── hooks/          # Custom hooks
│   │   └── types/          # TypeScript types
│   └── public/             # Static assets
│
├── backend/                # Flask backend
│   ├── api/                # API routes
│   ├── models/             # Database models
│   ├── pdf_parser.py       # PDF parsing utility
│   └── database.py         # Database connection handling
│
└── data-pdf/               # PDF financial reports
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PDF financial reports from John Keells Holdings

### Backend Setup

1. Navigate to the backend directory:

   ```
   cd backend
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:

   ```
   python init_db.py
   ```

5. Run the backend server:
   ```
   python run.py
   ```

The API will be available at http://localhost:5000/api

### Frontend Setup

1. Navigate to the frontend directory:

   ```
   cd frontend
   ```

2. Install dependencies:

   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run dev
   ```

The frontend will be available at http://localhost:5173

## API Endpoints

- `GET /api/health` - API health check
- `GET /api/metrics` - Get all financial metrics
- `GET /api/metrics/:id` - Get specific metric with yearly data
- `GET /api/reports` - Get all financial reports
- `GET /api/reports/:id` - Get specific report with metrics
- `GET /api/shareholders` - Get top shareholders data

## License

This project is licensed under the MIT License.
