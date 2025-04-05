# CI/CD Workflow Updates

The following files need to be updated to complete the standardization to "librarylens":

## 1. .github/workflows/ci-cd.yml

Replace all references to "librarypulse" with "librarylens":

- Line 23: Change Docker image name from `librarypulse-datacollector` to `librarylens-datacollector`
- Lines 142, 143, 192, 193, 205, 206: Update database URLs from `librarypulse_test` to `librarylens_test`
- Lines 317, 329: Update Docker image tags from `librarypulse-backend:test` to `librarylens-backend:test`
- Lines 339, 345, 356: Update network name from `librarypulse-test-network` to `librarylens-test-network`
- Line 348: Change `POSTGRES_DB=librarypulse_test` to `POSTGRES_DB=librarylens_test`
- Line 454, 516: Update database URLs from `librarypulse` to `librarylens`
- Line 506: Change directory from `/opt/librarypulse-staging` to `/opt/librarylens-staging`

## 2. docker-compose.nomount.yml

- Line 14: Update database URL from `librarypulse` to `librarylens`
- Line 44: Change `POSTGRES_DB=librarypulse` to `POSTGRES_DB=librarylens`

## Next Steps

1. Edit each file with the changes mentioned above:
   ```bash
   nano .github/workflows/ci-cd.yml
   nano docker-compose.nomount.yml
   ```

2. Commit the changes:
   ```bash
   git add .github/workflows/ci-cd.yml docker-compose.nomount.yml
   git commit -m "Update CI/CD workflows to use librarylens naming"
   ```

3. Push the branch to GitHub:
   ```bash
   git push -u origin standardize-to-librarylens
   ```

4. Create a pull request to merge these changes into main

## Testing

After these changes are committed, test the CI/CD workflow by:

1. Running a manual workflow dispatch on the standardize-to-librarylens branch
2. Verifying that all tests pass with the new database naming
3. Testing a full deployment to ensure the production environment is correctly updated 