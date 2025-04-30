import pytest
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from openapi_schema_validator import OAS30Validator, OAS31Validator
from modules.api.spec import OpenAPISpecValidator, ValidationError


@pytest.fixture
def valid_openapi_30_yaml():
    return """
openapi: "3.0.1"
info:
  title: Sample API
  version: 1.0.0
paths: {}
    """


@pytest.fixture
def valid_openapi_31_yaml():
    return """
openapi: "3.1.0"
info:
  title: Sample API
  version: 1.0.0
paths: {}
    """


@pytest.fixture
def invalid_yaml():
    return """
openapi: "3.0.1"
info:
  title: Sample API
  version: 1.0.0
paths
  - invalid
    """


def test_load_spec_from_file_yaml(valid_openapi_30_yaml):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write(valid_openapi_30_yaml)
        tmp_path = tmp.name

    validator = OpenAPISpecValidator(tmp_path, source_type="file")
    spec = validator.load_spec()
    assert spec["openapi"] == "3.0.1"
    Path(tmp_path).unlink()  # cleanup


@patch("requests.get")
def test_load_spec_from_url_yaml(mock_get, valid_openapi_30_yaml):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = valid_openapi_30_yaml

    validator = OpenAPISpecValidator("http://example.com/openapi.yaml", source_type="url")
    spec = validator.load_spec()
    assert spec["openapi"] == "3.0.1"


def test_load_spec_file_not_found():
    validator = OpenAPISpecValidator("nonexistent.yaml", source_type="file")
    with pytest.raises(FileNotFoundError):
        validator.load_spec()


@patch("requests.get")
def test_load_spec_url_failure(mock_get):
    mock_get.return_value.status_code = 404
    validator = OpenAPISpecValidator("http://invalid-url", source_type="url")
    with pytest.raises(ValueError):
        validator.load_spec()


def test_load_spec_invalid_yaml(invalid_yaml):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write(invalid_yaml)
        tmp_path = tmp.name

    validator = OpenAPISpecValidator(tmp_path, source_type="file")
    with pytest.raises(ValueError):
        validator.load_spec()
    Path(tmp_path).unlink()


def test_get_validator_for_30(valid_openapi_30_yaml):
    validator = OpenAPISpecValidator("dummy.yaml")
    validator.spec = {"openapi": "3.0.1"}
    validator.version = "3.0.1"
    assert isinstance(validator.get_validator(), OAS30Validator)


def test_get_validator_for_31(valid_openapi_31_yaml):
    validator = OpenAPISpecValidator("dummy.yaml")
    validator.spec = {"openapi": "3.1.0"}
    validator.version = "3.1.0"
    assert isinstance(validator.get_validator(), OAS31Validator)


def test_get_validator_invalid_version():
    validator = OpenAPISpecValidator("dummy.yaml")
    validator.spec = {"openapi": "2.0.0"}
    validator.version = "2.0.0"
    with pytest.raises(ValueError):
        validator.get_validator()


@patch.object(OpenAPISpecValidator, "get_validator")
def test_validate_valid_spec(mock_get_validator, valid_openapi_30_yaml):
    mock_validator = MagicMock()
    mock_validator.validate.return_value = None
    mock_get_validator.return_value = mock_validator

    validator = OpenAPISpecValidator("dummy.yaml")
    validator.spec = {"openapi": "3.0.1"}
    validator.version = "3.0.1"
    assert validator.validate() is True
    assert validator.get_errors() == []


@patch.object(OpenAPISpecValidator, "get_validator")
def test_validate_invalid_spec(mock_get_validator):
    mock_validator = MagicMock()
    mock_validator.validate.side_effect = ValidationError("Schema error")
    mock_get_validator.return_value = mock_validator

    validator = OpenAPISpecValidator("dummy.yaml")
    validator.spec = {"openapi": "3.0.1"}
    validator.version = "3.0.1"
    assert validator.validate() is False
    assert "Schema error" in validator.get_errors()


@patch.object(OpenAPISpecValidator, "load_spec")
@patch.object(OpenAPISpecValidator, "validate")
def test_run_valid(c_validate, c_load):
    c_validate.return_value = True
    validator = OpenAPISpecValidator("dummy.yaml")
    validator.run()  # Just ensure it runs without exception


@patch.object(OpenAPISpecValidator, "load_spec")
@patch.object(OpenAPISpecValidator, "validate")
@patch.object(OpenAPISpecValidator, "get_errors")
def test_run_invalid(c_get_errors, c_validate, c_load):
    c_validate.return_value = False
    c_get_errors.return_value = ["Oops"]
    validator = OpenAPISpecValidator("dummy.yaml")
    validator.run()


def test_validation_error_str():
    e = ValidationError("Error message")
    assert str(e) == "Error message"
