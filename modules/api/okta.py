import time
import urllib.parse
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pkce import generate_pkce_pair

class OktaSeleniumAuth:
    """
    Automates the Okta OAuth2 Authorization Code flow using Selenium.

    This class performs a headless browser login to Okta to retrieve an authorization code,
    which is then exchanged for an access token. It supports PKCE and optional scopes.

    Attributes:
        okta_domain (str): Base URL of the Okta domain (e.g., https://your-org.okta.com).
        client_id (str): OAuth2 client ID registered in Okta.
        redirect_uri (str): Redirect URI registered with the OAuth2 client.
        username (str): Okta username for login.
        password (str): Okta password for login.
        scopes (str): OAuth2 scopes (default: "openid profile email").
        auth_server (str): Authorization server name (default: "default").
    """

    def __init__(self, okta_domain, client_id, redirect_uri, username, password,
                 scopes="openid profile email", auth_server="default"):
        """
        Initializes the OktaSeleniumAuth object with configuration details.

        Args:
            okta_domain (str): Okta domain (e.g., "https://your-org.okta.com").
            client_id (str): OAuth2 client ID.
            redirect_uri (str): Redirect URI for the OAuth2 flow.
            username (str): Okta account username.
            password (str): Okta account password.
            scopes (str): Requested OAuth2 scopes.
            auth_server (str): Okta authorization server (default is "default").
        """
        self.okta_domain = okta_domain.rstrip('/')
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.username = username
        self.password = password
        self.scopes = scopes
        self.auth_server = auth_server

    def build_auth_url(self, code_challenge, state):
        """
        Builds the Okta authorization URL with PKCE parameters.

        Args:
            code_challenge (str): Code challenge derived from the code verifier.
            state (str): Opaque value to maintain state between request and callback.

        Returns:
            str: Complete authorization URL.
        """
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": self.scopes,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "code_challenge_method": "S256",
            "code_challenge": code_challenge
        }
        return f"{self.okta_domain}/oauth2/{self.auth_server}/v1/authorize?" + urllib.parse.urlencode(params)

    def automate_login(self, auth_url):
        """
        Automates the login and 2FA process using Selenium and retrieves the final redirect URL.

        Args:
            auth_url (str): Okta authorization URL.

        Returns:
            str: Final redirect URL containing the authorization code.
        """
        driver = self._login(auth_url)
        current_url = self._2fa(driver)
        driver.quit()
        return current_url

    def _2fa(self, driver):
        """
        Waits until the final URL contains an authorization code.

        Args:
            driver (webdriver.Chrome): Selenium WebDriver instance.

        Returns:
            str: Final URL containing the authorization code.
        """
        count = 0
        while not self.has_code_parameter(driver.current_url) and count < 100:
            print(driver.current_url)
            time.sleep(1)
            count += 1
            print(count)
        return driver.current_url

    def _login(self, auth_url):
        """
        Launches a headless Chrome browser to perform Okta login steps.

        Args:
            auth_url (str): The authorization URL to load in the browser.

        Returns:
            webdriver.Chrome: Selenium WebDriver instance after submitting login.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(auth_url)
        time.sleep(2)
        driver.find_element(By.ID, "okta-signin-username").send_keys(self.username)
        driver.find_element(By.ID, "okta-signin-password").send_keys(self.password)
        driver.find_element(By.ID, "okta-signin-submit").click()
        time.sleep(2)
        driver.find_element(By.CLASS_NAME, "button-primary").click()
        return driver

    def has_code_parameter(self, url):
        """
        Checks if the given URL contains an OAuth2 authorization code parameter.

        Args:
            url (str): URL to inspect.

        Returns:
            bool: True if 'code' is present in the query string, False otherwise.
        """
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        return 'code' in query_params

    def exchange_code_for_token(self, code, code_verifier):
        """
        Exchanges the authorization code for an access token.

        Args:
            code (str): Authorization code received from Okta.
            code_verifier (str): Original code verifier used in PKCE flow.

        Returns:
            str: Access token returned by Okta.

        Raises:
            requests.HTTPError: If the HTTP request fails.
        """
        token_url = f"{self.okta_domain}/oauth2/{self.auth_server}/v1/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "code_verifier": code_verifier
        }
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

    def authorize(self):
        """
        Performs the full authorization code flow:
        - Generates PKCE pair
        - Builds authorization URL
        - Automates browser login and 2FA
        - Extracts authorization code
        - Exchanges code for access token

        Returns:
            str: Access token retrieved from Okta.

        Raises:
            RuntimeError: If the authorization code is not found in the final URL.
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
