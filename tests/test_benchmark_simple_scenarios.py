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

from mvs_eland_tool import main
from src.B0_data_input_json import convert_from_json_to_special_types
from src.C0_data_processing import bus_suffix

from .constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    TESTS_ON_DEV,
    TEST_REPO_PATH,
    CSV_EXT,
)

from src.constants_json_strings import EXCESS, AUTO_SINK, ENERGY_CONVERSION, ENERGY_PROVIDERS, VALUE

TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_inputs")
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_outputs")


class TestACElectricityBus:
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
    def test_benchmark_AB_grid_pv(self, margs):
        use_case = "AB_grid_PV"
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )

        df_busses_flow = pd.read_excel(
            os.path.join(TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"),
            sheet_name=bus_suffix("Electricity"),
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
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_AE_grid_battery(self, margs):
        use_case = "AE_grid_battery"
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )

        df_busses_flow = pd.read_excel(
            os.path.join(TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"),
            sheet_name=bus_suffix("Electricity"),
        )
        # make the time the index
        df_busses_flow = df_busses_flow.set_index("Unnamed: 0")
        # make sure battery is not used
        assert sum(df_busses_flow["battery"]) == 0

    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_ABE_grid_pv_bat(self, margs):
        # define the two cases needed for comparison (grid + PV) and (grid + PV + battery)
        use_case = ["AB_grid_PV", "ABE_grid_PV_battery"]
        # define an empty dictionary for excess electricity
        excess = {}
        for case in use_case:
            main(
                overwrite=True,
                display_output="warning",
                path_input_folder=os.path.join(TEST_INPUT_PATH, case),
                input_type=CSV_EXT,
                path_output_folder=os.path.join(TEST_OUTPUT_PATH, case),
            )
            busses_flow = pd.read_excel(
                os.path.join(TEST_OUTPUT_PATH, case, "timeseries_all_busses.xlsx"),
                sheet_name=bus_suffix("Electricity"),
            )
            # compute the sum of the excess electricity for all timesteps
            excess[case] = sum(
                busses_flow[bus_suffix("Electricity") + EXCESS + AUTO_SINK]
            )
        # compare the total excess electricity between the two cases
        assert excess["AB_grid_PV"] < excess["ABE_grid_PV_battery"]

        @pytest.mark.skipif(
            EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
            reason="Benchmark test deactivated, set env variable "
            "EXECUTE_TESTS_ON to 'master' to run this test",
        )
        @mock.patch(
            "argparse.ArgumentParser.parse_args", return_value=argparse.Namespace()
        )
        def test_benchmark_AD_grid_diesel(self, margs):
            # define the two cases needed for comparison (grid + PV) and (grid + PV + battery)
            use_case = "AD_grid_diesel"
            # define an empty dictionary for excess electricity
            main(
                overwrite=True,
                display_output="warning",
                path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
                input_type=CSV_EXT,
                path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
            )
            # read timeseries_all_busses excel file
            busses_flow = pd.read_excel(
                os.path.join(TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"),
                sheet_name=bus_suffix("Electricity"),
            )
            # make the time the index
            busses_flow = busses_flow.set_index("Unnamed: 0")
            # read json with results file
            with open(
                os.path.join(TEST_OUTPUT_PATH, use_case, "json_with_results.json"), "r"
            ) as results:
                data = json.load(results)
            # make sure LCOE_dieset is less than grid price
            assert (
                data[ENERGY_CONVERSION]["diesel_generator"][
                    "levelized_cost_of_energy_of_asset"
                ][VALUE]
                < data[ENERGY_PROVIDERS]["DSO"]["energy_price"][VALUE]
            )
            # make sure grid is not used
            assert sum(busses_flow["Diesel generator"]) == sum(busses_flow["demand_01"])

    # todo: Add test for fuel consumption (kWh/l).
    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
