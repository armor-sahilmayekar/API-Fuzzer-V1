import pytest
from unittest.mock import patch, MagicMock
from modules.jira.jira_integration import JiraClient, AioTestClient


@patch('modules.jira.jira_integration.JIRA')
def test_create_issue_success(mock_jira):
    mock_instance = mock_jira.return_value
    mock_issue = MagicMock()
    mock_issue.key = "JIRA-123"
    mock_instance.create_issue.return_value = mock_issue

    client = JiraClient("https://example.atlassian.net", "user@example.com", "token", "TEST")
    result = client.create_issue({"request_url": "http://test.com"})

    assert result == "JIRA-123"


@patch('modules.jira.jira_integration.JIRA')
def test_update_issue_success(mock_jira):
    mock_instance = mock_jira.return_value
    client = JiraClient("https://example.atlassian.net", "user@example.com", "token", "TEST")

    client.update_issue("JIRA-123", {"request_url": "http://test.com"})
    mock_instance.add_comment.assert_called_once()


@patch('modules.jira.jira_integration.requests.post')
def test_create_test_case_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"key": "AIO-TC-1"}
    mock_post.return_value = mock_response

    client = AioTestClient("https://example.atlassian.net", "user@example.com", "token", "TEST")
    key = client.create_test_case("Sample Test", "Desc")
    assert key == "AIO-TC-1"


@patch('modules.jira.jira_integration.requests.put')
def test_update_test_case_success(mock_put):
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_put.return_value = mock_response

    client = AioTestClient("https://example.atlassian.net", "user@example.com", "token", "TEST")
    client.update_test_case("AIO-TC-1", new_name="New Name")
    mock_put.assert_called_once()


@patch('modules.jira.jira_integration.requests.post')
def test_log_test_execution_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "EXEC-123"}
    mock_post.return_value = mock_response

    client = AioTestClient("https://example.atlassian.net", "user@example.com", "token", "TEST")
    result_id = client.log_test_execution("AIO-TC-1", "Cycle1", "Pass")
    assert result_id == "EXEC-123"


@patch('modules.jira.jira_integration.requests.put')
def test_update_test_execution_success(mock_put):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_put.return_value = mock_response

    client = AioTestClient("https://example.atlassian.net", "user@example.com", "token", "TEST")
    client.update_test_execution("EXEC-123", new_status="Fail")
    mock_put.assert_called_once()
