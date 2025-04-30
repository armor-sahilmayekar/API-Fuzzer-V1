import json
import os
from typing import Dict, List

from modules.case.operators import *
from modules.util.loggable import Loggable as log


class TestCaseRunner:
    def __init__(self, cases_directory: str = "cases"):
        """
        Initialize the Runner instance.

        Args:
            cases_directory (str): Directory containing JSON test cases (default: 'cases/')
        """
        self.cases_directory = cases_directory

    def load_test_cases_from_directory(self, directory: str) -> List[Dict]:
        """
        Load all .json test cases from a directory.

        Args:
            directory (str): Directory path containing JSON test files.

        Returns:
            List[Dict]: List of test case data dictionaries.
        """
        test_cases = []
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                path = os.path.join(directory, filename)
                with open(path, "r", encoding="utf-8") as file:
                    raw_content = file.read()
                    try:
                        # Directly load JSON without stripping comments
                        data = json.loads(raw_content)
                        test_cases.append(data)
                    except json.JSONDecodeError as e:
                        print(f"[ERROR] Failed to parse {filename}: {e}")
        return test_cases

    def run(self):
        """
        Entry point for executing tests using the directory specified at initialization.
        """
        cwd = os.getcwd()
        test_case_dir = os.path.join(cwd, self.cases_directory)
        log.info(f"Loading test cases from '{test_case_dir}' directory")
        all_data = self.load_test_cases_from_directory(self.cases_directory)
        log.info(f"Loaded {len(all_data)} cases!")
        for item in all_data:
            # Support both single-dictionary and list of test cases in each file
            test_set = item if isinstance(item, list) else [item]

            for test in test_set:
                try:
                    test_cases = TestCaseBuilder.build(test)
                    for test_case in test_cases:
                        print(f"[INFO] Running test: {test_case.name} ({test_case.method} {test_case.url})")
                        test_case.execute()
                        test_case.save_report()
                        print(f"[✓] Report saved for {test_case.name}\n")
                except Exception as ex:
                    name = test.get("name", "UNKNOWN") if isinstance(test, dict) else "UNKNOWN"
                    print(f"[ERROR] Failed to run test {name}: {ex}")