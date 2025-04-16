# 🧪 API Testing Tools Suite

Welcome to the **API Testing Tools Suite**! This repository is a collection of tools designed for comprehensive API testing — from basic functional validation to advanced security testing like fuzzing.

Whether you're building, securing, or validating APIs, this suite gives you the power and flexibility to test your endpoints thoroughly.

---

## 📦 Tools Included

### ✅ Functional Testing
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
- `golang` (limited usage)
- `Docker` (optional, for isolated testing environments)

### Cloning the Repo
```bash
git clone https://github.com/your-org/api-testing-tools.git
cd api-testing-tools


api-testing-tools/
│
├── api-fuzzer/         # Coverage-guided API fuzzer
├── jwt-manipulator/     # JWT attack testing utility
├── header-injector/     # Header fuzzing tool
├── postman-runner-cli/  # CLI runner for Postman collections
├── pyapi-validator/     # Functional testing with Python
├── restassure-plus/     # Java-based functional tests
├── openapi-mock/             # OpenAPI mock server generator
├── ratelimit-tester/    # Stress & rate limit testing
└── spec-analyzer/       # OpenAPI specification analyzer

```

### Using .env Files
A .env file is a plain text file used to store application configuration settings and environment variables. It typically follows a key-value pair format, where each line represents a variable and its value. .env files are commonly used for local development, protecting sensitive information by not committing them to version control. 
Key aspects of .env files:

#### Format:
Each line in a .env file consists of a variable name, an equals sign (=), and the variable's value. 

#### Purpose:
Used to store configuration data that varies between different environments (e.g., development, testing, production). 
#### Security:
.env files should not be committed to source control, as they often contain sensitive information like API keys or database credentials. 
#### Tools:
Libraries like `python-dotenv in Python or `dotenv in Node.js can be used to load variables from .env files into your application's environment. 

Example:
```dotenv
    API_KEY=your_api_key
    DATABASE_URL=your_database_url
    DEBUG=true
```
#### Comments:
Lines starting with # are treated as comments and ignored. 
#### Escaping:
Escape characters like \n need to be escaped in both single and double quotes. 
#### Multiple .env files:
Some frameworks (e.g., Astro) support using multiple .env files for different environments, like .env.development or .env.production. 
#### File Naming:
File extensions like .local are often used to indicate that a file contains local development configurations. 
#### Prioritization:
If the same variable is defined in multiple .env files, the one with the highest priority (e.g., environment-specific files) will take precedence. 
Interpolation:
Some tools (like Docker Compose) support variable interpolation within .env files, allowing you to use variables within other variable values. 