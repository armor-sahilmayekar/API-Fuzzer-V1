# Pre-Read
https://github.com/ticarpi/jwt_tool/wiki


# JWT Analyzer Tool

This tool helps you analyze and test JWT (JSON Web Tokens). It decodes the JWT without verifying its signature and allows you to inspect its claims (e.g., `exp`, `iat`). You can also validate the structure of the JWT to ensure it consists of three parts separated by periods.

## Features
- Decode JWT tokens without verifying the signature.
- Validate the structure of the JWT token.
- Dump decoded JWT payload.
- Check for common claims (`exp`, `iat`).

## Prerequisites

- Python 3.x
- `jwt_tool` library

## Installation

1. Clone or download this repository.
2. Install dependencies using `requirements.txt`.

   ```bash
   pip install -r requirements.txt

## Usage

### Running the Tool

To run the tool, pass a JWT token as an argument on the command line.

```bash
python DumpJWT.py <your_jwt_token>
```

### Example

If you have the following JWT token:

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHBpcmVkX2F0IjoxNjE2NzE0MTcyLCJpYXQiOjE2MTY3MTAwMjh9.SvTdIqV9xLZx5dxbyVlmG9se7Iz2lAqMvTugF9O3


Run the following command:

```bash
python DumpJWT.py eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHBpcmVkX2F0IjoxNjE2NzE0MTcyLCJpYXQiOjE2MTY3MTAwMjh9.SvTdIqV9xLZx5dxbyVlmG9se7Iz2lAqMvTugF9O3g5c
```

### Output Example

The output will display the following information:

```yaml
Testing JWT token...
Decoded JWT Payload:
{
  "exp": 1616714172,
  "iat": 1616710028
}
Expiration (exp) claim found: 1616714172
Issued At (iat) claim found: 1616710028
JWT test completed successfully.

```

### Script Breakdown
