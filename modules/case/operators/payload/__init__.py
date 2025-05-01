import json
from typing import Any

from modules.case.data_objects import Expected
from modules.case.operators import TestCase
from modules.util.loggable import Loggable as log

class ExactPayloadMatchTestCase(TestCase):
    """Test case that checks for an exact match of the entire payload."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate_results(self) -> bool:
        """Evaluate if the response payload exactly matches the expected payload(s)."""
        if not self.response:
            return False

        if isinstance(self.expected, Expected):
            return self._check_result(self.expected.expected)

        if isinstance(self.expected, list) and all(isinstance(item, Expected) for item in self.expected):
            for item in self.expected:
                if item.expected_type == "payload" and not self._check_result(item):
                    log.error(f"[{self.test_number}] Payload mismatch: expected {item.expected}")
                    return False
            return True

        raise AssertionError(f"Invalid 'expected' type: {type(self.expected)}")

    def _check_result(self, expected: Expected) -> bool:
        try:
            response_payload = self.response.json()
            expected_payload = expected.expected

            # Return False if types do not match
            if type(response_payload) != type(expected_payload):
                log.error(f"[{self.test_number}]")
                return False

            # Return the result of direct comparison
            return response_payload == expected_payload

        except (ValueError, TypeError, AttributeError) as e:
            log.error(f"e")
            return False

