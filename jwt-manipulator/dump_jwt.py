import sys
from jwt_analyzer import JWTAnalyzer

def main() -> None:
    """
    Main entry point to run the JWTAnalyzer with the provided JWT token from the command line.
    """
    if len(sys.argv) < 2:
        print("Usage: python DumpJWT.py <JWT_TOKEN>")
        sys.exit(1)

    token = sys.argv[1]
    analyzer = JWTAnalyzer(token)
    analyzer.dump_jwt()
    result = analyzer.test_jwt()

    if result is None:
        print("JWT test failed.")
    else:
        print("JWT test completed successfully.")


if __name__ == "__main__":
    main()
