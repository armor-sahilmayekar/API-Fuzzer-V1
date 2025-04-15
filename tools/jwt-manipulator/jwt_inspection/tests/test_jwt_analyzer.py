import pytest
from unittest.mock import patch
from modules.api.authn import JWTAnalyzer  # Assuming the class is saved in authn.py


@pytest.fixture
def valid_token():
    """Fixture providing a valid JWT token."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHBpcmVkX2F0IjoxNjE2NzE0MTcyLCJpYXQiOjE2MTY3MTAwMjh9.SvTdIqV9xLZx5dxbyVlmG9se7Iz2lAqMvTugF9O3g5c"


@pytest.fixture
def invalid_token():
    """Fixture providing an invalid JWT token."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9eyJleHBpcmVkX2F0IjoxNjE2NzE0MTcyLCJpYXQiOjE2MTY3MTAwMjh9SvTdIqV9xLZx5dxbyVlmG9se7Iz2lAqMvTugF9O3g5c"


@patch("jwt.decode")
def test_load_jwt_token_success(mock_decode, valid_token):
    """Test decoding a valid JWT token."""
    analyzer = JWTAnalyzer(valid_token)
    mock_decode.return_value = {"exp": 1616714172, "iat": 1616710028}

    decoded_payload = analyzer.load_jwt_token()
    assert decoded_payload is not None
    assert decoded_payload["exp"] == 1616714172
    assert decoded_payload["iat"] == 1616710028


@patch("jwt.decode")
def test_load_jwt_token_failure(mock_decode, invalid_token):
    """Test failure when decoding an invalid JWT token."""
    analyzer = JWTAnalyzer(invalid_token)
    mock_decode.side_effect = Exception("Invalid token format")

    decoded_payload = analyzer.load_jwt_token()
    assert decoded_payload is None


def test_validate_jwt_structure_valid(valid_token):
    """Test valid JWT structure (three parts separated by periods)."""
    analyzer = JWTAnalyzer(valid_token)
    assert analyzer.validate_jwt_structure()


def test_validate_jwt_structure_invalid(invalid_token):
    """Test invalid JWT structure (not three parts)."""
    analyzer = JWTAnalyzer(invalid_token)
    assert not analyzer.validate_jwt_structure()


@patch("builtins.print")  # Mock print to test the output
def test_dump_jwt(mock_print, valid_token):
    """Test dumping the JWT token in a formatted manner."""
    analyzer = JWTAnalyzer(valid_token)
    analyzer.dump_jwt()

    # Check that the formatted JWT output has been printed
    mock_print.assert_any_call("--- JWT Token Dump ---")
    mock_print.assert_any_call("Header: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
    mock_print.assert_any_call("Payload: eyJleHBpcmVkX2F0IjoxNjE2NzE0MTcyLCJpYXQiOjE2MTY3MTAwMjh9")
    mock_print.assert_any_call("Signature: SvTdIqV9xLZx5dxbyVlmG9se7Iz2lAqMvTugF9O3g5c")
    mock_print.assert_any_call("-----------------------")


@patch("builtins.print")  # Mock print to test the output
def test_test_jwt_success(mock_print, valid_token):
    """Test the test_jwt method when the JWT is valid."""
    analyzer = JWTAnalyzer(valid_token)
    analyzer.test_jwt()

    # Check for printed statements
    mock_print.assert_any_call("Testing JWT token...")
    mock_print.assert_any_call("Decoded JWT Payload:")
    mock_print.assert_any_call("Expiration (exp) claim found: 1616714172")
    mock_print.assert_any_call("Issued At (iat) claim found: 1616710028")


@patch("builtins.print")  # Mock print to test the output
def test_test_jwt_invalid_structure(mock_print, invalid_token):
    """Test the test_jwt method when the JWT has an invalid structure."""
    analyzer = JWTAnalyzer(invalid_token)
    analyzer.test_jwt()

    mock_print.assert_any_call("Testing JWT token...")
    mock_print.assert_any_call("Invalid JWT structure.")


@patch("builtins.print")  # Mock print to test the output
def test_check_claims(mock_print, valid_token):
    """Test checking claims (exp and iat)."""
    analyzer = JWTAnalyzer(valid_token)
    decoded_token = {
        "exp": 1616714172,
        "iat": 1616710028
    }
    analyzer.check_claims(decoded_token)

    mock_print.assert_any_call("Expiration (exp) claim found: 1616714172")
    mock_print.assert_any_call("Issued At (iat) claim found: 1616710028")
