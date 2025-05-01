import pytest
from unittest.mock import patch, MagicMock
from requests.models import Response
from modules.case.operators.payload import ExactPayloadMatchTestCase
from modules.case.operators.tests import DummyExpected


@pytest.fixture
def mock_response():
    response = Response()
    response.status_code = 200
    response._content = b'{"key": "value"}'
    return response

@pytest.fixture
def patch_session_get(mock_response):
    with patch("requests.Session.get") as mock_get:
        mock_get.return_value = mock_response
        yield mock_get

def test_exact_payload_match_success(patch_session_get):
    expected_payload = {
      "type": "payload",
      "field": "all",
      "expected": {"key": "value"}
    }

    test_case = ExactPayloadMatchTestCase(
        test_number=1,
        name="Exact Payload Success",
        jira_description="",
        method="GET",
        url="https://example.com",
        headers={},
        body={},
        parameter="",
        expected=[DummyExpected(payload=expected_payload)]
    )
    test_case.execute()
    test_case.response._content = b'{"key": "value"}'
    test_case.response.json = lambda: {"key": "value"}
    assert test_case.evaluate_results() is True

def test_exact_payload_match_failure(patch_session_get):
    expected_payload = {
        "type": "payload",
        "field": "all",
        "expected": {"key": "different"}
      }
    test_case = ExactPayloadMatchTestCase(
        test_number=2,
        name="Exact Payload Failure",
        jira_description="",
        method="GET",
        url="https://example.com",
        headers={},
        body={},
        parameter="",
        expected=[DummyExpected(payload=expected_payload)]
    )
    test_case.execute()
    test_case.response._content = b'{"key": "value"}'
    test_case.response.json = lambda: {"key": "value"}
    assert test_case.evaluate_results() is False

def test_exact_payload_match_null_response():
    expected_payload = {
      "type": "payload",
      "field": "all",
      "expected": {"key": "value"}
    }

    test_case = ExactPayloadMatchTestCase(
        test_number=3,
        name="Exact Payload Null",
        jira_description="",
        method="GET",
        url="https://example.com",
        headers={},
        body={},
        parameter="",
        expected=[DummyExpected(payload=expected_payload)]
    )
    test_case._response = None  # simulate no response received
    assert test_case.evaluate_results() is False
