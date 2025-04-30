import os
import time
from unittest.mock import MagicMock
from unittest.mock import patch

import jwt
import pytest

from modules.api.authn import JWTAnalyzer, JWTClaims  # Assuming the class is saved in authn.py


@pytest.fixture(scope="module", autouse=True)
def set_env_secret():
    os.environ["JWT_SECRET"] = "testsecret"
    yield
    del os.environ["JWT_SECRET"]


@pytest.fixture
def valid_jwt():
    payload = {
        "sub": "1234567890",
        "name": "John Doe",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    secret = os.environ["JWT_SECRET"]
    return jwt.encode(payload, secret, algorithm="HS256")


def test_structure(valid_jwt):
    analyzer = JWTAnalyzer(valid_jwt)
    assert analyzer.validate_jwt_structure() is True


def test_header(valid_jwt):
    analyzer = JWTAnalyzer(valid_jwt)
    header = analyzer.get_jwt_header()
    assert header is not None
    assert header["alg"] == "HS256"


def test_decode(valid_jwt):
    analyzer = JWTAnalyzer(valid_jwt)
    payload = analyzer.load_jwt_token()
    assert payload is not None
    assert payload["sub"] == "1234567890"


def test_check_claims(capfd, valid_jwt):
    analyzer = JWTAnalyzer(valid_jwt)
    payload = analyzer.load_jwt_token()
    analyzer.check_claims(payload)
    out, _ = capfd.readouterr()
    assert "IAT claim found" in out
    assert "EXP claim found" in out


def test_verify(valid_jwt):
    analyzer = JWTAnalyzer(valid_jwt)
    assert analyzer.verify_jwt(key=os.environ["JWT_SECRET"], algorithms=["HS256"]) is True


def test_expiration(valid_jwt):
    analyzer = JWTAnalyzer(valid_jwt)
    assert analyzer.is_expired() is False


def test_reencode(valid_jwt):
    analyzer = JWTAnalyzer(valid_jwt)
    new_token = analyzer.reencode_jwt(os.environ["JWT_SECRET"])
    assert new_token is not None
    assert isinstance(new_token, str)


def test_get_algorithm(valid_jwt):
    analyzer = JWTAnalyzer(valid_jwt)
    alg = analyzer.get_algorithm()
    assert alg == "HS256"


def test_check_claims(valid_jwt):
    analyzer = JWTAnalyzer(valid_jwt)
    decoded = analyzer.load_jwt_token()
    claims = analyzer.check_claims(decoded)

    assert claims.exp is not None
    assert claims.iat is not None
    assert claims.sub == "1234567890"


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

    with pytest.raises(Exception, match="Invalid token format"):
        analyzer.load_jwt_token()


def test_validate_jwt_structure_valid(valid_token):
    """Test valid JWT structure (three parts separated by periods)."""
    analyzer = JWTAnalyzer(valid_token)
    assert analyzer.validate_jwt_structure()


def test_validate_jwt_structure_invalid(invalid_token):
    """Test invalid JWT structure (not three parts)."""
    analyzer = JWTAnalyzer(invalid_token)
    assert not analyzer.validate_jwt_structure()


def test_dump_jwt_valid_token(caplog):
    """Test that a well-formed JWT is logged correctly."""
    valid_token = "header.payload.signature"
    analyzer = JWTAnalyzer(valid_token)

    with caplog.at_level("DEBUG"):
        analyzer.dump_jwt()

    assert "--- JWT Token Dump ---" in caplog.text
    assert "Header: header" in caplog.text
    assert "Payload: payload" in caplog.text
    assert "Signature: signature" in caplog.text
    assert "Invalid JWT structure" not in caplog.text


def test_dump_jwt_invalid_token(caplog):
    """Test that an improperly formatted JWT logs an error."""
    invalid_token = "malformed.token"
    analyzer = JWTAnalyzer(invalid_token)

    with caplog.at_level("ERROR"):
        analyzer.dump_jwt()

    assert "Invalid JWT structure" in caplog.text
    assert "--- JWT Token Dump ---" not in caplog.text


def test_test_jwt_success(monkeypatch):
    """Test full JWT analysis flow succeeds and returns decoded payload."""
    token = "header.payload.signature"
    expected_payload = {"sub": "user123", "exp": 1234567890}
    analyzer = JWTAnalyzer(token)

    monkeypatch.setattr(analyzer, "dump_jwt", MagicMock())
    monkeypatch.setattr(analyzer, "validate_jwt_structure", MagicMock(return_value=True))
    monkeypatch.setattr(analyzer, "load_jwt_token", MagicMock(return_value=expected_payload))
    monkeypatch.setattr(analyzer, "check_claims", MagicMock())

    result = analyzer.test_jwt()

    assert result == expected_payload
    analyzer.dump_jwt.assert_called_once()
    analyzer.validate_jwt_structure.assert_called_once()
    analyzer.load_jwt_token.assert_called_once()
    analyzer.check_claims.assert_called_once_with(expected_payload)


def test_test_jwt_invalid_structure(monkeypatch, caplog):
    """Test JWT analysis fails due to invalid structure."""
    token = "invalid.token"
    analyzer = JWTAnalyzer(token)

    monkeypatch.setattr(analyzer, "dump_jwt", MagicMock())
    monkeypatch.setattr(analyzer, "validate_jwt_structure", MagicMock(return_value=False))
    monkeypatch.setattr(analyzer, "load_jwt_token", MagicMock())
    monkeypatch.setattr(analyzer, "check_claims", MagicMock())

    with caplog.at_level("ERROR"):
        result = analyzer.test_jwt()

    assert result is None
    assert "Invalid JWT structure." in caplog.text
    analyzer.dump_jwt.assert_called_once()
    analyzer.validate_jwt_structure.assert_called_once()
    analyzer.load_jwt_token.assert_not_called()
    analyzer.check_claims.assert_not_called()


def test_test_jwt_decode_failure(monkeypatch, caplog):
    """Test JWT analysis fails during decoding."""
    token = "header.payload.signature"
    analyzer = JWTAnalyzer(token)

    monkeypatch.setattr(analyzer, "dump_jwt", MagicMock())
    monkeypatch.setattr(analyzer, "validate_jwt_structure", MagicMock(return_value=True))
    monkeypatch.setattr(analyzer, "load_jwt_token", MagicMock(return_value=None))
    monkeypatch.setattr(analyzer, "check_claims", MagicMock())

    with caplog.at_level("ERROR"):
        result = analyzer.test_jwt()

    assert result is None
    assert "Failed to decode JWT." in caplog.text
    analyzer.dump_jwt.assert_called_once()
    analyzer.validate_jwt_structure.assert_called_once()
    analyzer.load_jwt_token.assert_called_once()
    analyzer.check_claims.assert_not_called()


def test_check_claims_all_present(caplog):
    """Test check_claims with all standard claims present."""
    token = "dummy.token.value"
    analyzer = JWTAnalyzer(token)

    decoded_token = {
        "exp": 1712345678,
        "iat": 1712340000,
        "nbf": 1712330000,
        "aud": "my-audience",
        "iss": "issuer.com",
        "sub": "user123",
        "jti": "token-id-456"
    }

    with caplog.at_level("DEBUG"):
        claims = analyzer.check_claims(decoded_token)

    assert isinstance(claims, JWTClaims)
    assert claims.exp == 1712345678
    assert claims.iat == 1712340000
    assert claims.nbf == 1712330000
    assert claims.aud == "my-audience"
    assert claims.iss == "issuer.com"
    assert claims.sub == "user123"
    assert claims.jti == "token-id-456"

    for field in decoded_token:
        assert f"{field.upper()} claim found" in caplog.text


def test_check_claims_partial_missing(caplog):
    """Test check_claims when some claims are missing from the decoded token."""
    token = "dummy.token.value"
    analyzer = JWTAnalyzer(token)

    decoded_token = {
        "exp": 1712345678,
        "sub": "user123"
    }

    with caplog.at_level("DEBUG"):
        claims = analyzer.check_claims(decoded_token)

    assert isinstance(claims, JWTClaims)
    assert claims.exp == 1712345678
    assert claims.sub == "user123"
    assert claims.iat is None
    assert claims.nbf is None
    assert claims.aud is None
    assert claims.iss is None
    assert claims.jti is None

    assert "EXP claim found" in caplog.text
    assert "SUB claim found" in caplog.text
    assert "IAT claim not found." in caplog.text
    assert "AUD claim not found." in caplog.text
