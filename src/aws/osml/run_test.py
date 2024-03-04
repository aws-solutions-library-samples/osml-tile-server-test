#  Copyright 2024 Amazon.com, Inc. or its affiliates.

# import first for locust workaround https://github.com/gevent/gevent/issues/1016
import logging
import os
import sys
import traceback
from argparse import ArgumentParser
from typing import Dict, Tuple

import requests
from gevent import monkey
from integ import TestTileServer, TileServerIntegTestConfig
from load import run_load_test

monkey.patch_all()


def set_integ_test_config(runtime_params: Dict) -> TileServerIntegTestConfig:
    endpoint = runtime_params.get("endpoint")
    image_bucket = runtime_params.get("source_image_bucket", "")
    image_key = runtime_params.get("source_image_key", "")
    test_config = TileServerIntegTestConfig(endpoint=endpoint, s3_bucket=image_bucket, s3_key=image_key)
    return test_config


def set_load_test_env(args) -> None:
    # https://stackoverflow.com/questions/46397580/how-to-invoke-locust-tests-programmatically
    os.environ["LOCUST_LOCUSTFILE"] = "locust_ts_user.py"
    os.environ["LOCUST_HEADLESS"] = str(True)
    os.environ["LOCUST_CSV"] = str(True)
    os.environ["LOCUST_HTML"] = str(True)
    os.environ["LOCUST_HOST"] = args.get("endpoint", "")
    os.environ["LOCUST_RUN_TIME"] = args.get("LOCUST_RUN_TIME", "5m")
    os.environ["LOCUST_CLIENTS"] = str(args.get("LOCUST_CLIENTS"))
    os.environ["LOCUST_HATCH_RATE"] = str(args.get("LOCUST_HATCH_RATE"))
    # custom Locus params
    os.environ["LOCUST_TEST_IMAGES_BUCKET"] = args.get("source_image_bucket", "")
    os.environ["LOCUST_TEST_IMAGES_PREFIX"] = args.get("source_image_key", "")


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
            sys.exit(0)
        except Exception as err:
            if lambda_runtime_api and lambda_request_id:
                error_info = {
                    "errorMessage": str(err),
                    "errorType": type(err).__name__,
                    "stackTrace": [traceback.format_exc()],
                }
                lambda_send_failure(lambda_runtime_api, lambda_request_id, error_info)
            sys.exit(f"{err}")
    elif "load" in runtime_args.get("test_type", "").lower():
        load_test_config = set_load_test_env(runtime_args)
        run_load_test(load_test_config)
    else:
        message = f"--test_type {runtime_args.get('test_type')} not recognized. Valid options are [ 'integ' | 'load' ]."
        if lambda_runtime_api and lambda_request_id:
            error_info = {"errorMessage": message, "errorType": "ArgumentError", "stackTrace": []}
            lambda_send_failure(lambda_runtime_api, lambda_request_id, error_info)
        sys.exit(message)


if __name__ == "__main__":
    parser = ArgumentParser("test_tile_server")
    parser.add_argument("--endpoint", help="Endpoint of the Tile Server to test", type=str, required=True)
    parser.add_argument("--test_type", help="Type of test to run against Tile Server. Options: Integ | Load", type=str)
    parser.add_argument("--source_image_bucket", help="Bucket containing images to use for Tile Server tests.", type=str)
    parser.add_argument("--source_image_key", help="S3 object key of the image to use for Tile Server tests.", type=str)
    parser.add_argument("-v", help="Increase output verbosity", action="store_true")
    parser.add_argument("-vv", help="Additional increase in output verbosity", action="store_true")
    main(vars(parser.parse_args()))
