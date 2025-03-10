# Historical Data Dashboard for West Babylon Public Library

This document provides an overview of the historical data dashboard implementation for the West Babylon Public Library.

## Overview

The dashboard visualizes historical library data from 1988 to the present, allowing users to explore trends, analyze growth patterns, and gain insights into the library's performance over time.

## Components

### Backend

1. **Historical Data API**: Built with FastAPI, the API provides endpoints for retrieving historical data, trend analysis, and summaries.

Key endpoints:
- `/api/historical/summary`: Provides an overview of available historical data
- `/api/historical/years`: Lists available years of data
- `/api/historical/data/{year}`: Retrieves data for a specific year
- `/api/historical/data`: Retrieves all available historical data
- `/api/historical/trends/{metric}`: Gets trend data for a specific metric
- `/api/historical/trends?metrics=metric1&metrics=metric2`: Gets trend data for multiple metrics

2. **PostgreSQL Database**: Stores historical data in a dedicated `library_historical_data` table.

### Frontend

1. **Historical Trends Page**: React component that provides visualization of historical trends.
   - Route: `/historical`
   - Features:
     - Line and bar chart visualization
     - Metric selection by category
     - Year range filtering
     - Growth rate analysis

2. **Historical Data Service**: TypeScript service for API integration.
   - Methods:
     - `getSummary()`: Retrieves a summary of available historical data
     - `getYears()`: Gets all available years
     - `getDataForYear(year)`: Gets data for a specific year
     - `getAllData()`: Gets all historical data
     - `getTrendData(metric)`: Gets trend data for a specific metric
     - `getMultipleTrendData(metrics)`: Gets trend data for multiple metrics

## Features

The historical data dashboard includes the following features:

1. **Interactive Visualizations**: Users can view historical data as line or bar charts.

2. **Metric Selection**: Users can select from a wide range of metrics organized by category:
   - Circulation: total, electronic, physical
   - Visits: total visits, reference transactions, website visits
   - Collections: print, electronic, audio, video
   - Programs: total programs, attendance (total, children, adult)
   - Financial: revenue, expenditures, staff expenditures, collection expenditures

3. **Growth Analysis**: For each selected metric, the dashboard displays:
   - Total growth over the entire period
   - Average annual growth rate
   - Significant years with notable growth or decline

4. **Date Range Filtering**: Users can filter the data by selecting a specific year range.

## Technical Implementation

1. **Data Visualization**: Uses Recharts for responsive, interactive charts.

2. **State Management**: Uses React hooks (useState, useEffect) for local state and React Query for API data fetching.

3. **API Integration**: Uses Axios for API requests with proper TypeScript typing.

4. **Styling**: Uses Tailwind CSS for responsive styling.

## How to Use

1. Start the backend API:
   ```bash
   cd backend && python -m api.main
   ```

2. Start the frontend development server:
   ```bash
   cd frontend && npm run dev
   ```

3. Navigate to `http://localhost:5173/historical` in your browser to view the historical trends dashboard.

## Next Steps

1. **Data Filtering Enhancements**: Add more filtering options based on various library attributes.

2. **Comparative Analysis**: Implement comparison with similar libraries or national averages.

3. **Export Features**: Add ability to export charts and data in various formats.

4. **Dashboard Customization**: Allow users to create custom dashboards with their preferred metrics.

5. **Predictive Analytics**: Implement forecasting based on historical trends. 