import json
import os

from kitty.interfaces import WebInterface

from modules.fuzzer.fuzz_model import APIFuzzerModel
from modules.fuzzer.fuzzer_target.fuzz_request_sender import FuzzerTarget
from modules.fuzzer.openapi_template_generator import OpenAPITemplateGenerator
from modules.fuzzer.server_fuzzer import OpenApiServerFuzzer
from modules.fuzzer.utils import set_logger
from modules.fuzzer.version import get_version
from modules.util.loggable import Loggable as log
from modules.fuzzer.fuzzer_target.fuzz_request_sender import timestamp_dir as timestamp_dir

class Fuzzer(object):
    def __init__(
        self,
        report_dir,
        test_level,
        log_level,
        basic_output,
        alternate_url=None,
        test_result_dst=None,
        auth_headers=None,
        api_definition_url=None,
        api_definition_file=None,
        junit_report_path=None,
    ):
        self.base_url = None
        self.alternate_url = alternate_url
        self.templates = None
        self.test_level = test_level
        self.report_dir = report_dir
        self.test_result_dst = test_result_dst
        self.auth_headers = auth_headers if auth_headers else {}
        self.junit_report_path = junit_report_path
        self.logger = set_logger(log_level, basic_output)
        self.logger.info("%s initialized", get_version())
        self.api_definition_url = api_definition_url
        self.api_definition_file = api_definition_file
        self._run_tests_for_status_code = None

    def prepare(self):
        log.info("Preparing Fuzzer")
        # here we will be able to branch the template generator if we will support other than Swagger / OpenAPI
        template_generator = OpenAPITemplateGenerator(
            api_definition_url=self.api_definition_url,
            api_definition_file=self.api_definition_file,
        )
        try:
            template_generator.process_api_resources()
        except Exception as e:
            self.logger.error(f"Exception: {e}", exc_info=True)
            raise e
        self.templates = template_generator.templates
        self.base_url = template_generator.compile_base_url(self.alternate_url)

    # def run(self):
    #
    #     target = FuzzerTarget(
    #         name="target",
    #         base_url=self.base_url,
    #         report_dir=self.report_dir,
    #         auth_headers=self.auth_headers,
    #         junit_report_path=self.junit_report_path,
    #     )
    #     interface = WebInterface()
    #     model = APIFuzzerModel()
    #     for template in self.templates:
    #         model.connect(template.compile_template())
    #         model.content_type = template.get_content_type()
    #     fuzzer = OpenApiServerFuzzer()
    #     fuzzer.set_model(model)
    #     fuzzer.set_target(target)
    #     fuzzer.set_interface(interface)
    #     fuzzer.start()
    #     fuzzer.stop()


    # create a new function to call individual cases depending on its status code and individual testcase number

    def run(self, status_code=None, folder=None):
        """
        Run the fuzzer based on the presence or absence of a status_code.
        If status_code is provided, run tests for that specific status code folder.
        If status_code is not provided, run all tests.
        """
        # Set up the target and other fuzzer components
        self._run_tests_for_status_code = status_code
        target = FuzzerTarget(
            name="target",
            base_url=self.base_url,
            report_dir=self.report_dir,
            auth_headers=self.auth_headers,
            junit_report_path=self.junit_report_path,
        )
        interface = WebInterface()
        model = APIFuzzerModel()
        for template in self.templates:
            model.connect(template.compile_template())
            model.content_type = template.get_content_type()

        fuzzer = OpenApiServerFuzzer()
        fuzzer.set_model(model)
        fuzzer.set_target(target)
        fuzzer.set_interface(interface)

        # If no status_code is provided (called as prog.run()), run all tests
        if status_code is None:
            print("Running all test cases...")
            fuzzer.start()
            fuzzer.stop()
        else:
            # If a specific status_code is provided (called as prog.run(200), for example), run tests for that status code
            print(f"Running tests for status code {status_code}...")
            self.run_tests_for_status_code(fuzzer, status_code, folder)

    def run_tests_for_status_code(self, fuzzer, status_code, folder):
        """
        Runs tests specifically for the given status code folder inside the report directory.
        """

        statuscode_folders = folder
        print("statuscode_folders:", statuscode_folders)

        # statuscode_str = str(status_code)
        # statuscode_path = os.path.join(passedfolder_path, statuscode_str)
        #
        # if statuscode_str not in statuscode_folders or not os.path.isdir(statuscode_path):
        #     print(f"Status code folder '{statuscode_str}' not found.")
        #     return

        print(f"Found status code folder: {statuscode_folders}")
        files = [f for f in os.listdir(statuscode_folders) if os.path.isfile(os.path.join(statuscode_folders, f))]
        print("Files:", files)

        if len(files) > 1:
            self.run_tests_in_status_folder(statuscode_folders, fuzzer)
        else:
            print("Not enough files to run tests.")

        # select the status code folder in passed directory


    def run_tests_in_status_folder(self, status_folder, fuzzer):
        """
        Runs the tests inside the specific status code folder.
        """
        print(f"Running tests for status code folder: {status_folder}")
        for file_name in os.listdir(status_folder):
            if file_name.endswith(".json"):
                file_path = os.path.join(status_folder, file_name)
                print(f"Running test case from {file_path}")
                # Load the test case JSON and run it with the fuzzer
                self.run_test_case(file_path, fuzzer)


    def run_test_case(self, file_path, fuzzer):
        """
        Loads and executes the test case from a JSON file.
        """
        print(f"Loading test case from {file_path}")
        try:
            with open(file_path, 'r') as f:
                test_case_data = json.load(f)
                print("test case data -", test_case_data)
                is_dict = isinstance(test_case_data, dict)
                response_code_matches = test_case_data.get("response_code") == self._run_tests_for_status_code
          # if isinstance(dict, test_case_data) is not None and test_case_data.get("response_code") == self._run_tests_for_status_code :
                if is_dict and response_code_matches:
                    print(f"Running test case: {test_case_data}")
                    fuzzer.start()

                # fuzzer.run_test(test_case_data)  # Example call to a fuzzer method
            fuzzer.stop()
        except Exception as e:
            print(f"Error running test case from {file_path}: {e}")













# Yet to check


    # def run_singlecase(self, status_code, test_case_name):
    #     """
    #     Run a specific test case file by status code and test case name.
    #     Example path: passed_dir/404/testcase_1.json
    #     """
    #     file_path = os.path.join(self.passed_dir, str(status_code), f"{test_case_name}.json")
    #
    #     if not os.path.exists(file_path):
    #         self.logger.error(f"Test case file does not exist: {file_path}")
    #         return
    #
    #     self.logger.info(f"Running single test case: {file_path}")
    #     self.run_test_from_json(file_path)
    #
    def run_test_from_json(self, file_path):
        """
        This function handles the running of individual test cases from a .json file.
        """
        try:
            with open(file_path, 'r') as f:
                test_case_data = json.load(f)
                # Add your test execution logic here
                # You would probably pass the test_case_data to the fuzzer
                self.logger.info(f"Running test case: {file_path}")
                # Example:
                # self.fuzzer.execute(test_case_data)
        except Exception as e:
            self.logger.error(f"Failed to run test from {file_path}: {e}")

