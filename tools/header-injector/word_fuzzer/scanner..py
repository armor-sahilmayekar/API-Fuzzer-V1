import argparse
import os
import random
import json
import logging
import time

from colorama import init, Fore
import requests

# Initialize colorama
init(autoreset=True)

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scanner.log"),
        logging.StreamHandler()
    ]
)

# Constants
DEFAULT_ATTACKER = 'attacker.com'
DEFAULT_REDIRECTS = 10
DEFAULT_SSL = False
DEFAULT_METHOD = 'GET'
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
DEFAULT_REPORT_DIR = 'reports/'


class VulnerabilityScanner:
    """Core class responsible for running vulnerability scans on a URL."""

    def __init__(self, attacker, output_dir, max_redirects, use_ssl, method, user_agent, verbose, body, proxy, debug, recursive):
        self.attacker = attacker
        self.output_dir = output_dir
        self.max_redirects = max_redirects
        self.use_ssl = use_ssl
        self.method = method
        self.user_agent = user_agent
        self.verbose = verbose
        self.body = body
        self.proxy = proxy
        self.debug = debug
        self.recursive = recursive

    def get_headers_list(self, wordlist_path):
        self.log_and_print(f'Using wordlist {wordlist_path}')
        if wordlist_path:
            try:
                with open(wordlist_path, 'r') as file:
                    return [line.strip() for line in file.readlines()]
            except Exception as e:
                logging.error(f"Error reading wordlist: {e}")
        return ['Host', 'Max-Forwards', 'Origin', 'Proxy-Authorization', 'Range', 'Referer', 'Upgrade', 'User-Agent', 'X-Forwarded-For', 'X-Forwarded-Host']

    def log_and_print(self, message, level=logging.INFO, color=None):
        logging.log(level, message)
        if color:
            print(color + message)
        else:
            print(message)

    def save_json_report(self, test_num, data):
        try:
            if not os.path.exists(DEFAULT_REPORT_DIR):
                os.makedirs(DEFAULT_REPORT_DIR)
            json_path = os.path.join(DEFAULT_REPORT_DIR, f'header_injection_{test_num}_{time.time()}.json')
            with open(json_path, 'a') as f:
                json.dump(data, f)
                f.write('\n')
        except Exception as e:
            logging.error(f"Error saving JSON reports: {e}")

    def detect(self, url, wordlists):
        headers_list = self.get_headers_list(wordlists)
        test_num = 0
        for header in headers_list:
            test_num = test_num + 1
            headers_dict = {
                'Host': url.split('/')[2],
                'User-Agent': self.user_agent,
                header: self.attacker
            }

            if self.debug:
                self.log_and_print(f"[Request] URL: {url}, Method: {self.method}, Headers: {headers_dict}, Body: {self.body}, Proxy: {self.proxy}", logging.DEBUG, Fore.CYAN)

            proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
            json_report = {
                "status": "success",
                "name": f'header_injection_{header}',
                "sub_reports": [],
                "test_number": test_num,
                "state": "COMPLETED",
                "request_url": url,
                "request_method": self.method,
                "request_headers": json.dumps(headers_dict),
                "exception": None,
                "request_body": self.body or {},
                "response": "",
                "details": "",
                "reason": ""
            }

            try:
                response = requests.request(self.method, url, headers=headers_dict, allow_redirects=self.max_redirects, verify=self.use_ssl, data=self.body, proxies=proxies)
                json_report["status"] = response.status_code
                json_report["response"] = response.text

                if self.debug:
                    self.log_and_print(f"[Response] Status Code: {response.status_code}, Headers: {response.headers}, Body: {response.text}", logging.DEBUG, Fore.CYAN)

                # Cache poisoning detection
                if 'Cache-Control' in response.headers and 'private' not in response.headers['Cache-Control']:
                    message = f"[Vulnerability] [Potential Web Cache Poisoning] {url}"
                    self.log_and_print(message, logging.INFO, Fore.YELLOW)
                    json_report["details"] = message

                # CORS misconfiguration detection
                if 'Access-Control-Allow-Origin' in response.headers:
                    allow_origin = response.headers.get('Access-Control-Allow-Origin')
                    if allow_origin != '*' and self.attacker.lower() not in allow_origin.lower():
                        message = f"[Vulnerability] [Potential CORS Misconfiguration] {url}"
                        self.log_and_print(message, logging.INFO, Fore.YELLOW)
                        json_report["details"] = message

                # Host header injection
                if self.attacker.lower() in response.headers or self.attacker.lower() in response.text.lower():
                    message = f"[Vulnerability] [Header: {header}] {url}"
                    self.log_and_print(message, logging.INFO, Fore.YELLOW)
                    json_report["details"] = message

                elif self.verbose:
                    message = f"[No Vulnerability] [Header: {header}] {url}"
                    self.log_and_print(message, logging.INFO, Fore.RED)

            except requests.exceptions.RequestException as e:
                json_report["state"] = "FAILED"
                json_report["exception"] = str(e)
                json_report["reason"] = "request_failed"
                json_report["details"] = str(e)
                self.log_and_print(f"[Error] {e}", logging.ERROR, Fore.MAGENTA)

            self.save_json_report(test_num, json_report)

class ScannerCLI:
    """Command line interface for running the vulnerability scanner."""

    @staticmethod
    def run():
        parser = argparse.ArgumentParser(description='Hostinject (Host Header Injection Scanner)')
        parser.add_argument('-u', '--url', help='Target URL')
        parser.add_argument('-l', '--list', help='List of target URLs')
        parser.add_argument('-w', '--wordlists', help='Wordlist file containing header values', required=True)
        parser.add_argument('-a', '--attacker', help='Attacker domain', default=DEFAULT_ATTACKER)
        parser.add_argument('-o', '--output', help='Reports directory where final test reports will be output', default=DEFAULT_REPORT_DIR)
        parser.add_argument('-r', '--redirect', type=int, default=DEFAULT_REDIRECTS, help='Maximum number of redirects')
        parser.add_argument('-rc', '--recursive', action='store_true', help='Enable recursive scanning')
        parser.add_argument('-s', '--ssl', action='store_true', default=DEFAULT_SSL, help='Enable SSL verification')
        parser.add_argument('-x', '--method', default=DEFAULT_METHOD, help='HTTP method')
        parser.add_argument('-b', '--body', help='Body request as string or file')
        parser.add_argument('-U', '--user-agent', help='User-Agent string or wordlist file')
        parser.add_argument('-p', '--proxy', help='Proxy server URL')
        parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
        parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')

        args = parser.parse_args()

        if not args.url and not args.list:
            parser.error('Provide a single URL or a list of URLs.')

        if args.url and args.list:
            parser.error('Cannot use both URL and list together.')

        if args.user_agent:
            if os.path.isfile(args.user_agent):
                with open(args.user_agent, 'r') as ua_file:
                    user_agents = ua_file.readlines()
                args.user_agent = random.choice(user_agents).strip()
            else:
                args.user_agent = args.user_agent.strip()

        urls = []
        if args.url:
            urls.append(args.url.strip())
        elif args.list:
            try:
                with open(args.list, 'r') as file:
                    urls = [line.strip() for line in file if line.strip()]
            except FileNotFoundError:
                logging.error(f"URL list file not found: {args.list}")
                return

        scanner = VulnerabilityScanner(
            attacker=args.attacker,
            output_dir=args.output,
            max_redirects=args.redirect,
            use_ssl=args.ssl,
            method=args.method,
            user_agent=args.user_agent or DEFAULT_USER_AGENT,
            verbose=args.verbose,
            body=args.body,
            proxy=args.proxy,
            debug=args.debug,
            recursive=args.recursive
        )

        for url in urls:
            scanner.detect(url, args.wordlists)


if __name__ == '__main__':
    ScannerCLI.run()
