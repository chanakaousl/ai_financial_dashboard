# John Keells Financial Dashboard Frontend

This is the frontend application for the AI-Powered Financial Dashboard for John Keells Holdings.

## Tech Stack

- React 18
- TypeScript
- Vite
- React Router
- Chart.js
- Tailwind CSS
- Axios

## Setup

### Prerequisites

- Node.js 14+ installed
- Backend server running (see backend README)

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at http://localhost:5173

## Features

The dashboard visualizes key financial metrics from John Keells Holdings:

- Total Revenue (5-Year Curve)
- Cost of Sales vs. Operating Expenses (5-Year Comparison)
- Gross Profit Margin (5-Year Trend)
- Earnings Per Share (EPS) (5-Year Curve)
- Net Asset Per Share (5-Year Trend)
- Top 20 Shareholders Overview

## Structure

- `/src/api`: API client and services
- `/src/components`: Reusable UI components
- `/src/views`: Page components
- `/src/utils`: Utility functions
- `/src/assets`: Static assets
