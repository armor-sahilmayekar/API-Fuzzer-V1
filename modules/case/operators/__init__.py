import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from modules.export.report import TestReport
from modules.case.data_objects import Expected, TestCaseData, HTTPMethod
from modules.util.loggable import Loggable as log
from dataclasses import dataclass
from typing import Any, Union, Dict



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
            expected: [Expected]
    ) -> object:
        self._test_number = test_number
        self._name = name
        self._jira_description = jira_description
        self._method = HTTPMethod.get_method_property(method.upper())
        self._url = url
        self._headers = headers
        self._body = body
        self._parameter = parameter
        if isinstance(expected, dict):
            self._expected = [Expected.from_dict(expected)]
        elif isinstance(expected, Expected):
            self._expected = [expected]
        elif all(isinstance(item, Expected) for item in expected):
            self._expected = expected
        else:
            raise ValueError(f"Expected {type(Expected)} but got {type(expected)}")
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

