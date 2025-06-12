import pytest

from modules.util.config import HeaderBuilder  # Replace with actual path


@pytest.fixture
def env_token_account(monkeypatch):
    monkeypatch.setenv("TOKEN", "env-token")
    monkeypatch.setenv("ACCOUNT_ID", "env-account")


def test_header_builder_with_env(env_token_account):
    builder = HeaderBuilder(referrer="https://testsite")
    headers = builder.to_dict()

    assert headers["authorization"] == "Bearer env-token"
    assert headers["x-account-context"] == "env-account"
    assert headers["origin"] == "https://testsite"
    assert headers["referer"] == "https://testsite"
    assert "accept" in headers
    assert builder.authorization == "Bearer env-token"


def test_header_builder_with_direct_input():
    builder = HeaderBuilder(referrer="https://direct", token="mytoken", account_id="myaccount")
    headers = builder.build()

    assert headers["authorization"] == "Bearer mytoken"
    assert headers["x-account-context"] == "myaccount"
    assert headers["origin"] == "https://direct"


def test_header_builder_missing_token(monkeypatch):
    monkeypatch.delenv("TOKEN", raising=False)
    monkeypatch.setenv("ACCOUNT_ID", "some-account")

    with pytest.raises(ValueError, match="Missing TOKEN"):
        HeaderBuilder()


def test_header_builder_missing_account_id(monkeypatch):
    monkeypatch.delenv("ACCOUNT_ID", raising=False)
    monkeypatch.setenv("TOKEN", "some-token")

    with pytest.raises(ValueError, match="Missing ACCOUNT_ID"):
        HeaderBuilder()


def test_header_builder_sanitized_json():
    builder = HeaderBuilder(referrer="https://site", token="secret-token", account_id="acc-x")
    sanitized = builder.sanitize_json()

    assert '"authorization": "Bearer SANITIZED"' in sanitized
    assert "secret-token" not in sanitized
