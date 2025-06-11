import pytest
from unittest.mock import patch, MagicMock
from requests.models import Response
from modules.case.operators.field.exclude import FieldNotExistTestCase
from modules.case.data_objects import Expected
from modules.case.operators.tests import DummyExpected


@pytest.fixture
def mock_response():
    response = Response()
    response.status_code = 200
    return response

@pytest.fixture
def patch_session_get(mock_response):
    with patch("requests.Session.get") as mock_get:
        mock_get.return_value = mock_response
        yield mock_get

def test_field_not_exist_success(patch_session_get):
    expected_payload = {
      "type": "field_not_exist",
      "field": "sensitive_info",
      "expected": None
    }
    test_case = FieldNotExistTestCase(
        test_number=1,
        name="Field Not Exist Success",
        jira_description="",
        method="GET",
        url="https://example.com",
        headers={},
        body={},
        parameter="",
        expected=[DummyExpected(payload=expected_payload)]
    )
    test_case.execute()
    test_case.response._content = b'{"username": "user1", "email": "user1@example.com"}'
    test_case.response.json = lambda: {"username": "user1", "email": "user1@example.com"}
    assert test_case.evaluate_results() is True

def test_field_not_exist_failure(patch_session_get):
    expected_payload = {
      "type": "field_not_exist",
      "field": "sensitive_info",
      "expected": None
    }
    test_case = FieldNotExistTestCase(
        test_number=2,
        name="Field Not Exist Failure",
        jira_description="",
        method="GET",
        url="https://example.com",
        headers={},
        body={},
        parameter="",
        expected=[DummyExpected(payload=expected_payload)]
    )
    test_case.execute()
    test_case.response._content = b'{"sensitive_info": "secret_value", "username": "user2"}'
    test_case.response.json = lambda: {"sensitive_info": "secret_value", "username": "user2"}
    assert test_case.evaluate_results() is False

def test_field_not_exist_null_response():
    expected_payload = {
      "type": "field_not_exist",
      "field": "sensitive_info",
      "expected": None
    }
    test_case = FieldNotExistTestCase(
        test_number=3,
        name="Field Not Exist Null",
        jira_description="",
        method="GET",
        url="https://example.com",
        headers={},
        body={},
        parameter="",
        expected=[DummyExpected(payload=expected_payload)]
    )
    test_case.execute()
    test_case._response._content = ""  # simulate missing response
    assert test_case.evaluate_results() is False

def test_field_not_exist_null2_response():
    expected_payload = {
      "type": "field_not_exist",
      "field": "sensitive_info",
      "expected": None
    }
    test_case = FieldNotExistTestCase(
        test_number=3,
        name="Field Not Exist Null",
        jira_description="",
        method="GET",
        url="https://example.com",
        headers={},
        body={},
        parameter="",
        expected=[DummyExpected(payload=expected_payload)]
    )
    test_case.execute()
    test_case._response._content = None  # simulate missing response
    assert test_case.evaluate_results() is False