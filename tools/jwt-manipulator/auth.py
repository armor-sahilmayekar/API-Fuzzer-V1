from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import urllib.parse
import requests
from pkce import generate_pkce_pair

from modules.util.config import EnvConfig


class OktaSeleniumAuth:
    def __init__(self, okta_domain, client_id, redirect_uri, username, password, scopes="openid profile email", auth_server="default"):
        self.okta_domain = okta_domain.rstrip('/')
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.username = username
        self.password = password
        self.scopes = scopes
        self.auth_server = auth_server

    def build_auth_url(self, code_challenge, state):
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
        driver = self._login(auth_url)
        current_url = self._2fa(driver)
        driver.quit()
        return current_url

    def _2fa(self, driver):
        count = 0
        while not self.has_code_parameter(driver.current_url) and count < 100:
            print(driver.current_url)
            time.sleep(1)
            count += 1
            print(count)
        current_url = driver.current_url
        return current_url

    def _login(self, auth_url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(auth_url)
        # Wait for login page and enter credentials
        time.sleep(2)
        driver.find_element(By.ID, "okta-signin-username").send_keys(self.username)
        driver.find_element(By.ID, "okta-signin-password").send_keys(self.password)
        driver.find_element(By.ID, "okta-signin-submit").click()
        time.sleep(2)
        driver.find_element(By.CLASS_NAME, "button-primary").click()
        return driver

    def has_code_parameter(self, url):
        # Parse the URL
        parsed_url = urllib.parse.urlparse(url)

        # Get the query parameters as a dictionary
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Check if 'code' is a key in the query parameters
        return 'code' in query_params
    def exchange_code_for_token(self, code, code_verifier):
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


# Usage example
if __name__ == "__main__":
    config = EnvConfig()
    okta_domain = config.okta_base_url
    client_id = config.okta_client_id
    redirect_uri = config.okta_redirect_url
    scopes = ["openid", "profile", "email"]  # and any custom scopes you need
    username = config.user
    password = config.password
    auth = OktaSeleniumAuth(
        okta_domain=okta_domain,
        client_id=client_id,
        redirect_uri=redirect_uri,
        username=username,
        password=password,
    )

    token = auth.authorize()
    print("Access Token:\n", token)

    config = EnvConfig()
    okta_domain = config.okta_base_url
    client_id = config.okta_client_id
    redirect_uri = config.okta_redirect_url
    scopes = ["openid", "profile", "email"]  # and any custom scopes you need
    username = config.user
    password = config.password