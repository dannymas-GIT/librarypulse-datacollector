# Migration Plan: Standardizing on "librarylens"

## Overview

This migration will standardize our naming across all environments to use "librarylens" consistently, aligning with our production environment and branding.

## Step 1: Development Environment Migration

1. Run the migration script:
   ```bash
   ./migrate_to_librarylens.sh
   ```

   This script will:
   - Create a backup of the current database
   - Update docker-compose.yml to use "librarylens" naming
   - Recreate the environment with the new naming
   - Restore data to the new database

2. Test the development environment thoroughly to ensure it works with the new database name.

## Step 2: CI/CD Pipeline Updates

1. Make the following changes to GitHub Actions workflows:

   - Update `.github/workflows/deploy.yml`:
     - Change database names from `librarypulse` to `librarylens`
     - Update deployment directory from `/opt/projects/librarypulse/datacollector` to `/opt/projects/librarylens`
   
   - Update `.github/workflows/ci-cd.yml`:
     - Change all database names from `librarypulse` to `librarylens`
     - Update Docker image names if they contain "librarypulse"

2. Update the `update-vps.sh` script:
   - Change container names from `datacollector_db_1` to `librarylens-db-1`
   - Change database names from `librarypulse` to `librarylens`

## Step 3: Code and Configuration Updates

1. Check for hardcoded database references:
   ```bash
   grep -r "librarypulse" --include="*.py" --include="*.js" --include="*.ts" --include="*.tsx" --include="*.yml" --include="*.sh" .
   ```

2. Update any configuration files (.env, etc.) that might reference "librarypulse"

3. Update documentation to use "librarylens" consistently.

## Step 4: Git Repository Changes

1. Create a feature branch for these changes:
   ```bash
   git checkout -b standardize-to-librarylens
   ```

2. Commit all the changes:
   ```bash
   git add .
   git commit -m "Standardize naming to use librarylens across all environments"
   ```

3. Push the branch and create a pull request:
   ```bash
   git push -u origin standardize-to-librarylens
   ```

## Step 5: Deployment and Verification

1. Once the PR is approved, merge it to main.

2. Monitor the CI/CD pipeline to ensure it completes successfully.

3. Verify that the production deployment works correctly:
   - SSH into the production server
   - Check that the containers are running
   - Verify the database connection
   - Test key functionality

## Migration Rollback Plan

If issues arise during migration:

1. For development: 
   - Restore from the database backup
   - Revert docker-compose.yml changes

2. For production:
   - Revert the GitHub repository to the previous state
   - Redeploy using the previous configurations

## Post-Migration Tasks

1. Update team documentation about standardizing on "librarylens"

2. Consider eventually renaming the GitHub repository from "librarypulse" to "librarylens" (requires additional planning)

3. Update any external references or integrations that might use the old naming convention 