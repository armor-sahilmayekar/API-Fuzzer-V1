# HeaderInject: Header-Based Vulnerability Scanner

**HeaderInject** is a Python-based tool designed to scan for various web vulnerabilities such as:

- Host Header Injection
- Web Cache Poisoning
- CORS Misconfiguration

It allows for recursive header testing, detailed reporting in JSON format, and debug output for advanced users.

---

## Features

- 🌐 Support for single URL or list of URLs
- 🔁 Recursive scanning using custom or built-in header wordlists
- 🔎 Debug and verbose output for deep inspection
- 📄 JSON-based output report with request/response metadata
- 🕵️ Host Header Injection and CORS misconfiguration detection
- 📂 Reports saved in `../reports/`
- 📄 Customer word list for header injection located in `../universal_data/headers.txt`

---

## Installation

```bash
git clone git@github.com:armor/api-testing-tools.git
cd header-injector
pip install -r requirements.txt
```

---

## Usage

```bash
python scanner.py --url https://example.com --wordlists ../data/headers.txt --attacker evil.com --output ../reports
```

### Arguments

| Flag           | Description                             |
|----------------|-----------------------------------------|
| `-u, --url`    | Target URL                              |
| `-l, --list`   | File with a list of URLs                |
| `-w, --wordlists` | Header wordlist file                    |
| `-a, --attacker` | Attacker domain (default: attacker.com) |
| `-o, --output` | Output directory for results            |
| `-r, --redirect` | Max redirects (default: 10)             |
| `--ssl` | Enable SSL certificate verification     |
| `-x, --method` | HTTP method to use (default: GET)       |
| `-b, --body` | Request body as string or file          |
| `-U, --user-agent` | User-Agent string or file               |
| `-p, --proxy` | Proxy (e.g. `http://localhost:8080`)    |
| `-v, --verbose` | Verbose output                          |
| `-d, --debug` | Debug mode for full request/response    |
| `--recursive` | Enable recursive scanning               |

---

## Output

- Console output with color-coded results
- JSON report: `../reports/header_injectin_X_{EPOCH}.json`
  - Includes headers, request details, response status, and any detected issues

Example JSON entry:

```json
{
  "status": "error",
  "name": "-1",
  "sub_reports": [],
  "test_number": -1,
  "state": "COMPLETED",
  "request_url": "https://example.com",
  "request_method": "GET",
  "request_headers": "{\"User-Agent\": \"Scanner\", \"X-Forwarded-For\": \"attacker.com\"}",
  "exception": "TimeoutError",
  "request_body": {},
  "response": "",
  "details": "Request timed out",
  "reason": "error"
}
```

