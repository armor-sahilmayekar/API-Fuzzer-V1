from modules.case.operators import TestCase

import json

class FuzzyMatchTestCase(TestCase):
    """Test case that checks if any expected word exists in the response body (JSON).

    Example input for the expected value:
    {
      "test_number": 1,
      "name": "header_injection_Accept",
      "jira_description" : "",
      "method": "GET",
      "url": "https://mdr.api.secure-dev.services/metrics/incidents",
      "headers": {
        "Host": "mdr-api.secure-dev.services",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "attacker.com"
      },
      "body": {},
      "parameter": "?sort=1",
      "expected": {
        "status_code": 200,
        "operators": [{
          "type" : "match",
          "expected": "somevalue"
        }]
      }
    }

    In the above example, the "expected" field contains the "operators" array with each operator object having a "type" and an "expected" word or phrase to match in the response JSON body.
    """

    def evaluate_results(self) -> bool:
        if self.response and self.response.status_code == self.expected.status_code:
            try:
                # Parse the JSON response
                response_json = self.response.json()

                # Iterate over all operators in the "operators" array
                for operator in self.expected.expected:
                    if operator.get("type") == "match":
                        expected_words = operator.get("expected", "").split()

                        # Check if any of the expected words exist in the JSON response
                        for word in expected_words:
                            if self._contains_word(response_json, word):
                                return True
            except ValueError:
                # If the response is not valid JSON, return False
                return False
        return False

    def _contains_word(self, obj, word):
        """Recursively search for the word in JSON-like structures."""
        if isinstance(obj, dict):
            # Check all values in the dictionary
            for value in obj.values():
                if self._contains_word(value, word):
                    return True
        elif isinstance(obj, list):
            # Check all items in the list
            for item in obj:
                if self._contains_word(item, word):
                    return True
        elif isinstance(obj, str):
            # Check if the word is in the string
            if word in obj:
                return True
        return False
