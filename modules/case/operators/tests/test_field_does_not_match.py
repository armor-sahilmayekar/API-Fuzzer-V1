import pytest
from unittest.mock import MagicMock, patch
from requests.models import Response

from modules.case.operators.field.exclude import FieldDoesNotMatchTestCase
from modules.case.operators.tests import DummyExpected


@pytest.fixture
def mock_response():
    # Create a mock response object
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"response_field": "value_to_check"}
    return mock_response


@pytest.fixture
def test_case(mock_response):
    # Create a sample instance of FieldDoesNotMatchTestCase with mock response
    expected_data = {"type": "does_not_match", "field": "response_field", "expected": "^unexpected_value$"}

    expected = MagicMock()
    expected.status_code = 200
    expected.expected = expected_data["expected"]

    test_case = FieldDoesNotMatchTestCase(
        test_number=1,
        name="Test case for DoesNotMatch",
        jira_description="Test case for checking regex non-matching",
        method="GET",
        url="http://test.com",
        headers={},
        body=None,
        parameter="",
        expected=[DummyExpected(payload=expected_data)]
    )
    test_case._response = mock_response
    return test_case

@pytest.fixture
def patch_session_get(mock_response):
    with patch("requests.Session.get") as mock_get:
        mock_get.return_value = mock_response
        yield mock_get

def test_does_not_match_success(test_case, patch_session_get):
    """Test case where the field matches the 'does not match' regex."""
    test_case.execute()
    result = test_case.evaluate_results()
    assert result is True, "Expected result to be True, as value doesn't match the regex."


def test_does_not_match_failure(test_case, patch_session_get):
    """Test case where the field matches the 'does not match' regex (failure case)."""
    test_case.response.json.return_value = {"response_field": "unexpected_value"}
    result = test_case.evaluate_results()
    assert result is False, "Expected result to be False, as value matches the regex."


def test_does_not_match_no_field(test_case, patch_session_get):
    """Test case where the field doesn't exist in the response."""
    test_case.response.json.return_value = {}
    result = test_case.evaluate_results()
    assert result is True, "Expected result to be True, as the field doesn't exist."


def test_does_not_match_no_response(test_case, patch_session_get):
    """Test case where there is no response."""
    test_case._response = None
    result = test_case.evaluate_results()
    assert result is False, "Expected result to be False, as no response is available."


def test_does_not_match_invalid_status_code(test_case, patch_session_get):
    """Test case where the status code does not match."""
    test_case.response.status_code = 404
    result = test_case.evaluate_results()
    assert result is False, "Expected result to be False, as status code doesn't match."


def test_match_regex_edge_case(test_case, patch_session_get):
    """Test case where regex matching with edge case input."""
    test_case.response.json.return_value = {"response_field": "valid_value"}
    test_case.expected[0]._expected = "^valid_value$"
    result = test_case.evaluate_results()
    assert result is False, "Expected result to be False, as value matches the regex."


def test_empty_field(test_case, patch_session_get):
    """Test case where the field is empty in response."""
    test_case.response.json.return_value = {}
    test_case.expected[0]._field = "response_field"
    result = test_case.evaluate_results()
    assert result is True, "Expected result to be True, as the field is empty and doesn't match."


if __name__ == "__main__":
    pytest.main()
