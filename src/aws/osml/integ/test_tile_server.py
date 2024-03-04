#  Copyright 2024 Amazon.com, Inc. or its affiliates.

import logging
import traceback
from collections import Counter
from enum import Enum, auto
from time import sleep
from typing import Dict

from requests import Session

from .endpoints import (
    create_viewpoint,
    create_viewpoint_invalid,
    delete_viewpoint,
    delete_viewpoint_invalid,
    describe_viewpoint,
    get_bounds,
    get_crop,
    get_info,
    get_metadata,
    get_preview,
    get_statistics,
    get_tile,
    list_viewpoints,
    update_viewpoint,
)
from .test_config import TileServerIntegTestConfig


class AutoStringEnum(Enum):
    """
    A class used to represent an Enum where the value of the Enum member is the same as the name of the Enum member.
    """

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> str:
        """
        Function to iterate through the Enum members.

        :param: name: Name of the Enum member.
        :param: start: Initial integer to start with.
        :param: count: Number of existing members.
        :param: last_values: List of values for existing members.

        :return: The next value of the enumeration which is the same as the name.
        """
        return name


class TestResult(str, AutoStringEnum):
    """
    Provides enumeration of test result.

    :cvar PASSED: Test passed.
    :cvar FAILED: Test failed.
    """

    PASSED = auto()
    FAILED = auto()


class TestTileServer:
    def __init__(self, test_config: TileServerIntegTestConfig):
        self.config: TileServerIntegTestConfig = test_config
        self.session: Session = Session()
        self.viewpoint_id = None
        self.test_results = {}
        self.viewpoints_url = f"{self.config.endpoint}/viewpoints"

    def run_integ_test(self) -> None:
        logging.info("Running Tile Server integration test")
        self.test_create_viewpoint()
        self.test_describe_viewpoint()
        self.wait_for_viewpoint_ready()
        self.test_list_viewpoints()
        self.test_update_viewpoint()
        self.test_get_metadata()
        self.test_get_bounds()
        self.test_get_info()
        self.test_get_statistics()
        self.test_get_preview()
        self.test_get_tile()
        self.test_get_crop()
        self.test_delete_viewpoint()
        test_summary = self._pretty_print_test_results(self.test_results)
        if TestResult.FAILED in self.test_results.values():
            raise Exception(test_summary)
        logging.info(test_summary)

    def wait_for_viewpoint_ready(self) -> None:
        polling_interval_sec = 2
        timeout_sec = 300
        elapsed_wait_time = 0
        logging.info("Waiting for viewpoint status to be READY")
        status = "REQUESTED"
        while status == "REQUESTED":
            if elapsed_wait_time > timeout_sec:
                raise Exception(f"Test timed out waiting for viewpoint to be READY after {elapsed_wait_time} seconds.")
            res = self.session.get(f"{self.viewpoints_url}/{self.viewpoint_id}")
            res.raise_for_status()
            status = res.json().get("viewpoint_status")
            logging.info("...")
            sleep(polling_interval_sec)
            elapsed_wait_time += polling_interval_sec
        if status != "READY":
            raise Exception(f"Viewpoint status is {status}. Expected READY")

    def test_create_viewpoint(self) -> None:
        try:
            logging.info("Testing create invalid viewpoint")
            create_viewpoint_invalid(self.session, self.viewpoints_url, self.config.invalid_viewpoint)
            self.test_results["Create Viewpoint - Invalid"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Create Viewpoint - Invalid"] = TestResult.FAILED
        try:
            logging.info("Testing create viewpoint")
            self.viewpoint_id = create_viewpoint(self.session, self.viewpoints_url, self.config.test_viewpoint)
            self.test_results["Create Viewpoint"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Create Viewpoint"] = TestResult.FAILED

    def test_describe_viewpoint(self) -> None:
        try:
            logging.info("Testing describe viewpoint")
            describe_viewpoint(self.session, self.viewpoints_url, self.viewpoint_id)
            self.test_results["Describe Viewpoint"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Describe Viewpoint"] = TestResult.FAILED

    def test_list_viewpoints(self) -> None:
        try:
            logging.info("Testing list viewpoints")
            list_viewpoints(self.session, self.viewpoints_url)
            self.test_results["List Viewpoints"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["List Viewpoints"] = TestResult.FAILED

    def test_update_viewpoint(self) -> None:
        try:
            logging.info("Testing update viewpoint")
            update_viewpoint(self.session, self.viewpoints_url, self.viewpoint_id, self.config.valid_update_test_body)
            self.test_results["Update Viewpoint"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Update Viewpoint"] = TestResult.FAILED

    def test_get_metadata(self) -> None:
        try:
            logging.info("Testing get metadata")
            get_metadata(self.session, self.viewpoints_url, self.viewpoint_id)
            self.test_results["Get Metadata"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Get Metadata"] = TestResult.FAILED

    def test_get_bounds(self) -> None:
        try:
            logging.info("Testing get bounds")
            get_bounds(self.session, self.viewpoints_url, self.viewpoint_id)
            self.test_results["Get Bounds"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Get Bounds"] = TestResult.FAILED

    def test_get_info(self) -> None:
        try:
            logging.info("Testing get info")
            get_info(self.session, self.viewpoints_url, self.viewpoint_id)
            self.test_results["Get Info"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Get Info"] = TestResult.FAILED

    def test_get_statistics(self) -> None:
        try:
            logging.info("Testing get statistics")
            get_statistics(self.session, self.viewpoints_url, self.viewpoint_id)
            self.test_results["Get Statistics"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Get Statistics"] = TestResult.FAILED

    def test_get_preview(self) -> None:
        try:
            logging.info("Testing get preview")
            get_preview(self.session, self.viewpoints_url, self.viewpoint_id)
            self.test_results["Get Preview"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Get Preview"] = TestResult.FAILED

    def test_get_tile(self) -> None:
        try:
            logging.info("Testing get tile")
            get_tile(self.session, self.viewpoints_url, self.viewpoint_id)
            self.test_results["Get Tile"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Get Tile"] = TestResult.FAILED

    def test_get_crop(self) -> None:
        try:
            logging.info("Testing get crop")
            get_crop(self.session, self.viewpoints_url, self.viewpoint_id)
            self.test_results["Get Crop"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Get Crop"] = TestResult.FAILED

    def test_delete_viewpoint(self) -> None:
        try:
            logging.info("Testing delete viewpoint")
            delete_viewpoint(self.session, self.viewpoints_url, self.viewpoint_id)
            self.test_results["Delete Viewpoint"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Delete Viewpoint"] = TestResult.FAILED
        try:
            logging.info("Testing delete viewpoint invalid")  # viewpoint already deleted
            delete_viewpoint_invalid(self.session, self.viewpoints_url, self.viewpoint_id)
            self.test_results["Delete Viewpoint - Invalid"] = TestResult.PASSED
        except Exception as err:
            logging.info(f"\tFailed. {err}")
            logging.error(traceback.print_exception(err))
            self.test_results["Delete Viewpoint - Invalid"] = TestResult.FAILED

    @staticmethod
    def _pretty_print_test_results(test_results: Dict[str, TestResult]) -> str:
        max_key_length = max([len(k) for k in test_results.keys()])
        sorted_results = dict(sorted(test_results.items(), key=lambda x: x[0].lower()))
        test_counter = Counter(test_results.values())
        results_str = "\nTest Summary\n-------------------------------------\n"
        for k, v in sorted_results.items():
            results_str += f"{k.ljust(max_key_length + 5)}{v.value}\n"
        n_tests = len(test_results)
        passed = test_counter[TestResult.PASSED]
        failed = test_counter[TestResult.FAILED]
        success = passed / n_tests * 100
        results_str += f"    Tests: {n_tests}, Passed: {passed}, Failed: {failed}, Success: {success:.2f}%"
        return results_str
