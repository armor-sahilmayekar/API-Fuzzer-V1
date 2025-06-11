import json
import os

import requests
from kitty.interfaces import WebInterface

from modules.fuzzer.fuzz_model import APIFuzzerModel
from modules.fuzzer.fuzzer_target.fuzz_request_sender import FuzzerTarget
from modules.fuzzer.openapi_template_generator import OpenAPITemplateGenerator
from modules.fuzzer.server_fuzzer import OpenApiServerFuzzer
from modules.fuzzer.utils import set_logger
from modules.fuzzer.version import get_version
from modules.util.loggable import Loggable as log

class Fuzzer(object):
    def __init__(
        self,
        report_dir,
        test_level,
        log_level,
        basic_output,
        retest_dir=None,
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
        self.retest_dir = retest_dir
        self.test_result_dst = test_result_dst
        self.auth_headers = auth_headers if auth_headers else {}
        self.junit_report_path = junit_report_path
        self.logger = set_logger(log_level, basic_output)
        self.logger.info("%s initialized", get_version())
        self.api_definition_url = api_definition_url
        self.api_definition_file = api_definition_file

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

    def prepare_retest(self,status_code):
        log.info("Preparing Retest Fuzzer")

        retest_template_generator = RetestAPITemplateGenerator(
            _report_dir=self.retest_dir,
            _status_code=status_code,
        )

        try:
            retest_template_generator.process_retest_api_resources()
        except Exception as e:
            self.logger.error(f"Exception: {e}", exc_info=True)
            raise e
        self.templates = retest_template_generator.templates
        self.base_url = retest_template_generator.compile_base_url(self.alternate_url)





        # ___________
        print(f"[Retest] Reading test results from: {self.retest_dir}")
        print(f"[Retest] Filtering by status code: {status_code}")

        print(f"[Retest] Reading test results from: {self.retest_dir}")
        count = 0
        print(self.retest_dir)
        print(status_code)

        for filename in os.listdir(self.retest_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.report_dir, filename)
                with open(file_path, 'r') as f:
                    try:
                        data = json.load(f)
                        resp_status = data.get("response", {}).get("status_code")
                        if str(resp_status) == str(status_code):
                            self.replay_request(data)
                            count += 1
                    except json.JSONDecodeError:
                        print(f"[Warning] Skipping invalid JSON: {file_path}")

        print(f"[Retest] Completed. {count} matching requests replayed.")

    def replay_request(self, data):
        method = data["request"]["method"]
        url = self.alternate_url or data["request"]["url"]
        headers = data["request"].get("headers", {})
        body = data["request"].get("body")

        print(f"[Replay] {method} {url}")
        response = requests.request(method, url, headers=headers, json=body)

        print(f"[Replay] Response Status: {response.status_code}")
        # Optionally log/store the result


    def run(self):

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
        fuzzer.start()
        fuzzer.stop()
