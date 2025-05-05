import ast
import copy
import json
import os
from datetime import datetime
from typing import Dict, Any

from modules.fuzzer.apifuzzerreport import ApifuzzerReport
from modules.util.loggable import Loggable as log


class TestReport(ApifuzzerReport):
    """
    A class representing a structured report, with built-in export via ReportWriter.

    Example:
        >>> report_data = {
        ...     "status": "passed",
        ...     "name": {"accept": "application/json"},
        ...     "test_number": 5,
        ...     "state": "COMPLETED",
        ...     "request_url": "https://api.example.com/test",
        ...     "request_method": "GET"
        ... }
        >>> report = TestReport("some_test", report_dir="reports")
        >>> report.from_dict(report_data)
        >>> report.save()
    """
    OUTPUT_DIR = None

    def __init__(self, name, report_dir: str = "reports") -> None:
        super().__init__(name)
        # Default values
        self.set_status("error")
        self.add("sub_reports", [])
        self.add ("test_number", -1)
        self.add("state", "UNKNOWN")
        self.add("request_url", "")
        self.add("request_method", "")
        self.add("request_headers", "")
        self.add("request_body", "")
        self.add("response", None)
        self.add("reason", "")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if TestReport.OUTPUT_DIR is None:
            TestReport.OUTPUT_DIR = os.path.join(report_dir, timestamp)
            os.makedirs(TestReport.OUTPUT_DIR, exist_ok=True)

    def save(self) -> str:
        """
        Saves the report using ReportWriter.

        Returns:
            str: Path to the written JSON file.
        """
        log.debug(f"Saving report {self.to_dict()}")
        return self._write_report(self.to_dict(), self.get("name"), self.get("test_number"))


    def _write_report(self, report_data: Dict[str, Any], name: str, test_number: int) -> str:
        """
        Writes an individual test report to a JSON file inside the timestamped run directory.

        The filename is constructed using the test number and test name, formatted as:
        `{test_number:03d}_{name}.json`.

        Args:
            report_data (Dict[str, Any]): A dictionary containing the report data to save.
            name (str): A human-readable name or test identifier for naming the file.
            test_number (int): The index of the test to help order report files.

        Returns:
            str: The full path to the saved JSON report file.
        """
        try:
            file_name = f"{test_number:03d}_{name}.json"
            file_path = os.path.join(TestReport.OUTPUT_DIR, file_name)
            clean_data = self._clean_auth()
            if not os.path.exists(TestReport.OUTPUT_DIR):
                try:
                    os.makedirs(TestReport.OUTPUT_DIR)
                except OSError:
                    pass
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(clean_data.to_dict(), f, indent=2, ensure_ascii=False)
        except FileNotFoundError as fnf:
            log.error(fnf)
        except PermissionError as pm:
            log.error(pm)
        except Exception as ex:
            log.error(ex)
        return file_path

    def _clean_auth(self) -> ApifuzzerReport:
        b = copy.deepcopy(self)
        check = b.get("request_headers")
        if check is None:
            rh = ast.literal_eval(b.get("request_headers"))
            rh["authorization"] = "**********"
            b.add("request_headers", rh)
        elif isinstance(self.get("request_headers"), dict):
            rh = b.get("request_headers")
            rh["authorization"] = "**********"
            b.add("request_headers", rh)
        return b

    def from_dict(self, d):
        '''
        Construct a ``Report`` object from dictionary.

        :type d: dictionary
        :param d: dictionary representing the report
        :param encoding: encoding of strings in the dictionary (default: 'base64')
        :return: Report object
        '''
        try:
            report = TestReport(d.get('name'))
            report.set_status(d.get('status'))
            sub_reports = d.get('sub_reports')
            del d['sub_reports']
            for k, v in d.items():
                if k in sub_reports:
                    report.add(k, TestReport.from_dict(v))
                else:
                    if k.lower() == 'status':
                        report.set_status(v)
                    else:
                        report.add(k, v)
        except Exception as e:
            log.error(e)

        return report

