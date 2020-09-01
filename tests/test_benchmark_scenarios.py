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

from pytest import approx
from mvs_eland.cli import main
from mvs_eland.B0_data_input_json import load_json
from mvs_eland.C0_data_processing import bus_suffix

from _constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    TEST_REPO_PATH,
    CSV_EXT,
    ENERGY_PRICE,
    OPTIMIZED_ADD_CAP,
)

from mvs_eland.utils.constants import JSON_WITH_RESULTS

from mvs_eland.utils.constants_json_strings import (
    EXCESS,
    AUTO_SINK,
    ENERGY_CONVERSION,
    ENERGY_PROVIDERS,
    VALUE,
    LCOE_ASSET,
    ENERGY_CONSUMPTION,
    FLOW,
    EFFICIENCY,
)

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
        r"""
        Benchmark test for simple case grid connected PV. Since the PV is already installed, this tests makes sure that the PV generation is totally used to supply the load and the rest in take from the grid.
        """
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
        r"""
        Benchmark test for simple case grid and battery scenario. The grid should solely be used to feed the load.
        """
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
        r"""
        Benchmark test for using a grid connected PV system with storage. In this case, the excess production should be used to charge the battery.
        """
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
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_AD_grid_diesel(self, margs):
        r"""
        Benchmark test for using a diesel generator with the electricity grid. In this benchmark test, the LCOE of the diesel generator is made less than the grid price and so it is solely used to supply the load.
        """
        use_case = "AD_grid_diesel"
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )

        # read json with results file
        data = load_json(os.path.join(TEST_OUTPUT_PATH, use_case, JSON_WITH_RESULTS))

        # make sure LCOE_diesel is less than grid price, so that below test makes sense
        assert (
            data[ENERGY_CONVERSION]["diesel_generator"][LCOE_ASSET][VALUE]
            < data[ENERGY_PROVIDERS]["DSO"]["energy_price"][VALUE]
        )

        # make sure grid is not used, ie. that diesel generator supplies all demand
        diesel_generator = data[ENERGY_CONVERSION]["diesel_generator"][FLOW]
        demand = data[ENERGY_CONSUMPTION]["demand_01"][FLOW]
        assert sum(diesel_generator) == approx(sum(demand), rel=1e-3)

    # todo: Add test for fuel consumption (kWh/l).

    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_AE_grid_battery_peak_pricing(self, margs):
        r"""
        Benchmark test for electricity grid peak demand pricing. To evaluate this, a battery is used. The battery should be charged at instances before the grid supplies peak demand. The battery is discharged when demand is higher than peak demand and charged when demand is smaller than peak demand.
        """
        use_case = "AE_grid_battery_peak_pricing"
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )
        # read json with results file
        with open(
            os.path.join(TEST_OUTPUT_PATH, use_case, JSON_WITH_RESULTS), "r"
        ) as results:
            data = json.load(results)
        peak_demand = [
            data[ENERGY_CONVERSION]["Electricity grid DSO_consumption_period_1"][
                OPTIMIZED_ADD_CAP
            ][VALUE],
            data[ENERGY_CONVERSION]["Electricity grid DSO_consumption_period_2"][
                OPTIMIZED_ADD_CAP
            ][VALUE],
            data[ENERGY_CONVERSION]["Electricity grid DSO_consumption_period_2"][
                OPTIMIZED_ADD_CAP
            ][VALUE],
        ]
        # read timeseries_all_busses excel file
        busses_flow = pd.read_excel(
            os.path.join(TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"),
            sheet_name=bus_suffix("Electricity"),
        )
        # make the time the index
        busses_flow = busses_flow.set_index("Unnamed: 0")
        # read the columns with the values to be used
        DSO_periods = [
            busses_flow["Electricity grid DSO_consumption_period_1"],
            busses_flow["Electricity grid DSO_consumption_period_2"],
            busses_flow["Electricity grid DSO_consumption_period_3"],
        ]
        demand = busses_flow["demand_01"]
        battery_charge = busses_flow["battery"]
        # todo storage_discharge calculation should be replaced by timeseries as soon as that is stored to excel or if json is accessed
        battery_discharge = (
            abs(busses_flow["demand_01"])
            - busses_flow["Electricity grid DSO_consumption_period_1"]
            - busses_flow["Electricity grid DSO_consumption_period_2"]
            - busses_flow["Electricity grid DSO_consumption_period_3"]
        )  # todo: replace this by discharge column when implemented

        # look for peak demand in period
        for j in range(0, 3):
            for i in range(0, len(DSO_periods[1])):
                # When the DSO is supplying peak demand while demand is smaller than supplied electricity.
                # Then, the battery is charged.
                if (
                    DSO_periods[j][i] == peak_demand[j]
                    and abs(demand[i]) < DSO_periods[j][i]
                ):
                    assert abs(battery_charge[i]) > 0
                # When DSO supplies peak demand and demand is larger then the peak demand,
                # Then, the battery has to be discharged
                if (
                    DSO_periods[j][i] == peak_demand[j]
                    and abs(demand[i]) > DSO_periods[j][i]
                ):
                    assert abs(battery_discharge[i]) > 0
                # If DSO supplies peak demand and the demand is larger then the supply,
                # then, in the previous timestep the battery must be charged,
                # as long as in the previous timestep the demand was smaller then the supply.
                if (
                    DSO_periods[j][i] == peak_demand[j]
                    and abs(demand[i]) > DSO_periods[j][i]
                    and DSO_periods[j][i - 1] > abs(demand[i - 1])
                ):
                    assert abs(battery_charge[i - 1]) > 0

    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_AFG_grid_heatpump_heat(self, margs):
        r"""
        Benchmark test for a sector coupled energy system, including electricity and heat demand. A heat pump is used as a sector coupling asset. Both an electricity and heat DSO are present. The electricity tariff is defined as a time series. The heat pump is only used when its cost (energy_price/efficiency) is less than the heat DSO price.
        """
        use_case = "AFG_grid_heatpump_heat"
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )
        # read json with results file
        with open(
            os.path.join(TEST_OUTPUT_PATH, use_case, "json_with_results.json"), "r"
        ) as results:
            data = json.load(results)
        # read excel sheet with time series
        busses_flow = pd.read_excel(
            os.path.join(TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"),
            sheet_name=bus_suffix("Heat"),
        )
        # create dict with electricity prices
        electricity_price = data[ENERGY_PROVIDERS]["Electricity DSO"][ENERGY_PRICE][
            VALUE
        ]["data"]
        # compare cost of using heat pump with electricity price to heat price
        cost_of_using_heatpump = "electricity_price[i] / data[ENERGY_CONVERSION]['heat_pump'][EFFICIENCY][VALUE] comp.data[ENERGY_PROVIDERS]['Heat DSO'][ENERGY_PRICE][VALUE]"
        cost_of_using_heat_dso = (
            "data[ENERGY_PROVIDERS]['Heat DSO'][ENERGY_PRICE][VALUE]"
        )
        for i in range(0, len(electricity_price)):
            if (
                electricity_price[i]
                / data[ENERGY_CONVERSION]["heat_pump"][EFFICIENCY][VALUE]
                > data[ENERGY_PROVIDERS]["Heat DSO"][ENERGY_PRICE][VALUE]
            ):
                assert busses_flow["Heat DSO_consumption_period"][i] == approx(
                    abs(busses_flow["demand_heat"][i])
                ), f"Even though the marginal costs to use the heat pump are higher than the heat DSO price with {cost_of_using_heatpump} comp. {cost_of_using_heat_dso}, the heat DSO is not solely used for energy supply."
            else:
                assert busses_flow["heat_pump"][i] == approx(
                    abs(busses_flow["demand_heat"][i])
                )

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
