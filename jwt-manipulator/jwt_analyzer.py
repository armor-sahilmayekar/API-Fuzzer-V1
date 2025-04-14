import jwt_tool
import json
from typing import Optional, Dict, Any


class JWTAnalyzer:
    """
    A class to analyze and dump information from a JWT token.
    """

    def __init__(self, token: str):
        """
        Initialize the JWTAnalyzer with a JWT token.

        :param token: JWT Token as a string.
        """
        self.token = token
        self.decoded_payload: Optional[Dict[str, Any]] = None

    def load_jwt_token(self) -> Optional[Dict[str, Any]]:
        """
        Decode the JWT token without verifying the signature.

        :return: Decoded JWT payload as a dictionary, or None if decoding fails.
        """
        try:
            self.decoded_payload = jwt_tool.decode(self.token, verify=False)
            return self.decoded_payload
        except Exception as e:
            print(f"Error decoding JWT: {e}")
            return None

    def validate_jwt_structure(self) -> bool:
        """
        Validate the structure of the JWT token (should be in three parts separated by periods).

        :return: True if the token structure is valid, False otherwise.
        """
        parts = self.token.split(".")
        return len(parts) == 3

    def test_jwt(self) -> Optional[Dict[str, Any]]:
        """
        Perform basic tests and dump the decoded JWT payload.

        :return: The decoded JWT payload if valid, or None if any test fails.
        """
        print("Testing JWT token...")

        # Validate JWT structure
        if not self.validate_jwt_structure():
            print("Invalid JWT structure.")
            return None

        # Decode the JWT token
        decoded_token = self.load_jwt_token()
        if decoded_token is None:
            print("Failed to decode JWT.")
            return None

        # Print the decoded token payload
        print("Decoded JWT Payload:")
        print(json.dumps(decoded_token, indent=2))

        # Additional validation (e.g., checking for specific claims)
        self.check_claims(decoded_token)

        return decoded_token

    def check_claims(self, decoded_token: Dict[str, Any]) -> None:
        """
        Check for specific claims in the decoded JWT payload and print the results.

        :param decoded_token: Decoded JWT token payload as a dictionary.
        """
        # Check if expiration claim 'exp' exists
        if "exp" in decoded_token:
            print("Expiration (exp) claim found:", decoded_token["exp"])
        else:
            print("Expiration (exp) claim not found.")

        # Check if issued at claim 'iat' exists
        if "iat" in decoded_token:
            print("Issued At (iat) claim found:", decoded_token["iat"])
        else:
            print("Issued At (iat) claim not found.")
