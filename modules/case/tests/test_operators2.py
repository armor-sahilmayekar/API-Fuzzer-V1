import pytest
from unittest.mock import MagicMock, patch
from requests import Response

from modules.case.operators import (
    MatchTestCase,
    ExactMatchTestCase,
    FuzzyMatchTestCase,
    FieldMatchTestCase,
    FieldSetMatchTestCase,
    Expected,
)


def mock_response(status=200, text="", json_data=None):
    """
    Helper to create a mock Response object.
    """
    response = MagicMock(spec=Response)
    response.status_code = status
    response.text = text
    response.json.return_value = json_data or {}
    return response


@pytest.fixture
def base_args():
    return {
        "test_number": 1,
        "name": "Basic Test",
        "jira_description": "JIRA-123",
        "method": "GET",
        "url": "http://example.com",
        "headers": {},
        "body": {},
        "parameter": "",
    }


def test_match_test_case_pass(base_args):
    """
    Should pass if status code matches expected.
    """
    expected = Expected(status_code=200, operators={})
    case = MatchTestCase(**base_args, expected=expected)
    case.collect_results(mock_response(status=200))
    assert case.evaluate_results()


def test_match_test_case_fail(base_args):
    """
    Should fail if status code does not match.
    """
    expected = Expected(status_code=404, operators={})
    case = MatchTestCase(**base_args, expected=expected)
    case.collect_results(mock_response(status=200))
    assert not case.evaluate_results()


def test_exact_match_pass(base_args):
    """
    Should pass if status code and response body match exactly.
    """
    expected = Expected(status_code=200, operators={"expected": "Success"})
    case = ExactMatchTestCase(**base_args, expected=expected)
    case.collect_results(mock_response(status=200, text="Success"))
    assert case.evaluate_results()


def test_exact_match_fail_body(base_args):
    """
    Should fail if response body does not match.
    """
    expected = Expected(status_code=200, operators={"expected": "Expected"})
    case = ExactMatchTestCase(**base_args, expected=expected)
    case.collect_results(mock_response(status=200, text="Wrong"))
    assert not case.evaluate_results()


def test_fuzzy_match_pass(base_args):
    """
    Should pass if expected substring is in response.
    """
    expected = Expected(status_code=200, operators={"expected": "needle"})
    case = FuzzyMatchTestCase(**base_args, expected=expected)
    case.collect_results(mock_response(status=200, text="haystack needle haystack"))
    assert case.evaluate_results()


def test_fuzzy_match_fail(base_args):
    """
    Should fail if expected substring is missing.
    """
    expected = Expected(status_code=200, operators={"expected": "missing"})
    case = FuzzyMatchTestCase(**base_args, expected=expected)
    case.collect_results(mock_response(status=200, text="nothing here"))
    assert not case.evaluate_results()


def test_field_match_pass(base_args):
    """
    Should pass if JSON field matches expected value.
    """
    expected = Expected(status_code=200, operators={"field": "status", "expected": "ok"})
    case = FieldMatchTestCase(**base_args, expected=expected)
    case.collect_results(mock_response(status=200, json_data={"status": "ok"}))
    assert case.evaluate_results()


def test_field_match_fail_value(base_args):
    """
    Should fail if field value is incorrect.
    """
    expected = Expected(status_code=200, operators={"field": "status", "expected": "ok"})
    case = FieldMatchTestCase(**base_args, expected=expected)
    case.collect_results(mock_response(status=200, json_data={"status": "fail"}))
    assert not case.evaluate_results()


def test_field_set_match_pass(base_args):
    """
    Should pass if all fields match their expected values.
    """
    expected = Expected(
        status_code=200,
        operators={"fields": {"status": "ok", "version": "1.2"}}
    )
    case = FieldSetMatchTestCase(**base_args, expected=expected)
    case.collect_results(mock_response(status=200, json_data={"status": "ok", "version": "1.2"}))
    assert case.evaluate_results()


def test_field_set_match_fail_partial(base_args):
    """
    Should fail if any one field does not match.
    """
    expected = Expected(
        status_code=200,
        operators={"fields": {"status": "ok", "version": "1.2"}}
    )
    case = FieldSetMatchTestCase(**base_args, expected=expected)
    case.collect_results(mock_response(status=200, json_data={"status": "ok", "version": "1.0"}))
    assert not case.evaluate_results()
