"""
Module E4 - Verification of results
===================================

- Detect excessive excess generation
- Verify that minimal renewable share constraint is adhered to
"""

import logging
import pandas as pd
from multi_vector_simulator.utils.constants_json_strings import (
    CONSTRAINTS,
    MINIMAL_RENEWABLE_FACTOR,
    VALUE,
    KPI,
    KPI_SCALARS_DICT,
    RENEWABLE_FACTOR,
    OPTIMIZED_FLOWS,
    MAXIMUM_EMISSIONS,
    TOTAL_EMISSIONS,
)


def minimal_renewable_share_test(dict_values):
    r"""
    Test if renewable share constraint was correctly applied

    Parameters
    ----------
    dict_values

    Returns
    -------
    Nothing

    - Nothing if the constraint is confirmed
    - Prints logging.warning message if the deviation from the constraint is < 10^-6.
    - Prints a logging.error message if the deviation from the constraint is >= 10^-6.

    Notes
    -----
    Tested with:
    - E4.test_minimal_renewable_share_test_passes()
    - E4.test_minimal_renewable_share_test_fails()

    """
    if dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_FACTOR][VALUE] > 0:
        boolean_test = (
            dict_values[KPI][KPI_SCALARS_DICT][RENEWABLE_FACTOR]
            >= dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_FACTOR][VALUE]
        )
        if boolean_test is False:
            deviation = (
                dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_FACTOR][VALUE]
                - dict_values[KPI][KPI_SCALARS_DICT][RENEWABLE_FACTOR]
            ) / dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_FACTOR][VALUE]
            if abs(deviation) < 10 ** (-6):
                logging.warning(
                    "Minimal renewable factor criterion strictly not fullfilled, but deviation is less then e6."
                )
            else:
                logging.error(
                    f"ATTENTION: Minimal renewable factor criterion NOT fullfilled! The deviation is {round(deviation,5)}."
                )
                return False

        else:
            logging.debug(
                f"Minimal renewable factor of {dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_FACTOR][VALUE]} is fullfilled."
            )
    else:
        pass


def maximum_emissions_test(dict_values):
    r"""
    Tests if maximum emissions constraint was correctly applied.

    Parameters
    ----------
    dict_values : dict
        all input parameters and results up to E0

    Returns
    -------
    Nothing

    - Nothing if the constraint is confirmed
    - Prints logging.warning message if the difference from the constraint is < 10^-6.
    - Prints a logging.error message if the difference from the constraint is >= 10^-6.

    Notes
    -----
    Tested with:
    - E4.test_maximum_emissions_test_passes()
    - E4.test_maximum_emissions_test_fails()

    """
    if dict_values[CONSTRAINTS][MAXIMUM_EMISSIONS][VALUE] is not None:
        boolean_test = (
            dict_values[KPI][KPI_SCALARS_DICT][TOTAL_EMISSIONS]
            <= dict_values[CONSTRAINTS][MAXIMUM_EMISSIONS][VALUE]
        )
        if boolean_test is False:
            diff = (
                dict_values[CONSTRAINTS][MAXIMUM_EMISSIONS][VALUE]
                - dict_values[KPI][KPI_SCALARS_DICT][TOTAL_EMISSIONS]
            )
            if abs(diff) < 10 ** (-6):
                logging.warning(
                    "Maximum emissions criterion strictly not fullfilled, but difference is less then e6."
                )
            else:
                logging.error(
                    f"ATTENTION: Maximum emissions factor criterion NOT fullfilled! The difference is {round(diff,6)}."
                )
                return False

        else:
            logging.debug(
                f"Maximum emissions constraint of {dict_values[CONSTRAINTS][MAXIMUM_EMISSIONS][VALUE]} is fullfilled."
            )
    else:
        pass


def detect_excessive_excess_generation_in_bus(dict_values):
    r"""
    Warning for any bus with excessive excess generation is given.

    A logging.warning message is printed when the ratio between total outflows and
    total inflows of a bus is < 0.9.

    Parameters
    ----------
    dict_values

    Returns
    -------
    - Nothing if the there is no excessive excess generation
    - Prints logging.warning message for every bus with excessive excess generation.

    """
    for bus_label, bus_df in dict_values[OPTIMIZED_FLOWS].items():
        # disregard excess sinks
        cols = [col for col in bus_df.columns if "excess" not in col]
        df = pd.DataFrame(bus_df[cols].sum(), columns=["sum"])
        # get total in- and outflow of bus
        total_inflow_bus = df[df > 0].dropna().sum().values[0]
        total_outflow_bus = abs(df[df < 0].dropna().sum().values[0])
        if not total_inflow_bus == 0:
            # give a warning in case ratio > 0.9
            ratio = total_outflow_bus / total_inflow_bus
            if ratio < 0.9:
                msg = f"Attention, on bus {bus_label} there is excessive excess generation, totalling up to {round((1 - ratio) * 100)}% of the inflows. The total inflows are {round(total_inflow_bus)} and outflows {round(total_outflow_bus)}  It seems to be cheaper to have this excess generation than to install more capacities that forward the energy carrier to other busses (if those assets can be optimized)."
                logging.warning(msg)
