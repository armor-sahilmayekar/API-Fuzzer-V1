import json

import requests
from jira import JIRA


class JiraClient:
    """
    JiraClient provides high-level interactions with the Atlassian JIRA REST API.
    It uses the `jira` Python module to create and update issues within a given project.

    Typical usage example:

        client = JiraClient(jira_url, jira_user, jira_token, project_key)
        issue_key = client.create_issue(report_data)
        client.update_issue(issue_key, additional_data)

    :param jira_url: Base URL of the JIRA instance (e.g., https://yourcompany.atlassian.net)
    :param jira_user: User email used for authenticating with JIRA
    :param jira_token: API token for authentication
    :param project_key: The JIRA project key (e.g., "TEST")
    """

    def __init__(self, jira_url: str, jira_user: str, jira_token: str, project_key: str):
        self.project_key = project_key
        self.jira = JIRA(server=jira_url, basic_auth=(jira_user, jira_token))

    def create_issue(self, report_data: dict) -> str | None:
        """
        Creates a new issue in the specified JIRA project with the provided report data.

        :param report_data: Dictionary containing scan results (must include 'request_url')
        :return: The issue key (e.g., "TEST-123") or None if creation failed
        """
        summary = f"Automated Scan Report: {report_data.get('request_url')}"
        description = json.dumps(report_data, indent=2)

        issue_dict = {
            'project': {'key': self.project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': 'Task'}
        }

        try:
            issue = self.jira.create_issue(fields=issue_dict)
            print(f"[JIRA] Created issue: {issue.key}")
            return issue.key
        except Exception as e:
            print(f"[JIRA] Failed to create issue: {e}")
            return None

    def update_issue(self, issue_key: str, report_data: dict) -> None:
        """
        Appends a comment with new scan data to an existing JIRA issue.

        :param issue_key: The unique key of the issue to update (e.g., "TEST-123")
        :param report_data: Dictionary of scan results to be added as a comment
        """
        comment = f"New scan result:\n\n{json.dumps(report_data, indent=2)}"
        try:
            self.jira.add_comment(issue_key, comment)
            print(f"[JIRA] Updated issue {issue_key} with a comment.")
        except Exception as e:
            print(f"[JIRA] Failed to update issue {issue_key}: {e}")


class AioTestClient:
    """
    AioTestClient integrates with the AIO Tests plugin for Jira to manage test cases and executions.

    It supports:
    - Creating and updating test cases
    - Logging test executions to test cycles
    - Updating test execution results

    Typical usage example:

        client = AioTestClient(jira_url, jira_user, jira_token, project_key)
        test_key = client.create_test_case("Scan Test", "Scan for XSS")
        exec_id = client.log_test_execution(test_key, "Nightly", "Pass")
        client.update_test_execution(exec_id, new_status="Fail", new_comment="Found XSS")

    :param jira_url: Base JIRA URL
    :param jira_user: API user email
    :param jira_token: API token
    :param project_key: Key of the JIRA project to use
    """

    def __init__(self, jira_url: str, jira_user: str, jira_token: str, project_key: str):
        self.jira_url = jira_url
        self.project_key = project_key
        self.auth = (jira_user, jira_token)
        self.headers = {"Content-Type": "application/json"}

    def create_test_case(self, title: str, description: str = "") -> str | None:
        """
        Creates a new test case in AIO Tests.

        :param title: The name of the test case
        :param description: Optional objective/description for the test case
        :return: The test case key (e.g., "AIO-TC-1") or None on failure
        """
        url = f"{self.jira_url}/rest/atm/1.0/testcase"
        payload = {
            "projectKey": self.project_key,
            "name": title,
            "objective": description
        }

        response = requests.post(url, headers=self.headers, auth=self.auth, json=payload)
        if response.status_code in [200, 201]:
            print(f"[AIO] Created test case: {response.json().get('key')}")
            return response.json().get('key')
        else:
            print(f"[AIO] Failed to create test case: {response.status_code} | {response.text}")
            return None

    def update_test_case(self, test_case_key: str, new_name: str = None, new_description: str = None) -> None:
        """
        Updates an existing test case with a new name or description.

        :param test_case_key: The test case ID (e.g., "AIO-TC-1")
        :param new_name: New title for the test case
        :param new_description: New description for the test case
        """
        url = f"{self.jira_url}/rest/atm/1.0/testcase/{test_case_key}"
        payload = {}
        if new_name:
            payload["name"] = new_name
        if new_description:
            payload["objective"] = new_description

        response = requests.put(url, headers=self.headers, auth=self.auth, json=payload)
        if response.status_code in [200, 204]:
            print(f"[AIO] Updated test case {test_case_key}")
        else:
            print(f"[AIO] Failed to update test case: {response.status_code} | {response.text}")

    def log_test_execution(self, test_case_key: str, cycle_name: str, status: str, comment: str = None) -> str | None:
        """
        Logs a new test result under the given test cycle.

        :param test_case_key: ID of the test case to log results for
        :param cycle_name: The name of the test cycle (e.g., "Regression Run")
        :param status: Result status (e.g., "Pass", "Fail")
        :param comment: Optional comment for the result
        :return: ID of the created test result or None on failure
        """
        url = f"{self.jira_url}/rest/atm/1.0/testresult"
        payload = {
            "testCaseKey": test_case_key,
            "status": status,
            "testCycle": {"name": cycle_name},
            "comment": comment or ""
        }

        response = requests.post(url, headers=self.headers, auth=self.auth, json=payload)
        if response.status_code in [200, 201]:
            print(f"[AIO] Logged test result: {response.json().get('id')}")
            return response.json().get("id")
        else:
            print(f"[AIO] Failed to log test result: {response.status_code} | {response.text}")
            return None

    def update_test_execution(self, test_result_id: str, new_status: str = None, new_comment: str = None) -> None:
        """
        Updates a previously logged test execution.

        :param test_result_id: ID of the test execution to update
        :param new_status: New result status (e.g., "Blocked")
        :param new_comment: New comment or update notes
        """
        url = f"{self.jira_url}/rest/atm/1.0/testresult/{test_result_id}"
        payload = {}
        if new_status:
            payload["status"] = new_status
        if new_comment:
            payload["comment"] = new_comment

        response = requests.put(url, headers=self.headers, auth=self.auth, json=payload)
        if response.status_code in [200, 204]:
            print(f"[AIO] Updated test execution {test_result_id}")
        else:
            print(f"[AIO] Failed to update test execution: {response.status_code} | {response.text}")
