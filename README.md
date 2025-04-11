# 🧪 API Testing Tools Suite

Welcome to the **API Testing Tools Suite**! This repository is a collection of tools designed for comprehensive API testing — from basic functional validation to advanced security testing like fuzzing.

Whether you're building, securing, or validating APIs, this suite gives you the power and flexibility to test your endpoints thoroughly.

---

## 📦 Tools Included

### ✅ Functional Testing
- **RestAssure+**: Lightweight wrapper for functional API tests using Java & RestAssured.
- **Postman Runner CLI**: Run and validate Postman collections via command line.
- **PyAPI Validator**: Python-based API test runner with schema validation support.

### 🛡️ Security Testing & Fuzzing
- **API FuzzerX**: Coverage-guided API fuzzing tool with OpenAPI/Swagger spec support.
- **JWT Manipulator**: Tool for testing token-based auth flows with various JWT attack vectors.
- **HeaderInjector**: Sends requests with malformed/malicious headers to detect security flaws.

### 🔧 Utilities
- **Spec Analyzer**: Parses and validates OpenAPI/Swagger specs for common issues.
- **MockGen**: Generates realistic mock servers from OpenAPI definitions.
- **RateLimit Tester**: Stress-tests endpoints for throttling & rate-limiting behaviors.

---

## 🛠️ Getting Started

### Prerequisites
- `Python 3.12+`
- `Node.js` (for some JS-based tools)
- `Docker` (optional, for isolated testing environments)

### Cloning the Repo
```bash
git clone https://github.com/your-org/api-testing-tools.git
cd api-testing-tools

api-testing-tools/
│
├── APIFuzzers/         # Coverage-guided API fuzzer
├── jwt-manipulator/     # JWT attack testing utility
├── header-injector/     # Header fuzzing tool
├── postman-runner-cli/  # CLI runner for Postman collections
├── pyapi-validator/     # Functional testing with Python
├── restassure-plus/     # Java-based functional tests
├── mockgen/             # OpenAPI mock server generator
├── ratelimit-tester/    # Stress & rate limit testing
└── spec-analyzer/       # OpenAPI specification analyzer
