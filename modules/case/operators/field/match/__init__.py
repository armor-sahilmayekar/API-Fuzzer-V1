from modules.case.operators.base import TestCase
import re


class ExactMatchTestCase(TestCase):
    """Test case that checks if a field has an exact match with the expected value."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate_results(self) -> bool:
        # Check status code match
        status_code_match = self.response and self.response.status_code == self.expected.status_code

        # Check exact match for operators
        exact_match_check_result = True
        for operator in self.expected.expected:
            if operator["type"] == "exact_match":
                field = operator.get("field")
                expected_value = operator.get("expected")

                # Get the actual value from the response field
                actual_value = self.get_response_field(field)

                # Check for exact match depending on type
                if not self.is_exact_match(actual_value, expected_value):
                    exact_match_check_result = False
                    break

        return status_code_match and exact_match_check_result

    def get_response_field(self, field):
        # Method to extract specific field from the response body.
        # Adjust logic based on how the response is structured.
        if field == "response_field":
            return self.response.json().get("response_field")  # Modify as per actual structure
        return None

    def is_exact_match(self, actual_value, expected_value):
        """Compares actual_value with expected_value for various types."""
        if type(expected_value) != type(actual_value):
            return False

        if isinstance(expected_value, str):
            # Direct string comparison
            return actual_value == expected_value
        elif isinstance(expected_value, list):
            # Compare lists element by element
            return actual_value == expected_value
        elif isinstance(expected_value, dict):
            # Compare dictionaries key by key
            return actual_value == expected_value
        elif isinstance(expected_value, int):
            # Direct integer comparison
            return actual_value == expected_value
        else:
            # For unsupported types, return False
            return False



class FieldMatchTestCase(TestCase):
    """Test case that validates a specific field in a JSON response."""

    def evaluate_results(self) -> bool:
        if not self.response:
            return False
        try:
            json_body = self.response.json()
            field = self.expected.expected.get("field")
            expected_value = self.expected.expected.get("expected")
            return json_body.get(field) == expected_value
        except Exception:
            return False


class MatchTestCase(TestCase):
    """Test case that checks status code match and regex match on data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate_results(self) -> bool:
        # Check status code match
        status_code_match = self.response and self.response.status_code == self.expected.status_code

        # Check regex match for operators
        regex_match_result = True
        for operator in self.expected.expected:
            if operator["type"] == "exact_match_regex":
                field = operator.get("field")
                expected_pattern = operator.get("expected")

                # Get the actual value from the response field
                actual_value = self.get_response_field(field)

                if not self.match_regex(actual_value, expected_pattern):
                    regex_match_result = False
                    break

        return status_code_match and regex_match_result

    def get_response_field(self, field):
        # Method to extract specific field from the response body.
        # Adjust logic based on how the response is structured.
        if field == "response_body_field":
            return self.response.json().get("response_body_field")  # Modify as per actual structure
        return None

    def match_regex(self, value: str, pattern: str) -> bool:
        # Compile and match the regex pattern against the value
        if value is None:
            return False
        return bool(re.match(pattern, value))

class ExactMatchTestCase(TestCase):
    """Test case that requires exact response body match."""

    def evaluate_results(self) -> bool:
        response_value = self.response.text.strip()
        expected_response_value = self.expected.expected.get("expected", "").strip()
        return bool(
                self.response and
                self.response.status_code == self.expected.status_code and
                response_value == expected_response_value
        )


class InstanceOfTypeTestCase(TestCase):
    """Test case that checks if a field is an instance of the specified type."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate_results(self) -> bool:
        # Check status code match
        status_code_match = self.response and self.response.status_code == self.expected.status_code

        # Check instance type match for operators
        instance_type_check_result = True
        for operator in self.expected.expected:
            if operator.expected_type == "instance_of_type":
                field = operator.field
                expected_type = operator.expected

                # Get the actual value from the response field
                actual_value = self.get_response_field(operator.field)

                # Check if actual_value is an instance of the expected_type
                if not isinstance(actual_value, operator.expected):
                    instance_type_check_result = False
                    break

        return status_code_match and instance_type_check_result

    def get_response_field(self, field):
        # Method to extract specific field from the response body.
        # Adjust logic based on how the response is structured.
        if field == "response_field":
            return self.response.json().get(field)  # Modify as per actual structure
        return None
