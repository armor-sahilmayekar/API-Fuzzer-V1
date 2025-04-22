import pytest
import requests
from unittest.mock import patch
from modules.util.loggable import Loggable as log
from modules.export.report import TestReport
from modules.case.operators import (HTTPMethod, TestCaseData, Expected, MatchTestCase, ExactMatchTestCase,
                                    FuzzyMatchTestCase, FieldMatchTestCase, FieldSetMatchTestCase)


@pytest.fixture
def mock_response():
    """Fixture to mock a requests Response object."""
    mock_resp = requests.Response()
    mock_resp.status_code = 200
    mock_resp._content = b'{"status": "ok"}'
    return mock_resp


@pytest.fixture
def test_case_data():
    """Fixture to create sample test case data."""
    expected = Expected(status_code=200, operators={"expected": {"status": "ok"}})
    return TestCaseData(
        test_number=1,
        name="Test GET request",
        jira_description="https://jira.example.com/12345",
        method=HTTPMethod.GET,
        url="https://httpbin.org/get",
        headers={"Content-Type": "application/json"},
        body={},
        parameter="",
        expected=expected,
    )


@pytest.fixture
def test_case(test_case_data):
    """Fixture to create an actual test case."""
    return MatchTestCase(
        test_case_data.test_number,
        test_case_data.name,
        test_case_data.jira_description,
        test_case_data.method,
        test_case_data.url,
        test_case_data.headers,
        test_case_data.body,
        test_case_data.parameter,
        test_case_data.expected,
    )


def test_http_method_enum():
    """Test to verify that HTTPMethod enum contains all standard methods."""
    assert HTTPMethod.GET == "GET"
    assert HTTPMethod.POST == "POST"
    assert HTTPMethod.PUT == "PUT"
    assert HTTPMethod.DELETE == "DELETE"
    assert HTTPMethod.PATCH == "PATCH"
    assert HTTPMethod.HEAD == "HEAD"
    assert HTTPMethod.OPTIONS == "OPTIONS"


def test_expected_from_dict():
    """Test the Expected class conversion from a dictionary."""
    data = {
        "status_code": 200,
        "operators": {"expected": "ok"}
    }
    expected = Expected.from_dict(data)

    assert expected.status_code == 200
    assert expected.operators == {"expected": "ok"}


def test_test_case_data_from_dict():
    """Test the TestCaseData class conversion from a dictionary."""
    data = {
        "test_number": 1,
        "name": "Test GET request",
        "jira_description": "https://jira.example.com/12345",
        "method": HTTPMethod.GET,
        "url": "https://httpbin.org/get",
        "headers": {"Content-Type": "application/json"},
        "body": {},
        "parameter": "",
        "expected": {
            "status_code": 200,
            "operators": {"expected": "ok"}
        }
    }
    test_case_data = TestCaseData.from_dict(data)

    assert test_case_data.test_number == 1
    assert test_case_data.name == "Test GET request"
    assert test_case_data.jira_description == "https://jira.example.com/12345"
    assert test_case_data.method == HTTPMethod.GET
    assert test_case_data.url == "https://httpbin.org/get"
    assert test_case_data.expected.status_code == 200


def test_execute_get_request(test_case, mock_response):
    """Test the execute method for a GET request."""
    with patch.object(test_case._session, "get", return_value=mock_response) as mock_get:
        test_case.execute()
        mock_get.assert_called_once_with(test_case.url, headers=test_case.headers, timeout=10)
        assert test_case.response.status_code == 200
        assert test_case.response.text == '{"status": "ok"}'


def test_evaluate_results_match(test_case, mock_response):
    """Test the evaluation logic for a MatchTestCase (status code match)."""
    test_case.collect_results(mock_response)
    result = test_case.evaluate_results()
    assert result is True


def test_evaluate_results_failure(test_case, mock_response):
    """Test the evaluation logic when the result does not match."""
    # Modify the mock response to simulate a failure
    mock_response.status_code = 500
    test_case.collect_results(mock_response)
    result = test_case.evaluate_results()
    assert result is False


def test_save_report(test_case, mock_response):
    """Test the saving of a report after test execution."""
    test_case.collect_results(mock_response)

    with patch.object(TestReport, "save") as mock_save:
        test_case.save_report()
        mock_save.assert_called_once()
        assert test_case.response.status_code == 200


def test_exact_match_test_case(test_case_data):
    """Test the ExactMatchTestCase class logic."""
    expected = Expected(status_code=200, operators={"expected": "ok"})
    test_case_data.expected = expected
    test_case = ExactMatchTestCase(
        test_case_data.test_number,
        test_case_data.name,
        test_case_data.jira_description,
        test_case_data.method,
        test_case_data.url,
        test_case_data.headers,
        test_case_data.body,
        test_case_data.parameter,
        test_case_data.expected,
    )

    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'ok'
    test_case.collect_results(mock_response)
    result = test_case.evaluate_results()
    assert result is True


def test_fuzzy_match_test_case(test_case_data):
    """Test the FuzzyMatchTestCase class logic."""
    expected = Expected(status_code=200, operators={"expected": "ok"})
    test_case_data.expected = expected
    test_case = FuzzyMatchTestCase(
        test_case_data.test_number,
        test_case_data.name,
        test_case_data.jira_description,
        test_case_data.method,
        test_case_data.url,
        test_case_data.headers,
        test_case_data.body,
        test_case_data.parameter,
        test_case_data.expected,
    )

    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'{"status": "ok"}'
    test_case.collect_results(mock_response)

    assert test_case.evaluate_results() is True


def test_field_match_test_case(test_case_data):
    """Test the FieldMatchTestCase class logic."""
    expected = Expected(status_code=200, operators={"field": "status", "expected": "ok"})
    test_case_data.expected = expected
    test_case = FieldMatchTestCase(
        test_case_data.test_number,
        test_case_data.name,
        test_case_data.jira_description,
        test_case_data.method,
        test_case_data.url,
        test_case_data.headers,
        test_case_data.body,
        test_case_data.parameter,
        test_case_data.expected,
    )

    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'{"status": "ok"}'
    test_case.collect_results(mock_response)

    assert test_case.evaluate_results() is True


def test_field_set_match_test_case(test_case_data):
    """Test the FieldSetMatchTestCase class logic."""
    expected = Expected(status_code=200, operators={"fields": {"status": "ok", "message": "success"}})
    test_case_data.expected = expected
    test_case = FieldSetMatchTestCase(
        test_case_data.test_number,
        test_case_data.name,
        test_case_data.jira_description,
        test_case_data.method,
        test_case_data.url,
        test_case_data.headers,
        test_case_data.body,
        test_case_data.parameter,
        test_case_data.expected,
    )

    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'{"status": "ok", "message": "success"}'
    test_case.collect_results(mock_response)

    assert test_case.evaluate_results() is True
