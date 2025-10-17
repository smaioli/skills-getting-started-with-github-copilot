# Tests for Mergington High School Activities API

This directory contains comprehensive tests for the FastAPI application using pytest.

## Test Structure

- `conftest.py` - Test configuration and fixtures
- `test_activities_api.py` - Main API endpoint tests
- `__init__.py` - Package initialization

## Test Coverage

The test suite provides **100% code coverage** for the API endpoints and includes:

### API Endpoint Tests (`TestActivitiesAPI`)

1. **Root Endpoint**
   - Tests redirect to static files

2. **Get Activities**
   - Validates activity list structure
   - Checks data types and required fields

3. **Signup for Activities**
   - Successful signup scenarios
   - Error handling for nonexistent activities
   - Duplicate participant prevention
   - Activity capacity enforcement

4. **Unregister from Activities**
   - Successful unregistration
   - Error handling for nonexistent activities
   - Error handling for non-participants

5. **URL Handling**
   - Activity names with spaces (URL encoding)
   - Email addresses with special characters

### Data Integrity Tests (`TestDataIntegrity`)

1. **Data Persistence**
   - Verifies activity data persists across requests

2. **Multiple Activities**
   - Tests students can join multiple activities

3. **Capacity Limits**
   - Validates capacity enforcement across all activities

## Running Tests

### Option 1: Direct pytest
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test class
pytest tests/test_activities_api.py::TestActivitiesAPI -v
```

### Option 2: Using the test runner script
```bash
python run_tests.py
```

This will run all tests with coverage and generate an HTML coverage report.

## Test Dependencies

The following packages are required for testing (included in `requirements.txt`):

- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for testing FastAPI

## Test Fixtures

- `client` - FastAPI test client for making HTTP requests
- `reset_activities` - Resets activity data before each test to ensure test isolation

## Coverage Report

After running tests with coverage, you can view the detailed HTML report by opening:
```
htmlcov/index.html
```

This provides line-by-line coverage analysis of the source code.