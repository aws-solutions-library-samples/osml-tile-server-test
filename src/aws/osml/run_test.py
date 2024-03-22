#  Copyright 2024 Amazon.com, Inc. or its affiliates.

import json
import logging
import os
import sys
import traceback
from argparse import ArgumentParser
from datetime import datetime, timezone
from distutils.util import strtobool
from typing import Dict, Tuple

import requests
from gevent import monkey
from integ import TestTileServer, TileServerIntegTestConfig
from load import run_load_test

# locust workaround https://github.com/gevent/gevent/issues/1016
monkey.patch_all()


def set_integ_test_config(runtime_params: Dict) -> TileServerIntegTestConfig:
    endpoint = runtime_params.get("endpoint")
    image_bucket = runtime_params.get("source_image_bucket", "")
    image_key = runtime_params.get("source_image_key", "")
    test_config = TileServerIntegTestConfig(endpoint=endpoint, s3_bucket=image_bucket, s3_key=image_key)
    return test_config


def set_load_test_env(args: Dict) -> None:
    datetime_now_string = datetime.now(timezone.utc).isoformat(timespec="seconds").replace(":", "")
    is_headless = args.get("locust_headless")
    # https://stackoverflow.com/questions/46397580/how-to-invoke-locust-tests-programmatically
    os.environ["LOCUST_LOCUSTFILE"] = "src/aws/osml/load/locust_ts_user.py"
    if is_headless:
        os.environ["LOCUST_HEADLESS"] = str(is_headless)
        os.environ["LOCUST_RUN_TIME"] = args.get("locust_run_time")
        os.environ["LOCUST_USERS"] = args.get("locust_users")
        os.environ["LOCUST_SPAWN_RATE"] = args.get("locust_spawn_rate")
    else:
        os.environ["LOCUST_CSV"] = datetime_now_string
        os.environ["LOCUST_HTML"] = datetime_now_string
    os.environ["LOCUST_HOST"] = args.get("endpoint", "")

    # custom Locus params
    os.environ["LOCUST_TEST_IMAGES_BUCKET"] = args.get("source_image_bucket", "")
    os.environ["LOCUST_TEST_IMAGE_KEYS"] = json.dumps(args.get("locust_image_keys", []))


def lambda_get_next(lambda_runtime_api: str, function_name: str) -> Tuple[Dict, Dict]:
    res = requests.get(f"http://{lambda_runtime_api}/2018-06-01/runtime/invocation/next")
    logging.debug(f"Lambda job info (header): {res.headers}")
    logging.debug(f"Lambda job parameters (json body): {res.json()}")
    if function_name in res.headers.get("Lambda-Runtime-Invoked-Function-Arn", ""):
        return res.headers, res.json()
    else:
        return {}, {}


def lambda_send_success(lambda_runtime_api: str, request_id: str) -> None:
    res = requests.post(f"http://{lambda_runtime_api}/2018-06-01/runtime/invocation/{request_id}/response", data="SUCCESS")
    logging.debug(f"lambda_send_success headers: {res.headers}, response: {res.text}")


def lambda_send_failure(lambda_runtime_api: str, request_id: str, error_info: Dict) -> None:
    res = requests.post(f"http://{lambda_runtime_api}/2018-06-01/runtime/invocation/{request_id}/error", json=error_info)
    logging.debug(f"lambda_send_failure headers: {res.headers}, response: {res.text}")


def main(cmd_args: Dict) -> None:
    exit_message: str | int = 0
    # Set logging from cmd_args
    if cmd_args.get("v"):
        logging.basicConfig(level=logging.INFO)
    if cmd_args.get("vv"):
        logging.basicConfig(level=logging.DEBUG)

    # AWS Lambda setup, if applicable
    this_lambda_name = os.getenv("AWS_LAMBDA_FUNCTION_NAME")
    lambda_runtime_api = os.getenv("AWS_LAMBDA_RUNTIME_API")
    lambda_args = {}
    lambda_request_id = None
    if lambda_runtime_api:
        lambda_headers, lambda_args = lambda_get_next(lambda_runtime_api, this_lambda_name)
        lambda_request_id = lambda_headers.get("Lambda-Runtime-Aws-Request-Id") if lambda_runtime_api else None
        logging.info(f"lambda_runtime_api: {lambda_runtime_api}, RequestId: {lambda_request_id}")

    runtime_args = cmd_args | lambda_args  # lambda args take precedent over cmd args

    logging.info(f"Executing test with runtime arguments: {runtime_args}")

    # Run test
    if "integ" in runtime_args.get("test_type", "").lower():
        integ_test_config = set_integ_test_config(runtime_args)
        server_to_test = TestTileServer(test_config=integ_test_config)
        try:
            server_to_test.run_integ_test()
            if lambda_runtime_api and lambda_request_id:
                lambda_send_success(lambda_runtime_api, lambda_request_id)
        except Exception as err:
            if lambda_runtime_api and lambda_request_id:
                error_info = {
                    "errorMessage": str(err),
                    "errorType": type(err).__name__,
                    "stackTrace": [traceback.format_exc()],
                }
                lambda_send_failure(lambda_runtime_api, lambda_request_id, error_info)
            exit_message = f"{err}"
    elif "load" in runtime_args.get("test_type", "").lower():
        set_load_test_env(runtime_args)
        try:
            run_load_test(os.environ.get("LOCUST_RUN_TIME", ""))
            if lambda_runtime_api and lambda_request_id:
                lambda_send_success(lambda_runtime_api, lambda_request_id)
        except Exception as err:
            if lambda_runtime_api and lambda_request_id:
                error_info = {
                    "errorMessage": str(err),
                    "errorType": type(err).__name__,
                    "stackTrace": [traceback.format_exc()],
                }
                lambda_send_failure(lambda_runtime_api, lambda_request_id, error_info)
            exit_message = f"{err}"
    else:
        message = f"--test_type {runtime_args.get('test_type')} not recognized. Valid options are [ 'integ' | 'load' ]."
        if lambda_runtime_api and lambda_request_id:
            error_info = {"errorMessage": message, "errorType": "ArgumentError", "stackTrace": []}
            lambda_send_failure(lambda_runtime_api, lambda_request_id, error_info)
        exit_message = message
    sys.exit(exit_message)


def list_of_strings(arg) -> list:
    return arg.split(",")


if __name__ == "__main__":
    parser = ArgumentParser("test_tile_server")
    parser.add_argument("--endpoint", help="Endpoint of the Tile Server to test", type=str)
    parser.add_argument("--test_type", help="Type of test to run against Tile Server.", choices=["integ", "load"], type=str)
    parser.add_argument("--source_image_bucket", help="Bucket containing images to use for Tile Server tests.", type=str)
    parser.add_argument("--source_image_key", help="S3 object key of the image to use for Tile Server tests.", type=str)
    parser.add_argument(
        "--locust_headless",
        help="Load Test: Disable the web interface, and start the test immediately.",
        type=lambda x: bool(strtobool(str(x))),
        default=False,
    )
    parser.add_argument("--locust_users", help="Load Test: Peak number of concurrent Locust users.", type=str, default="1")
    parser.add_argument(
        "--locust_run_time",
        help="Load Test: Stop after the specified amount of time, e.g. (300s, 20m, 3h, 1h30m, etc.)",
        type=str,
        default="5m",
    )
    parser.add_argument(
        "--locust_spawn_rate", help="Load Test: Rate to spawn users at (users per second).", type=str, default="1"
    )
    parser.add_argument(
        "--locust_image_keys",
        help="Load Test: Comma separated list of image keys to use for the load test.",
        type=list_of_strings,
        default=[],
    )

    parser.add_argument("-v", help="Increase output verbosity", action="store_true")
    parser.add_argument("-vv", help="Additional increase in output verbosity", action="store_true")
    main(vars(parser.parse_args()))
