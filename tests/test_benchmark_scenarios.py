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
import numpy as np
import pytest
from pytest import approx
from pandas.util.testing import assert_series_equal

from multi_vector_simulator.cli import main
from multi_vector_simulator.server import run_simulation
from multi_vector_simulator.B0_data_input_json import load_json

from _constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    TEST_REPO_PATH,
    BENCHMARK_TEST_INPUT_FOLDER,
    BENCHMARK_TEST_OUTPUT_FOLDER,
    CSV_EXT,
)

from multi_vector_simulator.utils.helpers import peak_demand_transformer_name

from multi_vector_simulator.utils.constants import (
    JSON_WITH_RESULTS,
    JSON_FILE_EXTENSION,
    CSV_ELEMENTS,
    TIME_SERIES,
)

from multi_vector_simulator.utils.constants_json_strings import (
    EXCESS_SINK,
    ENERGY_CONVERSION,
    ENERGY_PROVIDERS,
    ENERGY_STORAGE,
    VALUE,
    LCOE_ASSET,
    ENERGY_CONSUMPTION,
    TOTAL_FLOW,
    FLOW,
    EFFICIENCY,
    ENERGY_PRODUCTION,
    INSTALLED_CAP,
    SIMULATION_SETTINGS,
    EVALUATED_PERIOD,
    ENERGY_PRICE,
    OPTIMIZED_ADD_CAP,
    OPTIMIZE_CAP,
    INPUT_POWER,
    OUTPUT_POWER,
    STORAGE_CAPACITY,
    TIMESERIES_SOC,
)

from multi_vector_simulator.utils.data_parser import convert_epa_params_to_mvs


TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, BENCHMARK_TEST_INPUT_FOLDER)
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, BENCHMARK_TEST_OUTPUT_FOLDER)


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
        Benchmark test for simple case grid connected PV, in which a fix capacity of PV is installed (installedCap, no optimization).

        Assertions performed:
        - The sum of energy consumption from the grid and PV generation is equal to the load (and flow to excess sink) at all times (ie. energy balance)
        - The sum of the flow to the excess sink is zero for time steps where demand equals or is greater than generation. This ensures that the total PV generation is used to cover the demand.
        - The PV generation time series in the results equals the input time series of specific PV generation multiplied by installed capacity. This ensures that `installedCap` is processed correctly within the model when an asset is not optimized.

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
            sheet_name="Electricity",
        )
        # make the time the index
        df_busses_flow = df_busses_flow.set_index("Unnamed: 0")
        # compute the sum of the in and out of the electricity bus
        df_busses_flow["net_sum"] = df_busses_flow.sum(axis=1)

        # make sure the sum of the bus flow is always zero (there are rounding errors), energy balance
        assert df_busses_flow.net_sum.map(lambda x: 0 if x < 1e-4 else 1).sum() == 0

        # make sure that electricity excess is zero whenever demand >= generation (this means that total pv generation
        # is used to cover the demand)
        selected_time_steps = df_busses_flow.loc[
            df_busses_flow["demand_01"].abs() >= df_busses_flow["pv_plant_01"]
        ]
        excess = selected_time_steps[f"Electricity{EXCESS_SINK}"].sum()
        assert (
            excess == 0
        ), f"Total PV generation should be used to cover demand, i.e. electricity excess should be zero whenever demand >= generation, but excess is {excess}."

        # make sure that installedCap is processed correctly - pv time series of results
        # equal input pv time series times installedCap
        # get pv input time series and evaluated period (to shorten time series)
        input_time_series_pv = pd.read_csv(
            os.path.join(TEST_INPUT_PATH, use_case, TIME_SERIES, "pv_solar_input.csv")
        )
        simulation_settings = pd.read_csv(
            os.path.join(
                TEST_INPUT_PATH, use_case, CSV_ELEMENTS, f"{SIMULATION_SETTINGS}.csv"
            )
        ).set_index("Unnamed: 0")
        evaluated_period = float(
            simulation_settings[SIMULATION_SETTINGS][EVALUATED_PERIOD]
        )
        # shorten input pv time series according to `evaluated_period`
        input_time_series_pv_shortened = input_time_series_pv[
            : int(evaluated_period * 24)
        ]["kW"]
        # get result time series and installed pv capacity
        result_time_series_pv = df_busses_flow["pv_plant_01"]
        energy_production_data = pd.read_csv(
            os.path.join(
                TEST_INPUT_PATH, use_case, CSV_ELEMENTS, f"{ENERGY_PRODUCTION}.csv"
            )
        ).set_index("Unnamed: 0")
        installed_capacity = float(energy_production_data["pv_plant_01"][INSTALLED_CAP])
        # adapt index
        result_time_series_pv.index = input_time_series_pv_shortened.index

        assert_series_equal(
            result_time_series_pv.astype(np.float64),
            input_time_series_pv_shortened * installed_capacity,
            check_names=False,
        )

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

        data = load_json(
            os.path.join(
                TEST_OUTPUT_PATH, use_case, JSON_WITH_RESULTS + JSON_FILE_EXTENSION
            )
        )

        No_optimize_no_cap_in_out = "No_optimize_no_cap_in_out"
        No_optimize_with_cap_in_out = "No_optimize_with_cap_in_out"

        description = "description"
        implemented_storage_assets = {
            No_optimize_no_cap_in_out: {
                description: "Storage asset with a set storage capacity but no input or output power capacity, not to be optimized.",
                OPTIMIZE_CAP: False,
            },
            No_optimize_with_cap_in_out: {
                description: "Storage asset with a set storage capacity as well as set input or output power capacity, not to be optimized.",
                OPTIMIZE_CAP: False,
            },
        }

        for storage_asset in data[ENERGY_STORAGE].keys():
            # Assertions that validate that the input files have not been changed.
            assert (
                storage_asset in implemented_storage_assets
            ), f"The defined storage asset {storage_asset} is not expected. It should be one of the assets {implemented_storage_assets.keys()}. It should be {implemented_storage_assets[storage_asset][description]}"
            exp_optimize = implemented_storage_assets[storage_asset][OPTIMIZE_CAP]
            res_optimize = data[ENERGY_STORAGE][storage_asset][OPTIMIZE_CAP][VALUE]
            assert (
                res_optimize == exp_optimize
            ), f"The {OPTIMIZE_CAP} of storage asset {storage_asset} should be {exp_optimize}, but is {res_optimize}. "

            if storage_asset == No_optimize_no_cap_in_out:
                for sub_item in [INPUT_POWER, OUTPUT_POWER, STORAGE_CAPACITY]:
                    # Assertions that validate that the input files are correct
                    if sub_item == STORAGE_CAPACITY:
                        assert (
                            data[ENERGY_STORAGE][storage_asset][sub_item][
                                INSTALLED_CAP
                            ][VALUE]
                            > 0
                        ), f"For this storage asset {storage_asset} the {INSTALLED_CAP} or {sub_item} should be > 0, as {implemented_storage_assets[storage_asset][description]}"
                        # Assertion that checks if flows are as expected
                        res = data[ENERGY_STORAGE][storage_asset][sub_item][TOTAL_FLOW][
                            VALUE
                        ]
                        assert (
                            res is None
                        ), f"With no input/output power capacities, storage asset {storage_asset} should have no flow though the {sub_item}."

                    else:
                        assert (
                            data[ENERGY_STORAGE][storage_asset][sub_item][
                                INSTALLED_CAP
                            ][VALUE]
                            == 0
                        ), f"For this storage asset {storage_asset} the {INSTALLED_CAP} or {sub_item} should be == 0, as {implemented_storage_assets[storage_asset][description]}."
                        # Assertion that checks if flows are as expected
                        res = data[ENERGY_STORAGE][storage_asset][sub_item][TOTAL_FLOW][
                            VALUE
                        ]
                        assert (
                            res == 0
                        ), f"With no input/output power capacities, storage asset {storage_asset} should have 0 flow though the {sub_item}."

            if storage_asset == No_optimize_with_cap_in_out:
                for sub_item in [INPUT_POWER, OUTPUT_POWER, STORAGE_CAPACITY]:
                    # Assertions that validate that the input files are correct
                    assert (
                        data[ENERGY_STORAGE][storage_asset][sub_item][INSTALLED_CAP][
                            VALUE
                        ]
                        > 0
                    ), f"For this storage asset {storage_asset} the {INSTALLED_CAP} or {sub_item} should be > 0, as {implemented_storage_assets[storage_asset][description]}."

                    # Assertion that checks if flows are as expected
                    res = data[ENERGY_STORAGE][storage_asset][sub_item][TOTAL_FLOW][
                        VALUE
                    ]
                    if sub_item == STORAGE_CAPACITY:
                        assert (
                            res is None
                        ), f"With input/output power capacities, storage asset {storage_asset} does have a timeseries, but as the stored energy in a timestep is not a flow, it does not have a {TOTAL_FLOW}."
                    else:
                        assert (
                            res >= 0
                        ), f"With input/output power capacities, storage asset {storage_asset} can have an flow though the {sub_item}, ie. {TOTAL_FLOW} can be >=0. Its value, though, is {res}."

            assert (
                TIMESERIES_SOC in data[ENERGY_STORAGE][storage_asset]
            ), f"The {TIMESERIES_SOC} of {storage_asset} was not calculated."

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
                sheet_name="Electricity",
            )
            # compute the sum of the excess electricity for all timesteps
            excess[case] = sum(busses_flow["Electricity" + EXCESS_SINK])
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
        data = load_json(
            os.path.join(
                TEST_OUTPUT_PATH, use_case, JSON_WITH_RESULTS + JSON_FILE_EXTENSION
            ),
            flag_missing_values=False,
        )

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
        data = load_json(
            os.path.join(
                TEST_OUTPUT_PATH, use_case, JSON_WITH_RESULTS + JSON_FILE_EXTENSION
            ),
            flag_missing_values=False,
        )
        peak_demand = [
            data[ENERGY_CONVERSION][
                peak_demand_transformer_name("Electricity grid DSO", peak_number=i)
            ][OPTIMIZED_ADD_CAP][VALUE]
            for i in (1, 2, 3)
        ]
        # read timeseries_all_busses excel file
        busses_flow = pd.read_excel(
            os.path.join(TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"),
            sheet_name="Electricity",
        )
        # make the time the index
        busses_flow = busses_flow.set_index("Unnamed: 0")
        # read the columns with the values to be used
        DSO_periods = [
            busses_flow[
                peak_demand_transformer_name("Electricity grid DSO", peak_number=i)
            ]
            for i in (1, 2, 3)
        ]
        demand = busses_flow["demand_01"]
        battery_charge = busses_flow[f"battery {INPUT_POWER}"]
        battery_discharge = busses_flow[f"battery {OUTPUT_POWER}"]

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
        data = load_json(
            os.path.join(
                TEST_OUTPUT_PATH, use_case, JSON_WITH_RESULTS + JSON_FILE_EXTENSION
            ),
            flag_missing_values=False,
        )
        # read excel sheet with time series
        busses_flow = pd.read_excel(
            os.path.join(TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"),
            sheet_name="Heat",
        )
        # create dict with electricity prices
        electricity_price = data[ENERGY_PROVIDERS]["Grid_DSO"][ENERGY_PRICE][
            VALUE
        ].values
        # compare cost of using heat pump with electricity price to heat price
        cost_of_using_heatpump = "electricity_price[i] / data[ENERGY_CONVERSION]['heat_pump'][EFFICIENCY][VALUE] comp.data[ENERGY_PROVIDERS]['Heat_DSO'][ENERGY_PRICE][VALUE]"
        cost_of_using_heat_dso = (
            "data[ENERGY_PROVIDERS]['Heat_DSO'][ENERGY_PRICE][VALUE]"
        )
        for i in range(0, len(electricity_price)):
            if (
                electricity_price[i]
                / data[ENERGY_CONVERSION]["heat_pump"][EFFICIENCY][VALUE]
                > data[ENERGY_PROVIDERS]["Heat_DSO"][ENERGY_PRICE][VALUE]
            ):
                assert busses_flow[peak_demand_transformer_name("Heat_DSO")][
                    i
                ] == approx(
                    abs(busses_flow["demand_heat"][i])
                ), f"Even though the marginal costs to use the heat pump are higher than the heat DSO price with {cost_of_using_heatpump} comp. {cost_of_using_heat_dso}, the heat DSO is not solely used for energy supply."
            else:
                assert busses_flow["heat_pump"][i] == approx(
                    abs(busses_flow["demand_heat"][i])
                )

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)


# this ensure that the test is only ran if explicitly executed
# alone is called
@pytest.mark.skipif(
    EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
    reason="Benchmark test deactivated, set env variable "
    "EXECUTE_TESTS_ON to 'master' to run this test",
)
def test_benchmark_EPA_run_through():
    r"""
    Benchmark test which runs a simulation with a json file coming from EPA interface
    """

    with open(os.path.join(TEST_INPUT_PATH, "epa_benchmark.json")) as json_file:
        epa_dict = json.load(json_file)

    dict_values = convert_epa_params_to_mvs(epa_dict)

    run_simulation(dict_values)
