#  Copyright 2024 Amazon.com, Inc. or its affiliates.

# import first for locust workaround https://github.com/gevent/gevent/issues/1016
from gevent import monkey
monkey.patch_all()

import logging
import sys
from argparse import ArgumentParser
from typing import Dict

from integ import TestTileServer, TileServerIntegTestConfig
from load import run_load_test


def set_integ_test_config(args) -> TileServerIntegTestConfig:
    endpoint = args.get("endpoint")
    image_bucket = args.get("source_image_bucket", "")
    image_key = args.get("source_image_key", "")
    test_config = TileServerIntegTestConfig(endpoint=endpoint, s3_bucket=image_bucket, s3_key=image_key)
    return test_config

def set_load_test_env(args) -> None:
    # https://stackoverflow.com/questions/46397580/how-to-invoke-locust-tests-programmatically
    os.environ["LOCUST_LOCUSTFILE"] = "locust_ts_user.py"
    os.environ["LOCUST_HEADLESS"] = str(True)
    os.environ["LOCUST_CSV"] = str(True)
    os.environ["LOCUST_HTML"] = str(True)
    os.environ['LOCUST_HOST'] = args.get("endpoint", "")
    os.environ['LOCUST_RUN_TIME'] = kwargs.get('LOCUST_RUN_TIME', '5m')
    os.environ['LOCUST_CLIENTS'] = str(kwargs.get('LOCUST_CLIENTS'))
    os.environ['LOCUST_HATCH_RATE'] = str(kwargs.get('LOCUST_HATCH_RATE'))
    # custom Locus params
    os.environ['LOCUST_TEST_IMAGES_BUCKET'] = args.get("source_image_bucket", "")
    os.environ['LOCUST_TEST_IMAGES_PREFIX'] = args.get("source_image_key", "")


def main(args: Dict) -> None:
    if args.get("v"):
        logging.basicConfig(level=logging.INFO)
    if args.get("vv"):
        logging.basicConfig(level=logging.DEBUG)

    if "integ" in args.get("test_type", "").lower():
        integ_test_config = set_integ_test_config(args)
        server_to_test = TestTileServer(test_config=integ_test_config)
        try:
            server_to_test.run_integ_test()
            sys.exit(0)
        except Exception as err:
            sys.exit(f"{err}")
    elif "load" in args.get("test_type", "").lower():
        load_test_config = set_load_test_env(args)
        run_load_test(load_test_config)
    else:
        sys.exit(f"--test_type {args.get('test_type', '')} not recognized.  Valid options are 'integ' and 'load'.")


if __name__ == "__main__":
    parser = ArgumentParser("test_tile_server")
    parser.add_argument("--endpoint", help="Endpoint of the Tile Server to test", type=str, required=True)
    parser.add_argument("--test_type", help="Type of test to run against Tile Server. Options: Integ | Load", type=str, default="integ")
    parser.add_argument("--source_image_bucket", help="Bucket containing images to use for Tile Server tests.", type=str)
    parser.add_argument("--source_image_key", help="S3 object key of the image to use for Tile Server tests.", type=str)
    parser.add_argument("-v", help="Increase output verbosity", action="store_true")
    parser.add_argument("-vv", help="Additional increase in output verbosity", action="store_true")
    main(vars(parser.parse_args()))
