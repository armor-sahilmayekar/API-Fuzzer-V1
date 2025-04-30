import os
import requests
import time
import jwt
import json
import datetime
from typing import Optional, Dict, Any, Union
from modules.util.loggable import Loggable as log
from dataclasses import dataclass
from typing import Optional


@dataclass
class JWTClaims:
    exp: Optional[int] = None   # Expiration Time
    iat: Optional[int] = None   # Issued At
    nbf: Optional[int] = None   # Not Before
    aud: Optional[str] = None   # Audience
    iss: Optional[str] = None   # Issuer
    sub: Optional[str] = None   # Subject
    jti: Optional[str] = None   # JWT ID



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
            log.info(f"Error decoding JWT: {e}")
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
        log.info the JWT token in a formatted manner (e.g., in three parts: header, payload, signature).
        """
        parts = self.token.split(".")
        if len(parts) == 3:
            log.debug("\n--- JWT Token Dump ---")
            log.debug(f"Header: {parts[0]}")
            log.debug(f"Payload: {parts[1]}")
            log.debug(f"Signature: {parts[2]}")
            log.debug("-----------------------")
        else:
            log.error("Invalid JWT structure. Unable to dump the token.")

    def test_jwt(self) -> Optional[Dict[str, Any]]:
        """
        Run a full test: dump token, validate structure, decode, and check claims.

        :return: Decoded JWT payload or None if test fails.
        """
        log.info("Testing JWT token...")
        self.dump_jwt()

        if not self.validate_jwt_structure():
            log.error("Invalid JWT structure.")
            return None

        decoded_token = self.load_jwt_token()
        if decoded_token is None:
            log.error("Failed to decode JWT.")
            return None

        log.debug("Decoded JWT Payload:")
        log.debug(json.dumps(decoded_token, indent=2))
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
                log.debug(f"{field.upper()} claim found: {value}")
            else:
                log.debug(f"{field.upper()} claim not found.")

        return claims

    def get_jwt_header(self) -> Optional[Dict[str, Any]]:
        """
        Extract and return the JWT header without verifying the signature.

        :return: Header dictionary or None on error.
        """
        try:
            self.header = jwt.get_unverified_header(self.token)
            log.debug("JWT Header:")
            log.debug(json.dumps(self.header, indent=2))
            return self.header
        except jwt.DecodeError as e:
            log.error(f"Error decoding JWT header: {e}")
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
            log.info("JWT successfully verified.")
            log.debug(json.dumps(decoded, indent=2))
            return True
        except jwt.ExpiredSignatureError:
            log.error("JWT has expired.")
        except jwt.InvalidTokenError as e:
            log.error(f"Invalid JWT: {e}")
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
            log.info("Re-encoded JWT:")
            log.debug(new_token)
            return new_token
        except Exception as e:
            log.error(f"Error re-encoding JWT: {e}")
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
    >>> log.debug(response)

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
        self.session_token = None
        self.access_token = None

    def authenticate(self):
        """Authenticate user and trigger MFA if required."""
        authn_url = f"{self.base_url}/api/v1/authn"
        payload = {
            "username": self.username,
            "password": self.password,
            "options": {
                "multiOptionalFactorEnroll": True,
                "warnBeforePasswordExpired": True
            }
        }
        resp = requests.post(authn_url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data['status'] == 'MFA_REQUIRED':
            factor = data['_embedded']['factors'][0]
            factor_id = factor['id']
            factor_type = factor['factorType']
            verify_url = factor['_links']['verify']['href']

            log.info(f"[+] MFA Required: {factor_type} - Sending verification...")

            verify_resp = requests.post(verify_url, json={"stateToken": data['stateToken']})
            verify_resp.raise_for_status()
            verify_data = verify_resp.json()

            log.info("[+] Waiting for MFA approval...")

            while verify_data['status'] == 'MFA_CHALLENGE':
                time.sleep(2)
                poll_url = verify_data['_links']['next']['href']
                verify_resp = requests.post(poll_url, json={"stateToken": data['stateToken']})
                verify_resp.raise_for_status()
                verify_data = verify_resp.json()

            if verify_data['status'] == 'SUCCESS':
                self.session_token = verify_data['sessionToken']
                log.info("[+] MFA Success!")
            else:
                raise Exception("MFA Failed or not approved.")

        elif data['status'] == 'SUCCESS':
            self.session_token = data['sessionToken']
            log.info("[+] Authentication Success!")

        else:
            raise Exception(f"Unhandled status: {data['status']}")

    def get_access_token(self):
        """
        Placeholder for exchanging session token for an OAuth2 access token.

        You must implement this depending on your Okta application's setup.
        """
        raise NotImplementedError("OAuth token exchange must be implemented based on your Okta setup.")

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
