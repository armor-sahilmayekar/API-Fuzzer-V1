import requests
import json


class JiraIntegration:
    def __init__(self, jira_url, jira_user, jira_token, project_key):
        """
        Initialize the JiraIntegration class with required credentials and project info.

        :param jira_url: JIRA base URL (e.g., https://yourcompany.atlassian.net)
        :param jira_user: JIRA email address used for API access
        :param jira_token: JIRA API token for authentication
        :param project_key: JIRA project key where test tickets will be created
        """
        self.jira_url = jira_url
        self.jira_user = jira_user
        self.jira_token = jira_token
        self.project_key = project_key
        self.auth = (jira_user, jira_token)
        self.headers = {
            "Content-Type": "application/json"
        }

    def create_issue(self, report_data):
        """
        Create a new JIRA issue with the scan results.

        :param report_data: The test report data as a dictionary
        :return: None
        """
        summary = "Automated Scan Report: {}".format(report_data.get("request_url"))
        description = json.dumps(report_data, indent=2)

        url = f"{self.jira_url}/rest/api/3/issue"
        payload = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": "Task"  # Can be changed based on project configuration (e.g., "Bug", "Test")
                }
            }
        }

        response = requests.post(url, headers=self.headers, auth=self.auth, json=payload)

        if response.status_code in [200, 201]:
            print("[JIRA] Successfully created a new JIRA issue.")
        else:
            print(f"[JIRA] Failed to create JIRA issue. Status: {response.status_code} | {response.text}")

    def update_issue(self, issue_key, report_data):
        """
        Update an existing JIRA issue with the scan results.

        :param issue_key: JIRA issue ID to update
        :param report_data: The test report data as a dictionary
        :return: None
        """
        url = f"{self.jira_url}/rest/api/3/issue/{issue_key}/comment"
        description = json.dumps(report_data, indent=2)

        payload = {
            "body": f"New scan result:\n\n{description}"
        }

        response = requests.post(url, headers=self.headers, auth=self.auth, json=payload)

        if response.status_code in [200, 201]:
            print("[JIRA] Successfully updated JIRA issue with new scan results.")
        else:
            print(f"[JIRA] Failed to update JIRA issue. Status: {response.status_code} | {response.text}")
