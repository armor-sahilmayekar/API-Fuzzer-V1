import json
import secrets
import time
import webbrowser
from dataclasses import dataclass
from typing import Dict, Any, Union
from typing import Optional
from urllib.parse import urlencode

import jwt
import requests
from werkzeug.datastructures import Accept


@dataclass
class JWTClaims:
    exp: Optional[int] = None  # Expiration Time
    iat: Optional[int] = None  # Issued At
    nbf: Optional[int] = None  # Not Before
    aud: Optional[str] = None  # Audience
    iss: Optional[str] = None  # Issuer
    sub: Optional[str] = None  # Subject
    jti: Optional[str] = None  # JWT ID


class JWTAnalyzer:
    """
    A class to analyze, decode, validate, and re-encode JWT tokens.
    """

    def __init__(self, token: str):
        """
        Initialize the JWTAnalyzer with a JWT token.

        :param token: JWT Token as a string.
        """
        self.token = token
        self.decoded_payload: Optional[Dict[str, Any]] = None
        self.header: Optional[Dict[str, Any]] = None

    def load_jwt_token(self) -> Optional[Dict[str, Any]]:
        """
        Decode the JWT token without verifying the signature.

        :return: Decoded JWT payload as a dictionary, or None if decoding fails.
        """
        try:
            self.decoded_payload = jwt.decode(self.token, options={"verify_signature": False})
            return self.decoded_payload
        except jwt.DecodeError as e:
            print(f"Error decoding JWT: {e}")
            return None

    def validate_jwt_structure(self) -> bool:
        """
        Validate the structure of the JWT token (should be in three parts separated by periods).

        :return: True if the token structure is valid, False otherwise.
        """
        parts = self.token.split(".")
        return len(parts) == 3

    def dump_jwt(self) -> None:
        """
        Print the JWT token in a formatted manner (e.g., in three parts: header, payload, signature).
        """
        parts = self.token.split(".")
        if len(parts) == 3:
            print("\n--- JWT Token Dump ---")
            print(f"Header: {parts[0]}")
            print(f"Payload: {parts[1]}")
            print(f"Signature: {parts[2]}")
            print("-----------------------")
        else:
            print("Invalid JWT structure. Unable to dump the token.")

    def test_jwt(self) -> Optional[Dict[str, Any]]:
        """
        Run a full test: dump token, validate structure, decode, and check claims.

        :return: Decoded JWT payload or None if test fails.
        """
        print("Testing JWT token...")
        self.dump_jwt()

        if not self.validate_jwt_structure():
            print("Invalid JWT structure.")
            return None

        decoded_token = self.load_jwt_token()
        if decoded_token is None:
            print("Failed to decode JWT.")
            return None

        print("Decoded JWT Payload:")
        print(json.dumps(decoded_token, indent=2))
        self.check_claims(decoded_token)

        return decoded_token

    def check_claims(self, decoded_token: Dict[str, Any]) -> JWTClaims:
        """
        Extract common claims from a decoded JWT payload into a structured data class.

        :param decoded_token: Dictionary of decoded JWT payload.
        :return: JWTClaims object with extracted claim values.
        """
        claims = JWTClaims(
            exp=decoded_token.get("exp"),
            iat=decoded_token.get("iat"),
            nbf=decoded_token.get("nbf"),
            aud=decoded_token.get("aud"),
            iss=decoded_token.get("iss"),
            sub=decoded_token.get("sub"),
            jti=decoded_token.get("jti"),
        )

        # Verbose output
        for field, value in claims.__dict__.items():
            if value is not None:
                print(f"{field.upper()} claim found: {value}")
            else:
                print(f"{field.upper()} claim not found.")

        return claims

    def get_jwt_header(self) -> Optional[Dict[str, Any]]:
        """
        Extract and return the JWT header without verifying the signature.

        :return: Header dictionary or None on error.
        """
        try:
            self.header = jwt.get_unverified_header(self.token)
            print("JWT Header:")
            print(json.dumps(self.header, indent=2))
            return self.header
        except jwt.DecodeError as e:
            print(f"Error decoding JWT header: {e}")
            return None

    def verify_jwt(self, key: Union[str, bytes], algorithms: Optional[list] = None) -> bool:
        """
        Verify the JWT using a given key and algorithm(s).

        :param key: Secret or public key to verify the signature.
        :param algorithms: List of accepted algorithms (e.g., ["HS256"]).
        :return: True if valid, False otherwise.
        """
        try:
            decoded = jwt.decode(self.token, key=key, algorithms=algorithms)
            print("JWT successfully verified.")
            print(json.dumps(decoded, indent=2))
            return True
        except jwt.ExpiredSignatureError:
            print("JWT has expired.")
        except jwt.InvalidTokenError as e:
            print(f"Invalid JWT: {e}")
        return False

    def is_expired(self) -> bool:
        """
        Check if the token is expired using the 'exp' claim.

        :return: True if expired, False otherwise.
        """
        if not self.decoded_payload:
            self.load_jwt_token()
        if "exp" in self.decoded_payload:
            exp_time = self.decoded_payload["exp"]
            current_time = int(time.time())
            return exp_time < current_time
        return False

    def reencode_jwt(self, secret: Union[str, bytes], algorithm: str = "HS256") -> Optional[str]:
        """
        Re-encode the decoded payload using a secret and algorithm.

        :param secret: Secret key for signing.
        :param algorithm: Algorithm to use (default is HS256).
        :return: New encoded JWT or None on error.
        """
        if not self.decoded_payload:
            self.load_jwt_token()
        if not self.header:
            self.get_jwt_header()
        try:
            new_token = jwt.encode(self.decoded_payload, secret, algorithm=algorithm, headers=self.header)
            print("Re-encoded JWT:")
            print(new_token)
            return new_token
        except Exception as e:
            print(f"Error re-encoding JWT: {e}")
            return None

    def get_all_claims(self) -> Optional[Dict[str, Any]]:
        """
        Return all claims from the decoded token.

        :return: Claims dictionary or None if decoding fails.
        """
        return self.load_jwt_token()

    def get_algorithm(self) -> Optional[str]:
        """
        Return the algorithm specified in the JWT header.

        :return: Algorithm string or None.
        """
        if not self.header:
            self.get_jwt_header()
        return self.header.get("alg") if self.header else None


class OktaMFAClient:
    """
    OktaMFAClient handles user authentication via Okta with Multi-Factor Authentication (MFA),
    and allows access to a protected API after successful authentication.

    Usage:
    -------
    Set the following environment variables before running:
        - OKTA_BASE_URL:        Your Okta domain, e.g., https://dev-123456.okta.com
        - USER:                 Your Okta username
        - PASS:                 Your Okta password
        - PROTECTED_API_URL:   The API endpoint to call after authentication

    Example:
    --------
    >>> client = OktaMFAClient(
            base_url=os.getenv("OKTA_BASE_URL"),
            username=os.getenv("USER"),
            password=os.getenv("PASS"),
            api_url=os.getenv("PROTECTED_API_URL")
        )
    >>> client.authenticate()
    >>> response = client.call_protected_api()
    >>> print(response)

    Notes:
    ------
    - This implementation assumes the first available MFA factor will be used.
    - Only Okta session token is used here; for OAuth2 token exchange, implement get_access_token().
    - Intended for educational or internal tools. Use OAuth2 properly for production applications.
    """

    def __init__(self, base_url, username, password, api_url):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.api_url = api_url
        self.api_url = 'https://mdr.console-demo.armorlabs.co/login/callback'
        self.session_token = None
        self.access_token = None
        self.client_id = None

    def authenticate(self):
        """Authenticate user and trigger MFA if required."""
        authn_url = f"{self.base_url}/api/v1/authn"
        payload = {
            "username": self.username,
            "password": self.password,
            "options": {
                "multiOptionalFactorEnroll": True,
                "warnBeforePasswordExpired": False
            }
        }

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        resp = requests.post(authn_url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        if data['status'] == 'MFA_REQUIRED':
            factor = data['_embedded']['factors'][0]
            factor_id = factor['id']
            factor_type = factor['factorType']
            verify_url = factor['_links']['verify']['href']

            print(f"[+] MFA Required: {factor_type} - Sending verification...")

            verify_resp = requests.post(verify_url, json={"stateToken": data['stateToken']})
            verify_resp.raise_for_status()
            verify_data = verify_resp.json()

            print("[+] Waiting for MFA approval...")

            while verify_data['status'] == 'MFA_CHALLENGE':
                time.sleep(2)
                poll_url = verify_data['_links']['next']['href']
                verify_resp = requests.post(poll_url, json={"stateToken": data['stateToken']})
                verify_resp.raise_for_status()
                verify_data = verify_resp.json()

            if verify_data['status'] == 'SUCCESS':
                self.session_token = verify_data['sessionToken']
                print("[+] MFA Success!")
            else:
                raise Exception("MFA Failed or not approved.")

        elif data['status'] == 'SUCCESS':
            self.session_token = data['sessionToken']
            print("[+] Authentication Success!")

        else:
            raise Exception(f"Unhandled status: {data['status']}")

    def get_access_token(self, client_id: str = 'None', redirect_uri: str = 'http://localhost', scope: str = "openid profile"):
        """
        Exchange the MFA-authenticated session token for an OAuth2 access token.

        :param client_id: Okta OIDC client ID
        :param redirect_uri: Redirect URI registered in the Okta app
        :param scope: OAuth scopes (default: "openid profile")
        :return: Access token string
        """
        if not self.session_token:
            raise Exception("Session token missing. Call authenticate() first to complete MFA.")

        token_url = f"{self.base_url}/oauth2/default/v1/token"
        headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "session_token": self.session_token,
            "scope": scope,
            # For authorization_code flow, code_verifier and code are normally used here,
            # but we're simulating it using session_token for a one-step access token request.
        }

        response = requests.post(token_url, data=data, headers=headers)
        if response.status_code != 200:
            print("[!] Failed to get access token.")
            print(response.text)
            response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data.get("access_token")
        print("[+] Access token acquired via session_token + MFA.")
        return self.access_token

    def mfa_authenticate(self):
        code_verifier, code_challenge = self._generate_pkce_pair()

        auth_url = (
                f"{self.base_url}/oauth2/default/v1/authorize?"
                + urlencode({
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scopes,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": secrets.token_urlsafe(16)
        })
        )

        print(f"[+] Opening browser for authorization: {auth_url}")
        webbrowser.open(auth_url)

        httpd = self._start_local_http_server()
        print("[*] Waiting for user authorization...")
        httpd.handle_request()
        auth_code = httpd.auth_code
        if not auth_code:
            raise Exception("Authorization code not received.")

        token_url = f"{self.base_url}/oauth2/default/v1/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "code": auth_code,
            "code_verifier": code_verifier
        }

        print("[+] Exchanging code for access token...")
        resp = requests.post(token_url, data=data, headers=headers)
        resp.raise_for_status()
        tokens = resp.json()
        self.token = tokens.get("access_token")
        self.id_token = tokens.get("id_token")
        print("[+] Access token obtained.")

        return self.token

    def get_access_token(self):
        return self.token

    def get_id_token(self):
        return self.id_token

    def call_protected_api(self):
        """Call a protected API using the Okta session token."""
        if not self.session_token:
            raise Exception("Not authenticated. Call authenticate() first.")

        headers = {
            "Authorization": f"SSWS {self.session_token}",
            "Content-Type": "application/json"
        }

        resp = requests.get(self.api_url, headers=headers)
        resp.raise_for_status()
        return resp.json()
