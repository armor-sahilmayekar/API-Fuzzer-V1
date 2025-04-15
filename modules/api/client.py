import os

import requests


class APIClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        """
        Initializes the APIClient with the base URL of the API and the API key.

        Args:
            base_url (str): The base URL for the API.
            api_key (str): The API key used for authentication in headers.
        """
        self.base_url = base_url
        self.api_key = api_key

    def send_request(self, method: str, endpoint: str, params: dict = None, headers: dict = None) -> requests.Response:
        """
        Sends an HTTP request to the API and returns the response.

        Args:
            method (str): The HTTP method (GET, POST, etc.).
            endpoint (str): The API endpoint to be appended to the base URL.
            params (dict, optional): The query parameters to be included in the request.
            headers (dict, optional): The headers to be included in the request.

        Returns:
            requests.Response: The response object from the request.
        """
        url = os.path.join(self.base_url, endpoint)
        if headers is None:
            headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.request(method, url, params=params, headers=headers)
        return response