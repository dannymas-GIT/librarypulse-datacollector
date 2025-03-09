# LibraryPulse Data Collector Test Suite

This directory contains a comprehensive test suite for the LibraryPulse data collector, which is responsible for fetching, processing, and storing public library survey data from IMLS.

## Test Strategy

The test suite is designed to verify the functionality of the data collector at multiple levels:

1. **Isolated Component Tests**: Tests for specific components of the data collector, such as data discovery, downloading, and processing.
2. **Integration Tests**: Tests that verify the interaction between multiple components.
3. **End-to-End Tests**: Tests that verify the complete data pipeline, from discovery to database loading.
4. **Standalone Tests**: Tests that can run without database dependencies, using a simplified version of the collector.

## Test Files

### Basic Component Tests

- `test_discovery.py`: Tests the discovery of available years of IMLS public library survey data.
- `test_sample_data.py`: Tests the loading and processing of sample data files.
- `test_sample_fallback.py`: Tests the fallback mechanism that uses sample data when direct downloads fail.
- `test_data_processing.py`: Tests the processing of library data, including extracting, filtering, and summarizing.

### Integration Tests

- `test_full_collector.py`: Tests the full data collector class with database dependencies.
- `test_collector_standalone.py`: Tests a standalone version of the collector without database dependencies.

## Running the Tests

Each test file can be run independently using Python:

```bash
python test_discovery.py
python test_sample_data.py
python test_sample_fallback.py
python test_data_processing.py
python test_collector_standalone.py
```

## Sample Data

The test suite uses sample data files located in the `data/sample` directory:

- `pls_sample_2021_library.csv`: Sample library data file
- `pls_sample_2021_outlet.csv`: Sample library outlet data file

These files are used to test the data processing functionality when direct downloads from IMLS are not available or not desired.

## Key Testing Approach

1. **Graceful Fallback**: The tests verify that the collector can gracefully fall back to using sample data when direct downloads fail.
2. **Offline Testing**: The standalone tests can run without an internet connection or database connection.
3. **Data Validation**: The tests verify that the collected data meets the expected format and contains the expected fields.
4. **Error Handling**: The tests verify that the collector handles errors gracefully and provides meaningful error messages.

## Extending the Tests

To add new tests:

1. Create a new test file with a descriptive name.
2. Import the necessary modules and set up logging.
3. Define test functions that verify specific aspects of the collector.
4. Add a main block that runs the tests and reports results.

## Troubleshooting

If tests fail, check the following:

1. **Sample Data**: Ensure that the sample data files are present in the `data/sample` directory.
2. **Environment Variables**: Ensure that the required environment variables are set in the `.env` file.
3. **Dependencies**: Ensure that all required dependencies are installed.
4. **Permissions**: Ensure that the application has permission to read and write to the data directories.

## Logging

All tests use the Loguru logger to provide detailed information about the test execution. Log files are created in the application root directory with names corresponding to the test file. 