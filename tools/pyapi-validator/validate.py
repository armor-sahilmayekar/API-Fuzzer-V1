import argparse
import os.path

from modules.case.runner import TestCaseRunner

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run vulnerability tests from JSON files.")
    parser.add_argument(
        "--cases", "-c",
        type=str,
        default="data/cases",
        help="Directory containing JSON test cases (default: cases/)"
    )
    args = parser.parse_args()
    try:
        os.listdir(args.cases)
    except FileNotFoundError:
        parser.print_help()
        parser.print_usage()
        parser.exit(1, "Cases directory invalid!")

    # Initialize the Runner instance and call the run method
    runner = TestCaseRunner(cases_directory=args.cases)
    runner.run()
