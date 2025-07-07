Here is an updated version of your **API Fuzzer — Installation, Setup & Usage Guide** with the **PyCharm Run/Debug Configurations** section added. This includes the two configurations:

* **`APIFuzzer`**: for full fuzzing runs
* **`APIFuzzer retest`**: for retesting specific reports and status codes

---

# 🧪 API Fuzzer — Installation, Setup & Usage Guide

Welcome to the **API Fuzzer** documentation! This guide will help you install, set up, and use the API fuzzer for automated and security testing of your APIs. It also explains how the generated reports are organized.

---

## 🚀 Installation & Setup

### 1. Prerequisites

* **Python 3.12+**
* **pip** (Python package manager)
* **libcurl** and **openssl** development libraries (for `pycurl`)

  * On Ubuntu:

    ```bash
    sudo apt-get update
    sudo apt-get install libcurl4-openssl-dev libssl-dev gcc
    ```
* (Optional) **Docker** for containerized runs

### 2. Clone the Repository

```bash
git clone <your-repo-url>
cd API-fuzzer-v2
```

### 3. Create a Virtual Environment & Install Dependencies

You can use the provided setup script:

```bash
sh setup.sh
```

This will:

* Create a Python virtual environment in `.venv/`
* Install all required Python dependencies from `requirements.txt` and tool submodules

Or, to do it manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in the project root to store sensitive configuration (API tokens, account IDs, etc.):

```
TOKEN=your_api_token_here
ACCOUNT_ID=2
LOG_LEVEL=INFO
# Add other variables as needed
```

* **Never commit your .env file to version control!**
* The fuzzer will automatically load variables from this file if you use `python-dotenv`.

---

## 📁 API Definitions Location (data/openapi/)

The fuzzer requires an OpenAPI or Swagger specification file (in JSON or YAML format) that describes the APIs you want to fuzz.

- **Location:** Place your API definition files in the `data/openapi/` directory.
- **Example:**
  - `data/openapi/openapi_mdr_v3.json`
  - `data/openapi/your_api_spec.yaml`

You can add multiple API definition files to this directory. When running the fuzzer, specify the desired file using the `--src_file` argument:

```bash
--src_file data/openapi/openapi_mdr_v3.json
```

> **Tip:** Organize your API specs in this folder to keep your workspace clean and make it easy to switch between different APIs for fuzzing.

---

## 🏃‍♂️ Running the Fuzzer

### 🔹 Full Fuzzing Run — `APIFuzzer` (Default Mode)

Use this configuration when you want to run the **entire fuzzer** against an OpenAPI specification.

**PyCharm Configuration:**

* **Script**:
  `/Users/sahilmayekar/Desktop/Automation/API-fuzzer-v2/tools/api-fuzzer/APIFuzzer.py`
* **Parameters**:

  ```bash
  --src_file data/openapi/openapi_mdr_v3.json \
  -u https://mdr.api.secure-dev.services/ \
  --log debug -r ./reports
  ```
* **Working Directory**:
  `/Users/sahilmayekar/Desktop/Automation/API-fuzzer-v2`
* **Environment Variables**:
  `PYTHONUNBUFFERED=1`
* **.env file path**:
  `/Users/sahilmayekar/Desktop/Automation/API-fuzzer-v2/.env`

---

### 🔁 Retesting Specific Results — `APIFuzzer retest`

Use this configuration when you want to **retest specific requests** from a prior run, filtered by HTTP status code (e.g., 200).

**PyCharm Configuration:**

* **Script**:
  `/Users/sahilmayekar/Desktop/Automation/API-fuzzer-v2/tools/api-fuzzer/APIFuzzer.py`
* **Parameters**:

  ```bash
  --src_file data/openapi/openapi_mdr_v3.json \
  -u https://mdr.api.secure-dev.services/ \
  --log debug -r ./reports \
  --retest_dir ./reports/2025-06-24_10-14-26/Passed/200 \
  --status_code 200
  ```
* **Working Directory**:
  `/Users/sahilmayekar/Desktop/Automation/API-fuzzer-v2`
* **Environment Variables**:
  `PYTHONUNBUFFERED=1`
* **.env file path**:
  `/Users/sahilmayekar/Desktop/Automation/API-fuzzer-v2/.env`

> ✅ Tip: You can update the `--retest_dir` path and `--status_code` value as needed to retest different results from any prior run.

---

## 📂 Reports Directory Classification

All fuzzer results are saved in the `reports/` directory. The structure is as follows:

```
reports/
  ├── <timestamped_run_dir>/
  │     ├── junit_report.xml         # JUnit XML summary (for CI integration)
  │     ├── Passed/                  # Requests that passed
  │     └── Failed/                  # Requests that failed
  ├── <timestamped_run_dir> - retest/
  │     ├── <status_code>/           # e.g., 200/, 401/, 404/
  │     │     ├── <n>.json           # Individual retest result files
  │     │     └── ...
  │     └── ...
  └── ...
```

### Details

* **Timestamped Directories**: Each fuzzer run creates a new directory named with the current date and time.
* **Passed/Failed**: Within each run, requests are classified as `Passed` or `Failed` based on their outcome.
* **Retest Directories**: Retest runs are saved in directories with `- retest` in their name. Inside, results are further classified by HTTP status code (e.g., `200/`, `401/`).
* **JSON Files**: Each file contains the request and response details for a single test case.
* **JUnit XML**: Useful for CI/CD pipelines to visualize test results.

---

## 📝 Example Report File (JSON)

```json
{
  "request_url": "https://your.api.endpoint/resource",
  "status_code": 200,
  "headers": {"Content-Type": "application/json"}
  // ... other fields as applicable
}
```

---

## 🧑‍💻 Tips

* Use the **`APIFuzzer`** configuration for full exploratory fuzz testing.
* Use the **`APIFuzzer retest`** configuration to selectively retest by status code.
* Always check the `reports/` directory after a run for detailed results.
* Use the `--log debug` flag for verbose output and easier troubleshooting.
* For advanced usage, refer to `tools/api-fuzzer/README.md`.

---

Would you like this saved as a Markdown file or updated into your repo `README.md` directly?
