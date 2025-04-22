
from typing import Dict, List

from modules.case.operators import *
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
