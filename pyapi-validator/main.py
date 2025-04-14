import os
import json
from typing import List
import requests
from report_writer import ReportWriter


class APIClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        """
        Initializes the APIClient with the base URL of the API and the API key.

        Args:
            base_url (str): The base URL for the API.
            api_key (str): The API key used for authentication in headers.
        """
        self.base_url = base_url
        self.api_key = api_key

    def send_request(self, method: str, endpoint: str, params: dict = None, headers: dict = None) -> requests.Response:
        """
        Sends an HTTP request to the API and returns the response.

        Args:
            method (str): The HTTP method (GET, POST, etc.).
            endpoint (str): The API endpoint to be appended to the base URL.
            params (dict, optional): The query parameters to be included in the request.
            headers (dict, optional): The headers to be included in the request.

        Returns:
            requests.Response: The response object from the request.
        """
        url = os.path.join(self.base_url, endpoint)
        if headers is None:
            headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.request(method, url, params=params, headers=headers)
        return response


class TestRunner:
    def __init__(self, api_client: APIClient, report_writer: ReportWriter) -> None:
        """
        Initializes the TestRunner to run the tests and store the results using ReportWriter.

        Args:
            api_client (APIClient): The API client used to send requests.
            report_writer (ReportWriter): The report writer that stores test results.
        """
        self.api_client = api_client
        self.report_writer = report_writer

    def run_test(self, test_case: dict) -> dict:
        """
        Executes an individual test case, sends the request, and verifies the response.

        Args:
            test_case (dict): A dictionary containing test input data, including endpoint,
                               parameters, expected responses, and verification logic.

        Returns:
            dict: A dictionary representing the test result, including the request and response details.
        """
        method = test_case.get("method", "GET")
        endpoint = test_case["endpoint"]
        params = test_case.get("params", {})
        expected_status = test_case["expected_status"]

        # Send the request
        response = self.api_client.send_request(method, endpoint, params=params)

        # Verify the response status
        result = {
            "status": "success" if response.status_code == expected_status else "failure",
            "name": test_case["name"],
            "sub_reports": [],
            "test_number": test_case["test_number"],
            "state": "PASSED" if response.status_code == expected_status else "FAILED",
            "request_url": response.url,
            "request_method": method,
            "request_headers": json.dumps(response.request.headers),
            "request_body": params,
            "response": response.text,
            "details": "Success" if response.status_code == expected_status else "Unexpected status code",
            "reason": "response_success" if response.status_code == expected_status else "unexpected_status_code"
        }

        return result

    def run_tests(self, test_cases: List[dict]) -> None:
        """
        Runs all test cases in the provided list and writes each report to disk.

        Args:
            test_cases (List[dict]): A list of test cases, each being a dictionary containing
                                      the details of an individual test case.

        Returns:
            None
        """
        for test_case in test_cases:
            result = self.run_test(test_case)
            self.report_writer.write_report(result)


def load_test_cases(file_path: str) -> List[dict]:
    """
    Loads the test cases from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing the test cases.

    Returns:
        List[dict]: A list of dictionaries where each dictionary represents a test case.
    """
    with open(file_path, "r") as file:
        test_cases = json.load(file)
    return test_cases


def main():
    # Load environment variables or configuration
    base_url = "https://mdr-api.secure-dev.services/"
    api_key = os.getenv("API_KEY", "your_api_key_here")

    # Initialize the API client and report writer
    api_client = APIClient(base_url, api_key)
    report_writer = ReportWriter(report_dir="./reports")

    # Load test cases
    test_cases = load_test_cases("test_cases.json")

    # Initialize the test runner and execute tests
    test_runner = TestRunner(api_client, report_writer)
    test_runner.run_tests(test_cases)


if __name__ == "__main__":
    main()
