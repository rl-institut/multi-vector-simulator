"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""
import os
import sys
import argparse
import shutil
import mock
import pytest

from .constants import TEST_REPO_PATH, JSON_EXT, CSV_EXT
from mvs_eland_tool.mvs_eland_tool import main

TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_inputs")
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_outputs")
fname = os.path.basename(__file__)


class TestACElectricityBus:
    def setup_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
            os.mkdir(TEST_OUTPUT_PATH)

    # this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
    # alone is called
    @pytest.mark.skipif(
        "tests/{}".format(fname) not in sys.argv, reason="requires python3.3"
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_run_smoothly_json(self, margs):
        use_case = "AB"
        main(
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=JSON_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )
        assert 1 == 1

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
