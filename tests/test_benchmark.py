"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""
import argparse
import os
import shutil

import mock
import pytest

from mvs_eland_tool import main
from .constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    TESTS_ON_DEV,
    TEST_REPO_PATH,
    JSON_EXT,
    CSV_EXT,
)

OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "MVS_outputs_simulation")


class TestSimulation:
    def setup_method(self):
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)

    # this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
    # alone it called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER, TESTS_ON_DEV),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_run_smoothly_json(self, mock_args):
        main(input_type=JSON_EXT, path_output_folder=OUTPUT_PATH)
        # TODO: find typical output values to write better test, currently it only test that main() run
        # TODO: without crashing, but does not test if the output make sense
        assert 1 == 1

    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_run_smoothly_csv(self, mock_args):
        main(input_type=CSV_EXT, path_output_folder=OUTPUT_PATH)
        assert 1 == 1

    def teardown_method(self):
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
