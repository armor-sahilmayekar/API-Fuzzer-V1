import argparse

from modules.api.spec import OpenAPISpecValidator


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
