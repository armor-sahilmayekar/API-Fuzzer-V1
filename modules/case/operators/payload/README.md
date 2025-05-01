
# Test Framework - Exact Payload Match Operator

This document explains how to use the `ExactPayloadMatchTestCase` class to ensure that the entire payload of the API response exactly matches the expected payload. This operator is useful when you need to verify that all fields and values in the response are exactly as expected.

## Exact Match Operator (`ExactPayloadMatchTestCase`)

The `ExactPayloadMatchTestCase` class checks if the entire response payload exactly matches the expected payload. This includes verifying that all keys and values in a dictionary (or elements in a list) match the expected values.

### JSON Example of Test Case

Below is an example of how to use the `ExactPayloadMatchTestCase` in your test cases:

```json
{
  "test_number": 1,
  "name": "exact_payload_match",
  "jira_description": "",
  "method": "POST",
  "url": "https://api.example.com/data",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "field1": "value1",
    "field2": "value2"
  },
  "parameter": "",
  "expected": {
    "status_code": 200,
    "operators": [{
      "type": "payload",
      "field": "all",
      "expected": {
          "field1": "value1",
          "field2": "value2"
    }
  }
}
```

### Explanation:

- **test_number**: Unique identifier for the test case.
- **name**: The name of the test case.
- **jira_description**: Optional field for linking to Jira tickets or describing the issue being tested.
- **method**: The HTTP method (e.g., `GET`, `POST`) used for the request.
- **url**: The endpoint being tested.
- **headers**: Any custom headers for the request (optional).
- **body**: The body data sent in the request.
- **parameter**: Optional query string parameters.
- **expected**: Contains the expected status code and payload.

### Operator Description:

- **Exact Payload Match (`exact_match`)**: The `ExactPayloadMatchTestCase` class ensures that the entire payload (including nested fields) in the response matches the expected value exactly.

### Supported Data Types:

- **Dictionary**: The response payload must exactly match the expected dictionary, with the same keys and corresponding values.
- **List**: The response payload must exactly match the expected list, including the same order and elements.
- **Primitive Types**: For string, integer, etc., the response must exactly match the expected value.

### How it Works:

The `ExactPayloadMatchTestCase` class performs a deep comparison of the response payload and the expected payload. If they match exactly (including field names and values), the test passes. Otherwise, it fails.

### Example Response:

If the response looks like this:

```json
{
  "status_code": 200,
  "payload": {
    "field1": "value1",
    "field2": "value2"
  }
}
```

The test will check if the `payload` field in the response exactly matches:

```json
{
  "field1": "value1",
  "field2": "value2"
}
```

If the payload in the response is different in any way (e.g., missing a field, different value, or extra fields), the test will fail.

## Conclusion

The `ExactPayloadMatchTestCase` is useful for verifying that the entire structure and content of the response payload are correct. By using this operator, you ensure that the response contains exactly the values and structure you expect.

For any questions or clarifications, refer to the detailed documentation or reach out to the support team.
