from modules.api.okta import OktaSeleniumAuth
from modules.util.config import EnvConfig

if __name__ == "__main__":
    config = EnvConfig()
    okta_domain = config.okta_base_url
    client_id = config.okta_client_id
    redirect_uri = config.okta_redirect_url
    username = config.user
    password = config.password
    auth = OktaSeleniumAuth(
        okta_domain=okta_domain,
        client_id=client_id,
        redirect_uri=redirect_uri,
        username=username,
        password=password,
    )

    token = auth.authorize()
    print(f"Access Token:{token}\n")
