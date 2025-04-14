import os
import json
from datetime import datetime
from typing import Dict, Any


class ReportWriter:
    def __init__(self, report_dir: str) -> None:
        """
        Initializes the ReportWriter by creating a unique subdirectory inside the
        provided reports directory, based on the current datetime.

        Args:
            report_dir (str): The base directory where reports should be stored.
        """
        # Create a timestamped folder like '2025-04-14_16-12-33'
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.run_dir = os.path.join(report_dir, timestamp)

        # Ensure the subdirectory exists
        os.makedirs(self.run_dir, exist_ok=True)

    def write_report(self, report_data: Dict[str, Any]) -> str:
        """
        Writes an individual test report to a JSON file inside the timestamped run directory.

        Args:
            report_data (Dict[str, Any]): A dictionary containing all the test report details.
                Expected to include fields like 'name' and 'test_number'.

        Returns:
            str: The full path to the written JSON report file.
        """
        # Create a filename using test number and test name for easy identification
        file_name = f"{report_data['test_number']:03d}_{report_data['name']}.json"
        file_path = os.path.join(self.run_dir, file_name)

        # Write the report to the JSON file
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        return file_path
