from json import JSONDecodeError

from modules.case.operators import TestCase
import re
from modules.util.loggable import Loggable as log


class DoesNotMatchTestCase(TestCase):
    """Test case that checks if a field does not match a given regex pattern."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate_results(self) -> bool:
        # Check status code match
        status_code_match = self.response and self.response.status_code == self.expected.status_code

        # Check does_not_match for operators
        does_not_match_check_result = True
        for operator in self.expected.expected:
            if operator["type"] == "does_not_match":
                field = operator.get("field")
                expected_pattern = operator.get("expected")

                # Get the actual value from the response field
                actual_value = self.get_response_field(field)

                # Check if the value matches the regex; it should NOT match
                if self.match_regex(actual_value, expected_pattern):
                    does_not_match_check_result = False
                    break

        return status_code_match and does_not_match_check_result

    def get_response_field(self, field):
        # Method to extract specific field from the response body.
        # Adjust logic based on how the response is structured.
        if field == "response_field":
            return self.response.json().get("response_field")  # Modify as per actual structure
        return None

    def match_regex(self, value: str, pattern: str) -> bool:
        # Compile and match the regex pattern against the value
        if value is None:
            return False
        return bool(re.match(pattern, value))


class FieldNotExistTestCase(TestCase):
    """Test case that checks if a field does not exist or a value does not exist in the response."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate_results(self) -> bool:
        if not self.response:
            return False

        status_code_match = all(
            self.response.status_code == op.status_code for op in self.expected
        )

        for operator in self.expected:
            try:
                if operator.expected_type == "field_not_exist":
                    # Fail if the field *does* exist
                    if self.get_response_field(operator.field) is not None:
                        return False

                elif operator.expected_type == "value_not_exist":
                    actual_value = self.get_response_field(operator.field)
                    if actual_value is not None and operator.expected in str(actual_value):
                        return False

            except (JSONDecodeError, Exception) as e:
                log.error(f"[{self.test_number}] Evaluation error: {e}")
                return False

        return status_code_match

    def get_response_field(self, field) -> bool:
        if self.response.json().get(field, None) is not None:
            return True  # Modify as per actual structure
        return False
