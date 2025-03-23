# Library-Lens

Library-Lens is a unified dashboard application that provides insights and analytics for library management. It incorporates data collection, visualization, and mock services for comprehensive library administration.

## Project Structure

The Library-Lens project integrates several components under a unified architecture:

- **LibraryPulse Data Collector**: Core component that collects and processes library data
- **Frontend Application**: React-based user interface for data visualization and management
- **Mock Services**: Simplified implementations of switch, backup, and sonicwall functionality
- **Central Authentication**: Unified login system for all components

## Architecture Overview

```
                                  ┌──────────────┐
                                  │     Nginx    │
                                  │  Reverse Proxy│
                                  └───────┬──────┘
                                          │
                 ┌──────────────┬─────────┴───────┬──────────────┐
                 │              │                 │              │
        ┌────────▼─────┐ ┌──────▼───────┐ ┌───────▼──────┐ ┌────▼─────────┐
        │   Frontend   │ │ Data Backend │ │ Mock Services│ │ Landing Page │
        └────────┬─────┘ └──────┬───────┘ └───────┬──────┘ └──────────────┘
                 │              │                 │
                 └──────────────┼─────────────────┘
                                │
                      ┌─────────▼────────┐
                      │                  │
                      │    PostgreSQL    │
                      │                  │
                      └──────────────────┘
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/library-lens.git
   cd library-lens
   ```

2. Create a `.env` file:
   ```
   DATABASE_URL=postgresql://postgres:postgres@db:5432/librarylens
   SECRET_KEY=your_development_secret_key
   ENVIRONMENT=development
   ```

3. Start the development environment:
   ```bash
   docker compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/v1
   - API Documentation: http://localhost:8000/docs

## Production Deployment

### AWS Lightsail Setup

1. Create a Lightsail instance
2. Install Docker and Docker Compose:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y ca-certificates curl gnupg
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
   echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
   ```

3. Set up project directory:
   ```bash
   sudo mkdir -p /opt/docker-apps/library-lens
   sudo chown $USER:$USER /opt/docker-apps/library-lens
   ```

4. Deploy the application:
   ```bash
   cd /opt/docker-apps/library-lens
   # Copy docker-compose.yml and .env files
   docker compose up -d
   ```

## Components

### Frontend

The frontend application is built with:
- React 18+
- TypeScript
- Tailwind CSS
- React Router
- React Query

### Backend

The backend API is built with:
- FastAPI
- SQLAlchemy
- Pydantic
- Alembic for migrations

### Mock Services

Simplified implementations of:
- Switch management
- Backup management
- Sonicwall analytics

### Database

- PostgreSQL 15+
- Redis for caching

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://postgres:postgres@db:5432/librarylens |
| SECRET_KEY | Secret key for JWT encryption | (required) |
| ENVIRONMENT | Environment (development/production) | development |
| LOG_LEVEL | Logging level | INFO |
| CORS_ORIGINS | Allowed CORS origins | * |

## Docker Compose Configuration

The `docker-compose.yml` file defines all services required for the application:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - frontend
      - backend
    networks:
      - app-network

  frontend:
    image: ghcr.io/yourusername/library-lens-frontend:latest
    build:
      context: ./frontend
    environment:
      - VITE_API_URL=/api/v1
    networks:
      - app-network

  backend:
    image: ghcr.io/yourusername/library-lens-backend:latest
    build:
      context: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=${ENVIRONMENT}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=librarylens
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 