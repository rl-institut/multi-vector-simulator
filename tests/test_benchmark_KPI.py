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

from multi_vector_simulator.cli import main
from multi_vector_simulator.B0_data_input_json import load_json
import multi_vector_simulator.C2_economic_functions as C2

from _constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    JSON_WITH_RESULTS,
    TEST_REPO_PATH,
    CSV_EXT,
    TIME_SERIES,
)

from multi_vector_simulator.utils.constants import (
    JSON_WITH_RESULTS,
    JSON_FILE_EXTENSION,
)

from multi_vector_simulator.utils.constants_json_strings import (
    INPUT_POWER,
    OUTPUT_POWER,
    STORAGE_CAPACITY,
    VALUE,
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
    LCOeleq,
    CURR,
    DISCOUNTFACTOR,
    PROJECT_DURATION,
    ANNUITY_FACTOR,
    CRF,
    TOTAL_FLOW,
    KPI_UNCOUPLED_DICT,
    TOTAL_DEMAND,
    SUFFIX_ELECTRICITY_EQUIVALENT,
    RENEWABLE_FACTOR,
    RENEWABLE_SHARE_OF_LOCAL_GENERATION,
    TOTAL_NON_RENEWABLE_ENERGY_USE,
    TOTAL_RENEWABLE_ENERGY_USE,
    TOTAL_NON_RENEWABLE_GENERATION_IN_LES,
    TOTAL_RENEWABLE_GENERATION_IN_LES,
    ENERGY_CONSUMPTION,
    ENERGY_CONVERSION,
    ENERGY_PRODUCTION,
    ENERGY_STORAGE,
    KPI,
    KPI_SCALARS_DICT,
    FLOW,
    ATTRIBUTED_COSTS,
)

TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_inputs")
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_outputs")

DICT_ECONOMIC = {
    CURR: "Euro",
    DISCOUNTFACTOR: {VALUE: 0.08},
    PROJECT_DURATION: {VALUE: 20},
}

DICT_ECONOMIC.update(
    {
        ANNUITY_FACTOR: {
            VALUE: C2.annuity_factor(
                project_life=DICT_ECONOMIC[PROJECT_DURATION][VALUE],
                discount_factor=DICT_ECONOMIC[DISCOUNTFACTOR][VALUE],
            )
        },
        CRF: {
            VALUE: C2.crf(
                project_life=DICT_ECONOMIC[PROJECT_DURATION][VALUE],
                discount_factor=DICT_ECONOMIC[DISCOUNTFACTOR][VALUE],
            )
        },
    }
)

USE_CASE = "Economic_KPI_C2_E2"


def process_expected_values():
    """
    Processes expected values from `test_data_economic_expected_values.csv`.
    
    Derive expected values dependent on actual dispatch of the asset(s)
    for asset in expected_values.columns:


    Returns
    -------
    Save expected values to `expected_value_file`, to be used in benchmark tests
    """
    # To edit the values, please use the test_data_economic_expected_values.xls file first and convert the first tab to csv.
    expected_value_file = "test_data_economic_expected_values.csv"
    expected_values = pd.read_csv(
        os.path.join(TEST_INPUT_PATH, USE_CASE, expected_value_file),
        sep=",",
        index_col=0,
    )

    # read json with results file
    data = load_json(
        os.path.join(
            TEST_OUTPUT_PATH, USE_CASE, JSON_WITH_RESULTS + JSON_FILE_EXTENSION
        )
    )

    for asset in expected_values.index:

        # determine asset dictionary (special for storages)
        result_key = expected_values[asset]["group"]

        if asset in [INPUT_POWER, OUTPUT_POWER, STORAGE_CAPACITY]:
            asset_data = data[result_key]["storage_01"][asset]
        else:
            asset_data = data[result_key][asset]

        # get dispatch of the assets
        expected_values[asset][FLOW] = asset_data[FLOW]

        # calculate cost parameters that are dependent on the flow
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

        # process cost
        expected_values[asset][ANNUITY_OM] = (
            expected_values[asset][COST_OPERATIONAL_TOTAL] * DICT_ECONOMIC[CRF][VALUE]
        )
        expected_values[asset][ANNUITY_TOTAL] = (
            expected_values[asset][COST_TOTAL] * DICT_ECONOMIC[CRF][VALUE]
        )
        if sum(expected_values[asset][FLOW]) == 0:
            expected_values[asset][LCOE_ASSET] = 0
        else:
            expected_values[asset][LCOE_ASSET] = expected_values[asset][
                ANNUITY_TOTAL
            ] / sum(expected_values[asset][FLOW])

    # store to csv to enable manual check, eg. of lcoe_a. only previously empty rows have been changed.
    expected_values.drop("flow").to_csv(
        os.path.join(TEST_OUTPUT_PATH, USE_CASE, expected_value_file), sep=","
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

        # Execute the script
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, USE_CASE),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, USE_CASE),
        )

        # read json with results file
        data = load_json(
            os.path.join(
                TEST_OUTPUT_PATH, USE_CASE, JSON_WITH_RESULTS + JSON_FILE_EXTENSION
            )
        )

        # Read expected values from file.
        expected_value_file = "test_data_economic_expected_values.csv"
        expected_values = pd.read_csv(
            os.path.join(TEST_INPUT_PATH, USE_CASE, expected_value_file),
            sep=",",
            index_col=0,
        )

        KEYS_TO_BE_EVALUATED_PER_ASSET = [
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

        # Compare asset costs calculated in C2 and E2 with benchmark data from csv file
        for asset in expected_values.index:

            asset_group = expected_values.loc[asset, "group"]

            # determine asset dictionary (special for storages)
            if asset in [INPUT_POWER, OUTPUT_POWER, STORAGE_CAPACITY]:
                asset_data = data[asset_group]["storage_01"][asset]
            else:
                asset_data = data[asset_group][asset]
            # assertion
            for key in KEYS_TO_BE_EVALUATED_PER_ASSET:
                assert expected_values.loc[asset, key] == pytest.approx(
                    asset_data[key][VALUE], rel=1e-3
                ), f"Parameter {key} of asset {asset} is not of expected value, expected {expected_values.loc[asset, key]}, got {asset_data[key][VALUE]}."

        # Now we established that the externally calculated values are equal to the internally calculated values.
        # Therefore, we can now use the cost data from the assets to validate the cost data for the whole energy system.

        demand = pd.read_csv(
            os.path.join(TEST_INPUT_PATH, USE_CASE, TIME_SERIES, "demand.csv"), sep=",",
        )
        aggregated_demand = demand.sum()[0]

        KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM = {
            COST_INVESTMENT: 0,
            COST_UPFRONT: 0,
            COST_REPLACEMENT: 0,
            COST_OM: 0,
            COST_DISPATCH: 0,
            COST_OPERATIONAL_TOTAL: 0,
            COST_TOTAL: 0,
            ANNUITY_OM: 0,
            ANNUITY_TOTAL: 0,
        }

        def add_to_key(KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM, asset_data):
            """
            Add individual cost to each of the separate costs.

            Parameters
            ----------
            KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM: dict
                dict of keys to be evaluated for system costs, to be updated
            asset_data: dict
                Asset data with economic parameters

            Returns
            -------
            Updated KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM
            """
            for key in KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM:
                KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM.update(
                    {
                        key: KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM[key]
                        + asset_data[key][VALUE]
                    }
                )

        for asset_group in (
            ENERGY_CONSUMPTION,
            ENERGY_CONVERSION,
            ENERGY_PRODUCTION,
            ENERGY_STORAGE,
        ):
            for asset in data[asset_group]:
                # for storage we look at the annuity of the in and out flows and storage capacity
                if asset_group == ENERGY_STORAGE:
                    for storage_type in [INPUT_POWER, OUTPUT_POWER, STORAGE_CAPACITY]:
                        asset_data = data[asset_group][asset][storage_type]
                        add_to_key(KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM, asset_data)
                else:
                    asset_data = data[asset_group][asset]
                    add_to_key(KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM, asset_data)

        for key in KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM:
            assert KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM[key] == pytest.approx(
                data[KPI][KPI_SCALARS_DICT][key], rel=1e-3
            ), f"The key {key} is not of expected value {KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM[key]} but {data[KPI][KPI_SCALARS_DICT][key]}. This is based on the before established assertion, that the expected values of asset costs are equal to the ones in the json results file."

        # Compute the lcoe for this simple case from the data (single demand)
        lcoe = KEYS_TO_BE_EVALUATED_FOR_TOTAL_SYSTEM[ANNUITY_TOTAL] / aggregated_demand
        mvs_lcoe = data[KPI][KPI_SCALARS_DICT][LCOeleq]
        assert lcoe == pytest.approx(
            mvs_lcoe, rel=1e-3
        ), f"Parameter {LCOE_ASSET} of system is not of expected value (benchmark of {lcoe} versus computed value of {mvs_lcoe}."

        attributed_costs = 0
        for key in data[KPI][KPI_SCALARS_DICT]:
            if ATTRIBUTED_COSTS in key:

                attributed_costs += data[KPI][KPI_SCALARS_DICT][key]
        assert (
            attributed_costs == data[KPI][KPI_SCALARS_DICT][COST_TOTAL]
        ), f"The total attributed costs are not the costs of the total system."

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)


class TestTechnicalKPI:
    def setup_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
        if os.path.exists(TEST_OUTPUT_PATH) is False:
            os.mkdir(TEST_OUTPUT_PATH)

    # this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
    # alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def renewable_factor_and_renewable_share_of_local_generation(self, margs):
        r"""
        Benchmark test that checks the calculation of
        * TOTAL_NON_RENEWABLE_GENERATION_IN_LES
        * TOTAL_RENEWABLE_GENERATION_IN_LES
        * TOTAL_NON_RENEWABLE_ENERGY_USE
        * TOTAL_RENEWABLE_ENERGY_USE
        * RENEWABLE_FACTOR
        * RENEWABLE_SHARE_OF_LOCAL_GENERATION
        For one sector, with only grid and PV present. Uses the simple scenarios for MVS testing as an input.
        """
        use_case = "AB_grid_PV"
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )
        # Check for RENEWABLE_FACTOR and RENEWABLE_SHARE_OF_LOCAL_GENERATION:
        with open(
            os.path.join(
                TEST_OUTPUT_PATH, use_case, JSON_WITH_RESULTS + JSON_FILE_EXTENSION
            ),
            "r",
        ) as results:
            data = json.load(results)

        # Get total flow of PV
        total_res_local = data[ENERGY_PRODUCTION]["pv_plant_01"][TOTAL_FLOW][VALUE]
        # Get total demand
        total_demand = data[KPI][KPI_SCALARS_DICT][
            TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT
        ]
        assert (
            data[KPI][KPI_SCALARS_DICT][TOTAL_RENEWABLE_GENERATION_IN_LES]
            == total_res_local
        ), f"The total renewable generation is not equal to the generation of the PV system."
        assert (
            data[KPI][KPI_SCALARS_DICT][TOTAL_NON_RENEWABLE_GENERATION_IN_LES] == 0
        ), f"There is no local non-renewable generation asset, but there seems to be a non-renewable production."
        assert (
            data[KPI][KPI_SCALARS_DICT][TOTAL_RENEWABLE_ENERGY_USE] == total_res_local
        ), f"There is another renewable energy source apart from PV."
        assert (
            data[KPI][KPI_SCALARS_DICT][TOTAL_NON_RENEWABLE_ENERGY_USE]
            == total_demand - total_res_local
        ), "The non-renewable energy use was expected to be all grid supply, but this does not hold true."
        assert (
            data[KPI][KPI_SCALARS_DICT][RENEWABLE_FACTOR]
            == total_res_local / total_demand
        ), f"The {RENEWABLE_FACTOR} is not as expected."
        assert (
            data[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_FACTOR]["Electricity"]
            == total_res_local / total_demand
        ), f"The {RENEWABLE_FACTOR} is not as expected."
        assert (
            data[KPI][KPI_SCALARS_DICT][RENEWABLE_SHARE_OF_LOCAL_GENERATION] == 1
        ), f"The {RENEWABLE_SHARE_OF_LOCAL_GENERATION} is not as expected."
        assert (
            data[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_SHARE_OF_LOCAL_GENERATION][
                "Electricity"
            ]
            == 1
        ), f"The {RENEWABLE_SHARE_OF_LOCAL_GENERATION} is not as expected."

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
