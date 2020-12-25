import logging
import pandas as pd
import numpy as np
import multi_vector_simulator.E4_verification as E4

from multi_vector_simulator.utils.constants_json_strings import (
    CONSTRAINTS,
    MINIMAL_RENEWABLE_FACTOR,
    VALUE,
    KPI,
    KPI_SCALARS_DICT,
    RENEWABLE_FACTOR,
    MAXIMUM_EMISSIONS,
    TOTAL_EMISSIONS,
    ENERGY_STORAGE,
    TIMESERIES_SOC,
)

from multi_vector_simulator.utils.constants import DATA_TYPE_JSON_KEY


def test_minimal_renewable_share_test_passes():
    # No minimal renewable factor
    dict_values = {CONSTRAINTS: {MINIMAL_RENEWABLE_FACTOR: {VALUE: 0}}}
    return_value = E4.minimal_renewable_share_test(dict_values)
    assert (
        return_value == None
    ), f"When no minimal renewable factor is set, this test should not fail."
    # Min res < res
    dict_values = {
        CONSTRAINTS: {MINIMAL_RENEWABLE_FACTOR: {VALUE: 0.2}},
        KPI: {KPI_SCALARS_DICT: {RENEWABLE_FACTOR: 0.3}},
    }
    return_value = E4.minimal_renewable_share_test(dict_values)
    assert (
        return_value == None
    ), f"When minimal renewable factor < res, this test should not fail."
    # Min res < res, minimal deviation
    dict_values = {
        CONSTRAINTS: {MINIMAL_RENEWABLE_FACTOR: {VALUE: 0.2}},
        KPI: {KPI_SCALARS_DICT: {RENEWABLE_FACTOR: 0.2 - 10 ** (-7)}},
    }
    return_value = E4.minimal_renewable_share_test(dict_values)
    assert (
        return_value == None
    ), f"When minimal renewable factor is missed by < e6, this test should not fail."


def test_minimal_renewable_share_test_fails():
    dict_values = {
        CONSTRAINTS: {MINIMAL_RENEWABLE_FACTOR: {VALUE: 0.2}},
        KPI: {KPI_SCALARS_DICT: {RENEWABLE_FACTOR: 0.2 - 10 ** (-5)}},
    }
    return_value = E4.minimal_renewable_share_test(dict_values)
    assert (
        return_value is False
    ), f"When the minimal renewable share constraint is not met (allowed deviation: < e6), this test should fail."


def test_maximum_emissions_test_passes():
    # No maximum emissions constraint
    dict_values = {CONSTRAINTS: {MAXIMUM_EMISSIONS: {VALUE: None}}}
    return_value = E4.maximum_emissions_test(dict_values)
    assert (
        return_value == None
    ), f"When no maximum emissions constraint is set, this test should not fail."
    # Total emissions < maximum emissions constraint
    dict_values = {
        CONSTRAINTS: {MAXIMUM_EMISSIONS: {VALUE: 1000}},
        KPI: {KPI_SCALARS_DICT: {TOTAL_EMISSIONS: 999}},
    }
    return_value = E4.maximum_emissions_test(dict_values)
    assert (
        return_value == None
    ), f"When the maximum emissions constraint is met, this test should not fail."
    # Total emissions > maximum emissions constraint, minimal diff
    dict_values = {
        CONSTRAINTS: {MAXIMUM_EMISSIONS: {VALUE: 1000}},
        KPI: {KPI_SCALARS_DICT: {TOTAL_EMISSIONS: 1000 + 10 ** (-6)}},
    }
    return_value = E4.maximum_emissions_test(dict_values)
    assert (
        return_value == None
    ), f"At a minimal exceeding of the maximum emission constraint of < e6, this test should not fail."


def test_maximum_emissions_test_fails():
    dict_values = {
        CONSTRAINTS: {MAXIMUM_EMISSIONS: {VALUE: 1000}},
        KPI: {KPI_SCALARS_DICT: {TOTAL_EMISSIONS: 1000.00001}},
    }
    return_value = E4.maximum_emissions_test(dict_values)
    assert (
        return_value == False
    ), f"When the maximum emissions constraint is not met by a difference of >= e6 this test should fail."


def test_detect_excessive_excess_generation_in_bus_warning_is_logged(caplog):
    """A logging.warning is printed due to excessive excess generation. """
    bus_label = "Test_bus"
    dict_values = {
        "optimizedFlows": {
            bus_label: pd.DataFrame(
                {"inflow": [1, 2, 3], "outflow": [-1, -1, -2], "excess": [0, 1, 1]}
            )
        }
    }
    with caplog.at_level(logging.WARNING):
        E4.detect_excessive_excess_generation_in_bus(dict_values=dict_values)
    assert (
        f"Attention, on bus {bus_label} there is excessive excess generation"
        in caplog.text
    ), f"An intended warning is not logged although there is excessive excess generation."


def test_detect_excessive_excess_generation_in_bus_no_excess(caplog):
    """No excessive excess generation takes place. """
    bus_label = "Test_bus"
    dict_values = {
        "optimizedFlows": {
            bus_label: pd.DataFrame(
                {
                    "inflow": [1, 2, 3],
                    "outflow": [-1, -1.9, -2.5],
                    "excess": [0, 0.1, 0.5],
                }
            )
        }
    }
    with caplog.at_level(logging.WARNING):
        E4.detect_excessive_excess_generation_in_bus(dict_values=dict_values)
    assert (
        caplog.text == ""
    ), f"A warning is logged although there is no excessive excess generation."


def test_detect_excessive_excess_generation_in_bus_several_busses_two_warnings(caplog):
    """Excessive excess generation takes place in two busses. """
    excessive_excess_bus_1, excessive_excess_bus_2 = (
        "Bus_excessive_excess_1",
        "Bus_excessive_excess_2",
    )
    dict_values = {
        "optimizedFlows": {
            "Bus_no_excessive_excess": pd.DataFrame(
                {
                    "inflow": [1, 2, 3],
                    "outflow": [-1, -1.9, -2.5],
                    "excess": [0, 0.1, 0.5],
                }
            ),
            excessive_excess_bus_1: pd.DataFrame(
                {"inflow": [1, 2, 3], "outflow": [-1, -1, -2], "excess": [0, 1, 1],}
            ),
            excessive_excess_bus_2: pd.DataFrame(
                {"inflow": [1, 2, 3], "outflow": [-1, -1, -1], "excess": [0, 1, 2],}
            ),
        }
    }
    with caplog.at_level(logging.WARNING):
        E4.detect_excessive_excess_generation_in_bus(dict_values=dict_values)
    assert (
        f"Attention, on bus {excessive_excess_bus_1} there is excessive excess generation"
        in caplog.text
        and f"Attention, on bus {excessive_excess_bus_2} there is excessive excess generation"
        in caplog.text
    ), f"One or two intended warnings are missing although there is excessive excess generation in two busses."


def test_verify_state_of_charge_feasible(caplog):
    """Two cases are tested here
    Case 1 is no storage components in the energy system, hence no verification carried out
    Case 2 is that all the SoC values are physically feasible, so no WARNING log messages"""

    # Test case: No storage components present in the system, so function is exited before any verification
    # Make an empty energyStorage dict signifying that there are no storage components in the energy system
    dict_values = {"energyStorage": {}}
    return_value = E4.verify_state_of_charge(dict_values=dict_values)
    assert (
        return_value is None
    ), f"When there are no storage components in the energy system, this test should not fail"

    # Test case: All physically possible values and no WARNING message is logged
    # Create a series of SoC values with three physically feasible values

    # Generate a list of 50 floats between 0 and 1
    list_floats = np.random.uniform(low=00.00, high=01.00, size=(50,))
    data = np.array(list_floats)

    # Generate a date-time index
    index = pd.date_range(start="1/1/2018", periods=50, tz="Asia/Tokyo")

    # Create a SoC time series from above floats and date-time data
    soc_series = pd.Series(data=data, index=index)

    storage = "storage_01"
    # Add the SoC time series to the result JSON nested-dict
    dict_values = {ENERGY_STORAGE: {storage: {TIMESERIES_SOC: soc_series},}}
    # Test for the function's behavior with the current case
    with caplog.at_level(logging.WARNING):
        E4.verify_state_of_charge(dict_values=dict_values)
    assert (
        f"greater than 1. This is a physically impossible value!"
        not in caplog.text
    ), f"A WARNING message is logged even though the SoC values are all below 1."
    assert (
        f"is less than 0. This is a physically impossible value!"
        not in caplog.text
    ), f"A WARNING message is logged even though the SoC values are all above 0."


def test_verify_state_of_charge_soc_below_zero(caplog):
    """Test case: The SoC value are all below 0.00 and thus, physically infeasible
    Test if the WARNING log messages are logged"""

    # Create a list of floating-point numbers less than 0.00
    list_floats = [-1.23, -0.05, -1.05]
    data = np.array(list_floats)

    # Generate a date-time index
    index = pd.date_range(start="1/1/2018", periods=3, tz="Asia/Kolkata")

    # Create a SoC time series from above floats and date-time data
    soc_series = pd.Series(data=data, index=index)

    storage = "storage_01"

    # Add the SoC time series to the result JSON nested-dict
    dict_values = {ENERGY_STORAGE: {storage: {TIMESERIES_SOC: soc_series}}}

    # Test the function with the present case
    with caplog.at_level(logging.WARNING):
        E4.verify_state_of_charge(dict_values=dict_values)
    assert (
        f"SoC of {storage} has at least one time step where its value is less than 0. This is a physically impossible value!"
        in caplog.text
    ), f"A WARNING message is not logged even though the SoC values are all below 0."


def test_verify_state_of_charge_soc_above_zero(caplog):
    """Test case: The SoC value are all above 0.00 and thus, physically infeasible
    Test to check if the WARNING log messages are logged"""

    # Create a list of floats greater than 1.00
    list_floats = [1.23, 1.0001, 2.05]
    data = np.array(list_floats)

    # Generate a date-time index
    index = pd.date_range(start="1/1/2018", periods=3, tz="Asia/Kolkata")

    # Create a SoC time series from above floats and date-time data
    soc_series = pd.Series(data=data, index=index)

    storage = "storage_01"

    # Add the SoC time series to the result JSON nested-dict
    dict_values = {ENERGY_STORAGE: {storage: {TIMESERIES_SOC: soc_series}}}

    # Test the function with the present case
    with caplog.at_level(logging.WARNING):
        E4.verify_state_of_charge(dict_values=dict_values)
    assert (
        f"SoC of {storage} has at least one time step where its value is greater than 1. This is a physically impossible value!"
        in caplog.text
    ), f"A WARNING message is not logged even though the SoC values are all above 1."
