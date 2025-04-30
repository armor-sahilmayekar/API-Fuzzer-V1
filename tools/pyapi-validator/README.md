
# API Testing Framework

This repository contains an API testing framework that helps you validate API endpoints, generate detailed reports, and log test results. The framework is designed to support customizable test cases loaded from JSON files and includes features such as API call verification, status checking, and report generation.

## Features
- **Customizable Test Cases**: Load test cases from a JSON file with test inputs, expected responses, and verification logic.
- **API Call Simulation**: Send API requests and simulate responses for verification.
- **Detailed Reporting**: For each test, a report is generated in JSON format, containing detailed information on the test status, request details, and response.
- **Directory-Based Reporting**: Reports are stored in a subdirectory named with the datetime of the test run for easy tracking.

## Requirements

- Python 3.6+
- `requests` library for sending API requests
- `pytest` for testing framework
- `unittest.mock` for mocking external dependencies in tests

### Install Required Packages

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/api-testing-framework.git
   cd api-testing-framework
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Files Structure

- **`main.py`**: Contains the core logic for sending API requests, handling test cases, and writing reports.
- **`test_api.py`**: Contains unit tests for testing the API client, report writer, and overall test runner.
- **`test_cases.json`**: A JSON file where test cases are defined (endpoints, expected results, etc.).
- **`requirements.txt`**: List of Python packages required for the project.
- **`reports/`**: Directory where test reports are saved.

## Running the Tests

### Test the Framework

To run the tests for the framework, use `pytest`:

```bash
pytest test_api.py
```

This will run all tests in the `test_api.py` file, ensuring that the components of the framework are working correctly.

### Running the Test Suite

1. Ensure that the `test_cases.json` file exists and contains the test cases you want to run. Example:

   ```json
   [
     {
       "test_number": 1,
       "name": "test_get_incidents",
       "method": "GET",
       "endpoint": "/incidents",
       "params": {"status": "Closed"},
       "expected_status": 200
     }
   ]
   ```

2. Run the tests with the following command:

   ```bash
   python validate.py --reports_dir /path/to/export/directory
   ```

   This will run the tests based on the test cases defined in the `test_cases.json` file and save the reports in the specified directory.

### Example Output:

After running the tests, you will see output similar to this:

```
Running tests...
Tests completed. Reports saved in /path/to/reports/directory/2025-04-14_10-30-00/
```

### Report Format

Each test report is saved as a JSON file with the following structure:

```json
{
    "status": "success",
    "name": "test_get_incidents",
    "sub_reports": [],
    "test_number": 1,
    "state": "PASSED",
    "request_url": "https://mdr.api.secure-dev.services/metrics/incidents?status=Closed",
    "request_method": "GET",
    "request_headers": "{"Authorization": "Bearer fake_api_key"}",
    "exception": "",
    "request_body": {},
    "response": "{"totalRows": 10, "issues": []}",
    "details": "",
    "reason": "request_passed"
}
```

## Code Overview

### `main.py`

This file is the core of the testing framework. It contains the following key classes:

- **`APIClient`**: Handles sending API requests and receiving responses.
- **`TestRunner`**: Reads the test cases, runs them, and generates reports.
- **`ReportWriter`**: Writes the test results to the filesystem in a specified directory.

### `test_api.py`

This file contains unit tests for the classes and methods in `main.py`. It includes tests for:

- Mocking the API client and checking if the requests are being made correctly.
- Verifying the report writing logic to ensure proper report structure.
- Validating the loading of test cases from a JSON file.

### `test_cases.json`

This JSON file contains the test cases with the following structure:

- **`test_number`**: The unique identifier for the test case.
- **`name`**: The name of the test.
- **`method`**: The HTTP method (e.g., `GET`, `POST`).
- **`endpoint`**: The API endpoint to be tested.
- **`params`**: The query parameters for the request.
- **`expected_status`**: The expected status code of the response.

### Report Structure

The reports generated are stored in a subdirectory named with the datetime of the test run. Each individual test case gets its own JSON report.

