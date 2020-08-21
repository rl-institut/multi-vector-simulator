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
from src.C0_data_processing import bus_suffix

from .constants import (
    TEST_REPO_PATH,
    CSV_EXT,
)

from src.constants import JSON_WITH_RESULTS

from src.constants_json_strings import (
    ENERGY_CONVERSION,
    ENERGY_PROVIDERS,
    ENERGY_STORAGE,
    ENERGY_CONSUMPTION,
    VALUE,
    FLOW,
     LIFETIME_SPECIFIC_COST_OM,
     LIFETIME_PRICE_DISPATCH,
     LIFETIME_SPECIFIC_COST,
     ANNUITY_SPECIFIC_INVESTMENT_AND_OM,
     SIMULATION_ANNUITY,
     SPECIFIC_REPLACEMENT_COSTS_INSTALLED,
     SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED,
     OPTIMIZED_ADD_CAP,
     ANNUITY_OM,
     ANNUITY_TOTAL,
     COST_TOTAL,
     COST_OPERATIONAL_TOTAL,
     COST_OM,
     COST_DISPATCH,
     COST_INVESTMENT,
     COST_UPFRONT,
     COST_REPLACEMENT,
     LCOE_ASSET,
)

TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_inputs")
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_outputs")


class Test_Economic_KPI:
    def setup_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
        if os.path.exists(TEST_OUTPUT_PATH) is False:
            os.mkdir(TEST_OUTPUT_PATH)

    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_Economic_KPI_C2_E2(self, margs):
        r"""
        Notes
        -----
        With this benchmark test, we evaluate the performance of the economic pre- and post-processing in C2 and E2.
        Values that have to be compared for each asset
        - LIFETIME_SPECIFIC_COST_OM
        - LIFETIME_PRICE_DISPATCH
        - LIFETIME_SPECIFIC_COST
        - ANNUITY_SPECIFIC_INVESTMENT_AND_OM
        - SIMULATION_ANNUITY
        - SPECIFIC_REPLACEMENT_COSTS_INSTALLED
        - SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED
        - OPTIMIZED_ADD_CAP != 0, as we are not optimizing any asset
        - ANNUITY_OM
        - ANNUITY_TOTAL
        - COST_TOTAL
        - COST_OPERATIONAL_TOTAL
        - COST_OM
        - COST_DISPATCH
        - COST_INVESTMENT
        - COST_UPFRONT
        - COST_REPLACEMENT
        - LCOE_ASSET

        Overall economic values of the project:
        - NPV
        - Annuity

        """
        use_case = "Economic_KPI_C2_E2"

        """
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
        """
        expected_value_file = "test_data_economic_expected_values.csv"
        expected_values = pd.read_csv(os.path.join(TEST_INPUT_PATH, use_case, expected_value_file), sep=",")
        print(expected_values)
        # make sure grid is not used, ie. that diesel generator supplies all demand
        assets = expected_values.columns()
        groups = expected_values["group"]
        print(assets)
        print(groups)
