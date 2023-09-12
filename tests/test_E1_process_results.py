import pandas as pd
from pandas.util.testing import assert_series_equal

import os
import numpy as np
import logging
import shutil
import mock
from oemof import solph
import pickle

import multi_vector_simulator.A0_initialization as A0
import multi_vector_simulator.A1_csv_to_json as A1
import multi_vector_simulator.B0_data_input_json as B0
import multi_vector_simulator.C0_data_processing as C0
import multi_vector_simulator.D0_modelling_and_optimization as D0
import multi_vector_simulator.E1_process_results as E1

from multi_vector_simulator.utils.constants import OUTPUT_FOLDER, CSV_EXT

from multi_vector_simulator.utils.constants_json_strings import *

from _constants import (
    TEST_REPO_PATH,
    INPUT_FOLDER,
    PATH_INPUT_FILE,
    PATH_INPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
    TEST_INPUT_DIRECTORY,
    CSV_ELEMENTS,
)

PARSER = A0.mvs_arg_parser()
TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, TEST_INPUT_DIRECTORY, "inputs_for_E1")
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, OUTPUT_FOLDER)
BUS_DATA_DUMP = os.path.join(TEST_REPO_PATH, "bus_data_E1.p")

# Note: test functions might be summed up in classes..


class TestGetTimeseriesPerBus:
    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            [
                "-f",
                "-log",
                "warning",
                "-i",
                TEST_INPUT_PATH,
                "-o",
                TEST_OUTPUT_PATH,
                "-ext",
                CSV_EXT,
            ]
        ),
    )
    def setup_class(m_args):
        """Run the simulation up to module E0 and prepare bus_data for E1"""
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)

        logging.debug("Accessing script: A0_initialization")
        user_input = A0.process_user_arguments()

        A1.create_input_json(
            input_directory=os.path.join(user_input[PATH_INPUT_FOLDER], CSV_ELEMENTS)
        )

        logging.debug("Accessing script: B0_data_input_json")
        dict_values = B0.load_json(
            user_input[PATH_INPUT_FILE],
            path_input_folder=user_input[PATH_INPUT_FOLDER],
            path_output_folder=user_input[PATH_OUTPUT_FOLDER],
            move_copy=True,
            set_default_values=True,
        )
        logging.debug("Accessing script: C0_data_processing")
        C0.all(dict_values)

        logging.debug("Accessing script: D0_modelling_and_optimization")
        results_meta, results_main = D0.run_oemof(dict_values)

        bus_data = {}
        # Store all information related to busses in bus_data
        for bus in dict_values[ENERGY_BUSSES]:
            # Read all energy flows from busses
            bus_data.update({bus: solph.views.node(results_main, bus)})

        # Pickle dump bus data
        with open(BUS_DATA_DUMP, "wb") as handle:
            pickle.dump(bus_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def test_get_timeseries_per_bus_two_timeseries_for_directly_connected_storage(self):
        """A storage directly connected to a bus should have time series for input and output power."""
        with open(BUS_DATA_DUMP, "rb") as handle:
            bus_data = pickle.load(handle)
        # (('transformer_station_in', 'Electricity_bus'), 'flow')
        dict_values = {
            SIMULATION_SETTINGS: {
                TIME_INDEX: pd.date_range("2020-01-01", freq="H", periods=3)
            }
        }
        E1.get_timeseries_per_bus(dict_values=dict_values, bus_data=bus_data)
        # check updated dict_values
        df = dict_values[OPTIMIZED_FLOWS]["Electricity"]
        cols = [f"battery {i}" for i in [INPUT_POWER, OUTPUT_POWER]]
        assert {cols[0], cols[1]}.issubset(
            df.columns
        ), f"`E1.get_timeseries_per_bus()` should add input and output power time series of storage to `dict_values` also if it is connected directly to a bus."

    def test_get_timeseries_per_bus_one_bus(self):
        pass
        # check updated dict_values

    def test_get_timeseries_per_bus_three_busses(self):
        pass

    def teardown_class(self):
        # Remove the output folder
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
        # Remove pickle dump
        if os.path.exists(BUS_DATA_DUMP):
            os.remove(BUS_DATA_DUMP)


def test_get_storage_results_optimize():
    pass
    # check dict_asset updated. updated are for all functions:
    # charging_power (see add_info_flow,),
    #  discharging_power (see add_info_flow,),
    #  capacity, (see add_info_flow),
    # timeseries_soc

    # additionally only optimize is true. (false: 0 is added as optimizedAddCap)
    #  optimizedAddCap of charging_power, discharging_power and capacity


def test_get_storage_results_no_optimization():
    pass
    # NOTE: optimizedAddCap = 0 for no optimization


def test_get_storage_results_optimizeCap_not_in_dict_asset():
    pass
    # optimizedAddCap not added to dict_asset


def test_get_results_only_input_bus_single():
    pass


def test_get_results_only_output_bus_single():
    pass


def test_get_results_input_and_output_bus_single():
    pass


def test_get_results_multiple_input_busses():
    pass


def test_get_results_multiple_output_busses():
    pass
    # check if dict_asset is updated. see add_info_flows for keys
    # check optimal capacity


def test_get_parameter_to_be_evaluated_from_oemof_results():
    for asset_group in E1.ASSET_GROUPS_DEFINED_BY_INFLUX:
        param = E1.get_parameter_to_be_evaluated_from_oemof_results(
            asset_group, asset_label="a_label"
        )
        assert param == INFLOW_DIRECTION
    for asset_group in E1.ASSET_GROUPS_DEFINED_BY_OUTFLUX:
        param = E1.get_parameter_to_be_evaluated_from_oemof_results(
            asset_group, asset_label="a_label"
        )
        assert param == OUTFLOW_DIRECTION


def test_get_tuple_for_oemof_results():
    asset_label = "a_label"
    bus = "a_bus"
    for asset_group in E1.ASSET_GROUPS_DEFINED_BY_INFLUX:
        flux_tuple = E1.get_tuple_for_oemof_results(asset_label, asset_group, bus)
        assert flux_tuple == (bus, asset_label)
    for asset_group in E1.ASSET_GROUPS_DEFINED_BY_OUTFLUX:
        flux_tuple = E1.get_tuple_for_oemof_results(asset_label, asset_group, bus)
        assert flux_tuple == (asset_label, bus)


def test_cut_below_micro_scalar_value_below_0_larger_threshold(caplog):
    value = -1
    with caplog.at_level(logging.WARNING):
        result = E1.cut_below_micro(value=value, label="label")
    assert (
        "This is so far below 0, that the value is not changed" in caplog.text
    ), f"The value {value} is below 0 and larger then the threshold, but no warning is displayed that this value may be invalid."
    assert (
        result == value
    ), f"As value {value} is below 0 but larger then the threshold, its value should not be changed (but it is {result})."


def test_cut_below_micro_scalar_value_below_0_smaller_threshold(caplog):
    value = -0.5 * E1.THRESHOLD
    with caplog.at_level(logging.DEBUG):
        result = E1.cut_below_micro(value=value, label="label")
    assert (
        "Negative value (s)" in caplog.text
    ), f"The value {value} is below 0 and below the threshold, but the log does not register a debug message for this."
    assert (
        result == 0
    ), f"As value {value} is below 0 but smaller then the threshold, its value should be changed to zero (but it is {result})."


def test_cut_below_micro_scalar_value_0():
    value = 0
    result = E1.cut_below_micro(value=value, label="label")
    assert (
        result == value
    ), f"The value {value} is 0 and should not be changed (but it is {result})."


def test_cut_below_micro_scalar_value_larger_0():
    value = 1
    result = E1.cut_below_micro(value=value, label="label")
    assert (
        result == value
    ), f"The value {value} is larger 0 by more than the threshold and therefore should not be changed (but it is {result})."


def test_cut_below_micro_scalar_value_larger_0_smaller_threshold(caplog):
    value = 0.5 * E1.THRESHOLD
    with caplog.at_level(logging.DEBUG):
        result = E1.cut_below_micro(value=value, label="label")
    assert (
        "The positive value" in caplog.text
    ), f"The value {value} is larger 0 but below the threshold and should raise a debug message."

    assert (
        result == 0
    ), f"As value {value} positive but smaller then the threshold, its value should be changed to zero (but it is {result})."


def test_cut_below_micro_pd_Series_below_0_larger_threshold(caplog):
    value = pd.Series([0, -0.5 * E1.THRESHOLD, -1, 0])
    with caplog.at_level(logging.WARNING):
        result = E1.cut_below_micro(value=value, label="label")
    assert (
        "This is so far below 0, that the value is not changed" in caplog.text
    ), f"One value in pd.Series is below 0 and larger then the threshold, but no warning is displayed that this value may be invalid."
    assert (
        result == value
    ).all(), f"As value {value} is below 0 but larger then the threshold, its value should not be changed (but it is {result})."


def test_cut_below_micro_pd_Series_below_0_smaller_threshold(caplog):
    value = pd.Series([0, -0.5 * E1.THRESHOLD, 0, 1])
    exp = pd.Series([0, 0, 0, 1])
    with caplog.at_level(logging.DEBUG):
        result = E1.cut_below_micro(value=value, label="label")
    assert (
        "Negative value (s)" in caplog.text
    ), f"One value in pd.Series is below 0 and below the threshold, but the log does not register a debug message for this."
    assert (
        result[1] == 0
    ), f"As value {value[1]} is below 0 but smaller then the threshold, its value should be changed to zero (but it is {result[1]})."
    assert (
        result == exp
    ).all(), f"One value in pd.Series is below 0 but smaller then the threshold, its value should be changed to zero (but it is {result})."


def test_cut_below_micro_pd_Series_0():
    value = pd.Series([0, 0, 0, 1])
    result = E1.cut_below_micro(value=value, label="label")
    assert (
        result == value
    ).all(), (
        f"One value in pd.Series is 0 and should not be changed (but it is {result})."
    )


def test_cut_below_micro_pd_Series_larger_0():
    value = pd.Series([1, 2, 3, 4])
    result = E1.cut_below_micro(value=value, label="label")
    assert (
        result == value
    ).all(), f"All values in pd.Series are larger 0 by more than the threshold and therefore should not be changed (but it is {result})."


def test_cut_below_micro_pd_Series_larger_0_smaller_threshold(caplog):
    value = pd.Series([0, 0.5 * E1.THRESHOLD, 0, 1])
    exp = pd.Series([0, 0, 0, 1])
    with caplog.at_level(logging.DEBUG):
        result = E1.cut_below_micro(value=value, label="label")
    assert (
        " positive values smaller then the threshold" in caplog.text
    ), f"One value in pd.Series is above 0 and below the threshold, but the log does not register a debug message for this."
    assert (
        result[1] == 0
    ), f"As value {value[1]} is below 0 but smaller then the threshold, its value should be changed to zero (but it is {result[1]})."
    assert (
        result == exp
    ).all(), f"One value in pd.Series is below 0 but smaller then the threshold, its value should be changed to zero (but it is {result})."


def test_add_info_flows_storage_capacity():
    dict_test = {}
    flow = pd.Series(
        [0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2]
    )
    E1.add_info_flows(
        evaluated_period=1, dict_asset=dict_test, flow=flow, type=STORAGE_CAPACITY
    )
    for parameter in [FLOW, TOTAL_FLOW, ANNUAL_TOTAL_FLOW, PEAK_FLOW, AVERAGE_FLOW]:
        assert (
            parameter in dict_test
        ), f"Parameter {parameter} should have been added to the dict_asset."
        if parameter == FLOW:
            assert_series_equal(
                dict_test[FLOW].astype(np.int64), flow, check_names=False,
            )
        else:
            assert (
                UNIT in dict_test[parameter]
            ), f"Parameter {parameter} should have been added to the dict_asset with an {VALUE}."
            assert (
                VALUE in dict_test[parameter]
            ), f"Parameter {parameter} should have been added to the dict_asset with an {VALUE}."
            assert (
                dict_test[parameter][VALUE] is None
            ), f"For {STORAGE_CAPACITY}, the parameter {parameter} should have 'None' as value. It is {dict_test[parameter][VALUE]}."
            assert (
                dict_test[parameter][UNIT] == "NaN"
            ), f"For {STORAGE_CAPACITY}, the parameter {parameter} should have 'NaN'  as unit. It is {dict_test[parameter][UNIT]}."


def test_add_info_flows_1_day():
    dict_test = {}
    flow = pd.Series(
        [0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2]
    )
    E1.add_info_flows(evaluated_period=1, dict_asset=dict_test, flow=flow)
    for parameter in [FLOW, TOTAL_FLOW, ANNUAL_TOTAL_FLOW, PEAK_FLOW, AVERAGE_FLOW]:
        assert (
            parameter in dict_test
        ), f"Parameter {parameter} should have been added to the dict_asset."
        if parameter != FLOW:
            assert (
                UNIT in dict_test[parameter]
            ), f"Parameter {parameter} should have been added to the dict_asset with an {VALUE}."
            assert (
                VALUE in dict_test[parameter]
            ), f"Parameter {parameter} should have been added to the dict_asset with an {VALUE}."

    assert_series_equal(
        dict_test[FLOW].astype(np.int64), flow, check_names=False,
    )
    assert dict_test[TOTAL_FLOW][VALUE] == sum(
        flow
    ), f"The {TOTAL_FLOW} should be {sum(flow)}, but is {dict_test[TOTAL_FLOW][VALUE]}"
    assert (
        dict_test[ANNUAL_TOTAL_FLOW][VALUE] == sum(flow) * 365
    ), f"The {ANNUAL_TOTAL_FLOW} should be {sum(flow)*365}, but is {dict_test[ANNUAL_TOTAL_FLOW][VALUE]}"
    assert dict_test[PEAK_FLOW][VALUE] == max(
        flow
    ), f"The {PEAK_FLOW} should be {max(flow)}, but is {dict_test[PEAK_FLOW][VALUE]}"
    assert (
        dict_test[AVERAGE_FLOW][VALUE] == flow.mean()
    ), f"The {AVERAGE_FLOW} should be {flow.mean()}, but is {dict_test[AVERAGE_FLOW][VALUE]}"


def test_add_info_flows_365_days():
    dict_test = {}
    flow = pd.Series(
        [0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2]
    )
    E1.add_info_flows(evaluated_period=365, dict_asset=dict_test, flow=flow)
    for parameter in [FLOW, TOTAL_FLOW, ANNUAL_TOTAL_FLOW, PEAK_FLOW, AVERAGE_FLOW]:
        assert (
            parameter in dict_test
        ), f"Parameter {parameter} should have been added to the dict_asset."
        if parameter != FLOW:
            assert (
                UNIT in dict_test[parameter]
            ), f"Parameter {parameter} should have been added to the dict_asset with an {VALUE}."
            assert (
                VALUE in dict_test[parameter]
            ), f"Parameter {parameter} should have been added to the dict_asset with an {VALUE}."

    assert_series_equal(
        dict_test[FLOW].astype(np.int64), flow, check_names=False,
    )
    assert dict_test[TOTAL_FLOW][VALUE] == sum(
        flow
    ), f"The {TOTAL_FLOW} should be {sum(flow)}, but is {dict_test[TOTAL_FLOW][VALUE]}"
    assert dict_test[ANNUAL_TOTAL_FLOW][VALUE] == sum(
        flow
    ), f"The {ANNUAL_TOTAL_FLOW} should be {sum(flow)}, but is {dict_test[ANNUAL_TOTAL_FLOW][VALUE]}"
    assert dict_test[PEAK_FLOW][VALUE] == max(
        flow
    ), f"The {PEAK_FLOW} should be {max(flow)}, but is {dict_test[PEAK_FLOW][VALUE]}"
    assert (
        dict_test[AVERAGE_FLOW][VALUE] == flow.mean()
    ), f"The {AVERAGE_FLOW} should be {flow.mean()}, but is {dict_test[AVERAGE_FLOW][VALUE]}"


def test_get_state_of_charge_info():
    flow = pd.Series([0, 2, 0, 2, 0, 2])
    dict_test = {
        STORAGE_CAPACITY: {
            FLOW: flow,
            INSTALLED_CAP: {VALUE: 1},
            OPTIMIZED_ADD_CAP: {VALUE: 1},
        }
    }
    E1.get_state_of_charge_info(dict_test)
    assert (
        TIMESERIES_SOC in dict_test
    ), f"Parameter {TIMESERIES_SOC} should be added to the dict."
    exp_timeseries_soc = pd.Series([0, 1, 0, 1, 0, 1])
    assert_series_equal(
        dict_test[TIMESERIES_SOC].astype(np.int64),
        exp_timeseries_soc,
        check_names=False,
    )
    assert (
        AVERAGE_SOC in dict_test
    ), f"Parameter {AVERAGE_SOC} should be added to the dict."
    assert (
        VALUE in dict_test[AVERAGE_SOC]
    ), f"Parameter {AVERAGE_SOC} should be added to the dict with a {VALUE}."
    assert (
        UNIT in dict_test[AVERAGE_SOC]
    ), f"Parameter {AVERAGE_SOC} should be added to the dict with a {UNIT}."
    assert (
        dict_test[AVERAGE_SOC][VALUE] == 0.5
    ), f"Parameter {AVERAGE_SOC} should have {VALUE} 0.5 but has {dict_test[AVERAGE_SOC][VALUE] }."
    assert (
        dict_test[AVERAGE_SOC][UNIT] == "factor"
    ), f"Parameter {AVERAGE_SOC} should have {UNIT} 'factor' but has {dict_test[AVERAGE_SOC][UNIT]}"


def test_convert_components_to_dataframe():
    pv = "PV"
    diesel = "diesel"
    storage = "storage"
    generator = "genset"
    dict_components = {
        # 2 examples energy production assets, as this does not seem to work currently
        ENERGY_PRODUCTION: {
            pv: {
                OEMOF_ASSET_TYPE: OEMOF_SOURCE,
                ENERGY_VECTOR: "vector",
                UNIT: UNIT,
                INSTALLED_CAP: {VALUE: 1},
                OPTIMIZE_CAP: {VALUE: True},
            },
            diesel: {
                OEMOF_ASSET_TYPE: OEMOF_SOURCE,
                ENERGY_VECTOR: "vector",
                UNIT: UNIT,
                INSTALLED_CAP: {VALUE: 1},
                OPTIMIZE_CAP: {VALUE: True},
            },
        },
        # Example for energy conversion asset, not optimized
        ENERGY_CONVERSION: {
            generator: {
                OEMOF_ASSET_TYPE: OEMOF_TRANSFORMER,
                ENERGY_VECTOR: "vector",
                UNIT: UNIT,
                INSTALLED_CAP: {VALUE: 1},
                OPTIMIZE_CAP: {VALUE: False},
            }
        },
        # Example for energy storage asset
        ENERGY_STORAGE: {
            storage: {
                OPTIMIZE_CAP: {VALUE: True},
                OEMOF_ASSET_TYPE: OEMOF_GEN_STORAGE,
                ENERGY_VECTOR: "vector",
                INPUT_POWER: {
                    LABEL: storage + INPUT_POWER,
                    INSTALLED_CAP: {VALUE: 1, UNIT: UNIT},
                },
                OUTPUT_POWER: {
                    LABEL: storage + OUTPUT_POWER,
                    INSTALLED_CAP: {VALUE: 1, UNIT: UNIT},
                },
                STORAGE_CAPACITY: {
                    LABEL: storage + STORAGE_CAPACITY,
                    INSTALLED_CAP: {VALUE: 1, UNIT: UNIT},
                },
            }
        },
    }

    df_comp = E1.convert_components_to_dataframe(dict_components)

    for parameter in [
        "Type of Component",
        "Energy Vector",
        UNIT,
        "Installed Capacity",
        "Capacity optimization",
    ]:
        assert (
            parameter in df_comp.columns
        ), f"Parameter {parameter} has not been added as a column to the table to be printed in the autoreport."

    for component in [
        pv,
        diesel,
        generator,
        storage + INPUT_POWER,
        storage + OUTPUT_POWER,
        storage + STORAGE_CAPACITY,
    ]:
        assert (
            component in df_comp["Component"].values
        ), f"Asset {component} is not included in the table to be printed in the autoreport."

    for row in range(0, len(df_comp)):
        if df_comp.iloc[row, df_comp.columns.get_loc("Component")] == generator:
            assert (
                df_comp.iloc[row, df_comp.columns.get_loc("Capacity optimization")]
                == "No"
            ), f"The {generator} is not being capacity optimized, so `Capacity optimization` should be `No`, which is not the case."
        else:
            assert (
                df_comp.iloc[row, df_comp.columns.get_loc("Capacity optimization")]
                == "Yes"
            ), f"The {df_comp.iloc[row,df_comp.columns.get_loc('Component')]} is being capacity optimized, so `Capacity optimization` should be `Yes`, which is not the case."


def test_translate_optimizeCap_from_boolean_to_yes_no():
    # Not optimized:
    optimize = E1.translate_optimizeCap_from_boolean_to_yes_no(False)
    assert (
        optimize == "No"
    ), f"Without optimization, `no` should be returned but it is not."
    optimize = E1.translate_optimizeCap_from_boolean_to_yes_no(True)
    assert (
        optimize == "Yes"
    ), f"Without optimization, `yes` should be returned but it is not."


"""
def test_get_optimal_cap_optimize_input_flow_timeseries_peak_provided():
    pass


def test_get_optimal_cap_optimize_input_flow_timeseries_peak_not_provided():
    pass


def test_get_optimal_cap_optimize_output_flow():
    pass
    # check dict_asset updated with optimizedAddCap


def test_get_optimal_cap_optimize_invalid_direction_raises_value_error():
    pass


def test_get_optimal_cap_optimize_negative_time_series_peak_logging_warning():
    pass


def test_get_optimal_cap_optimize_time_series_peak_is_zero_logging_warning():
    pass


def test_get_opitmal_cap_no_optimization():
    pass
    # check dict_asset updated with optimizedAddCap = 0


def test_get_optimal_cap_optimizeCap_not_in_dict_asset():
    pass
    # check that dict_asset did not change
"""
