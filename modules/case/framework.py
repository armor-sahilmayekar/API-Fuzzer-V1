import json
import os
from typing import Dict, List

from modules.case.operators import *
from modules.util.loggable import Loggable as log


class TestCaseFactory(ABC):
    """
    Abstract factory for creating TestCase instances.
    """

    def __init__(self, test_case_cls: type):
        """
        Args:
            test_case_cls (type): A TestCase subclass this factory will create.
        """
        self.test_case_cls = test_case_cls

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> TestCase:
        pass


class MatchTestCaseFactory(TestCaseFactory):
    """Factory for MatchTestCase."""

    def create(self, data: Dict[str, Any]) -> TestCase:
        log.debug(f"Creating Test Case with {data}")
        return self.test_case_cls(**TestCase.parse_data(data).to_dict())




class ExactMatchTestCaseFactory(TestCaseFactory):
    """Factory for ExactMatchTestCase."""

    def create(self, data: Dict[str, Any]) -> TestCase:
        log.debug(f"Creating Test Case with {data}")
        return self.test_case_cls(**TestCase.parse_data(data).to_dict())


class FuzzyMatchTestCaseFactory(TestCaseFactory):
    """Factory for FuzzyMatchTestCase."""

    def create(self, data: Dict[str, Any]) -> TestCase:
        log.debug(f"Creating Test Case with {data}")
        return self.test_case_cls(**TestCase.parse_data(data).to_dict())


class FieldMatchTestCaseFactory(TestCaseFactory):
    """Factory for FieldMatchTestCase."""

    def create(self, data: Dict[str, Any]) -> TestCase:
        log.debug(f"Creating Test Case with {data}")
        return self.test_case_cls(**TestCase.parse_data(data).to_dict())


class FieldSetMatchTestCaseFactory(TestCaseFactory):
    """Factory for FieldSetMatchTestCase."""

    def create(self, data: Dict[str, Any]) -> TestCase:
        log.debug(f"Creating Test Case with {data}")
        return self.test_case_cls(**TestCase.parse_data(data).to_dict())


class TestCaseBuilder:
    """
    Dispatcher class that maps operator types to corresponding TestCaseFactory.
    """

    _factory_registry: Dict[str, TestCaseFactory] = {
        "match": MatchTestCaseFactory(MatchTestCase),
        "exact_match": ExactMatchTestCaseFactory(ExactMatchTestCase),
        "fuzzy_match": FuzzyMatchTestCaseFactory(FuzzyMatchTestCase),
        "field_match": FieldMatchTestCaseFactory(FieldMatchTestCase),
        "field_set_match": FieldSetMatchTestCaseFactory(FieldSetMatchTestCase),
    }

    @staticmethod
    def _strip_json_comments(data: str) -> str:
        """
        Removes comments from JSON formatted text (removes lines that start with `##`).

        Args:
            data (str): The raw JSON data as a string.

        Returns:
            str: The cleaned JSON data as a string.
        """
        log.debug(f"Removing comments from {data}")
        return "\n".join(line for line in data.splitlines() if not line.strip().startswith('#'))

    @staticmethod
    def build(data: Dict[str, Any]) -> List[TestCase]:
        """
        Build and return TestCase instances based on the input data.

        Args:
            data (Dict[str, Any]): Test case data, which may be a dictionary or list of dictionaries.

        Returns:
            List[TestCase]: A list of TestCase instances.
        """
        # In case it's an array of test cases
        if isinstance(data, list):
            return [TestCaseBuilder._build_single(test_case_data) for test_case_data in data]
        # In case it's a single test case in dictionary format
        elif isinstance(data, dict):
            return [TestCaseBuilder._build_single(data)]
        else:
            raise ValueError("Input data must be a dictionary or a list of dictionaries.")

    @staticmethod
    def _build_single(data: Dict[str, Any]) -> TestCase:
        """
        Helper method to build a single test case from a dictionary.

        Args:
            data (Dict[str, Any]): Test case data.

        Returns:
            TestCase: An instance of the appropriate TestCase subclass.
        """
        match_type = (
            data.get("expected", {})
            .get("operators", {})
            .get("type", "match")
            .lower()
        )
        factory = TestCaseBuilder._factory_registry.get(match_type)
        if not factory:
            raise ValueError(f"Unsupported match type: {match_type}")
        return factory.create(data)


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
