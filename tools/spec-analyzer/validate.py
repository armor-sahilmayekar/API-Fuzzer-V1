import json
import yaml
import requests
import argparse
from pathlib import Path
from typing import Optional, Any, List, Literal
from openapi_schema_validator import OAS30Validator, OAS31Validator, validate


class OpenAPISpecValidator:
    """
    A reusable and runnable class to validate an OpenAPI 3.0 or 3.1 specification
    from a file or URL, supporting YAML and JSON.
    """

    def __init__(self, source: str, source_type: Literal["file", "url"] = "file") -> None:
        """
        Initialize the validator with a file path or URL to the OpenAPI specification.

        Args:
            source (str): Path or URL to the OpenAPI specification file.
            source_type (Literal["file", "url"]): Indicates if the source is a file or a URL.
        """
        self.source: str = source
        self.source_type: Literal["file", "url"] = source_type
        self.spec: Optional[dict[str, Any]] = None
        self.version: Optional[str] = None
        self.errors: List[str] = []

    def load_spec(self) -> dict[str, Any]:
        """
        Load the OpenAPI specification from file or URL. Tries YAML first, falls back to JSON.

        Returns:
            dict[str, Any]: Parsed OpenAPI specification.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the content can't be parsed or URL fails.
        """
        if self.source_type == "file":
            path = Path(self.source)
            if not path.exists():
                raise FileNotFoundError(f"Spec file not found: {self.source}")
            content = path.read_text(encoding='utf-8')

        elif self.source_type == "url":
            response = requests.get(self.source, timeout=10)
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch spec from URL: {self.source}")
            content = response.text
        else:
            raise ValueError("source_type must be either 'file' or 'url'")

        try:
            self.spec = yaml.safe_load(content)
        except yaml.YAMLError:
            try:
                self.spec = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse content as YAML or JSON: {e}")

        if not isinstance(self.spec, dict):
            raise ValueError("Parsed content is not a valid OpenAPI object.")

        self.version = self.spec.get("openapi", "")
        return self.spec

    def get_validator(self) -> type:
        """
        Determine the correct validator class based on OpenAPI version.

        Returns:
            type: The appropriate validator class (OAS30Validator or OAS31Validator).

        Raises:
            ValueError: If the version is missing or unsupported.
        """
        if not self.version:
            raise ValueError("OpenAPI version not found in spec.")

        if self.version.startswith("3.0"):
            return OAS30Validator(self.spec)
        elif self.version.startswith("3.1"):
            return OAS31Validator(self.spec)
        else:
            raise ValueError(f"Unsupported OpenAPI version: {self.version}")

    def validate(self) -> bool:
        """
        Validate the loaded OpenAPI specification.

        Returns:
            bool: True if valid, False if validation errors are found.
        """
        if self.spec is None:
            self.load_spec()

        validator = self.get_validator()

        try:
            if not self.spec:
                self.load_spec()
            validator.validate(self.spec)

            return True
        except ValidationError as e:
            self.errors.append(str(e))
            return False
        except Exception as e:
            self.errors.append(str(e))
            return False

    def get_errors(self) -> List[str]:
        """
        Retrieve any validation errors that were collected.

        Returns:
            List[str]: List of error messages.
        """
        return self.errors

    def run(self) -> None:
        """
        Run the full validation pipeline and print results to the console.
        """
        try:
            self.load_spec()
            if self.validate():
                print("✅ OpenAPI specification is valid.")
            else:
                print("❌ OpenAPI specification is invalid.")
                for err in self.get_errors():
                    print(f"  - {err}")
        except Exception as e:
            print(f"❌ Error: {e}")


class ValidationError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def main() -> None:
    """
    CLI entry point to validate OpenAPI specs from the command line.
    """
    parser = argparse.ArgumentParser(description="Validate an OpenAPI 3.0/3.1 specification.")
    parser.add_argument('-s', '--source', help='Path or URL to the OpenAPI spec file"', required=True)
    parser.add_argument("--source-type", choices=["file", "url"], default="file",
                        help="Specify if the source is a 'file' or 'url' (default: file)")
    args = parser.parse_args()

    validator = OpenAPISpecValidator(source=args.source, source_type=args.source_type)
    validator.run()


if __name__ == "__main__":
    main()

