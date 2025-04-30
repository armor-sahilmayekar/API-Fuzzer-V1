import pytest
from unittest import mock
from modules.api.okta import OktaSeleniumAuth  # Replace with your actual module
import time
import urllib.parse
from selenium import webdriver

@pytest.fixture
def okta_auth():
    return OktaSeleniumAuth(
        okta_domain="https://example.okta.com",
        client_id="client_id",
        redirect_uri="https://redirect.uri",
        username="user@example.com",
        password="password"
    )


# Test the URL building method
def test_build_auth_url(okta_auth):
    code_challenge = "some_challenge"
    state = "xyz123"
    auth_url = okta_auth.build_auth_url(code_challenge, state)
    expected_url = (
        "https://example.okta.com/oauth2/default/v1/authorize?"
        "client_id=client_id&response_type=code&scope=openid+profile+email&"
        "redirect_uri=https%3A%2F%2Fredirect.uri&state=xyz123&code_challenge_method=S256&"
        "code_challenge=some_challenge"
    )
    assert auth_url == expected_url


# Test the automate_login method by mocking the login and 2FA
@mock.patch("selenium.webdriver.Chrome")
@mock.patch("time.sleep", return_value=None)  # Mock sleep to avoid delays
def test_automate_login(mock_sleep, MockChrome, okta_auth):
    # Mock the behavior of the WebDriver and 2FA
    mock_driver = mock.Mock()
    mock_driver.current_url = "https://example.okta.com/callback?code=authorization_code"
    MockChrome.return_value = mock_driver

    # Mock the login steps
    mock_driver.find_element.return_value.send_keys = mock.Mock()

    final_url = okta_auth.automate_login("https://auth.url")

    # Check if the final URL contains the authorization code
    assert "code=authorization_code" in final_url


# Test the has_code_parameter method
def test_has_code_parameter(okta_auth):
    url = "https://example.okta.com/callback?code=authorization_code"
    assert okta_auth.has_code_parameter(url) is True

    url_without_code = "https://example.okta.com/callback?state=xyz123"
    assert okta_auth.has_code_parameter(url_without_code) is False


# Test the exchange_code_for_token method by mocking requests.post
@mock.patch("requests.post")
def test_exchange_code_for_token(mock_post, okta_auth):
    code = "authorization_code"
    code_verifier = "code_verifier"

    # Mock the response of the token request
    mock_response = mock.Mock()
    mock_response.json.return_value = {"access_token": "fake_token"}
    mock_post.return_value = mock_response

    access_token = okta_auth.exchange_code_for_token(code, code_verifier)

    # Check if the access token is returned correctly
    assert access_token == "fake_token"


# Test the full authorization flow
@mock.patch("selenium.webdriver.Chrome")
@mock.patch("time.sleep", return_value=None)
@mock.patch("requests.post")
def test_authorize(mock_post, mock_sleep, MockChrome, okta_auth):
    # Mock the WebDriver login and 2FA
    mock_driver = mock.Mock()
    mock_driver.current_url = "https://example.okta.com/callback?code=authorization_code"
    MockChrome.return_value = mock_driver

    # Mock the token exchange
    mock_response = mock.Mock()
    mock_response.json.return_value = {"access_token": "fake_token"}
    mock_post.return_value = mock_response

    # Run the authorization process
    access_token = okta_auth.authorize()

    # Check if the access token is returned correctly
    assert access_token == "fake_token"
    mock_post.assert_called_once()  # Ensure that the post request was made


if __name__ == "__main__":
    pytest.main()
