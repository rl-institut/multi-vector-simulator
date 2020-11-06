import logging
import pandas as pd
import multi_vector_simulator.E4_verification as E4

from multi_vector_simulator.utils.constants_json_strings import (
    CONSTRAINTS,
    MINIMAL_RENEWABLE_FACTOR,
    VALUE,
    KPI,
    KPI_SCALARS_DICT,
    RENEWABLE_FACTOR,
)


def test_minimal_renewable_share_test_passes():
    # No minimal renewable factor
    dict_values = {CONSTRAINTS: {MINIMAL_RENEWABLE_FACTOR: {VALUE: 0}}}
    E4.minimal_renewable_share_test(dict_values)
    # Min res < res
    dict_values = {
        CONSTRAINTS: {MINIMAL_RENEWABLE_FACTOR: {VALUE: 0.2}},
        KPI: {KPI_SCALARS_DICT: {RENEWABLE_FACTOR: 0.3}},
    }
    E4.minimal_renewable_share_test(dict_values)
    # Min res < res, minimal deviation
    dict_values = {
        CONSTRAINTS: {MINIMAL_RENEWABLE_FACTOR: {VALUE: 0.2}},
        KPI: {KPI_SCALARS_DICT: {RENEWABLE_FACTOR: 0.2 - 10 ** (-7)}},
    }
    E4.minimal_renewable_share_test(dict_values)


def test_minimal_renewable_share_test_fails():
    dict_values = {
        CONSTRAINTS: {MINIMAL_RENEWABLE_FACTOR: {VALUE: 0.2}},
        KPI: {KPI_SCALARS_DICT: {RENEWABLE_FACTOR: 0.2 - 10 ** (-5)}},
    }
    return_value = E4.minimal_renewable_share_test(dict_values)
    assert return_value is False


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
