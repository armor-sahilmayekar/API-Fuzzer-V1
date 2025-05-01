
# Test Framework - Operators Overview

This document provides an overview of all the operators available in the test framework. The operators are used to define how to match, exclude, or check conditions in the API response. These operators are essential for validating various fields, types, values, and patterns.

## Operators Overview

### 1. Match Operators

These operators are used to ensure that the field in the response meets specific criteria.

#### Exact Match (`exact_match`)

**Description**: Ensures the field exactly matches the expected value.

**Example**:
```json
{
  "type": "exact_match",
  "field": "response_field",
  "expected": "exact_value"
}
```

- **field**: The field to check.
- **expected**: The exact value that the field must match.

**Use Case**: To ensure a field's value is exactly what is expected (e.g., a status code of `200`).

---

#### Regex Match (`match`)

**Description**: Uses regular expressions to check if the field matches a given pattern. This can be useful for flexible matching such as prefix, suffix, or substring matching.

**Example**:
```json
{
  "type": "match",
  "field": "response_field",
  "expected": "^start_value$"
}
```

- **field**: The field to check.
- **expected**: The regex pattern the field should match.

**Use Case**: To check for fields that start with or end with a specific value.

---

#### Instance of Type (`instance_of_type`)

**Description**: Ensures the field is an instance of a specific type such as `str`, `list`, `dict`, `int`.

**Example**:
```json
{
  "type": "instance_of_type",
  "field": "response_field",
  "expected": "str"
}
```

- **field**: The field to check.
- **expected**: The expected type (e.g., `"str"`, `"list"`, `"dict"`, `"int"`).

**Use Case**: To verify that a field is of the expected type.

---

### 2. Excluding Operators

These operators are used to ensure that the field either does not exist or does not match a given value or pattern.

#### Does Not Match (`does_not_match`)

**Description**: Ensures that a field does not match the specified pattern.

**Example**:
```json
{
  "type": "does_not_match",
  "field": "response_field",
  "expected": "^unexpected_value$"
}
```

- **field**: The field to check.
- **expected**: The regex pattern the field should not match.

**Use Case**: To ensure that a field does not contain a specific value or pattern.

---

#### Field Does Not Exist (`field_not_exist`)

**Description**: Ensures that a specific field does not exist in the response.

**Example**:
```json
{
  "type": "field_not_exist",
  "field": "response_field"
}
```

- **field**: The field that should not exist.

**Use Case**: To ensure that a field is missing from the response.

---

#### Value Does Not Exist (`value_not_exist`)

**Description**: Ensures that the field does not contain a specific value.

**Example**:
```json
{
  "type": "value_not_exist",
  "field": "response_field",
  "expected": "value_to_avoid"
}
```

- **field**: The field to check.
- **expected**: The value that should not appear in the field.

**Use Case**: To ensure that a value does not appear in the response field.

---

### 3. Existence and Presence Operators

These operators are used to ensure the presence or absence of a field in the response.

#### Field Exists (`field_exists`)

**Description**: Ensures that a specific field exists in the response, even if the field value is `null` or an empty string.

**Example**:
```json
{
  "type": "field_exists",
  "field": "response_field"
}
```

- **field**: The field that should exist in the response.

**Use Case**: To check if a field is present in the response.

---

## Conclusion

This framework supports a variety of match and exclusion operators to validate your API responses. The operators allow for fine-grained control over the testing process, whether you're ensuring the exact value, checking for the presence or absence of fields, or using patterns for flexible matching.

### Supported Match Types:
- **exact_match**: Ensures the field has an exact value.
- **match**: Ensures the field matches a regex pattern.
- **instance_of_type**: Ensures the field is of the correct type.

### Supported Exclusion Types:
- **does_not_match**: Ensures the field does not match a regex pattern.
- **field_not_exist**: Ensures the field does not exist.
- **value_not_exist**: Ensures the field does not contain the specified value.
- **field_exists**: Ensures the field exists.

For further assistance, please refer to the detailed documentation or reach out to the support team.
