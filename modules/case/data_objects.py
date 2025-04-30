
from typing import Dict, List

from modules.case.operators import *
from modules.util.loggable import Loggable as log


class HTTPMethod:
    """
    Common HTTP methods for standardization and reference.

    This class defines standard HTTP methods as class constants and provides
    utility methods to validate and retrieve the correct HTTP method property.

    Class Constants:
        GET (str): HTTP GET method.
        POST (str): HTTP POST method.
        PUT (str): HTTP PUT method.
        DELETE (str): HTTP DELETE method.
        PATCH (str): HTTP PATCH method.
        HEAD (str): HTTP HEAD method.
        OPTIONS (str): HTTP OPTIONS method.

    Methods:
        is_valid_method(cls, method: str) -> bool:
            Validates if the provided method is one of the standard HTTP methods.

        get_method_property(cls, method: str) -> str:
            Returns the HTTP method constant if valid. Raises a ValueError if invalid.

    Example usage:
        method_input = "GET"

        # Validate if the method is a valid HTTP method
        if HTTPMethod.is_valid_method(method_input):
            print(f"{method_input} is a valid HTTP method.")
            # Retrieve the correct property for the HTTP method
            print(f"Returned property: {HTTPMethod.get_method_property(method_input)}")
        else:
            print(f"{method_input} is not a valid HTTP method.")
    """
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

    @classmethod
    def is_valid_method(cls, method: str) -> bool:
        """
        Validates if the provided method is one of the standard HTTP methods.

        Args:
            method (str): The HTTP method string to validate.

        Returns:
            bool: True if the method is a valid HTTP method, False otherwise.

        Example:
            >>> HTTPMethod.is_valid_method("GET")
            True
            >>> HTTPMethod.is_valid_method("FETCH")
            False
        """
        return method in {cls.GET, cls.POST, cls.PUT, cls.DELETE, cls.PATCH, cls.HEAD, cls.OPTIONS}

    @classmethod
    def get_method_property(cls, method: str) -> str:
        """
        Returns the HTTP method constant if valid, otherwise raises an exception.

        Args:
            method (str): The HTTP method string to get the property for.

        Returns:
            str: The HTTP method constant corresponding to the provided method.

        Raises:
            ValueError: If the provided method is not a valid HTTP method.

        Example:
            >>> HTTPMethod.get_method_property("POST")
            'POST'

            >>> HTTPMethod.get_method_property("INVALID")
            ValueError: 'INVALID' is not a valid HTTP method.
        """
        if cls.is_valid_method(method):
            return getattr(cls, method)
        else:
            raise ValueError(f"{method} is not a valid HTTP method.")


@dataclass
class Expected:
    """
    Data structure to hold the expected test results.
    """

    def __init__(self, status_code: int, operators: Dict[str, Any]):
        self._status_code = status_code
        self._operators = operators

    @property
    def status_code(self) -> int:
        return self._status_code

    @status_code.setter
    def status_code(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("status_code must be an integer")
        self._status_code = value

    @property
    def operators(self) -> Dict[str, Any]:
        return self._operators

    @operators.setter
    def operators(self, value: Dict[str, Any]) -> None:
        if not isinstance(value, dict):
            raise ValueError("operators must be a dictionary")
        self._operators = value

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Expected":
        log.debug(f"Creating Expected object from dictionary {data}")
        status_code = data.get("status_code")
        operators = data.get("operators", {})
        if not isinstance(operators, dict):
            raise AttributeError(f"Operators is not a dictionary. Received {operators}")

        # Create and return an Expected object
        return Expected(
            status_code=status_code,
            operators=operators
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
