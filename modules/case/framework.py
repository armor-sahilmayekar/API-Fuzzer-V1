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


