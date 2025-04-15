import pytest
import json
from unittest.mock import MagicMock

#TODO fix this
from validator import TestRunner, load_test_cases
from modules.export.writer import ReportWriter
from modules.api.client import APIClient

@pytest.fixture
def mock_report_writer() -> MagicMock:
    """
    Creates a mock of the ReportWriter to avoid writing actual files during testing.

    Returns:
        MagicMock: A mock instance of ReportWriter.
    """
    return MagicMock(ReportWriter)


@pytest.fixture
def mock_api_client() -> MagicMock:
    """
    Creates a mock of the APIClient to simulate API calls in tests.

    Returns:
        MagicMock: A mock instance of APIClient.
    """
    return MagicMock(APIClient)


@pytest.fixture
def test_runner(mock_api_client: MagicMock, mock_report_writer: MagicMock) -> TestRunner:
    """
    Creates an instance of TestRunner with mocked dependencies for testing.

    Args:
        mock_api_client (MagicMock): The mocked APIClient instance.
        mock_report_writer (MagicMock): The mocked ReportWriter instance.

    Returns:
        TestRunner: A TestRunner instance with mocked APIClient and ReportWriter.
    """
    return TestRunner(mock_api_client, mock_report_writer)


def test_run_tests(test_runner: TestRunner, mock_api_client: MagicMock, mock_report_writer: MagicMock):
    """
    Test the `run_tests` method of TestRunner to ensure export are generated correctly.

    Args:
        test_runner (TestRunner): The instance of TestRunner to be tested.
        mock_api_client (MagicMock): The mocked APIClient.
        mock_report_writer (MagicMock): The mocked ReportWriter.

    Returns:
        None
    """
    # Mock test case
    test_case = {
        "test_number": 1,
        "name": "test_get_incidents",
        "method": "GET",
        "endpoint": "/incidents",
        "params": {"status": "Closed"},
        "expected_status": 200
    }

    # Mock API client response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.url = "https://mdr-api.secure-dev.services/incidents?status=Closed"
    mock_response.text = '{"totalRows": 10, "issues": []}'
    mock_response.request.headers = {"Authorization": "Bearer fake_api_key"}
    mock_api_client.send_request.return_value = mock_response

    # Run the test
    test_runner.run_tests([test_case])

    # Check that the report_writer was called with the correct data
    mock_report_writer.write_report.assert_called_once()

    # Verify that the export data contains expected values
    report_data = mock_report_writer.write_report.call_args[0][0]
    assert report_data["state"] == "PASSED"
    assert report_data["test_number"] == 1
    assert report_data["name"] == "test_get_incidents"
    assert report_data["status"] == "success"


def test_load_test_cases() -> None:
    """
    Test the `load_test_cases` function to ensure test cases are loaded correctly from a JSON file.

    Returns:
        None
    """
    # Mock test case JSON file content
    test_cases_json = [
        {
            "test_number": 1,
            "name": "test_get_incidents",
            "method": "GET",
            "endpoint": "/incidents",
            "params": {"status": "Closed"},
            "expected_status": 200
        }
    ]
    with open("../test_cases.json", "w") as f:
        json.dump(test_cases_json, f)

    # Load test cases
    loaded_test_cases = load_test_cases("test_cases.json")

    # Verify that the loaded data matches the expected test cases
    assert len(loaded_test_cases) == 1
    assert loaded_test_cases[0]["name"] == "test_get_incidents"
    assert loaded_test_cases[0]["test_number"] == 1
