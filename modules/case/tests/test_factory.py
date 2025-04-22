from unittest.mock import MagicMock

import pytest

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
    test_case = MatchTestCase(**MatchTestCase.parse_data(base_data))
    test_case.collect_results(sample_response)
    assert test_case.evaluate_results() is True


def test_match_test_case_failure(base_data, sample_response):
    sample_response.status_code = 404
    test_case = MatchTestCase(**MatchTestCase.parse_data(base_data))
    test_case.collect_results(sample_response)
    assert test_case.evaluate_results() is False


# -------- ExactMatchTestCase --------
def test_exact_match_success(base_data, sample_response):
    base_data["expected"]["operators"] = {"expected": "somevalue"}
    test_case = ExactMatchTestCase(**ExactMatchTestCase.parse_data(base_data))
    test_case.collect_results(sample_response)
    assert test_case.evaluate_results() is True


def test_exact_match_fail_text(base_data, sample_response):
    base_data["expected"]["operators"] = {"expected": "wrongvalue"}
    test_case = ExactMatchTestCase(**ExactMatchTestCase.parse_data(base_data))
    test_case.collect_results(sample_response)
    assert not test_case.evaluate_results()


# -------- FuzzyMatchTestCase --------
def test_fuzzy_match_success(base_data, sample_response):
    base_data["expected"]["operators"] = {"expected": "some"}
    test_case = FuzzyMatchTestCase(**FuzzyMatchTestCase.parse_data(base_data))
    test_case.collect_results(sample_response)
    assert test_case.evaluate_results()


def test_fuzzy_match_fail(base_data, sample_response):
    base_data["expected"]["operators"] = {"expected": "notfound"}
    test_case = FuzzyMatchTestCase(**FuzzyMatchTestCase.parse_data(base_data))
    test_case.collect_results(sample_response)
    assert not test_case.evaluate_results()


# -------- FieldMatchTestCase --------
def test_field_match_success(base_data, sample_response):
    base_data["expected"]["operators"] = {"field": "field", "expected": "match"}
    test_case = FieldMatchTestCase(**FieldMatchTestCase.parse_data(base_data))
    test_case.collect_results(sample_response)
    assert test_case.evaluate_results()


def test_field_match_fail(base_data, sample_response):
    base_data["expected"]["operators"] = {"field": "field", "expected": "wrong"}
    test_case = FieldMatchTestCase(**FieldMatchTestCase.parse_data(base_data))
    test_case.collect_results(sample_response)
    assert not test_case.evaluate_results()


# -------- FieldSetMatchTestCase --------
def test_field_set_match_success(base_data, sample_response):
    base_data["expected"]["operators"] = {
        "fields": {"field1": "foo", "field2": "bar"}
    }
    test_case = FieldSetMatchTestCase(**FieldSetMatchTestCase.parse_data(base_data))
    test_case.collect_results(sample_response)
    assert test_case.evaluate_results()


def test_field_set_match_partial_fail(base_data, sample_response):
    base_data["expected"]["operators"] = {
        "fields": {"field1": "foo", "field2": "wrong"}
    }
    test_case = FieldSetMatchTestCase(**FieldSetMatchTestCase.parse_data(base_data))
    test_case.collect_results(sample_response)
    assert not test_case.evaluate_results()


# -------- Edge & Null Cases --------
def test_missing_field_data(base_data):
    base_data.pop("method")
    with pytest.raises(TypeError):
        MatchTestCase(**MatchTestCase.parse_data(base_data))


def test_incorrect_type_field(base_data):
    base_data["expected"]["operators"] = "not-a-dict"
    with pytest.raises(AttributeError):
        FieldMatchTestCase(**FieldMatchTestCase.parse_data(base_data))


def test_null_expected_field(base_data):
    base_data["expected"] = None
    with pytest.raises(AttributeError):
        MatchTestCase(**MatchTestCase.parse_data(base_data))


# -------- Dispatcher --------
def test_testcasebuilder_dispatch_match(base_data):
    base_data["expected"]["operators"] = {"type": "match"}
    case = TestCaseBuilder.build(base_data)
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
class TestCaseBuilderTest:

    @pytest.mark.parametrize("input_data, expected_output", [
        # Test case with comments
        (
                '''{
                    "test_number": 1,
                    "name": "header_injection_Accept",
                    "jira_description" : "",
                    "method": "GET",
                    "url": "https://mdr-api.secure-dev.services/",
                    "headers": {
                        "Host": "mdr-api.secure-dev.services",
                        "User-Agent": "Mozilla/5.0"
                    },
                    "body": {},
                    "parameter": "?sort=1",
                    "expected": {
                        "status_code": 200,
                        "operators": {
                            "type" : "contains",
                            "expected": "somevalue"
                        }
                    }
                } ## Comment here
                ## Comment there''',
                {
                    "test_number": 1,
                    "name": "header_injection_Accept",
                    "jira_description": "",
                    "method": "GET",
                    "url": "https://mdr-api.secure-dev.services/",
                    "headers": {
                        "Host": "mdr-api.secure-dev.services",
                        "User-Agent": "Mozilla/5.0"
                    },
                    "body": {},
                    "parameter": "?sort=1",
                    "expected": {
                        "status_code": 200,
                        "operators": {
                            "type": "contains",
                            "expected": "somevalue"
                        }
                    }
                }
        ),

        # Test case with no comments
        (
                '''{
                    "test_number": 1,
                    "name": "header_injection_Accept",
                    "jira_description" : "",
                    "method": "GET",
                    "url": "https://mdr-api.secure-dev.services/",
                    "headers": {
                        "Host": "mdr-api.secure-dev.services",
                        "User-Agent": "Mozilla/5.0"
                    },
                    "body": {},
                    "parameter": "?sort=1",
                    "expected": {
                        "status_code": 200,
                        "operators": {
                            "type" : "contains",
                            "expected": "somevalue"
                        }
                    }
                }''',
                {
                    "test_number": 1,
                    "name": "header_injection_Accept",
                    "jira_description": "",
                    "method": "GET",
                    "url": "https://mdr-api.secure-dev.services/",
                    "headers": {
                        "Host": "mdr-api.secure-dev.services",
                        "User-Agent": "Mozilla/5.0"
                    },
                    "body": {},
                    "parameter": "?sort=1",
                    "expected": {
                        "status_code": 200,
                        "operators": {
                            "type": "contains",
                            "expected": "somevalue"
                        }
                    }
                }
        ),

        # Test case with empty data
        (
                '',
                {}
        ),

        # Test case with invalid JSON (malformed input)
        (
                '''{
                    "test_number": 1,
                    "name": "header_injection_Accept",
                    "jira_description" : "",
                    "method": "GET",
                    "url": "https://mdr-api.secure-dev.services/"
                ''',
                {}
        )
    ])
    def test_strip_json_comments(self, input_data, expected_output):
        """
        Test _strip_json_comments to ensure it processes and strips comments from JSON correctly.
        """
        result = TestCaseBuilder._strip_json_comments(input_data)
        assert result == expected_output


# Test for different TestCase subclasses

@pytest.mark.parametrize("test_data, expected_result", [
    (
            {
                "test_number": 1,
                "name": "header_injection_Accept",
                "jira_description": "",
                "method": "GET",
                "url": "https://mdr-api.secure-dev.services/",
                "headers": {
                    "Host": "mdr-api.secure-dev.services",
                    "User-Agent": "Mozilla/5.0"
                },
                "body": {},
                "parameter": "?sort=1",
                "expected": {
                    "status_code": 200,
                    "operators": {
                        "type": "match",
                        "expected": "somevalue"
                    }
                }
            },
            True
    ),
])
def test_match_test_case(test_data, expected_result):
    test_case = MatchTestCase(**TestCase.parse_data(test_data))
    test_case.collect_results(MockResponse(200, "somevalue"))
    assert test_case.evaluate_results() == expected_result


@pytest.mark.parametrize("test_data, expected_result", [
    (
            {
                "test_number": 1,
                "name": "ExactMatch",
                "jira_description": "",
                "method": "GET",
                "url": "https://mdr-api.secure-dev.services/",
                "headers": {
                    "Host": "mdr-api.secure-dev.services",
                    "User-Agent": "Mozilla/5.0"
                },
                "body": {},
                "parameter": "?sort=1",
                "expected": {
                    "status_code": 200,
                    "operators": {
                        "type": "exact_match",
                        "expected": "expected_body"
                    }
                }
            },
            True
    ),
])
def test_exact_match_test_case(test_data, expected_result):
    test_case = ExactMatchTestCase(**TestCase.parse_data(test_data))
    test_case.collect_results(MockResponse(200, "expected_body"))
    assert test_case.evaluate_results() == expected_result


@pytest.mark.parametrize("test_data, expected_result", [
    (
            {
                "test_number": 1,
                "name": "FuzzyMatch",
                "jira_description": "",
                "method": "GET",
                "url": "https://mdr-api.secure-dev.services/",
                "headers": {
                    "Host": "mdr-api.secure-dev.services",
                    "User-Agent": "Mozilla/5.0"
                },
                "body": {},
                "parameter": "?sort=1",
                "expected": {
                    "status_code": 200,
                    "operators": {
                        "type": "fuzzy_match",
                        "expected": "somevalue"
                    }
                }
            },
            True
    ),
])
def test_fuzzy_match_test_case(test_data, expected_result):
    test_case = FuzzyMatchTestCase(**TestCase.parse_data(test_data))
    test_case.collect_results(MockResponse(200, "this is somevalue in the body"))
    assert test_case.evaluate_results() == expected_result


@pytest.mark.parametrize("test_data, expected_result", [
    (
            {
                "test_number": 1,
                "name": "FieldMatch",
                "jira_description": "",
                "method": "GET",
                "url": "https://mdr-api.secure-dev.services/",
                "headers": {
                    "Host": "mdr-api.secure-dev.services",
                    "User-Agent": "Mozilla/5.0"
                },
                "body": {},
                "parameter": "?sort=1",
                "expected": {
                    "status_code": 200,
                    "operators": {
                        "type": "field_match",
                        "field": "field",
                        "expected": "value"
                    }
                }
            },
            True
    ),
])
def test_field_match_test_case(test_data, expected_result):
    test_case = FieldMatchTestCase(**TestCase.parse_data(test_data))
    test_case.collect_results(MockResponse(200, '{"field": "value"}'))
    assert test_case.evaluate_results() == expected_result


@pytest.mark.parametrize("test_data, expected_result", [
    (
            {
                "test_number": 1,
                "name": "FieldSetMatch",
                "jira_description": "",
                "method": "GET",
                "url": "https://mdr-api.secure-dev.services/",
                "headers": {
                    "Host": "mdr-api.secure-dev.services",
                    "User-Agent": "Mozilla/5.0"
                },
                "body": {},
                "parameter": "?sort=1",
                "expected": {
                    "status_code": 200,
                    "operators": {
                        "type": "field_set_match",
                        "fields": {
                            "field1": "value1",
                            "field2": "value2"
                        }
                    }
                }
            },
            True
    ),
])
def test_field_set_match_test_case(test_data, expected_result):
    test_case = FieldSetMatchTestCase(**TestCase.parse_data(test_data))
    test_case.collect_results(MockResponse(200, '{"field1": "value1", "field2": "value2"}'))
    assert test_case.evaluate_results() == expected_result
