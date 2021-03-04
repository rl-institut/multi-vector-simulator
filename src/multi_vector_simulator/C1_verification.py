"""
Module C1 - Verification
========================

Module C1 is used to validate the input data compiled in A1 or read in B0.

In A1/B0, the input parameters were parsed to str/bool/float/int. This module
tests whether the parameters are in correct value ranges:
- Display error message when wrong type
- Display error message when outside defined range
- Display error message when feed-in tariff > electricity price (would cause loop, see #119)

"""

import logging
import os

import pandas as pd

from multi_vector_simulator.utils.helpers import find_value_by_key

from multi_vector_simulator.utils.exceptions import (
    UnknownEnergyVectorError,
    DuplicateLabels,
)
from multi_vector_simulator.utils.constants import (
    PATH_INPUT_FILE,
    PATH_INPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
    DISPLAY_OUTPUT,
    OVERWRITE,
    DEFAULT_WEIGHTS_ENERGY_CARRIERS,
)
from multi_vector_simulator.utils.constants_json_strings import (
    PROJECT_DURATION,
    DISCOUNTFACTOR,
    TAX,
    LABEL,
    CURR,
    DISPATCH_PRICE,
    SPECIFIC_COSTS_OM,
    DEVELOPMENT_COSTS,
    SPECIFIC_COSTS,
    AGE_INSTALLED,
    LIFETIME,
    INSTALLED_CAP,
    FILENAME,
    EFFICIENCY,
    EVALUATED_PERIOD,
    START_DATE,
    SOC_INITIAL,
    SOC_MAX,
    SOC_MIN,
    FEEDIN_TARIFF,
    MAXIMUM_CAP,
    SCENARIO_NAME,
    PROJECT_NAME,
    LONGITUDE,
    LATITUDE,
    PERIODS,
    COUNTRY,
    ENERGY_PRICE,
    ENERGY_PROVIDERS,
    ENERGY_PRODUCTION,
    ENERGY_BUSSES,
    ENERGY_STORAGE,
    STORAGE_CAPACITY,
    VALUE,
    ASSET_DICT,
    RENEWABLE_ASSET_BOOL,
    TIMESERIES,
    ENERGY_VECTOR,
    PROJECT_DATA,
    LES_ENERGY_VECTOR_S,
    SIMULATION_ANNUITY,
    TIMESERIES_TOTAL,
    DISPATCHABILITY,
    OPTIMIZE_CAP,
    EMISSION_FACTOR,
    MAXIMUM_EMISSIONS,
    CONSTRAINTS,
    RENEWABLE_SHARE_DSO,
)

# Necessary for check_for_label_duplicates()
from collections import Counter


def lookup_file(file_path, name):
    """
    Checks whether file specified in `file_path` exists.

    If it does not exist, a FileNotFoundError is raised.

    :param file_path: File name including path of file that is checked.
    :param name: Something referring to which component the file belongs. In\
    :func:`~.CO_data_processing.get_timeseries_multiple_flows` the label of the\
    asset is used.
    :return:
    """
    if os.path.isfile(file_path) is False:
        msg = (
            f"Missing file! The timeseries file '{file_path}' \nof asset "
            + f"{name} can not be found. Operation terminated."
        )
        raise FileNotFoundError(msg)


def check_for_label_duplicates(dict_values):
    """
    This function checks if any LABEL provided for the energy system model in dict_values is a duplicate.
    This is not allowed, as oemof can not build a model with identical labels.

    Parameters
    ----------
    dict_values: dict
        All simulation inputs

    Returns
    -------
    pass or error message: DuplicateLabels
    """
    values_of_label = find_value_by_key(dict_values, LABEL)
    count = Counter(values_of_label)
    msg = ""
    for item in count:
        if count[item] > 1:
            msg += f"Following asset label is not unique with {count[item]} occurrences: {item}. \n"
    if len(msg) > 1:
        msg += f"Please make sure that each label is only used once, as oemof otherwise can not build the model."
        raise DuplicateLabels(msg)


def check_feedin_tariff_vs_levelized_cost_of_generation_of_production(dict_values):
    r"""
    Raises error if feed-in tariff > levelized costs of generation for energy asset in ENERGY_PRODUCTION with capacity to be optimized and no maximum capacity constraint.

    This is not allowed, as oemof otherwise may be subjected to an unbound problem, ie.
    a business case in which an asset should be installed with infinite capacities to maximize revenue.

    In case of a set maximum capacity or no capacity optimization logging messages are logged.

    Parameters
    ----------
    dict_values : dict
        Contains all input data of the simulation.

    Returns
    -------
    Raises error message in case of feed-in tariff > levelized costs of generation for energy asset of any
    asset in ENERGY_PRODUCTION

    Notes
    -----
    Tested with:
    - C1.test_check_feedin_tariff_vs_levelized_cost_of_generation_of_production_non_dispatchable_not_greater_costs()
    - C1.test_check_feedin_tariff_vs_levelized_cost_of_generation_of_production_non_dispatchable_greater_costs()
    - C1.test_check_feedin_tariff_vs_levelized_cost_of_generation_of_production_dispatchable_higher_dispatch_price()
    - C1.test_check_feedin_tariff_vs_levelized_cost_of_generation_of_production_dispatchable_lower_dispatch_price()
    - C1.test_check_feedin_tariff_vs_levelized_cost_of_generation_of_production_non_dispatchable_greater_costs_with_maxcap()
    - C1.test_check_feedin_tariff_vs_levelized_cost_of_generation_of_production_non_dispatchable_greater_costs_dispatch_mode()

    This test does not cover cross-sectoral invalid feedin tariffs.
    Example: If there is very cheap electricity generation but a high H2 feedin tariff, then it might be a business case to install a large Electrolyzer, and the simulation would fail. In that case one should set bounds to the solution.
    """

    warning_message_hint_unbound = f"This may cause an unbound solution and terminate the optimization, if there are no additional costs in the supply line. If this happens, please check the costs of your assets or the feed-in tariff. If both are correct, consider setting a maximum capacity constraint (maximumCap) for the relevant assets."
    warning_message_hint_maxcap = f"This will cause the optimization to result into the maximum capacity of this asset."
    warning_message_hint_dispatch = (
        f"No error expected but strange dispatch behaviour might occur."
    )

    # Check if feed-in tariff of any provider is less then expected minimal levelized energy generation costs
    for provider in dict_values[ENERGY_PROVIDERS].keys():
        feedin_tariff = dict_values[ENERGY_PROVIDERS][provider][FEEDIN_TARIFF]
        energy_vector = dict_values[ENERGY_PROVIDERS][provider][ENERGY_VECTOR]

        # Loop though all produciton assets
        for production_asset in dict_values[ENERGY_PRODUCTION]:
            # Only compare those assets to the provider that serve the same energy vector
            if (
                dict_values[ENERGY_PRODUCTION][production_asset][ENERGY_VECTOR]
                == energy_vector
            ):
                log_message_object = f"levelized costs of generation for energy asset '{dict_values[ENERGY_PRODUCTION][production_asset][LABEL]}'"

                # If energy production asset is a non-dispatchable source (PV plant)
                if (
                    dict_values[ENERGY_PRODUCTION][production_asset][DISPATCHABILITY]
                    is False
                ):
                    # Calculate cost per kWh generated
                    levelized_cost_of_generation = (
                        dict_values[ENERGY_PRODUCTION][production_asset][
                            SIMULATION_ANNUITY
                        ][VALUE]
                        / dict_values[ENERGY_PRODUCTION][production_asset][
                            TIMESERIES_TOTAL
                        ][VALUE]
                    )
                # If energy production asset is a dispatchable source (fuel source)
                else:
                    log_message_object += " (based on is dispatch price)"
                    # Estimate costs based on dispatch price (this is the lower minimum, as actually o&m and investment costs would need to be added as well, but can not be added as the dispatch is not known yet.
                    levelized_cost_of_generation = dict_values[ENERGY_PRODUCTION][
                        production_asset
                    ][DISPATCH_PRICE][VALUE]

                # Determine the margin between feedin tariff and generation costs
                diff = feedin_tariff[VALUE] - levelized_cost_of_generation
                # Get value of optimizeCap and maximumCap of production_asset
                optimze_cap = dict_values[ENERGY_PRODUCTION][production_asset][
                    OPTIMIZE_CAP
                ][VALUE]
                maximum_cap = dict_values[ENERGY_PRODUCTION][production_asset][
                    MAXIMUM_CAP
                ][VALUE]
                # If float/int values
                if isinstance(diff, float) or isinstance(diff, int):
                    if diff > 0:
                        # This can result in an unbound solution if optimizeCap is True and maximumCap is None
                        if optimze_cap == True and maximum_cap is None:
                            msg = f"Feed-in tariff of {energy_vector} ({round(feedin_tariff[VALUE],4)}) > {log_message_object} with {round(levelized_cost_of_generation,4)}. {warning_message_hint_unbound}"
                            raise ValueError(msg)
                        # If maximumCap is not None the maximum capacity of the production asset will be installed
                        elif optimze_cap == True and maximum_cap is not None:
                            msg = f"Feed-in tariff of {energy_vector} ({round(feedin_tariff[VALUE],4)}) > {log_message_object} with {round(levelized_cost_of_generation,4)}. {warning_message_hint_maxcap}"
                            logging.warning(msg)
                        # If the capacity of the production asset is not optimized there is no unbound problem but strange dispatch behaviour might occur
                        else:
                            logging.debug(
                                f"Feed-in tariff of {energy_vector} ({round(feedin_tariff[VALUE],4)}) > {log_message_object} with {round(levelized_cost_of_generation,4)}. {warning_message_hint_dispatch}"
                            )
                    else:
                        logging.debug(f"Feed-in tariff < {log_message_object}.")
                # If provided as a timeseries
                else:
                    boolean = [
                        k > 0 for k in diff.values
                    ]  # True if there is an instance where feed-in tariff > electricity_price
                    if any(boolean) is True:
                        # This can result in an unbound solution if optimizeCap is True and maximumCap is None
                        if optimze_cap == True and maximum_cap is None:
                            instances = sum(boolean)  # Count instances
                            msg = f"Feed-in tariff of {energy_vector} > {log_message_object} in {instances} during the simulation time. {warning_message_hint_unbound}"
                            raise ValueError(msg)
                        # If maximumCap is not None the maximum capacity of the production asset will be installed
                        elif optimze_cap == True and maximum_cap is not None:
                            msg = f"Feed-in tariff of {energy_vector} > {log_message_object} in {instances} during the simulation time. {warning_message_hint_maxcap}"
                            logging.warning(msg)
                        # If the capacity of the production asset is not optimized there is no unbound problem but strange dispatch behaviour might occur
                        else:
                            logging.debug(
                                f"Feed-in tariff of {energy_vector} > {log_message_object} in {instances} during the simulation time. {warning_message_hint_dispatch}"
                            )
                    else:
                        logging.debug(f"Feed-in tariff < {log_message_object}.")


def check_feedin_tariff_vs_energy_price(dict_values):
    r"""
    Raises error if feed-in tariff > energy price of any asset in 'energyProvider.csv'.
    This is not allowed, as oemof otherwise is subjected to an unbound and unrealistic problem, eg. one where the owner should consume electricity to feed it directly back into the grid for its revenue.

    Parameters
    ----------
    dict_values : dict
        Contains all input data of the simulation.

    Returns
    -------
    Indirectly, raises error message in case of feed-in tariff > energy price of any
    asset in 'energyProvider.csv'.

    Notes
    -----
    Tested with:
    - C1.test_check_feedin_tariff_vs_energy_price_greater_energy_price()
    - C1.test_check_feedin_tariff_vs_energy_price_not_greater_energy_price()

    """
    for provider in dict_values[ENERGY_PROVIDERS].keys():
        feedin_tariff = dict_values[ENERGY_PROVIDERS][provider][FEEDIN_TARIFF]
        electricity_price = dict_values[ENERGY_PROVIDERS][provider][ENERGY_PRICE]
        diff = feedin_tariff[VALUE] - electricity_price[VALUE]
        if isinstance(diff, float) or isinstance(diff, int):
            if diff > 0:
                msg = f"Feed-in tariff > energy price for the energy provider asset '{dict_values[ENERGY_PROVIDERS][provider][LABEL]}' would cause an unbound solution and terminate the optimization. Please reconsider your feed-in tariff and energy price."
                raise ValueError(msg)
            else:
                logging.debug(
                    f"Feed-in tariff < energy price for energy provider asset '{dict_values[ENERGY_PROVIDERS][provider][LABEL]}'"
                )
        else:
            boolean = [
                k > 0 for k in diff.values
            ]  # True if there is an instance where feed-in tariff > electricity_price
            if any(boolean) is True:
                instances = sum(boolean)  # Count instances
                msg = f"Feed-in tariff > energy price in {instances} during the simulation time for the energy provider asset '{dict_values[ENERGY_PROVIDERS][provider][LABEL]}'. This would cause an unbound solution and terminate the optimization. Please reconsider your feed-in tariff and energy price."
                raise ValueError(msg)
            else:
                logging.debug(
                    f"Feed-in tariff < energy price for energy provider asset '{dict_values[ENERGY_PROVIDERS][provider][LABEL]}'"
                )


def check_feasibility_of_maximum_emissions_constraint(dict_values):
    r"""
    Logs a logging.warning message in case the maximum emissions constraint could lead into an unbound problem.

    If the maximum emissions constraint is used it is checked whether there is any
    production asset with zero emissions that has a capacity to be optimized without
    maximum capacity constraint. If this is not the case a warning is logged.

    Parameters
    ----------
    dict_values : dict
        Contains all input data of the simulation.

    Returns
    -------
    Indirectly, logs a logging.warning message in case the maximum emissions constraint
    is used while no production with zero emissions is optimized without maximum capacity.

    Notes
    -----
    Tested with:
    - C1.test_check_feasibility_of_maximum_emissions_constraint_no_warning_no_constraint()
    - C1.test_check_feasibility_of_maximum_emissions_constraint_no_warning_although_emission_constraint()
    - C1.test_check_feasibility_of_maximum_emissions_constraint_maximumcap()
    - C1.test_check_feasibility_of_maximum_emissions_constraint_optimizeCap_is_False()
    - C1.test_check_feasibility_of_maximum_emissions_constraint_no_zero_emission_asset()

    """
    if dict_values[CONSTRAINTS][MAXIMUM_EMISSIONS][VALUE] is not None:
        count = 0
        for key, asset in dict_values[ENERGY_PRODUCTION].items():
            if (
                asset[EMISSION_FACTOR][VALUE] == 0
                and asset[OPTIMIZE_CAP][VALUE] == True
                and asset[MAXIMUM_CAP][VALUE] is None
            ):
                count += 1

        if count == 0:
            logging.warning(
                f"When the maximum emissions constraint is used and no production asset with zero emissions is optimized without maximum capacity this could result into an unbound problem. If this happens you can either raise the allowed maximum emissions or make sure you have enough production capacity with low emissions to cover the demand."
            )


def check_emission_factor_of_providers(dict_values):
    r"""
    Logs a logging.warning message in case the grid has a renewable share of 100 % but an emission factor > 0.

    This would affect the optimization if a maximum emissions contraint is used.
    Aditionally, it effects the KPIs connected to emissions.

    Parameters
    ----------
    dict_values : dict
        Contains all input data of the simulation.

    Returns
    -------
    Indirectly, logs a logging.warning message in case tthe grid has a renewable share
    of 100 % but an emission factor > 0.

    Notes
    -----
    Tested with:
    - C1.test_check_emission_factor_of_providers_no_warning_RE_share_lower_1()
    - C1.test_check_emission_factor_of_providers_no_warning_emission_factor_0()
    - C1.test_check_emission_factor_of_providers_warning()

    """
    for key, asset in dict_values[ENERGY_PROVIDERS].items():
        if asset[EMISSION_FACTOR][VALUE] > 0 and asset[RENEWABLE_SHARE_DSO][VALUE] == 1:
            logging.warning(
                f"The renewable share of provider {key} is {asset[RENEWABLE_SHARE_DSO][VALUE] * 100} % while its emission_factor is >0. Check if this is what you intended to define."
            )


def check_time_series_values_between_0_and_1(time_series):
    r"""
    Checks whether all values of `time_series` in [0, 1].

    Parameters
    ----------
    time_series : pd.Series
        Time series to be checked.

    Returns
    -------
    bool
        True if values of `time_series` within [0, 1], else False.

    """
    boolean = time_series.between(0, 1)

    return bool(boolean.all())


def check_non_dispatchable_source_time_series(dict_values):
    r"""
    Raises error if time series of non-dispatchable sources are not between [0, 1].

    Parameters
    ----------
    dict_values : dict
        Contains all input data of the simulation.

    Returns
    -------
    Indirectly, raises error message in case of time series of non-dispatchable sources
    not between [0, 1].

    """
    # go through all non-dispatchable sources
    for key, source in dict_values[ENERGY_PRODUCTION].items():
        if TIMESERIES in source and source[DISPATCHABILITY] is False:
            # check if values between 0 and 1
            result = check_time_series_values_between_0_and_1(
                time_series=source[TIMESERIES]
            )
            if result is False:
                logging.error(
                    f"{TIMESERIES} of non-dispatchable source {source[LABEL]} contains values out of bounds [0, 1]."
                )
                return False


def check_efficiency_of_storage_capacity(dict_values):
    r"""
    Raises error or logs a warning to help users to spot major change in PR #676.

    In #676 the `efficiency` of `storage capacity' in `storage_*.csv` was defined as the
    storages' efficiency/ability to hold charge over time. Before it was defined as
    loss rate.
    This function raises an error if efficiency of 'storage capacity' of one of the
    storages is 0 and logs a warning if efficiency of 'storage capacity' of one of the
    storages is <0.2.

    Parameters
    ----------
    dict_values : dict
        Contains all input data of the simulation.

    Notes
    -----
    Tested with:
    - test_check_efficiency_of_storage_capacity_is_0
    - test_check_efficiency_of_storage_capacity_is_btw_0_and_02
    - test_check_efficiency_of_storage_capacity_is_greater_02

    Returns
    -------
    Indirectly, raises error message in case of efficiency of 'storage capacity' is 0
    and logs warning message in case of efficiency of 'storage capacity' is <0.2.

    """
    # go through all storages
    for key, item in dict_values[ENERGY_STORAGE].items():
        eff = item[STORAGE_CAPACITY][EFFICIENCY][VALUE]
        if eff == 0:
            raise ValueError(
                f"You might use an old input file! The efficiency of the storage capacity of '{item[LABEL]}' is {eff}, although it should represent the ability of the storage to hold charge over time; check PR #676."
            )
        elif eff < 0.2:
            logging.warning(
                f"You might use an old input file! The efficiency of the storage capacity of '{item[LABEL]}' is {eff}, although it should represent the ability of the storage to hold charge over time; check PR #676."
            )


def check_input_values(dict_values):
    """

    :param dict_values:
    :return:
    """
    for asset_name in dict_values:
        if not (isinstance(dict_values[asset_name], dict)):
            # checking first layer of dict_values
            all_valid_intervals(asset_name, dict_values[asset_name], "")
        else:
            # logging.debug('Asset %s checked for validation.', asset_name)
            for sub_asset_name in dict_values[asset_name]:
                if not (isinstance(dict_values[asset_name][sub_asset_name], dict)):
                    # checking second layer of dict values
                    all_valid_intervals(
                        sub_asset_name,
                        dict_values[asset_name][sub_asset_name],
                        asset_name,
                    )
                else:
                    # logging.debug('\t Sub-asset %s checked for validation.', sub_asset_name)
                    for sub_sub_asset_name in dict_values[asset_name][sub_asset_name]:
                        if not (
                            isinstance(
                                dict_values[asset_name][sub_asset_name][
                                    sub_sub_asset_name
                                ],
                                dict,
                            )
                        ):
                            # checking third layer of dict values
                            all_valid_intervals(
                                sub_sub_asset_name,
                                dict_values[asset_name][sub_asset_name][
                                    sub_sub_asset_name
                                ],
                                asset_name + sub_asset_name,
                            )
                        else:
                            # logging.debug('\t\t Sub-sub-asset %s checked for validation.', sub_sub_asset_name)
                            logging.critical(
                                "Verification Error! Add another layer to evaluation."
                            )

    logging.info(
        "Input values have been verified. This verification can not replace a manual input parameter check."
    )


def all_valid_intervals(name, value, title):
    """
    Checks whether `value` of `name` is valid.

    Checks include the expected type and the expected range a parameter is
    supposed to be inside.

    :param name:
    :param value:
    :param title:
    :return:
    """
    valid_type_string = [
        PROJECT_NAME,
        SCENARIO_NAME,
        COUNTRY,
        "parent",
        "type",
        FILENAME,
        LABEL,
        CURR,
        PATH_OUTPUT_FOLDER,
        DISPLAY_OUTPUT,
        PATH_INPUT_FILE,
        PATH_INPUT_FOLDER,
        "sector",
    ]

    valid_type_int = [EVALUATED_PERIOD, "time_step", PERIODS]

    valid_type_timestamp = [START_DATE]

    valid_type_index = ["index"]

    valid_binary = ["optimize_cap", DSM, OVERWRITE]

    valid_intervals = {
        LONGITUDE: [-180, 180],
        LATITUDE: [-90, 90],
        LIFETIME: ["largerzero", "any"],
        AGE_INSTALLED: [0, "any"],
        INSTALLED_CAP: [0, "any"],
        MAXIMUM_CAP: [0, "any", None],
        SOC_MIN: [0, 1],
        SOC_MAX: [0, 1],
        SOC_INITIAL: [0, 1],
        "crate": [0, 1],
        EFFICIENCY: [0, 1],
        "electricity_cost_fix_annual": [0, "any"],
        "electricity_price_var_kWh": [0, "any"],
        "electricity_price_var_kW_monthly": [0, "any"],
        FEEDIN_TARIFF: [0, "any"],
        DEVELOPMENT_COSTS: [0, "any"],
        SPECIFIC_COSTS: [0, "any"],
        SPECIFIC_COSTS_OM: [0, "any"],
        DISPATCH_PRICE: [0, "any"],
        DISCOUNTFACTOR: [0, 1],
        PROJECT_DURATION: ["largerzero", "any"],
        TAX: [0, 1],
    }

    if name in valid_type_int:
        if not (isinstance(value, int)):
            logging.error(
                'Input error! Value %s/%s is not in recommended format "integer".',
                name,
                title,
            )

    elif name in valid_type_string:
        if not (isinstance(value, str)):
            logging.error(
                'Input error! Value %s/%s is not in recommended format "string".',
                name,
                title,
            )

    elif name in valid_type_index:
        if not (isinstance(value, pd.DatetimeIndex)):
            logging.error(
                'Input error! Value %s/%s is not in recommended format "pd.DatetimeIndex".',
                name,
                title,
            )

    elif name in valid_type_timestamp:
        if not (isinstance(value, pd.Timestamp)):
            logging.error(
                'Input error! Value %s/%s is not in recommended format "pd.DatetimeIndex".',
                name,
                title,
            )

    elif name in valid_binary:
        if not (value is True or value is False):
            logging.error(
                "Input error! Value %s/%s is neither True nor False.", name, title
            )

    elif name in valid_intervals:
        if name == SOC_INITIAL:
            if value is not None:
                if not (0 <= value and value <= 1):
                    logging.error(
                        "Input error! Value %s/%s should be None, or between 0 and 1.",
                        name,
                        title,
                    )
        else:

            if valid_intervals[name][0] == "largerzero":
                if value <= 0:
                    logging.error(
                        "Input error! Value %s/%s can not be to be smaller or equal to 0.",
                        name,
                        title,
                    )
            elif valid_intervals[name][0] == "nonzero":
                if value == 0:
                    logging.error("Input error! Value %s/%s can not be 0.", name, title)
            elif valid_intervals[name][0] == 0:
                if value < 0:
                    logging.error(
                        "Input error! Value %s/%s has to be larger than or equal to 0.",
                        name,
                        title,
                    )

            if valid_intervals[name][1] == "any":
                pass
            elif valid_intervals[name][1] == 1:
                if 1 < value:
                    logging.error(
                        "Input error! Value %s/%s can not be larger than 1.",
                        name,
                        title,
                    )

    else:
        logging.warning(
            "VALIDATION FAILED: Code does not define a valid range for value %s/%s",
            name,
            title,
        )


def check_if_energy_vector_of_all_assets_is_valid(dict_values):
    """
    Validates for all assets, whether 'energyVector' is defined within DEFAULT_WEIGHTS_ENERGY_CARRIERS and within the energyBusses.

    Parameters
    ----------
    dict_values: dict
        All input data in dict format

    Notes
    -----
    Function tested with
    - test_add_economic_parameters()
    - test_check_if_energy_vector_of_all_assets_is_valid_fails
    - test_check_if_energy_vector_of_all_assets_is_valid_passes
    """
    for level1 in dict_values.keys():
        for level2 in dict_values[level1].keys():
            if (
                isinstance(dict_values[level1][level2], dict)
                and ENERGY_VECTOR in dict_values[level1][level2].keys()
            ):
                energy_vector_name = dict_values[level1][level2][ENERGY_VECTOR]
                if (
                    energy_vector_name
                    not in dict_values[PROJECT_DATA][LES_ENERGY_VECTOR_S]
                ):
                    raise ValueError(
                        f"Asset {level2} of asset group {level1} has an energy vector that is not defined within the energyBusses. "
                        f"This prohibits proper processing of the assets dispatch."
                        f"Please check for typos or define another bus, as this hints at the energy system being faulty."
                    )
                    C1.check_if_energy_vector_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS(
                        energy_vector_name, level1, level2
                    )


def check_if_energy_vector_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS(
    energy_carrier, asset_group, asset
):
    r"""
    Raises an error message if an energy vector is unknown.

    It then needs to be added to the DEFAULT_WEIGHTS_ENERGY_CARRIERS in constants.py

    Parameters
    ----------
    energy_carrier: str
        Name of the energy carrier

    asset_group: str
        Name of the asset group

    asset: str
        Name of the asset

    Returns
    -------
    None

    Notes
    -----
    Tested with:
    - test_check_if_energy_vector_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS_pass()
    - test_check_if_energy_vector_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS_fails()
    """
    if energy_carrier not in DEFAULT_WEIGHTS_ENERGY_CARRIERS:
        raise UnknownEnergyVectorError(
            f"The energy carrier {energy_carrier} of asset group {asset_group}, asset {asset} is unknown, "
            f"as it is not defined within the DEFAULT_WEIGHTS_ENERGY_CARRIERS."
            f"Please check the energy carrier, or update the DEFAULT_WEIGHTS_ENERGY_CARRIERS in contants.py (dev)."
        )


def check_for_sufficient_assets_on_busses(dict_values):
    r"""
    Validating model regarding busses - each bus has to have 2+ assets connected to it, exluding energy excess sinks

    Parameters
    ----------
    dict_values: dict
        All simulation parameters

    Returns
    -------
    Logging error message if test fails
    """
    for bus in dict_values[ENERGY_BUSSES]:
        if len(dict_values[ENERGY_BUSSES][bus][ASSET_DICT]) < 3:
            asset_string = ", ".join(
                map(str, dict_values[ENERGY_BUSSES][bus][ASSET_DICT].keys())
            )
            logging.error(
                f"Energy system bus {bus} has too few assets connected to it. "
                f"The minimal number of assets that need to be connected "
                f"so that the bus is not a dead end should be two, excluding the excess sink. "
                f"These are the connected assets: {asset_string}"
            )
