# IMLS Library Pulse - Backend API

This is the backend API for the IMLS Library Pulse project. It provides endpoints for collecting, storing, and retrieving Public Libraries Survey (PLS) data.

## API Documentation

The API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs) or [http://localhost:8000/redoc](http://localhost:8000/redoc) when the server is running.

## API Endpoints

### Root Endpoints

- `GET /`: Returns basic API information
- `GET /health`: Health check endpoint

### Dataset Endpoints

- `GET /api/v1/datasets/`: List all datasets
- `GET /api/v1/datasets/{year}`: Get dataset for a specific year
- `GET /api/v1/datasets/years/available`: List available years

### Library Endpoints

- `GET /api/v1/libraries/`: List libraries with optional filtering
- `GET /api/v1/libraries/{library_id}`: Get a specific library
- `GET /api/v1/libraries/{library_id}/outlets`: Get outlets for a specific library
- `GET /api/v1/libraries/states/list`: List all states with libraries
- `GET /api/v1/libraries/counties/list?state={state}`: List counties in a state

### Statistics Endpoints

- `GET /api/v1/stats/summary`: Get summary statistics
- `GET /api/v1/stats/trends`: Get trend statistics over time
- `GET /api/v1/stats/comparison`: Compare libraries across selected metrics

### Data Collection Endpoints

- `POST /api/v1/collector/collect/{year}`: Collect data for a specific year
- `POST /api/v1/collector/collect-all`: Collect data for all available years
- `POST /api/v1/collector/update`: Update with latest available data
- `GET /api/v1/collector/status`: Get data collection status

## Development

### Prerequisites

- Python 3.11+
- PostgreSQL

### Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values as needed

4. Initialize the database:
   ```bash
   alembic upgrade head
   ```

5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Running Tests

```bash
pytest
```

### Database Migrations

To create a new migration:

```bash
alembic revision --autogenerate -m "description of changes"
```

To apply migrations:

```bash
alembic upgrade head
```

To roll back a migration:

```bash
alembic downgrade -1
``` 