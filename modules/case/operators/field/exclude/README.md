
# Response Validation Test Cases

This module defines test cases used to validate HTTP response payloads using custom logic such as:
- Field non-existence
- Value non-matching based on regex
- Status code assertions

## Classes

### `DoesNotMatchTestCase`

- Validates that a specified response field does **not** match a given regex pattern.
- Ensures HTTP status code matches expectation.
- Example `expected` operator block:
```json
{
  "type": "does_not_match",
  "field": "response_field",
  "expected": "^unexpected_value$"
}
```

### `FieldNotExistTestCase`

- Verifies that certain fields or values are **absent** from the HTTP response.
- Also ensures status code match.
- Example `expected` list for this case:
```json
[
  {
    "type": "field_not_exist",
    "field": "secret_token",
    "status_code": 200
  },
  {
    "type": "value_not_exist",
    "field": "data",
    "expected": "sensitive_info",
    "status_code": 200
  }
]
```

## Method Overview

### `evaluate_results()`
- Core logic to validate the test condition.
- Called automatically for each test case.

### `get_response_field(field: str)`
- Utility to fetch a field from the response JSON.

### `match_regex(value: str, pattern: str)` (in `DoesNotMatchTestCase`)
- Validates regex pattern match.

## Usage

Integrate these test cases into your test framework by instantiating them with appropriate request/response data and expected rules.

Make sure to install test dependencies and run using a test runner like `pytest`.
