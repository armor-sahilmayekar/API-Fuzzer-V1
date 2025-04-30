import os
import time

import jwt
import pytest

from modules.api.authn import JWTAnalyzer


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
