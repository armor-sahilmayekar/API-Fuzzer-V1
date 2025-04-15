import time

import jwt
import json
import datetime
from typing import Optional, Dict, Any, Union

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
