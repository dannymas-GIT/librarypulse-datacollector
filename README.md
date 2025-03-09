# IMLS Library Pulse

A comprehensive search and analytics utility for Library Directors, enabling data-driven decision making based on the Public Libraries Survey (PLS) data collected annually by the Institute of Museum and Library Services (IMLS).

## Project Overview

The IMLS Library Pulse project provides a modern web application that allows library directors and administrators to:

- Search and browse library data across the United States
- View detailed statistics for individual libraries
- Analyze trends in library metrics over time
- Compare multiple libraries across various metrics
- Access and manage PLS data from 1992 to the present

### Data Sources

- **Public Libraries Survey (PLS)**: Comprehensive annual data collection since 1988 (files available from 1992)
- Most recent data: FY 2022
- Coverage: ~9,000 public libraries with ~17,000 outlets across the US

### Data Pipeline

The application includes a sophisticated data pipeline that:

1. **Discovers Available Data** - Automatically scans the IMLS website to find available PLS data years
2. **Downloads Data Files** - Retrieves CSV data files directly from the IMLS website
3. **Processes and Standardizes** - Transforms raw data into a consistent format regardless of year
4. **Filters for Your Library** - After setup, focuses only on your library's data
5. **Stores in Database** - Maintains a clean, queryable database of your library's historical data

The data collector supports both initial setup (downloading all historical data) and regular updates (checking for new annual releases).

### Data Categories

- Library visits and circulation statistics
- Collection sizes (physical and electronic)
- Public service hours
- Staffing information
- Electronic resources usage
- Operating revenues and expenditures
- Service outlet information
- Program statistics and attendance

## Technology Stack

### Backend

- **Python 3.11+** - Programming language
- **FastAPI** - API framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **PostgreSQL** - Database
- **Alembic** - Database migrations
- **Pandas** - Data processing

### Frontend

- **React 18+** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Query** - Server state management
- **React Router** - Client-side routing
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

### Infrastructure

- **Docker** - Containerization
- **Docker Compose** - Container orchestration
- **Nginx** - Web server (for production)

## Project Structure

```
librarypulse/
├── backend/               # Data collection and API backend
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Core configurations
│   │   ├── db/           # Database models and connections
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic services
│   ├── tests/            # Pytest test files
│   ├── alembic/          # Database migrations
│   └── requirements.txt  # Python dependencies
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── ...
│   └── package.json      # JavaScript dependencies
├── docker/               # Docker configuration files
│   ├── backend/          # Backend Docker files
│   └── frontend/         # Frontend Docker files
├── docker-compose.yml    # Docker Compose configuration
├── setup.sh              # Setup script
├── run.sh                # Backend run script
└── run-frontend.sh       # Frontend run script
```

## Setup and Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Docker and Docker Compose (optional)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/librarypulse.git
   cd librarypulse
   ```

2. Run the setup script:
   ```bash
   ./setup.sh
   ```

3. Start the backend server:
   ```bash
   ./run.sh
   ```

4. In a separate terminal, start the frontend development server:
   ```bash
   ./run-frontend.sh
   ```

5. Access the application:
   - Frontend: http://localhost:5173
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Docker Setup

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. Access the application:
   - Frontend: http://localhost
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Data Collection

The application includes a data collector component that can download, process, and store PLS data from the IMLS website.

```bash
# Initial setup: collect data just for your library (after configuration)
python -m backend.app.collector --update

# Download data for a specific year
python -m backend.app.collector --year 2022

# Download all available years
python -m backend.app.collector --all-years

# Check for latest data and update
python -m backend.app.collector --update

# Just discover what years are available without downloading
python -m backend.app.collector --discover
```

The data collector will automatically:
- Find and download the appropriate CSV files from IMLS
- Process and standardize the data format
- Filter for your specific library's data (if configured)
- Store the data in your database for analysis

If direct download from IMLS fails for any reason, the collector will fall back to using sample data files included in the project.

## Development

### Backend Development

```bash
# Run tests
cd backend
pytest

# Run with auto-reload
uvicorn app.main:app --reload
```

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Database Migrations

```bash
# Create a new migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## API Documentation

The API documentation is available at http://localhost:8000/docs when the server is running. It provides a comprehensive overview of all available endpoints and their parameters.

## License

[Add appropriate license information]

## Contributors

[Add contributor information] 