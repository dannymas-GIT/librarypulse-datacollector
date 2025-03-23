# Library-Lens Integration Roadmap

## Overview

This roadmap outlines the plan to integrate the LibraryPulse datacollector project into the larger Library-Lens umbrella. The goal is to create a unified architecture that will be deployed at `/opt/docker-apps/library-lens` on the Lightsail server.

## Current State

- LibraryPulse datacollector: Standalone application with frontend and backend components
- Existing components (switch, backup, sonicwall): Will be replaced with mock data implementations

## Target Architecture

```
/opt/docker-apps/library-lens/
├── nginx/                    # Central reverse proxy configuration
├── frontend/                 # Main frontend application (React)
├── backend/                  # Main backend API (FastAPI)
├── data/                     # Shared data storage
├── postgres/                 # Database data
├── redis/                    # Redis data
├── docker-compose.yml        # Unified docker compose file
└── .env                      # Environment configuration
```

## Integration Phases

### Phase 1: Repository Restructuring (Current)

- [x] Develop CI/CD pipeline for automated testing and deployment
- [ ] Create a unified GitHub repository structure
- [ ] Set up main docker-compose.yml for all components
- [ ] Configure central nginx reverse proxy

### Phase 2: Application Integration (Next)

- [ ] Integrate LibraryPulse datacollector backend
- [ ] Integrate LibraryPulse datacollector frontend
- [ ] Implement mock data for switch, backup, and sonicwall components
- [ ] Create a unified landing page

### Phase 3: Authentication & Authorization

- [ ] Implement central authentication system
- [ ] Set up role-based access control
- [ ] Create user management interface

### Phase 4: Deployment & Infrastructure

- [ ] Set up AWS Lightsail instance
- [ ] Configure domain and SSL certificates
- [ ] Implement database backup system
- [ ] Set up monitoring and alerting

### Phase 5: Documentation & Refinement

- [ ] Create user documentation
- [ ] Develop technical documentation
- [ ] Optimize performance
- [ ] Implement analytics

## Deployment Plan

### AWS Lightsail Setup

1. Create a Lightsail instance with at least:
   - 4GB RAM
   - 80GB SSD
   - Ubuntu 22.04 LTS

2. Configure networking:
   - Static IP address
   - Domain name configuration
   - Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)

3. Install requirements:
   - Docker and Docker Compose
   - Nginx
   - Certbot for SSL

### Deployment Architecture

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

## Next Steps & Tasks

1. Create a new docker-compose.yml for the unified architecture
2. Set up a central Nginx configuration
3. Migrate backend services to the new structure
4. Develop a unified frontend interface
5. Test local deployment
6. Prepare AWS Lightsail environment
7. Deploy to production

## Timeline

- Phase 1: 1-2 weeks
- Phase 2: 2-3 weeks
- Phase 3: 2 weeks
- Phase 4: 1 week
- Phase 5: 1-2 weeks

Total estimated time: 7-10 weeks 