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


#
    "/incidents": {
      "get": {
        "summary": "Get list of incidents",
        "parameters": [
          {
            "name": "sortBy",
            "in": "query",
            "schema": {
              "type": "string",
              "default": "key"
            },
            "required": false
          },
          {
            "name": "sortDirection",
            "in": "query",
            "schema": {
              "type": "string",
              "enum": [
                "asc",
                "desc"
              ],
              "default": "desc"
            },
            "required": false
          },
          {
            "name": "startAt",
            "in": "query",
            "schema": {
              "type": "string",
              "default": "0"
            },
            "required": false
          },
          {
            "name": "priority",
            "in": "query",
            "schema": {
              "type": "string"
            },
            "required": false
          },
          {
            "name": "status",
            "in": "query",
            "schema": {
              "type": "string",
              "enum": [
                "Triage",
                "Escalated",
                "Closed"
              ]
            },
            "required": false
          },
          {
            "name": "tactic",
            "in": "query",
            "schema": {
              "type": "string"
            },
            "required": false
          },
          {
            "name": "organization",
            "in": "query",
            "schema": {
              "type": "string",
              "example": "2645,2646"
            },
            "required": false,
            "description": "It should be list of comma separated organization ids"
          },
          {
            "name": "pageSize",
            "in": "query",
            "schema": {
              "type": "string",
              "default": "20"
            },
            "required": false
          },
          {
            "name": "textSearch",
            "in": "query",
            "schema": {
              "type": "string"
            },
            "required": false,
            "description": "Passing the string Armor Defense will search for all issues that contain the words Armor and Defense, in no particular order."
          }
        ],
        "responses": {
          "200": {
            "description": "All good",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "totalRows": {
                      "type": "integer"
                    },
                    "issues": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "id": {
                            "type": "string",
                            "description": "E.g. SEC-12345"
                          },
                          "summary": {
                            "type": "string"
                          },
                          "status": {
                            "type": "string",
                            "description": "E.g. Closed"
                          },
                          "priority": {
                            "type": "string",
                            "description": "E.g. Medium"
                          },
                          "created": {
                            "type": "string",
                            "description": "ISO 8601"
                          },
                          "updated": {
                            "type": "string",
                            "description": "ISO 8601"
                          },
                          "assignee": {
                            "type": "string",
                            "description": "E.g. SOC Analyst 1"
                          },
                          "alertCount": {
                            "type": "integer",
                            "description": "Number of alerts in the incident"
                          },
                          "orgs": {
                            "type": "array",
                            "items": {
                              "type": "string",
                              "description": "E.g. Contoso"
                            }
                          }
                        }
                      }
                    },
                    "approvedOrgs": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "orgId": {
                            "type": "string",
                            "description": "9501"
                          },
                          "orgName": {
                            "type": "string",
                            "description": "Sample Demo Org"
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "400": {
            "description": "Invalid parameters like invalid startAt"
          }
        }
      }
    },
    "/incidents/{key}": {
      "get": {
        "summary": "Get details of an incident",
        "parameters": [
          {
            "name": "key",
            "in": "path",
            "schema": {
              "type": "string"
            },
            "required": true
          }
        ],
        "responses": {
          "200": {
            "description": "All good",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "tenantId": {
                      "type": "string",
                      "example": "UUID-1234"
                    },
                    "incidentId": {
                      "type": "string",
                      "example": "123"
                    },
                    "displayName": {
                      "type": "string",
                      "example": "Detect latest failure events per connector"
                    },
                    "status": {
                      "type": "string",
                      "example": "Closed"
                    },
                    "createdDateTime": {
                      "type": "string",
                      "format": "date-time",
                      "example": "2024-06-16T07:24:53.4433333Z"
                    },
                    "lastUpdateDateTime": {
                      "type": "string",
                      "format": "date-time",
                      "example": "2024-06-16T07:24:53.4433333Z"
                    },
                    "severity": {
                      "type": "string",
                      "example": "Medium"
                    },
                    "mitreTactics": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "name": {
                            "type": "string",
                            "example": "Execution"
                          },
                          "techniques": {
                            "type": "array",
                            "items": {
                              "type": "object",
                              "properties": {
                                "id": {
                                  "type": "string",
                                  "example": "T1039"
                                }
                              }
                            }
                          }
                        }
                      }
                    },
                    "source": {
                      "type": "array",
                      "items": {
                        "type": "string"
                      },
                      "example": [
                        "Defender for Endpoint",
                        "Defender for Cloud"
                      ]
                    },
                    "detectionSource": {
                      "type": "string",
                      "example": "SIEM"
                    },
                    "assignee": {
                      "type": "string",
                      "example": "SOC Analyst 1"
                    },
                    "ticketUpdatedDateTime": {
                      "type": "string",
                      "format": "date-time",
                      "example": "2024-06-10T06:16:41.488-0500"
                    },
                    "ticketCreatedDateTime": {
                      "type": "string",
                      "format": "date-time",
                      "example": "2024-06-10T06:16:41.488-0500"
                    },
                    "ticketFirstResponseDateTime": {
                      "type": "string",
                      "format": "date-time",
                      "example": "2024-06-10T06:16:41.488-0500"
                    },
                    "ticketFirstAssignedDateTime": {
                      "type": "string",
                      "format": "date-time",
                      "example": "2024-06-10T06:16:41.488-0500"
                    },
                    "ticketFirstTransitionedDateTime": {
                      "type": "string",
                      "format": "date-time",
                      "example": "2024-06-10T06:16:41.488-0500"
                    },
                    "ticketDescription": {
                      "type": "string",
                      "example": "Sample Org has detected the following activity.\n\n*This incident may require immediate attention.*\nWe ask that you have someone ready to assist with any questions or further investigation by our team."
                    },
                    "ticketSummary": {
                      "type": "string",
                      "example": "[High] Incident: Multi-stage incident involving Persistence & Discovery on one endpoint reported by multiple sources"
                    },
                    "orgId": {
                      "type": "string",
                      "example": "9501"
                    },
                    "orgName": {
                      "type": "string",
                      "example": "Sample Demo Org"
                    },
                    "comments": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "id": {
                            "type": "string",
                            "example": "328531"
                          },
                          "authorDisplayName": {
                            "type": "string",
                            "example": "328531"
                          },
                          "body": {
                            "type": "string",
                            "example": "328531"
                          },
                          "created": {
                            "type": "string",
                            "example": "328531"
                          },
                          "updated": {
                            "type": "string",
                            "example": "328531"
                          },
                          "isPublic": {
                            "type": "boolean",
                            "example": true
                          }
                        }
                      }
                    },
                    "alerts": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "id": {
                            "type": "string",
                            "example": "sn8b46ecca-43f6-483c-aa63-192bdc4ca8ff"
                          },
                          "category": {
                            "type": "string",
                            "example": "Impact"
                          },
                          "actorDisplayName": {
                            "type": "string",
                            "example": "unknown"
                          },
                          "classification": {
                            "type": "string",
                            "example": "unknown"
                          },
                          "createdDateTime": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2024-05-31T07:24:42.35Z"
                          },
                          "datatype": {
                            "type": "string",
                            "example": "mdrAlert"
                          },
                          "description": {
                            "type": "string",
                            "example": "Identifies when a rare Resource and ResourceGroup deployment occurs by a previously unseen Caller."
                          },
                          "detectionSource": {
                            "type": "string",
                            "example": "scheduledAlerts"
                          },
                          "detectorId": {
                            "type": "string",
                            "example": "87dc1909-0df2-4e91-af3f-c85a57829935_newresourcegroupsdeployedto"
                          },
                          "determination": {
                            "type": "string",
                            "example": "unknown"
                          },
                          "firstActivityDateTime": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2024-05-17T07:19:28.523984Z"
                          },
                          "incidentId": {
                            "type": "string",
                            "example": "728"
                          },
                          "lastActivityDateTime": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2024-05-31T07:19:28.523984Z"
                          },
                          "lastUpdateDateTime": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2024-06-14T02:48:58.82Z"
                          },
                          "mitreTechniques": {
                            "type": "array",
                            "items": {
                              "type": "string"
                            },
                            "example": [
                              "T1496"
                            ]
                          },
                          "productName": {
                            "type": "string",
                            "example": "Microsoft Sentinel"
                          },
                          "recommendedActions": {
                            "type": "string",
                            "example": "quarantine the resource"
                          },
                          "resolvedDateTime": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2024-06-14T02:48:58.82Z"
                          },
                          "serviceSource": {
                            "type": "string",
                            "example": "microsoftSentinel"
                          },
                          "severity": {
                            "type": "string",
                            "example": "low"
                          },
                          "status": {
                            "type": "string",
                            "example": "new"
                          },
                          "threatDisplayName": {
                            "type": "string",
                            "example": "sample threat family display name"
                          },
                          "threatFamilyName": {
                            "type": "string",
                            "example": "sample threat family name"
                          },
                          "title": {
                            "type": "string",
                            "example": "Suspicious Resource deployment"
                          },
                          "evidences": {
                            "type": "array",
                            "items": {
                              "type": "object",
                              "properties": {
                                "createdDateTime": {
                                  "type": "string",
                                  "format": "date-time",
                                  "example": "2024-05-31T07:24:42.4933333Z"
                                },
                                "evidenceBody": {
                                  "type": "string",
                                  "example": "{}"
                                },
                                "odatatype": {
                                  "type": "string",
                                  "example": "ipEvidence"
                                },
                                "remediationStatus": {
                                  "type": "string",
                                  "example": "unknown"
                                },
                                "remediationStatusDetails": {
                                  "type": "string",
                                  "example": "Some String"
                                },
                                "verdict": {
                                  "type": "string",
                                  "example": "unknown"
                                }
                              }
                            }
                          }
                        }
                      }
                    },
                    "timeline": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "name": {
                            "type": "string",
                            "example": "First Assigned"
                          },
                          "type": {
                            "type": "string",
                            "example": "Alert"
                          },
                          "dateTime": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2024-05-31T07:24:42.4933333Z"
                          }
                        }
                      }
                    },
                    "relatedIncidents": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "name": {
                            "type": "string",
                            "example": "[Low]: Suspicious Device Detected"
                          },
                          "url": {
                            "type": "string",
                            "example": "https://sandbox.atlassian.net/SEC-12345"
                          }
                        }
                      }
                    },
                    "impactedAssets": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "type": {
                            "type": "string",
                            "example": "Device"
                          },
                          "displayName": {
                            "type": "string",
                            "example": "Test Machine"
                          }
                        }
                      }
                    },
                    "actions": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "type": {
                            "type": "string",
                            "example": "SOCAction"
                          },
                          "displayName": {
                            "type": "string",
                            "example": "Quarantine the Device"
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/incidents/{issueKey}/comment/{commentId}": {
      "get": {
        "summary": "Get Comment Attachments by Comment ID",
        "description": "Retrieves a multipart/mixed response that has attachments data for a given comment.",
        "parameters": [
          {
            "name": "issueKey",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string"
            },
            "description": "incident/jira id."
          },
          {
            "name": "commentId",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string"
            },
            "description": "It's an id of a specific comment."
          }
        ],
        "responses": {
          "200": {
            "description": "A multipart/mixed stream with comment attachments.",
            "content": {
              "multipart/mixed": {
                "schema": {
                  "type": "string",
                  "format": "binary"
                },
                "example": "--boundary123\r\nContent-Disposition: form-data; name=\"files\"; filename=\"test-1.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n<binary of image>\r\n--boundary123\r\nContent-Disposition: form-data; name=\"files\"; filename=\"test-2.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n<binary of image>\r\n--boundary123--"
              }
            }
          },
          "400": {
            "description": "Bad Request or Not Found."
          }
        }
      }
    },
    "/incidents/{ticket-id}/comments": {
        "post": {
          "summary": "Add a comment and images (optional) to an incident",
          "description": "Accepts form data with fields comment text and array of image files with total combined size limit of 10 MB. Only image MIME types (`image/*`) are allowed. A maximum of 5 files can be uploaded.",
          "parameters": [
            {
              "in": "path",
              "name": "ticket-id",
              "required": true,
              "schema": {
                "type": "string",
                "example": "SEC-12345"
              },
              "description": "The SEC ticket ID of the incident to add a comment to"
            }
          ],
          "requestBody": {
            "required": true,
            "content": {
              "multipart/form-data": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "comment": {
                      "type": "string",
                      "example": "This is a test comment by Nic"
                    },
                    "files": {
                      "type": "array",
                      "items": {
                        "type": "string",
                        "format": "binary"
                      },
                      "maxItems": 5
                    }
                  },
                  "required": ["comment"]
                },
                "encoding": {
                  "files": {
                    "contentType": "image/*"
                  }
                }
              }
            }
          },
          "responses": {
            "200": {
              "description": "Comment added successfully",
              "content": {
                "text/plain": {
                  "schema": {
                    "type": "string",
                    "example": "Comment Successful"
                  }
                }
              }
            },
            "400": {
              "description": "Bad request"
            }
          }
        }
      },
    "/jsm-orgs/": {
        "get": {
          "summary": "Get jsm orgs for the logged in user",
          "responses": {
            "200": {
              "description": "List of JSM organization IDs and labels.",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "jsmOrgId": {
                          "type": "integer",
                          "example": 1
                        },
                        "label": {
                          "type": "string",
                          "example": "Org A"
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
    "/service-requests": {
          "get": {
            "summary": "Get list of service requests",
            "parameters": [
              {
                "name": "pageSize",
                "in": "query",
                "schema": {
                  "type": "string",
                  "default": "20"
                },
                "required": false
              },
              {
                "name": "startAt",
                "in": "query",
                "schema": {
                  "type": "string",
                  "default": "0"
                },
                "required": false
              },
              {
                "name": "organization",
                "in": "query",
                "schema": {
                  "type": "string",
                  "example": "2645,2646"
                },
                "required": false,
                "description": "It should be a list of comma-separated organization IDs"
              },
              {
                "name": "sortDirection",
                "in": "query",
                "schema": {
                  "type": "string",
                  "enum": ["asc", "desc"],
                  "default": "desc"
                },
                "required": false
              },
              {
                "name": "sortBy",
                "in": "query",
                "schema": {
                  "type": "string",
                  "default": "key"
                },
                "required": false
              }
            ],
            "responses": {
              "200": {
                "description": "Successful retrieval of service requests",
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "totalRows": {
                          "type": "integer",
                          "example": 2
                        },
                        "issues": {
                          "type": "array",
                          "items": {
                            "type": "object",
                            "properties": {
                              "id": {
                                "type": "string",
                                "example": "SP-142"
                              },
                              "summary": {
                                "type": "string",
                                "example": "Test SR"
                              },
                              "status": {
                                "type": "string",
                                "example": "New"
                              },
                              "priority": {
                                "type": "string",
                                "example": "3"
                              },
                              "created": {
                                "type": "string",
                                "format": "date-time",
                                "example": "2025-01-07T02:33:28.385-0600"
                              },
                              "updated": {
                                "type": "string",
                                "format": "date-time",
                                "example": "2025-01-07T02:33:28.584-0600"
                              },
                              "assignee": {
                                "type": "string",
                                "nullable": true,
                                "example": null
                              },
                              "orgs": {
                                "type": "array",
                                "items": {
                                  "type": "string"
                                },
                                "example": ["2644"]
                              }
                            }
                          }
                        },
                        "approvedOrgs": {
                          "type": "array",
                          "items": {
                            "type": "object",
                            "properties": {
                              "id": {
                                "type": "string",
                                "example": "2644"
                              },
                              "name": {
                                "type": "string",
                                "nullable": true,
                                "example": null
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              },
              "400": {
                "description": "Invalid request parameters",
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "error": {
                          "type": "string",
                          "example": "Invalid request parameters"
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        },
    "/metrics/incidents": {
        "get": {
          "summary": "Get summary of incidents",
          "parameters": [
            {
              "name": "priority",
              "in": "query",
              "schema": {
                "type": "string"
              },
              "required": false
            },
            {
              "name": "status",
              "in": "query",
              "schema": {
                "type": "string"
              },
              "required": false
            },
            {
              "name": "tactic",
              "in": "query",
              "schema": {
                "type": "string"
              },
              "required": false
            }
          ],
          "responses": {
            "200": {
              "description": "All good",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "statusTrend": {
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "date": { "type": "string" },
                            "value": {
                              "type": "array",
                              "items": {
                                "type": "object",
                                "properties": {
                                  "status": { "type": "string", "example": "New" },
                                  "count": { "type": "integer", "example": 5 }
                                }
                              }
                            }
                          }
                        }
                      },
                      "eventToIncidentRatioTrend": {
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "date": {
                              "type": "string",
                              "format": "date-time",
                              "example": "2024-08-27T00:00:00.00Z"
                            },
                            "value": {
                              "type": "object",
                              "properties": {
                                "events": { "type": "integer", "example": 1000000 },
                                "alerts": { "type": "integer", "example": 100 },
                                "incidents": { "type": "integer", "example": 10 }
                              }
                            }
                          }
                        }
                      },
                      "mttaTrend": {
                        "description": "Mean time to acknowledge in miliseconds, summarized per hour displayed in ISO 8601 String",
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "date": { "type": "string", "example": "2019-01-25T02:00:00.000Z" },
                            "value": {
                              "type": "array",
                              "items": {
                                "type": "object",
                                "properties": {
                                  "severity": { "type": "string", "example": "High" },
                                  "duration": { "type": "integer", "example": 5 }
                                }
                              }
                            }
                          }
                        }
                      },
                      "mttrTrend": {
                        "description": "Mean time to response in miliseconds, summarized per hour displayed in ISO 8601 String",
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "date": { "type": "string", "example": "2019-01-25T02:00:00.000Z" },
                            "value": {
                              "type": "array",
                              "items": {
                                "type": "object",
                                "properties": {
                                  "severity": { "type": "string", "example": "High" },
                                  "duration": { "type": "integer", "example": 5 }
                                }
                              }
                            }
                          }
                        }
                      },
                      "severityTrend": {
                        "description": "Past n days of incidents, incident counts summarized by severity per day displayed in ISO 8601 String",
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "date": { "type": "string" },
                            "value": {
                              "type": "array",
                              "items": {
                                "type": "object",
                                "properties": {
                                  "severity": { "type": "string", "example": "Low" },
                                  "count": { "type": "integer", "example": 5 }
                                }
                              }
                            }
                          }
                        }
                      },
                      "incidentResolutionNameTrend": {
                        "description": "Past n days of incidents, incident counts summarized by resolution name per day displayed in ISO 8601 String",
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "date": { "type": "string" },
                            "value": {
                              "type": "array",
                              "items": {
                                "type": "object",
                                "properties": {
                                  "name": { "type": "string", "example": "Benign Positive" },
                                  "count": { "type": "integer", "example": 4 }
                                }
                              }
                            }
                          }
                        }
                      },
                      "mitreTacticTrend": {
                        "description": "Past n days of incidents, incident counts summarized by mitre tactic per day displayed in ISO 8601 String",
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "date": { "type": "string" },
                            "value": {
                              "type": "array",
                              "items": {
                                "type": "object",
                                "properties": {
                                  "name": { "type": "string", "example": "DefenseEvasion" },
                                  "count": { "type": "integer", "example": 5 },
                                  "jsmIds": {
                                    "type": "array",
                                    "items": {
                                      "type": "object",
                                      "properties": {
                                        "issueId": { "type": "string", "example": "SEC-85564" },
                                        "severity": { "type": "string", "example": "low" },
                                        "status": { "type": "string", "example": "new" }
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      },
                      "incidentCategoryTrend": {
                        "description": "Past n days of incidents, incident counts summarized by non incident categories (that are non mitre-tactics) per day displayed in ISO 8601 String",
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "date": { "type": "string" },
                            "value": {
                              "type": "array",
                              "items": {
                                "type": "object",
                                "properties": {
                                  "name": { "type": "string", "example": "ComplianceManager" },
                                  "count": { "type": "integer", "example": 5 },
                                  "incidentIds": {
                                    "type": "array",
                                    "items": { "type": "string", "example": "858" }
                                  }
                                }
                              }
                            }
                          }
                        }
                      },
                      "mitreTechniqueTrend": {
                        "description": "Past n days of incidents, incident counts summarized by mitre technique per day displayed in ISO 8601 String",
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "date": { "type": "string" },
                            "value": {
                              "type": "array",
                              "items": {
                                "type": "object",
                                "properties": {
                                  "name": { "type": "string", "example": "T1496" },
                                  "count": { "type": "integer", "example": 5 },
                                  "incidentIds": {
                                    "type": "array",
                                    "items": { "type": "string", "example": "858" }
                                  }
                                }
                              }
                            }
                          }
                        }
                      },
                      "topAssetsTrend": {
                        "description": "Past n days of incidents, asset count summarized per day displayed in ISO 8601 String",
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "date": { "type": "string" },
                            "value": {
                              "type": "array",
                              "items": {
                                "type": "object",
                                "properties": {
                                  "assetDisplayName": { "type": "string", "example": "Asset name one" },
                                  "count": { "type": "integer", "example": 5 }
                                }
                              }
                            }
                          }
                        }
                      },
                      "topIncidentsTrend": {
                        "description": "Past n days of incidents, incident count summarized per day displayed in ISO 8601 String",
                        "type": "array",
                        "items": {
                          "type": "object",
                          "properties": {
                            "date": { "type": "string" },
                            "value": {
                              "type": "array",
                              "items": {
                                "type": "object",
                                "properties": {
                                  "name": { "type": "string", "example": "Incident name one" },
                                  "count": { "type": "integer", "example": 5 }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
    "/msr": {
        "get": {
          "summary": "Get list of MSRs for a particular customer",
          "responses": {
            "200": {
              "description": "All good",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "name": {
                          "type": "string",
                          "example": "XDR-dev"
                        },
                        "lastModified": {
                          "type": "string",
                          "format": "date-time",
                          "example": "2024-12-26T03:09:55.900Z"
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
    "/msr/{fileName}": {
        "get": {
          "summary": "Get an MSR file. Content-Type is dynamically fetched from S3 object metadata",
          "parameters": [
            {
              "name": "fileName",
              "in": "path",
              "required": true,
              "description": "Name of the file to fetch",
              "schema": {
                "type": "string",
                "example": "msr-report.pdf"
              }
            }
          ],
          "responses": {
            "200": {
              "description": "All good",
              "headers": {
                "Content-Type": {
                  "description": "Content-Type is dynamically fetched from S3 object metadata",
                  "schema": {
                    "type": "string",
                    "example": "application/pdf"
                  }
                }
              },
              "content": {
                "application/octet-stream": {
                  "schema": {
                    "type": "string",
                    "format": "binary"
                  }
                }
              }
            }
          }
        }
      }

#