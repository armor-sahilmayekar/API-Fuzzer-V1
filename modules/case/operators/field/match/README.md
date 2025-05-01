
# Test Framework - Field Matching Types

This document explains how to use various types of matching logic in the test framework. These matching types allow you to check the response for specific values, field types, and conditions. The following types of matching are supported:

## Test Case JSON Structure

Below is the overall JSON structure used for defining test cases. Each test case includes a `status_code` check and one or more operators for matching fields in the response.

```json
{
  "test_number": 1,
  "name": "header_injection_Accept",
  "jira_description": "",
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
    "operators": [
      {
        "type": "exact_match",
        "field": "response_field_str",
        "expected": "exact_value"
      },
      {
        "type": "instance_of_type",
        "field": "response_field_list",
        "expected": "list"
      },
      {
        "type": "does_not_match",
        "field": "response_field_dict",
        "expected": "^unexpected_value$"
      },
      {
        "type": "field_not_exist",
        "field": "response_field_missing"
      },
      {
        "type": "value_not_exist",
        "field": "response_field_int",
        "expected": 100
      },
      {
        "type": "match",
        "field": "response_field_str",
        "expected": "^start_value$"
      }
    ]
  }
}
```

### Description of Match Types:

## 1. Exact Match (`exact_match`)

### Description:
The `exact_match` type ensures that the field in the response contains the exact value you expect. This type is strict and does not allow for partial matches or regex.

### JSON Example:
```json
{
  "type": "exact_match",
  "field": "response_field",
  "expected": "exact_value"
}
```

- **field**: The field to check in the response.
- **expected**: The exact value that the field must match.

### Supported Types:
- **String**: The value of the field must exactly match the given string.
- **List**: The list in the response must exactly match the expected list (same order and elements).
- **Dictionary**: The dictionary in the response must exactly match the expected dictionary (same keys and values).
- **Integer**: The value must be the exact integer specified.

---

## 2. Instance of Type (`instance_of_type`)

### Description:
The `instance_of_type` type checks if a field in the response is an instance of a specific type (e.g., `str`, `list`, `dict`, `int`). This is useful when you want to ensure that a field matches a certain data type rather than an exact value.

### JSON Example:
```json
{
  "type": "instance_of_type",
  "field": "response_field",
  "expected": "str"
}
```

- **field**: The field to check in the response.
- **expected**: The expected type as a string (e.g., `"str"`, `"list"`, `"dict"`, `"int"`).

### Supported Types:
- **String**: The field must be a string (`str`).
- **List**: The field must be a list (`list`).
- **Dictionary**: The field must be a dictionary (`dict`).
- **Integer**: The field must be an integer (`int`).

---

## 3. Does Not Exist (`field_not_exist`)

### Description:
The `field_not_exist` type ensures that a particular field does not exist in the response. This is useful when you want to ensure that a field is missing or absent from the response.

### JSON Example:
```json
{
  "type": "field_not_exist",
  "field": "response_field"
}
```

- **field**: The field that should not exist in the response.

### Supported Types:
- No specific types—this operator simply checks for the absence of a field.

---

## 4. Value Does Not Exist (`value_not_exist`)

### Description:
The `value_not_exist` type ensures that a field does not contain a specific value. If the field exists and contains the specified value, the test will fail.

### JSON Example:
```json
{
  "type": "value_not_exist",
  "field": "response_field",
  "expected": "value_to_avoid"
}
```

- **field**: The field to check in the response.
- **expected**: The value that should not appear in the field.

### Supported Types:
- **String**: The field should not contain the specified string.
- **List**: The specified value should not exist as an element in the list.
- **Dictionary**: The field should not contain the specified value as one of its values.
- **Integer**: The field should not contain the specified integer.

---

## 5. Does Not Match (`does_not_match`)

### Description:
The `does_not_match` type ensures that a field in the response does not match a given pattern. This type uses regular expressions to check if the field does not match the pattern.

### JSON Example:
```json
{
  "type": "does_not_match",
  "field": "response_field",
  "expected": "^unexpected_value$"
}
```

- **field**: The field to check in the response.
- **expected**: The regular expression pattern the field should not match.

### Supported Types:
- **String**: The field must not match the given regex pattern.
- **List**: The list's string representation must not match the regex pattern.
- **Dictionary**: The dictionary's string representation must not match the regex pattern.

---

## 6. Field Exists (`field_exists`)

### Description:
The `field_exists` type checks if a field exists in the response. This can be useful if you want to verify that a certain field is present, even if the value is `null` or an empty string.

### JSON Example:
```json
{
  "type": "field_exists",
  "field": "response_field"
}
```

- **field**: The field that should exist in the response.

### Supported Types:
- No specific types—this operator simply checks for the presence of the field.

---

## 7. Regex Match (`match`)

### Description:
The `match` type uses regular expressions to check if the field matches a given pattern. This allows for flexible matching, such as matching the beginning (`^`), end (`$`), or a substring within the field.

### JSON Example:
```json
{
  "type": "match",
  "field": "response_field",
  "expected": "^start_value$"
}
```

- **field**: The field to check in the response.
- **expected**: The regular expression pattern the field should match.

### Supported Types:
- **String**: The field's string value should match the given regex pattern.
- **List**: The list's string representation should match the regex pattern.
- **Dictionary**: The dictionary's string representation should match the regex pattern.

---

## Conclusion

This framework allows you to test and validate various conditions in your API responses using a variety of match types. By using the operators outlined above, you can ensure that your responses meet the expected conditions, whether you're checking for exact values, type matches, or patterns.

### Supported Match Types:
- **exact_match**: Ensures the field has an exact value.
- **instance_of_type**: Ensures the field is of the correct type.
- **field_not_exist**: Ensures the field does not exist.
- **value_not_exist**: Ensures the field does not contain the given value.
- **does_not_match**: Ensures the field does not match the given regex pattern.
- **field_exists**: Ensures the field exists in the response.
- **match**: Ensures the field matches a regex pattern.

For any additional questions or clarifications, feel free to reach out to the team or consult the documentation.
