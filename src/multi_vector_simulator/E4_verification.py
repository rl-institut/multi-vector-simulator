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
    ENERGY_STORAGE,
    TIMESERIES_SOC,
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
                    "Minimal renewable factor criterion strictly not fulfilled, but deviation is less then e6."
                )
            else:
                logging.error(
                    f"ATTENTION: Minimal renewable factor criterion NOT fulfilled! The deviation is {round(deviation, 5)}."
                )
                return False

        else:
            logging.debug(
                f"Minimal renewable factor of {dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_FACTOR][VALUE]} is fulfilled."
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
                    "Maximum emissions criterion strictly not fulfilled, but difference is less then e6."
                )
            else:
                logging.error(
                    f"ATTENTION: Maximum emissions factor criterion NOT fulfilled! The difference is {round(diff, 6)}."
                )
                return False

        else:
            logging.debug(
                f"Maximum emissions constraint of {dict_values[CONSTRAINTS][MAXIMUM_EMISSIONS][VALUE]} is fulfilled."
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


def verify_state_of_charge(dict_values):
    r"""
    This function checks the state of charge of each storage component
    It raises warning log messages if the SoC has a physically infeasible value

    Parameters
    ----------
    dict_values: dict
        Dictionary with all information regarding the simulation, specifically including the energyStorage assets

    Returns
    -------
    - Nothing if there are no physically infeasible SoC values for the storage components
    - Prints log messages to console and log file if there are physically impossible SoC values

    Notes
    -----
    Tested with:
    - test_E4_verification.test_verify_state_of_charge_feasible()
    - test_E4_verification.test_verify_state_of_charge_soc_below_zero()
    - test_E4_verification.test_verify_state_of_charge_soc_above_zero()

    """
    # Dict holding the data of all of the storage components
    storage_data_dict = dict_values[ENERGY_STORAGE]

    # Check if storage components are present in the energy system and only then verify SoC values
    if bool(storage_data_dict) is not False:
        # Loop through the storage components
        for storage in list(storage_data_dict.keys()):
            # Get the SoC time-series in a pandas series data structure
            soc_timeseries = storage_data_dict[storage][TIMESERIES_SOC]
            # Check the SoC time-series for abnormal values
            if (soc_timeseries > 1).any():
                logging.warning(
                    f"SoC of {storage} has at least one time step where its value is greater than 1. This is a physically impossible value!"
                )
            elif (soc_timeseries < 0).any():
                logging.warning(
                    f"SoC of {storage} has at least one time step where its value is less than 0. This is a physically impossible value!"
                )
