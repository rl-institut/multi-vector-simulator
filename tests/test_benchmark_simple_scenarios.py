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
import pandas as pd

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
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )

        df_busses_flow = pd.read_excel(
            os.path.join(TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"),
            sheet_name="Electricity bus",
        )
        # make the time the index
        df_busses_flow = df_busses_flow.set_index("Unnamed: 0")
        # compute the sum of the in and out of the electricity bus
        df_busses_flow["net_sum"] = df_busses_flow.sum(axis=1)

        # make sure the sum of the bus flow is always zero (there are rounding errors)
        assert df_busses_flow.net_sum.map(lambda x: 0 if x < 1e-4 else 1).sum() == 0

        # this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
        # alone is called
        @pytest.mark.skipif(
            "tests/{}".format(fname) not in sys.argv, reason="requires python3.3"
        )
        @mock.patch(
            "argparse.ArgumentParser.parse_args", return_value=argparse.Namespace()
        )
        def test_run_generator(self, margs):
            use_case = "AD"

            # TODO inkove the functions inside main() and modify the fuel cost from close to 0 to
            #  larger than the grid cost directly in the `dict_values` before the simulation

            # TODO alternatively one could also input a variable fuel cost (as a list) over X
            #  days to be able to observe the trend
            assert 1 == 0

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
