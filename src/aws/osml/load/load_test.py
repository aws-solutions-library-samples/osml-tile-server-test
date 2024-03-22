#  Copyright 2024 Amazon.com, Inc. or its affiliates.

import logging
import subprocess


def run_load_test(locust_run_time: str = "") -> None:
    log_run_config = f"for {locust_run_time}" if locust_run_time else "UI on http://localhost:8089"
    logging.info(f"Running Tile Server locust load test {log_run_config}")
    result = subprocess.run("locust", capture_output=True)
    locust_exit_code = result.returncode
    locust_output = f"{result.stdout.decode()}{result.stderr.decode()}"
    if locust_exit_code:
        raise RuntimeError(f"{locust_output}\n\rExit code: {locust_exit_code}.")
    else:
        logging.info(f"{locust_output}\n\rLoad test succeeded with exit code: {locust_exit_code}.")
