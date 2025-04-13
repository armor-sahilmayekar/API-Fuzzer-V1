# OpenAPI Spec Validator

A reusable, CLI-compatible Python utility to **validate OpenAPI 3.0 and 3.1 specifications** from either a local file or a remote URL. Supports both YAML and JSON formats, and uses the `openapi-schema-validator` library.

---

## 🚀 Features

- ✅ Validate OpenAPI 3.0 / 3.1 specs
- 📁 Accepts input from local files or URLs
- 🔍 Auto-detects and parses YAML or JSON
- 🔁 Reusable as a Python class or CLI
- 📦 Lightweight and dependency minimal

---

## 📦 Installation

1. Clone the repo:

```bash
git clone https://github.com/yourusername/openapi-spec-validator.git
cd openapi-spec-validator
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

**Requirements:**

- `openapi-schema-validator`
- `PyYAML`
- `requests`

> You can also install manually:
> ```bash
> pip install openapi-schema-validator PyYAML requests
> ```

---

## 🛠 Usage

### 🔧 As a CLI

#### ✅ Validate from a file:

```bash
python openapi_spec_validator.py ./openapi.yaml
```

#### 🌐 Validate from a URL:

```bash
python openapi_spec_validator.py https://example.com/openapi.json --source-type url
```

---

### 🧩 As a Python module

```python
from openapi_spec_validator import OpenAPISpecValidator

validator = OpenAPISpecValidator(source="https://example.com/openapi.yaml", source_type="url")
validator.run()
```

---

## 📘 Example Output

### ✅ Valid spec:
```
✅ OpenAPI specification is valid.
```

### ❌ Invalid spec:
```
❌ OpenAPI specification is invalid.
  - 'paths' is a required property
```

### ❗ Load error:
```
❌ Error: Failed to fetch spec from URL: https://example.com/openapi.yaml
```

---
