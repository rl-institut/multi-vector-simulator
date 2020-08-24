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

from src.constants import JSON_WITH_RESULTS

from src.constants_json_strings import (
    ENERGY_CONVERSION,
    ENERGY_PROVIDERS,
    ENERGY_STORAGE,
    ENERGY_CONSUMPTION,
    INPUT_POWER,
    OUTPUT_POWER,
    STORAGE_CAPACITY,
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
    CURR,
    DISCOUNTFACTOR,
    PROJECT_DURATION,
    ANNUITY_FACTOR,
    CRF,
)

TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_inputs")
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_outputs")

dict_economic = {
    CURR: "Euro",
    DISCOUNTFACTOR: {VALUE: 0.08},
    PROJECT_DURATION: {VALUE: 20},
}

dict_economic.update(
    {
        ANNUITY_FACTOR: {
            VALUE: C2.annuity_factor(
                project_life=dict_economic[PROJECT_DURATION][VALUE],
                discount_factor=dict_economic[DISCOUNTFACTOR][VALUE],
            )
        },
        CRF: {
            VALUE: C2.crf(
                project_life=dict_economic[PROJECT_DURATION][VALUE],
                discount_factor=dict_economic[DISCOUNTFACTOR][VALUE],
            )
        },
    }
)


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

        # Read expected values from file. To edit the values, please use the .xls file first and convert the first tab to csv.
        expected_value_file = "test_data_economic_expected_values.csv"
        expected_values = pd.read_csv(
            os.path.join(TEST_INPUT_PATH, use_case, expected_value_file),
            sep=",",
            index_col=0,
        )
        # Define numbers in the csv as int/floats instead of str, but leave row "group" as a string
        groups = expected_values.loc["group"]
        expected_values = expected_values.convert_objects(convert_numeric=True)
        expected_values.loc["group"] = groups
        expected_values.loc[FLOW] = [0, 0, 0, 0, 0]

        KEYS_TO_BE_EVALUATED = [
            LIFETIME_SPECIFIC_COST_OM,
            LIFETIME_PRICE_DISPATCH,
            LIFETIME_SPECIFIC_COST,
            ANNUITY_SPECIFIC_INVESTMENT_AND_OM,
            SIMULATION_ANNUITY,
            SPECIFIC_REPLACEMENT_COSTS_INSTALLED,
            SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED,
            OPTIMIZED_ADD_CAP,
            COST_INVESTMENT,
            COST_UPFRONT,
            COST_REPLACEMENT,
            COST_OM,
            COST_DISPATCH,
            COST_OPERATIONAL_TOTAL,
            COST_TOTAL,
            ANNUITY_OM,
            ANNUITY_TOTAL,
            LCOE_ASSET,
        ]

        # Derive expected values dependent on actual dispatch of the asset(s)
        for asset in expected_values.columns:
            # determine asset dictionary (special for storages)
            if asset in [INPUT_POWER, OUTPUT_POWER, STORAGE_CAPACITY]:
                asset_data = data[expected_values[asset]["group"]]["storage_01"][asset]
            else:
                asset_data = data[expected_values[asset]["group"]][asset]
            # Get dispatch of the assets
            expected_values[asset][FLOW] = asset_data[FLOW]
            # Calculate cost parameters that are dependent on the flow
            expected_values[asset][COST_DISPATCH] = expected_values[asset][
                LIFETIME_PRICE_DISPATCH
            ] * sum(expected_values[asset][FLOW])
            expected_values[asset][COST_OPERATIONAL_TOTAL] = (
                expected_values[asset][COST_DISPATCH] + expected_values[asset][COST_OM]
            )
            expected_values[asset][COST_TOTAL] = (
                expected_values[asset][COST_OPERATIONAL_TOTAL]
                + expected_values[asset][COST_INVESTMENT]
            )
            # Process cost
            expected_values[asset][ANNUITY_OM] = (
                expected_values[asset][COST_OPERATIONAL_TOTAL]
                * dict_economic[CRF][VALUE]
            )
            expected_values[asset][ANNUITY_TOTAL] = (
                expected_values[asset][COST_TOTAL] * dict_economic[CRF][VALUE]
            )
            if sum(expected_values[asset][FLOW]) == 0:
                expected_values[asset][LCOE_ASSET] = 0
            else:
                expected_values[asset][LCOE_ASSET] = expected_values[asset][
                    ANNUITY_TOTAL
                ] / sum(expected_values[asset][FLOW])

        # Store to csv to enable manual check, eg. of LCOE_A. Only previously empty rows have been changed.
        expected_values.drop("flow").to_csv(
            os.path.join(TEST_OUTPUT_PATH, use_case, expected_value_file), sep=","
        )

        # Check if asset costs were correctly calculated in C2 and E2
        for asset in expected_values.columns:
            # determine asset dictionary (special for storages)
            if asset in [INPUT_POWER, OUTPUT_POWER, STORAGE_CAPACITY]:
                asset_data = data[expected_values[asset]["group"]]["storage_01"][asset]
            else:
                asset_data = data[expected_values[asset]["group"]][asset]
            # assertion
            for key in KEYS_TO_BE_EVALUATED:
                print(asset)
                assert expected_values[asset][key] == pytest.approx(
                    asset_data[key][VALUE], rel=1e-3
                ), f"Parameter {key} of asset {asset} is not of expected value."

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
