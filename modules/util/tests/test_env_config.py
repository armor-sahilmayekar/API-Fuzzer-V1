import pytest

from modules.util.config import EnvConfig  # Replace with actual path


@pytest.fixture
def set_env_vars(monkeypatch):
    monkeypatch.setenv("TOKEN", "test-token")
    monkeypatch.setenv("USERNAME", "test-user")
    monkeypatch.setenv("PASS", "test-pass")
    monkeypatch.setenv("ACCOUNT_ID", "acc_123456")
    monkeypatch.setenv("OKTA_BASE_URL", "bda")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("OKTA_CLIENT_ID", "2")
    monkeypatch.setenv("OKTA_REDIRECT_URL", "2")
    yield


def test_env_config_loads_all_vars(set_env_vars):
    config = EnvConfig()
    assert config.token == "test-token"
    assert config.user == "test-user"
    assert config.password == "test-pass"
    assert config.account_id == "acc_123456"
    assert config.log_level == "DEBUG"


@pytest.mark.parametrize("missing_var", ["TOKEN", "USERNAME", "PASS", "ACCOUNT_ID", "LOG_LEVEL"])
def test_env_config_missing_required_var(monkeypatch, missing_var):
    monkeypatch.delenv(missing_var, raising=False)
    for var in ["TOKEN", "USERNAME", "PASS", "ACCOUNT_ID", "LOG_LEVEL"]:
        if var != missing_var:
            monkeypatch.setenv(var, f"dummy_{var.lower()}")

    with pytest.raises(EnvironmentError) as excinfo:
        EnvConfig()
    assert f"Missing required environment variable: '{missing_var}'" in str(excinfo.value)
