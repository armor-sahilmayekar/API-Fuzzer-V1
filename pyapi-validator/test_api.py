import pytest
import os
import json
from main import run_test_case

@pytest.mark.parametrize("test_case", json.load(open("test_cases.json")))
def test_api_variants(monkeypatch, test_case):
    monkeypatch.setenv("API_KEY", "dummy_api_key")
    result = run_test_case(test_case, os.environ.get("API_KEY"))
    assert result["status"] == "success"
    assert result["state"] in ["PASSED", "FAILED"]
