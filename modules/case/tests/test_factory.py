import json
from typing import Dict, Any
from unittest.mock import MagicMock

import pytest

import modules.case.operators
from modules.case.framework import TestCaseBuilder, TestCase, MatchTestCase, ExactMatchTestCase, FuzzyMatchTestCase, \
    FieldMatchTestCase, FieldSetMatchTestCase


@pytest.fixture
def sample_response():
    response = MagicMock()
    response.status_code = 200
    response.text = "somevalue"
    response.json.return_value = {"key": "value", "field": "match", "field1": "foo", "field2": "bar"}
    return response


@pytest.fixture
def base_data():
    return {
        "test_number": 1,
        "name": "test_case",
        "jira_description": "",
        "method": "GET",
        "url": "https://example.com",
        "headers": {"Accept": "application/json"},
        "body": {},
        "parameter": "?id=1",
        "expected": {
            "status_code": 200,
            "operators": {}
        }
    }


# -------- MatchTestCase --------
def test_match_test_case_success(base_data, sample_response):
    test_case = MatchTestCase(**MatchTestCase.parse_data(base_data).to_dict())
    test_case.collect_results(sample_response)
    eval = test_case.evaluate_results()
    assert eval is True


def test_match_test_case_failure(base_data, sample_response):
    sample_response.status_code = 404
    test_case = MatchTestCase(**MatchTestCase.parse_data(base_data).to_dict())
    test_case.collect_results(sample_response)
    assert test_case.evaluate_results() is False


# -------- ExactMatchTestCase --------
def test_exact_match_success(base_data, sample_response):
    base_data["expected"]["operators"] = {"expected": "somevalue"}
    test_case = ExactMatchTestCase(**ExactMatchTestCase.parse_data(base_data).to_dict())
    test_case.collect_results(sample_response)
    assert test_case.evaluate_results() is True


def test_exact_match_fail_text(base_data, sample_response):
    base_data["expected"]["operators"] = {"expected": "wrongvalue"}
    test_case = ExactMatchTestCase(**ExactMatchTestCase.parse_data(base_data).to_dict())
    test_case.collect_results(sample_response)
    assert not test_case.evaluate_results()


# -------- FuzzyMatchTestCase --------
def test_fuzzy_match_success(base_data, sample_response):
    base_data["expected"]["operators"] = {"expected": "some"}
    test_case = FuzzyMatchTestCase(**FuzzyMatchTestCase.parse_data(base_data).to_dict())
    test_case.collect_results(sample_response)
    assert test_case.evaluate_results()


def test_fuzzy_match_fail(base_data, sample_response):
    base_data["expected"]["operators"] = {"expected": "notfound"}
    test_case = FuzzyMatchTestCase(**FuzzyMatchTestCase.parse_data(base_data).to_dict())
    test_case.collect_results(sample_response)
    assert not test_case.evaluate_results()


# -------- FieldMatchTestCase --------
def test_field_match_success(base_data, sample_response):
    base_data["expected"]["operators"] = {"field": "field", "expected": "match"}
    test_case = FieldMatchTestCase(**FieldMatchTestCase.parse_data(base_data).to_dict())
    test_case.collect_results(sample_response)
    assert test_case.evaluate_results()


def test_field_match_fail(base_data, sample_response):
    base_data["expected"]["operators"] = {"field": "field", "expected": "wrong"}
    test_case = FieldMatchTestCase(**FieldMatchTestCase.parse_data(base_data).to_dict())
    test_case.collect_results(sample_response)
    assert not test_case.evaluate_results()


# -------- FieldSetMatchTestCase --------
def test_field_set_match_success(base_data, sample_response):
    base_data["expected"]["operators"] = {
        "fields": {"field1": "foo", "field2": "bar"}
    }
    test_case = FieldSetMatchTestCase(**FieldSetMatchTestCase.parse_data(base_data).to_dict())
    test_case.collect_results(sample_response)
    assert test_case.evaluate_results()


def test_field_set_match_partial_fail(base_data, sample_response):
    base_data["expected"]["operators"] = {
        "fields": {"field1": "foo", "field2": "wrong"}
    }
    test_case = FieldSetMatchTestCase(**FieldSetMatchTestCase.parse_data(base_data).to_dict())
    test_case.collect_results(sample_response)
    assert not test_case.evaluate_results()


# -------- Edge & Null Cases --------
def test_missing_field_data(base_data):
    base_data.pop("method")
    with pytest.raises(TypeError):
        data: dict[str, Any] = MatchTestCase.parse_data(base_data).to_dict()
        data.pop("method")
        MatchTestCase(data)


def test_incorrect_type_field(base_data):
    base_data["expected"]["operators"] = "not-a-dict"
    with pytest.raises(AttributeError):
        data: dict[str, Any] = FieldMatchTestCase.parse_data(base_data).to_dict()
        data["expected"]["operators"] = "not-a-dict"
        FieldMatchTestCase(**FieldMatchTestCase.parse_data(base_data).to_dict())


def test_null_expected_field(base_data):
    base_data["expected"] = None
    with pytest.raises(AttributeError):
        MatchTestCase(**MatchTestCase.parse_data(base_data).to_dict())


# -------- Dispatcher --------
def test_testcasebuilder_dispatch_match(base_data):
    base_data["expected"]["operators"] = {"type": "match"}
    case = TestCaseBuilder.build(base_data).pop()
    assert isinstance(case, MatchTestCase)


def test_testcasebuilder_dispatch_unknown(base_data):
    base_data["expected"]["operators"] = {"type": "nonexistent"}
    with pytest.raises(ValueError):
        TestCaseBuilder.build(base_data)


# Mock Response for testing
class MockResponse:
    def __init__(self, status_code, text, json_data=None):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


# Tests for _strip_json_comments method
