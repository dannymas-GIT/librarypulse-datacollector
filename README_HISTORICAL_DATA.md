# West Babylon Public Library Historical Data

This directory contains tools for importing, managing, and querying historical data for the West Babylon Public Library. The data spans from 1988 to the present, providing a comprehensive view of the library's operations over time.

## Data Structure

The historical data is stored in a dedicated PostgreSQL table called `library_historical_data`. This table includes the following information for each year:

- Basic library information (name, address, contact details)
- Service area population
- Collection statistics (print, electronic, audio, video)
- Usage statistics (circulation, visits, reference transactions)
- Program statistics (programs offered, attendance)
- Staffing information (total staff, librarians)
- Financial data (revenue, expenditures)

## Tools

### Historical Data Import

The `create_historical_table.py` script creates a dedicated table for historical data and populates it with synthetic data for the West Babylon Public Library from 1988 to the present. The data is generated based on realistic growth trends and includes random variations to simulate real-world data.

```bash
python backend/create_historical_table.py
```

### Historical Data Query

The `query_historical_data.py` script provides a flexible interface for querying and analyzing the historical data. It supports the following operations:

- Retrieving data for a specific year
- Exporting data to JSON
- Generating trend analysis
- Creating visualizations of historical trends
- Displaying a summary of the library's current state

#### Usage Examples

Display a summary of the library's current state:

```bash
python backend/query_historical_data.py --summary
```

Show trend analysis for key metrics:

```bash
python backend/query_historical_data.py --trends
```

Generate a plot of circulation trends:

```bash
python backend/query_historical_data.py --plot circulation_trends.png --metrics total_circulation electronic_circulation physical_circulation
```

Export all historical data to JSON:

```bash
python backend/query_historical_data.py --export west_babylon_historical.json
```

Retrieve data for a specific year:

```bash
python backend/query_historical_data.py --year 2010
```

### API Access

The historical data is also accessible through a REST API built with FastAPI. The API provides endpoints for retrieving historical data, generating trend analysis, and more.

#### Running the API Server

```bash
cd backend && python -m api.main
```

The API server will start on port 8000, and you can access the API documentation at http://localhost:8000/docs.

#### API Endpoints

- **GET /api/historical/summary**: Get a summary of available historical data
- **GET /api/historical/years**: Get a list of available years
- **GET /api/historical/data/{year}**: Get library data for a specific year
- **GET /api/historical/data**: Get all historical data for the library
- **GET /api/historical/trends/{metric}**: Get trend data for a specific metric
- **GET /api/historical/trends?metrics=metric1&metrics=metric2**: Get trend data for multiple metrics

#### Example API Requests

Get a summary of available historical data:

```bash
curl http://localhost:8000/api/historical/summary
```

Get trend data for circulation and visits:

```bash
curl "http://localhost:8000/api/historical/trends?metrics=total_circulation&metrics=electronic_circulation&metrics=visits"
```

Get data for a specific year:

```bash
curl http://localhost:8000/api/historical/data/2022
```

## Data Analysis

The historical data reveals several interesting trends:

1. **Service Area Population**: Grew by 16.89% from 1988 to 2024, with an average annual growth rate of 0.48%.

2. **Collections**:
   - Print collection grew by 37.46% over the period.
   - Electronic collection started from zero in the early years and has grown significantly, especially since 2000.

3. **Circulation**:
   - Total circulation increased by 33.28% from 1988 to 2024.
   - Electronic circulation has been steadily replacing physical circulation, especially in recent years.
   - The COVID-19 pandemic caused a significant drop in physical circulation in 2020, but it has been recovering since.

4. **Library Visits**: Increased by 41.79% over the period, with a significant drop during the pandemic years.

5. **Programs**:
   - Total programs offered increased by 73.60%.
   - Program attendance grew by 80.93%.
   - Both metrics saw a dramatic decline during the pandemic but have rebounded strongly.

6. **Staffing**: Total staff increased by 27.86% from 1988 to 2024.

7. **Financials**:
   - Total operating revenue more than doubled (103.88% increase).
   - Total operating expenditures grew by 106.52%.
   - Both metrics have generally kept pace with inflation.

## Future Enhancements

Potential enhancements to the historical data tools include:

1. Integration with real IMLS data when available.
2. Comparative analysis with similar libraries.
3. Predictive modeling for future trends.
4. More sophisticated visualization options.
5. API endpoints for accessing historical data from web applications.

## Dependencies

- Python 3.11+
- PostgreSQL
- psycopg2
- pandas
- matplotlib
- FastAPI
- uvicorn

## Installation

```bash
pip install psycopg2-binary pandas matplotlib fastapi uvicorn
``` 