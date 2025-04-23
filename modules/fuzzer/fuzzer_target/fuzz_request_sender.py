import json
import os
import urllib.parse
from io import BytesIO
from time import time, perf_counter
from datetime import datetime
import os
import pycurl
from bitstring import Bits
from junit_xml import TestSuite, TestCase, to_xml_report_file
from kitty.targets.server import ServerTarget

from modules.fuzzer.apifuzzerreport import ApifuzzerReport as Report, ApifuzzerReport
from modules.fuzzer.fuzzer_target.request_base_functions import FuzzerTargetBase
from modules.fuzzer.utils import try_b64encode, init_pycurl, get_logger
from modules.export.report import TestReport

class Return:
    pass


class FuzzerTarget(FuzzerTargetBase, ServerTarget):
    def not_implemented(self, func_name):
        _ = func_name
        pass

    def __init__(self, name="target", base_url=None, report_dir="reports", auth_headers=None, junit_report_path="reports"):

            super(ServerTarget, self).__init__(name)
            super(FuzzerTargetBase, self).__init__(auth_headers)
            self.logger = get_logger(self.__class__.__name__)
            self.base_url = base_url
            self.accepted_status_codes = list(range(200, 300)) + list(range(400, 500))
            self.auth_headers = auth_headers

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.timestamp_dir = os.path.join(report_dir, timestamp)
            self.passed_dir = os.path.join(self.timestamp_dir, "passed")
            self.error_dir = os.path.join(self.timestamp_dir, "error")

            os.makedirs(self.passed_dir, exist_ok=True)
            os.makedirs(self.error_dir, exist_ok=True)

            self.report_dir = self.timestamp_dir  # update to point to the timestamp dir
            self.junit_report_path = os.path.join(self.timestamp_dir, "junit_report.xml")
            self.failed_test = list()
            self.logger.info("Logger initialized")
            self.resp_headers = dict()
            self.transmit_start_test = None

    def pre_test(self, test_num):
        """
        Called when a test is started
        """
        self.test_number = test_num
        self.report = ApifuzzerReport(str(test_num))
        if self.controller:
            self.controller.pre_test(test_number=self.test_number)
        for monitor in self.monitors:
            monitor.pre_test(test_number=self.test_number)
        self.report.add("test_number", test_num)
        self.report.add("state", "STARTED")
        self.transmit_start_test = perf_counter()

    def transmit(self, **kwargs):
        """
        Prepares fuzz HTTP request, sends and processes the response
        :param kwargs: url, method, params, querystring, etc
        :return:
        """
        self.logger.debug("Transmit: {}".format(kwargs))
        try:
            _req_url = list()
            for url_part in self.base_url, kwargs["url"]:
                if not url_part:
                    continue
                elif isinstance(url_part, Bits):
                    url_part = url_part.tobytes()
                elif isinstance(url_part, bytes):
                    url_part = url_part.decode()
                _req_url.append(url_part.strip("/"))
            kwargs.pop("url")
            # Replace back the placeholder for '/'
            # (this happens in expand_path_variables,
            # but if we don't have any path_variables, it won't)
            request_url = "/".join(_req_url).replace("+", "/")
            query_params = None

            if kwargs.get("params") is not None:
                self.logger.debug(
                    ("Adding query params: {}".format(kwargs.get("params", {})))
                )
                query_params = self.format_pycurl_query_param(
                    request_url, kwargs.get("params", {})
                )
                kwargs.pop("params")
            if kwargs.get("path_variables") is not None:
                request_url = self.expand_path_variables(
                    request_url, kwargs.get("path_variables")
                )
                kwargs.pop("path_variables")
            if kwargs.get("data") is not None:
                kwargs["data"] = self.fix_data(kwargs.get("data"))
            if query_params is not None:
                request_url = "{}{}".format(request_url, query_params)
            method = kwargs["method"]
            content_type = kwargs.get("content_type")
            kwargs.pop("content_type", None)
            self.logger.info("Request URL : {} {}".format(method, request_url))
            if kwargs.get("data") is not None:
                self.logger.info(
                    "Request data:{}".format(json.dumps(dict(kwargs.get("data"))))
                )
            if isinstance(method, Bits):
                method = method.tobytes()
            if isinstance(method, bytes):
                method = method.decode()
            kwargs.pop("method")
            kwargs["headers"] = self.compile_headers(kwargs.get("headers"))
            self.logger.debug(
                "Request url:{}\nRequest method: {}\nRequest headers: {}\nRequest body: {}".format(
                    request_url,
                    method,
                    json.dumps(dict(kwargs.get("headers", {})), indent=2),
                    kwargs.get("data"),
                )
            )
            self.report.set_status(Report.PASSED)
            self.report.add("request_url", request_url)
            self.report.add("request_method", method)
            self.report.add(
                "request_headers", json.dumps(dict(kwargs.get("headers", {})))
            )
            try:
                resp_buff_hdrs = BytesIO()
                resp_buff_body = BytesIO()
                buffer = BytesIO()
                _curl = init_pycurl()
                _curl.setopt(pycurl.URL, self.format_pycurl_url(request_url))
                _curl.setopt(pycurl.HEADERFUNCTION, self.header_function)
                _curl.setopt(pycurl.POST, len(kwargs.get("data", {}).items()))
                _curl.setopt(pycurl.CUSTOMREQUEST, method)
                headers = kwargs["headers"]
                if content_type:
                    self.logger.debug(f"Adding Content-Type: {content_type} header")
                    headers.update({"Content-Type": content_type})
                _curl.setopt(pycurl.HTTPHEADER, self.format_pycurl_header(headers))
                if content_type == "multipart/form-data":
                    post_data = list()
                    for k, v in kwargs.get("data", {}).items():
                        post_data.append((k, v))
                    _curl.setopt(pycurl.HTTPPOST, post_data)
                elif content_type == "application/json":
                    _json_data = (
                        json.dumps(kwargs.get("data", {}), ensure_ascii=True)
                            .encode("utf-8")
                            .decode("utf-8", "ignore")
                    )
                    _curl.setopt(pycurl.POSTFIELDS, _json_data)
                else:
                    # default content type: application/x-www-form-urlencoded
                    _curl.setopt(
                        pycurl.POSTFIELDS,
                        urllib.parse.urlencode(kwargs.get("data", {})),
                    )
                _curl.setopt(pycurl.HEADERFUNCTION, resp_buff_hdrs.write)
                _curl.setopt(pycurl.WRITEFUNCTION, resp_buff_body.write)
                for retries in reversed(range(0, 3)):
                    try:
                        _curl.perform()
                        self.report.set_status(Report.PASSED)
                        # TODO: Handle this: pycurl.error: (3, 'Illegal characters found in URL')
                    except pycurl.error as e:
                        self.logger.warning(f"Failed to send request because of {e}")
                        self.report.set_status(Report.ERROR)
                        self.report.add('exception', e.msg if hasattr(e, 'msg') else str(e))
                    except Exception as e:
                        if not retries:
                            raise
                        self.logger.error(
                            "Retrying... ({}) because {}".format(retries, e)
                        )
                        self.report.set_status(Report.ERROR)
                        self.report.add('exception', e.msg if hasattr(e, 'msg') else str(e))
                _return = Return()
                _return.status_code = _curl.getinfo(pycurl.RESPONSE_CODE)
                _return.headers = self.resp_headers
                _return.content = buffer.getvalue()
                _return.request = Return()
                _return.request.headers = kwargs.get("headers", {})
                _return.request.body = kwargs.get("data", {})
                _curl.close()
            except Exception as e:
                self.logger.exception(e)
                self.report.set_status(Report.ERROR)
                self.logger.error("Request failed, reason: {}".format(e))
                self.report.add('request_sending_failed', e.msg if hasattr(e, 'msg') else str(e))
                # self.export.add('request_sending_failed', e.msg if hasattr(e, 'msg') else e)
                self.report.add("request_method", method)
                return
            # overwrite request headers in export, add auto generated ones
            self.report.add(
                "request_headers",
                try_b64encode(json.dumps(dict(_return.request.headers))),
            )
            self.logger.debug(
                "Response code:{}\nResponse headers: {}\nResponse body: {}".format(
                    _return.status_code,
                    json.dumps(dict(_return.headers), indent=2),
                    _return.content,
                )
            )
            self.report.add("request_body", _return.request.body)
            self.report.add("response", _return.content.decode())
            status_code = _return.status_code
            print(status_code, "status code from fuzzer")
            self.report.add("response_code",  status_code)
            if not status_code:
                self.logger.warning(f"Failed to parse http response code, continue...")
                self.report.set_status(Report.ERROR)
                self.report.add("details", "Failed to parse http response code")
            elif status_code not in self.accepted_status_codes:
                if self.report.get_status() != Report.ERROR:
                    self.report.set_status(Report.FAILED)
                self.report.add("parsed_status_code", status_code)
                self.report_add_basic_msg(
                    ("Return code %s is not in the expected list:", status_code)
                )
            elif status_code == 500:
                self.logger.error(f"Response code {status_code} for payload is {self.report}")
            return _return
        except (
            UnicodeDecodeError,
            UnicodeEncodeError,
        ) as e:  # request failure such as InvalidHeader
            self.report_add_basic_msg(
                ("Failed to parse http response code, exception occurred: %s", e)
            )

    def post_test(self, test_num):
        """Called after a test is completed, perform cleanup etc."""
        if self.report.get("export") is None:
            self.report.add("reason", self.report.get_status())
        super(ServerTarget, self).post_test(test_num)
        _base =  super(ServerTarget, self)
        if self.junit_report_path:
            report_dict = self.report.to_dict()
            test_case = TestCase(
                    name=f"{self.test_number}: {report_dict['request_url']}",
                status=self.report.get_status(),
                timestamp=time(),
                elapsed_sec=perf_counter() - self.transmit_start_test
            )
            if self.report.get_status() == Report.FAILED:
                test_case.add_failure_info(message=json.dumps(self.report.to_dict()))
            if self.report.get_status() == Report.ERROR:
                test_case.add_error_info(message=json.dumps(self.report.to_dict()))
            self.failed_test.append(test_case)
            self.save_report_to_disc()

    def save_report_to_disc(self):
        self.logger.info("Report: {}".format(self.report.to_dict()))
        try:
            status_code = self.report.get("response_code")
            if status_code == 200:
                target_dir = self.passed_dir
            else:
                target_dir = self.error_dir

            file_name = f"{self.report.get('name')}.json"
            file_path = os.path.join(target_dir, file_name)

            with open(file_path, "w") as f:
                json.dump(self.report.to_dict(), f, indent=2)

            self.logger.info(f"Saved report to {file_path}")
        except Exception as e:
            self.logger.error(f'Failed to save report to folder: {e}')

    def report_add_basic_msg(self, msg):
        self.report.set_status(Report.FAILED)
        self.logger.warning(msg)
        self.report.failed(msg)

    def teardown(self):
        if len(self.failed_test):
            test_cases = self.failed_test
        else:
            test_cases = list()
            test_cases.append(TestCase(name="Fuzz test succeed", status="Pass"))
        if self.junit_report_path:
            with open(self.junit_report_path, "w") as report_file:
                to_xml_report_file(
                    report_file,
                    [TestSuite(name="API Fuzzer", test_cases=test_cases, timestamp=time())],
                    prettyprint=True
                )
        super(ServerTarget, self).teardown()  # pylint: disable=E1003
