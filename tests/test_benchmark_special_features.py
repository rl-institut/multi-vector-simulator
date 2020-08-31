"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""
import argparse
import os
import shutil
import json

import mock
import pandas as pd
import pytest
import random

from pytest import approx
from mvs_eland_tool import main
from src.B0_data_input_json import load_json
import src.C2_economic_functions as C2

from .constants import (
    TEST_REPO_PATH,
    CSV_EXT,
)

from src.constants import JSON_WITH_RESULTS, TIME_SERIES

from src.constants_json_strings import (
    ENERGY_PROVIDERS,
    ENERGY_PRODUCTION,
    ENERGY_CONVERSION,
    EFFICIENCY,
    VALUE,
    DSO_CONSUMPTION,
    DISPATCH_PRICE,
    ENERGY_PRICE,
)

TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_inputs")
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_outputs")


class Test_Parameter_Parsing:
    def setup_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
        if os.path.exists(TEST_OUTPUT_PATH) is False:
            os.mkdir(TEST_OUTPUT_PATH)

    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_feature_parameters_as_timeseries(self, margs):
        r"""
        Notes
        -----
        This benchmark test checks if a scalar value can be provided as a timeseries within a csv file.
        It also checks whether these timeseries can be provided within a single csv file.
        """
        use_case = "Feature_parameters_as_timeseries"

        # Execute the script
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )

        # read json with results file
        data = load_json(os.path.join(TEST_OUTPUT_PATH, use_case, JSON_WITH_RESULTS))

        # read csv with expected values of the timeseries
        csv_file = "parameter_timeseries.csv"
        csv_data = pd.read_csv(
            os.path.join(TEST_INPUT_PATH, use_case, TIME_SERIES, csv_file)
        )

        # constant variables
        diesel = "diesel_generator"
        dso = "DSO"
        diesel_efficiency = "diesel_efficiency"
        electricity_price = "electricity_price"

        for k in range(0, len(csv_data[diesel_efficiency])):
            assert data[ENERGY_CONVERSION][diesel][EFFICIENCY][VALUE][
                k
            ] == pytest.approx(csv_data[diesel_efficiency][k], rel=1e-6)
            assert data[ENERGY_PROVIDERS][dso][ENERGY_PRICE][VALUE][k] == pytest.approx(
                csv_data[electricity_price][k], rel=1e-6
            )
            assert data[ENERGY_PRODUCTION][dso + DSO_CONSUMPTION][DISPATCH_PRICE][
                VALUE
            ][k] == pytest.approx(csv_data[electricity_price][k], rel=1e-6)

    def test_benchmark_feature_input_flows_as_list(self, margs):
        r"""
        Notes
        -----
        This benchmark test checks if an energyConversion asset can have multiple input flows defined within a csv file.
        """
        use_case = "Feature_input_flows_as_list"

        # Execute the script
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )

        # read json with results file
        data = load_json(os.path.join(TEST_OUTPUT_PATH, use_case, JSON_WITH_RESULTS))

    def test_benchmark_feature_output_flows_as_list(self, margs):
        r"""
        Notes
        -----
        This benchmark test checks if an energyConversion asset can have multiple output flows defined within a csv file.
        """
        use_case = "Feature_output_flows_as_list"

        # Execute the script
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )

        # read json with results file
        data = load_json(os.path.join(TEST_OUTPUT_PATH, use_case, JSON_WITH_RESULTS))

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
