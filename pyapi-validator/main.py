import os
import json
import argparse
import requests
from requests.exceptions import RequestException
from report_writer import ReportWriter

def load_test_cases(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def run_test_case(test_case, api_key):
    try:
        headers = test_case.get("headers", {})
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.request(
            method=test_case.get("method", "GET"),
            url=test_case["url"],
            headers=headers,
            json=test_case.get("body", {})
        )

        expected = test_case.get("expected", {})
        is_success = (
            response.status_code == expected.get("status_code") and
            expected.get("contains", "") in response.text
        )

        return {
            "status": "success",
            "state": "PASSED" if is_success else "FAILED",
            "reason": "" if is_success else "verification_failed",
            "response": response.text,
            "details": f"Expected status {expected.get('status_code')}, got {response.status_code}",
            "request_headers": json.dumps(headers),
            "request_body": test_case.get("body", {}),
            "request_url": test_case["url"],
            "request_method": test_case.get("method", "GET"),
            "exception": "",
            "sub_reports": []
        }

    except RequestException as e:
        return {
            "status": "success",
            "state": "FAILED",
            "reason": "request_failed",
            "response": "",
            "details": str(e),
            "request_headers": json.dumps(test_case.get("headers", {})),
            "request_body": test_case.get("body", {}),
            "request_url": test_case["url"],
            "request_method": test_case.get("method", "GET"),
            "exception": str(e),
            "sub_reports": []
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--test-case-file", default="test_cases.json")
    args = parser.parse_args()

    api_key = os.getenv("API_KEY")
    test_cases = load_test_cases(args.test_case_file)
    writer = ReportWriter(args.report_dir)

    for test in test_cases:
        result = run_test_case(test, api_key)
        result.update({
            "test_number": test.get("test_number", 0),
            "name": test.get("name", "unnamed_test")
        })
        writer.write_report(result)

if __name__ == "__main__":
    main()
