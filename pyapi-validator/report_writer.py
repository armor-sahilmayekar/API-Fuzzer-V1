import os
import json
from datetime import datetime


class ReportWriter:
    def __init__(self, report_dir):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.run_dir = os.path.join(report_dir, timestamp)
        os.makedirs(self.run_dir, exist_ok=True)

    def write_report(self, report_data):
        file_name = f"{report_data['test_number']:03d}_{report_data['name']}.json"
        file_path = os.path.join(self.run_dir, file_name)
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2)