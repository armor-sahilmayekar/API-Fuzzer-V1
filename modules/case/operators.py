import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from modules.export.report import TestReport
from modules.util.loggable import Loggable as log


class HTTPMethod:
    """Common HTTP methods for standardization and reference."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class Expected:
    """
    Data structure to hold the expected test results.
    """
    status_code: int
    operators: Dict[str, Any]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Expected":
        log.debug(f"Creating Expected object from dictionary {data}")
        return Expected(
            status_code=data.get("status_code"),
            operators=data.get("operators", {})
        )


@dataclass
class TestCaseData:
    """
    Represents the structured data for an individual test case.

    Attributes:
        test_number (int): A unique identifier for the test.
        name (str): A human-readable name for the test case.
        jira_description (str): Optional link or reference to JIRA documentation.
        method (str): The HTTP method to use (GET, POST, etc.).
        url (str): The full target URL (excluding query params).
        headers (Dict[str, str]): HTTP headers to include with the request.
        body (Any): The body of the request (for POST/PUT methods).
        parameter (str): Query parameters as a string (e.g., '?id=5').
        expected (Expected): An `Expected` object that defines the result criteria.
    """
    test_number: int
    name: str
    jira_description: str
    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = field(default_factory=dict)
    parameter: str = ""
    expected: Expected = field(default_factory=Expected)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TestCaseData":
        """
        Parse raw dictionary data into a structured `TestCaseData` object.

        Args:
            data (Dict[str, Any]): Raw test case dictionary from a JSON file.

        Returns:
            TestCaseData: A populated dataclass instance.
        """
        log.debug(f"Parsing data for test: {data.get('name')} using {data}")
        return TestCaseData(
            test_number=data.get("test_number"),
            name=data.get("name"),
            jira_description=data.get("jira_description", ""),
            method=data.get("method", HTTPMethod.GET).upper(),
            url=data.get("url"),
            headers=data.get("headers", {}),
            body=data.get("body", {}),
            parameter=data.get("parameter", ""),
            expected=Expected.from_dict(data.get("expected", {}))
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the TestCaseData object to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary with all attributes of TestCaseData.
        """
        return {
            "test_number": self.test_number,
            "name": self.name,
            "jira_description": self.jira_description,
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "parameter": self.parameter,
            "expected": {
                "status_code": self.expected.status_code,
                "operators": self.expected.operators
            }
        }

class TestCase(ABC):
    """
    Abstract base class for all test cases. Implements reusable logic for execution,
    evaluation, and reporting of HTTP-based security test scenarios.
    """

    def __init__(
            self,
            test_number: int,
            name: str,
            jira_description: str,
            method: str,
            url: str,
            headers: Dict[str, str],
            body: Any,
            parameter: str,
            expected: Expected
    ):
        self._test_number = test_number
        self._name = name
        self._jira_description = jira_description
        self._method = method.upper()
        self._url = url
        self._headers = headers
        self._body = body
        self._parameter = parameter
        self._expected = expected
        self._response: Optional[requests.Response] = None

        self._session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    @property
    def test_number(self) -> int:
        return self._test_number

    @property
    def name(self) -> str:
        return self._name

    @property
    def method(self) -> str:
        return self._method

    @property
    def url(self) -> str:
        return self._url

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @property
    def body(self) -> Any:
        return self._body

    @property
    def parameter(self) -> str:
        return self._parameter

    @property
    def expected(self) -> Expected:
        return self._expected

    @property
    def response(self) -> Optional[requests.Response]:
        return self._response

    @staticmethod
    def parse_data(data: Dict[str, Any]) -> TestCaseData:
        return TestCaseData.from_dict(data)

    def collect_results(self, response: requests.Response):
        """Store HTTP response after request execution."""
        self._response = response

    @abstractmethod
    def evaluate_results(self) -> bool:
        """
        Evaluate response against expected criteria.
        Must be implemented in subclasses.
        """
        pass

    def execute(self):
        """
        Perform the HTTP request using session with:
        - Timeout
        - Retries
        - Form and raw body support
        - Logging and timing
        """
        full_url = self.url + self.parameter if self.parameter else self.url
        timeout = 10  # seconds

        log.info(f"[{self.test_number}] Starting execution: {self.method} {full_url}")
        log.debug(f"[{self.test_number}] Request headers: {self.headers}")
        log.debug(f"[{self.test_number}] Request body: {self.body if self.method != HTTPMethod.GET else 'N/A'}")

        try:
            start_time = time.time()
            method = self.method

            if method == HTTPMethod.GET:
                response = self._session.get(full_url, headers=self.headers, timeout=timeout)
            elif method == HTTPMethod.POST:
                response = self._handle_post_or_put("POST", full_url, timeout)
            elif method == HTTPMethod.PUT:
                response = self._handle_post_or_put("PUT", full_url, timeout)
            elif method == HTTPMethod.DELETE:
                response = self._session.delete(full_url, headers=self.headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {self.method}")

            duration = time.time() - start_time
            log.info(f"[{self.test_number}] Request completed in {duration:.2f}s with status {response.status_code}")
            log.debug(f"[{self.test_number}] Response body: {response.text[:500]}")

            self.collect_results(response)

        except requests.RequestException as e:
            log.error(f"[{self.test_number}] Request failed: {e}")
            self._response = None
        except Exception as e:
            log.error(f"[{self.test_number}] Unexpected error during execution: {e}")
            self._response = None

    def save_report(self):
        """Create and persist a structured test report."""
        log.info(f"[{self.test_number}] Saving report for test '{self.name}'")
        report = TestReport(name=self.name)
        report.add("test_number", self.test_number)
        report.add("state", "COMPLETED")
        report.add("request_url", self.url + self.parameter)
        report.add("request_method", self.method)
        report.add("request_headers", self.headers)
        report.add("request_body", self.body)
        report.add("response", {
            "status_code": self.response.status_code,
            "text": self.response.text
        } if self.response else "No response")

        passed = self.evaluate_results()
        report.set_status("passed" if passed else "failed")

        log.info(f"[{self.test_number}] Test result: {'PASSED' if passed else 'FAILED'}")
        if self.response:
            log.debug(f"[{self.test_number}] Final status code: {self.response.status_code}")
            log.debug(f"[{self.test_number}] Final response snippet: {self.response.text[:300]}")

        report.save()
        log.info(f"[{self.test_number}] Report saved successfully")

    def _handle_post_or_put(self, method: str, url: str, timeout: int) -> requests.Response:
        """
        Helper to handle POST/PUT requests for both raw and form-encoded data.
        """
        if isinstance(self.body, dict):
            return self._session.request(method, url, headers=self.headers, json=self.body, timeout=timeout)
        else:
            return self._session.request(method, url, headers=self.headers, data=self.body, timeout=timeout)


class MatchTestCase(TestCase):
    """Test case that checks status code match only."""

    def evaluate_results(self) -> bool:
        return self.response and self.response.status_code == self.expected.status_code


class ExactMatchTestCase(TestCase):
    """Test case that requires exact response body match."""

    def evaluate_results(self) -> bool:
        return (
                self.response and
                self.response.status_code == self.expected.status_code and
                self.response.text.strip() == self.expected.operators.get("expected", "").strip()
        )


class FuzzyMatchTestCase(TestCase):
    """Test case that checks if a substring exists in the response body."""

    def evaluate_results(self) -> bool:
        return (
                self.response and
                self.response.status_code == self.expected.status_code and
                self.expected.operators.get("expected", "") in self.response.text
        )


class FieldMatchTestCase(TestCase):
    """Test case that validates a specific field in a JSON response."""

    def evaluate_results(self) -> bool:
        if not self.response:
            return False
        try:
            json_body = self.response.json()
            field = self.expected.operators.get("field")
            expected_value = self.expected.operators.get("expected")
            return json_body.get(field) == expected_value
        except Exception:
            return False


class FieldSetMatchTestCase(TestCase):
    """Test case that matches a set of fields in a JSON response."""

    def evaluate_results(self) -> bool:
        if not self.response:
            return False
        try:
            json_body = self.response.json()
            fields = self.expected.operators.get("fields", {})
            return all(json_body.get(k) == v for k, v in fields.items())
        except Exception:
            return False
