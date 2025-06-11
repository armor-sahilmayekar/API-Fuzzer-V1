import copy
import os
import json
from dotenv import load_dotenv


class EnvConfig:
    """
    EnvConfig loads and validates environment variables for application configuration.

    Environment Variables:
    -----------------------
    - TOKEN      : API token (string)
    - USER       : Username (string)
    - PASS       : Password (string)
    - HEADERS    : HTTP headers in JSON format (string)
    - ACCOUNT_ID : Account identifier (string)

    Example .env:
    -------------
    TOKEN=your_api_token
    USER=your_username
    PASS=your_password
    HEADERS={"Authorization": "Bearer your_api_token", "Content-Type": "application/json"}
    ACCOUNT_ID=acc_123456

    Usage:
    ------
    >>> from modules.util.config import EnvConfig
    >>> config = EnvConfig()
    >>> print(config.token)
    >>> print(config.headers["Authorization"])
    >>> print(config.account_id)
    """

    def __init__(self, dotenv_path: str = '.env'):
        load_dotenv(dotenv_path)
        self._token = self._get_env_var('TOKEN')
        self._user = self._get_env_var('USERNAME')
        self._password = self._get_env_var('PASS')
        self._account_id = self._get_env_var('ACCOUNT_ID')
        self._log_level = self._get_env_var('LOG_LEVEL')
        self._okta_base_url = self._get_env_var('OKTA_BASE_URL')
        self._okta_client_id = self._get_env_var('OKTA_CLIENT_ID')
        self._okta_redirect_url = self._get_env_var('OKTA_REDIRECT_URL')

    def _get_env_var(self, var_name: str) -> str:
        """Fetches an environment variable or raises an error if not found."""
        value = os.getenv(var_name)
        if value is None:
            raise EnvironmentError(f"Missing required environment variable: '{var_name}'")
        return value

    def _get_json_env_var(self, var_name: str) -> dict:
        """Parses a JSON environment variable or raises an error if invalid."""
        raw = self._get_env_var(var_name)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError(f"Environment variable '{var_name}' must be a valid JSON string.")

    @property
    def okta_redirect_url(self) -> str:
        return self._okta_redirect_url

    @okta_redirect_url.setter
    def okta_redirect_url(self, url: str) -> None:
        self._okta_redirect_url = url

    @property
    def okta_client_id(self) -> str:
        return self._okta_client_id

    @okta_client_id.setter
    def okta_client_id(self, okta_client_id: str) -> None:
        self._okta_client_id = str(okta_client_id)

    @property
    def okta_base_url(self) -> str:
        return self._okta_base_url

    @property
    def token(self) -> str:
        return self._token

    @property
    def user(self) -> str:
        return self._user

    @property
    def password(self) -> str:
        return self._password

    @property
    def account_id(self) -> str | int:
        return self._account_id

    @property
    def log_level(self) -> str:
        return self._log_level


class HeaderBuilder:
    """
    HeaderBuilder constructs HTTP headers for API requests using dynamic input
    and environment configuration. All headers are exposed as properties.

    Required Environment Variables:
    -------------------------------
    - TOKEN        : Bearer token for Authorization header.
    - ACCOUNT_ID   : Account identifier for x-account-context.

    Usage:
    ------
    >>> builder = HeaderBuilder(referrer="https://mdr")
    >>> print(builder.authorization)
    >>> headers = builder.to_dict()
    >>> requests.get(url, headers=headers)
    """

    def __init__(self, referrer: str = None, token: str = None, account_id: str = None):
        self._referrer = referrer
        self._token = token or os.getenv("TOKEN")
        self._account_id = account_id or os.getenv("ACCOUNT_ID")

        if not self._token:
            raise ValueError("Missing TOKEN: provide it directly or set the TOKEN environment variable.")
        if not self._account_id:
            raise ValueError("Missing ACCOUNT_ID: provide it directly or set the ACCOUNT_ID environment variable.")

    @property
    def accept(self) -> str:
        return "application/json"

    @property
    def accept_language(self) -> str:
        return "en-US,en;q=0.9"

    @property
    def if_none_match(self) -> str:
        return 'W/"1b0cd-mBw7Z/VQAsFNfEzG1bLwgN7+CR0"'

    @property
    def internal(self) -> str:
        return "true"

    @property
    def origin(self) -> str:
        return self._referrer

    @property
    def priority(self) -> str:
        return "u=1, i"

    @property
    def referer(self) -> str:
        return self._referrer

    @property
    def x_account_context(self) -> str:
        return self._account_id

    @property
    def authorization(self) -> str:
        return f"Bearer {self._token}"

    def to_dict(self) -> dict:
        """Return the full headers as a dictionary."""
        return {
            "accept": self.accept,
            "accept-language": self.accept_language,
            "if-none-match": self.if_none_match,
            "internal": self.internal,
            "origin": self.origin,
            "priority": self.priority,
            "referer": self.referer,
            "x-account-context": self.x_account_context,
            "authorization": self.authorization,
        }

    def __str__(self):
        return json.dumps(self.to_dict())

    def sanitize_json(self) -> str:
        tmp = copy.copy(self)
        tmp._token = f'SANITIZED'
        return json.dumps(tmp.to_dict())

    def as_(self) -> dict:
        """Return the full headers as a dictionary."""
        return {
            "accept": self.accept,
            "accept-language": self.accept_language,
            "if-none-match": self.if_none_match,
            "internal": self.internal,
            "origin": self.origin,
            "priority": self.priority,
            "referer": self.referer,
            "x-account-context": self.x_account_context,
            "authorization": self.authorization,
        }

    def build(self) -> dict:
        """Alias for as_dict()."""
        return self.to_dict()
