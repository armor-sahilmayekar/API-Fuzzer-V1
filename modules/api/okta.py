import time
import urllib.parse

import requests
from pkce import generate_pkce_pair
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from modules.util.loggable import Loggable as log


class OktaSeleniumAuth:
    """
    Automates the Okta OAuth2 authorization code flow using Selenium and PKCE.

    This class launches a headless browser session to perform login and 2FA,
    then exchanges the resulting authorization code for an access token.

    Attributes:
        _okta_domain (str): The base URL of the Okta tenant.
        _client_id (str): The OAuth2 client ID registered with Okta.
        _redirect_uri (str): The URI to which the authorization code is sent.
        _username (str): The username used to log into Okta.
        _password (str): The password used to log into Okta.
        _scopes (str): A space-separated list of OAuth2 scopes.
        _auth_server (str): The Okta authorization server ID (e.g., 'default').
    """

    def __init__(self, okta_domain, client_id, redirect_uri, username, password,
                 scopes="openid profile email", auth_server="default"):
        """
        Initializes the authentication helper.

        Args:
            okta_domain (str): Okta domain URL.
            client_id (str): OAuth2 client ID.
            redirect_uri (str): Redirect URI for the OAuth2 flow.
            username (str): Okta username.
            password (str): Okta password.
            scopes (str, optional): OAuth2 scopes. Defaults to "openid profile email".
            auth_server (str, optional): Authorization server. Defaults to "default".
        """
        self._okta_domain = okta_domain.rstrip('/')
        self._client_id = client_id
        self._redirect_uri = redirect_uri
        self._username = username
        self._password = password
        self._scopes = scopes
        self._auth_server = auth_server

    def build_auth_url(self, code_challenge, state):
        """
        Constructs the OAuth2 authorization URL.

        Args:
            code_challenge (str): PKCE code challenge string.
            state (str): OAuth2 state parameter for CSRF protection.

        Returns:
            str: Fully constructed authorization URL.
        """
        params = {
            "client_id": self._client_id,
            "response_type": "code",
            "scope": self._scopes,
            "redirect_uri": self._redirect_uri,
            "state": state,
            "code_challenge_method": "S256",
            "code_challenge": code_challenge
        }
        return f"{self._okta_domain}/oauth2/{self._auth_server}/v1/authorize?" + urllib.parse.urlencode(params)

    def automate_login(self, auth_url):
        """
        Launches a headless browser, logs in via Selenium, and completes 2FA.

        Args:
            auth_url (str): The Okta authorization URL.

        Returns:
            str: Final URL containing the authorization code as a query parameter.
        """
        driver = self._login(auth_url)
        current_url = self._2fa(driver)
        driver.quit()
        return current_url

    def _2fa(self, driver):
        """
        Waits for the user to complete multi-factor authentication.

        Args:
            driver (webdriver.Chrome): Selenium WebDriver instance.

        Returns:
            str: Final redirected URL after successful login and MFA.
        """
        count = 0
        max_attempts = 100
        while not self.has_code_parameter(driver.current_url) and count < max_attempts:
            log.info(f"Waiting for user confirmation of MFA Code. Attempts left {max_attempts - count}")
            log.debug(driver.current_url)
            time.sleep(1)
            count += 1
            log.debug(count)
        return driver.current_url

    def _login(self, auth_url):
        """
        Automates the Okta login page using Selenium in headless mode.

        Args:
            auth_url (str): The authorization URL.

        Returns:
            webdriver.Chrome: The WebDriver after initiating MFA.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(auth_url)

        log.info("Logging in...")
        time.sleep(2)

        driver.find_element(By.ID, "okta-signin-username").send_keys(self._username)
        driver.find_element(By.ID, "okta-signin-password").send_keys(self._password)
        driver.find_element(By.ID, "okta-signin-submit").click()

        log.info("Logging in complete...")
        time.sleep(2)

        log.info("Sending MFA confirmation via push...")
        driver.find_element(By.CLASS_NAME, "button-primary").click()

        return driver

    def has_code_parameter(self, url):
        """
        Checks whether the given URL contains the OAuth2 authorization code.

        Args:
            url (str): URL to check.

        Returns:
            bool: True if the 'code' query parameter is present, else False.
        """
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        return 'code' in query_params

    def exchange_code_for_token(self, code, code_verifier):
        """
        Exchanges the authorization code for an access token.

        Args:
            code (str): The authorization code from the redirect URL.
            code_verifier (str): The PKCE code verifier used in the auth flow.

        Returns:
            str: The access token returned from Okta.
        """
        token_url = f"{self._okta_domain}/oauth2/{self._auth_server}/v1/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_uri,
            "client_id": self._client_id,
            "code_verifier": code_verifier
        }
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

    def authorize(self):
        """
        Performs the full OAuth2 authorization code flow using Selenium and PKCE.

        Returns:
            str: The final access token obtained from Okta.

        Raises:
            RuntimeError: If the authorization code could not be extracted.
        """
        code_verifier, code_challenge = generate_pkce_pair()
        state = "xyz123"
        auth_url = self.build_auth_url(code_challenge, state)

        final_url = self.automate_login(auth_url)
        parsed = urllib.parse.urlparse(final_url)
        query = urllib.parse.parse_qs(parsed.query)
        code = query.get("code", [None])[0]

        if not code:
            raise RuntimeError("Authorization code not found in redirect URL.")

        return self.exchange_code_for_token(code, code_verifier)
