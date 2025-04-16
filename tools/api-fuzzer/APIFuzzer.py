#!/usr/bin/env python3

import argparse
import signal
import sys
import tempfile
import traceback
from logging import _nameToLevel as levelNames

from modules.util.config import EnvConfig, HeaderBuilder
from modules.fuzzer.fuzz_utils import FailedToParseFileException
from modules.fuzzer.fuzzer import Fuzzer
from modules.fuzzer.utils import json_data, str2bool
from modules.fuzzer.version import get_version
from modules.util.loggable import Loggable as log

if __name__ == '__main__':

    def signal_handler(sig, frame):
        sys.exit(0)

    parser = argparse.ArgumentParser(description='api-fuzzer configuration')
    parser.add_argument('-s', '--src_file',
                        type=str,
                        required=False,
                        help='API definition file path. JSON and YAML format is supported',
                        dest='src_file')
    parser.add_argument('--src_url',
                        type=str,
                        required=False,
                        help='API definition url. JSON and YAML format is supported',
                        dest='src_url')
    parser.add_argument('-r', '--report_dir',
                        type=str,
                        required=False,
                        help='Directory where error export will be saved. Default is temporally generated directory',
                        dest='report_dir',
                        default=tempfile.mkdtemp())
    parser.add_argument('--level',
                        type=int,
                        required=False,
                        help='Test deepness: [1,2], higher is the deeper !!!Not implemented!!!',
                        dest='level',
                        default=1)
    parser.add_argument('-u', '--url',
                        type=str,
                        required=False,
                        help='Use CLI defined url instead compile the url from the API definition. Useful for testing',
                        dest='alternate_url',
                        default=None)
    parser.add_argument('-t', '--test_report',
                        type=str,
                        required=False,
                        help='JUnit test result xml save path ',
                        dest='test_result_dst',
                        default=None)
    parser.add_argument('--log',
                        type=str,
                        required=False,
                        help='Use different log level than the default WARNING',
                        dest='log_level',
                        default='warning',
                        choices=[level.lower() for level in levelNames if isinstance(level, str)])
    parser.add_argument('--basic_output',
                        type=str2bool,
                        required=False,
                        help='Use basic output for logging (useful if running in jenkins). Example --basic_output=True',
                        dest='basic_output',
                        default=False)
    parser.add_argument('--headers',
                        type=json_data,
                        required=False,
                        help='Http request headers added to all request. Example: \'[{"Authorization": "SuperSecret"}, '
                             '{"Auth2": "asd"}]\'',
                        dest='headers',
                        default=None)
    parser.add_argument('-v', '--version',
                        action='version',
                        version=get_version())
    args = parser.parse_args()
    if args.src_file is None and args.src_url is None:
        argparse.ArgumentTypeError('No API definition source provided -s, --src_file or --src_url should be defined')
        exit()

    headers = {}
    if args.headers is not None:
        log.info("Using headers from command line")
        headers = args.headers
    else:
        log.info("Using Environment Variables")
        headers = HeaderBuilder(token=EnvConfig().token, account_id=EnvConfig().account_id,
                                referrer="https://nexus.armorlabs.co/")
    log.debug(f"Headers: {headers.sanitize_json()}")

    prog = Fuzzer(report_dir=args.report_dir,
                  test_level=args.level,
                  alternate_url=args.alternate_url,
                  test_result_dst=args.test_result_dst,
                  log_level=args.log_level,
                  basic_output=args.basic_output,
                  auth_headers=headers.to_dict(),
                  api_definition_url=args.src_url,
                  api_definition_file=args.src_file,
                  junit_report_path=args.test_result_dst
                  )
    try:
        prog.prepare()
    except FailedToParseFileException:
        print('Failed to parse API definition')
        exit(1)
    except Exception as e:
        print(f'Unexpected exception happened during fuzz test preparation: {traceback.print_stack(*sys.exc_info())}.\n'
              f' Feel free to export the issue',)
        exit(1)
    signal.signal(signal.SIGINT, signal_handler)
    prog.run()


