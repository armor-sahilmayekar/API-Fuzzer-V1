import sys
import traceback

from modules.api.client import APIClient
from modules.fuzzer.exceptions import FailedToParseFileException
from modules.fuzzer.fuzzer import Fuzzer
from modules.api.spec import OpenAPISpecValidator
from modules.reports.writer import ReportWriter

REPORTS_DIR = "reports"
ALTERNATE_URL = ""
LOG_LEVEL = "INFO"
TEST_LEVEL = 1
ALTERNATE_URL = "http://127.0.0.1:5000"
API_SPEC_URL = None
API_SPEC_FILE = "data/openapi/openapi_mdr_v3.json"
SOURCE: str="file"
AUTH_HEADER = {}
BASIC_OUTPUT = False


def run_fuzzer():
    try:
        prog = Fuzzer(report_dir=REPORTS_DIR,
                      test_level=TEST_LEVEL,
                      alternate_url=ALTERNATE_URL,
                      test_result_dst=REPORTS_DIR,
                      log_level=LOG_LEVEL,
                      basic_output=BASIC_OUTPUT,
                      auth_headers=AUTH_HEADER,
                      api_definition_url=API_SPEC_URL,
                      api_definition_file=API_SPEC_FILE,
                      junit_report_path=REPORTS_DIR
                      )

        prog.prepare()
    except FailedToParseFileException:
        print('Failed to parse API definition')
        exit(1)
    except Exception as e:
        print(f'Unexpected exception happened during fuzz test preparation: {traceback.print_stack(*sys.exc_info())}.\n'
              f' Feel free to reports the issue', )
        exit(1)
    prog.run()


if __name__ == '__main__':
    # step 1: validate api spec
    validator = OpenAPISpecValidator(source=API_SPEC_FILE, source_type=SOURCE)
    validator.run()

    # step 1: run the api fuzzer
    run_fuzzer()


