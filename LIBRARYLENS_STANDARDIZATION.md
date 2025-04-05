# Standardization on "LibraryLens" Naming

This document outlines the process for standardizing our repository on the "librarylens" naming across all environments.

## Background

We currently have naming inconsistencies between environments:
- Development: Uses "librarypulse" as the database name
- Production: Uses "librarylens" as the database name and project name

For consistency and to reduce confusion, we're standardizing on "librarylens" across all environments.

## Migration Plan

### 1. Development Environment

1. Run the migration script:
   ```bash
   ./migrate_to_librarylens.sh
   ```

2. Verify the application works with the new database name:
   ```bash
   docker-compose ps  # Check all services are running
   curl http://localhost:8000/health  # Verify backend health
   ```

### 2. GitHub Actions Workflows

The following files need to be updated:

- `.github/workflows/deploy.yml`
- `.github/workflows/ci-cd.yml`
- Any other workflow files

Changes needed:
- Replace all instances of `librarypulse` with `librarylens` in database names
- Update any environment variables referencing the database name
- Update any Docker image names if they include `librarypulse`

### 3. Documentation

- Update README.md and other documentation to use "librarylens" consistently
- Update any environment setup instructions

### 4. Code Changes

Check for any hardcoded database names in:
- Backend code (Python files)
- Frontend code (if it makes direct database references)
- Configuration files (.env, etc.)

## Verification

After migration:

1. Run the local development environment to verify it works
2. Trigger a CI/CD pipeline to ensure it builds successfully
3. Deploy to production and verify it connects to the correct database

## Production Environment

The production environment is already using "librarylens" naming, so no changes are needed there.

## Future Development

Going forward:
- Always use "librarylens" for database names, project names, and Docker resource names
- Keep the GitHub repository name as is for now to avoid breaking links 