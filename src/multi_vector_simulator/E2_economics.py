"""
Module E2 - Economic processing
===============================

The module processes the simulation results regarding economic parameters:
- calculate lifetime expenditures based on variable energy flows
- calculate lifetime investment costs
- calculate present value of an asset
- calculate revenue
- calculate yearly cash flows of whole project for project lifetime (cash flow projection)
- calculate fuel price expenditures calculate upfront investment costs
- calculate operation management costs (FOM)
- calculate upfront investment costs (UIC)
- calculate annuity per asset
- calculate annuity for the whole project
- calculate net present value
- calculate levelised cost of energy
- calculate levelised cost of energy carriers (electricity, H2, heat)
"""

import logging
import pandas as pd
import warnings

from multi_vector_simulator.utils.constants_json_strings import (
    UNIT,
    CURR,
    UNIT_YEAR,
    VALUE,
    ECONOMIC_DATA,
    CURR,
    LABEL,
    DEVELOPMENT_COSTS,
    SPECIFIC_COSTS,
    INSTALLED_CAP,
    SIMULATION_SETTINGS,
    OUTFLOW_DIRECTION,
    LIFETIME_SPECIFIC_COST,
    CRF,
    LIFETIME_SPECIFIC_COST_OM,
    LIFETIME_PRICE_DISPATCH,
    ANNUAL_TOTAL_FLOW,
    OPTIMIZED_ADD_CAP,
    OUTFLOW_DIRECTION,
    ANNUITY_OM,
    ANNUITY_TOTAL,
    COST_TOTAL,
    COST_OPERATIONAL_TOTAL,
    COST_INVESTMENT,
    COST_DISPATCH,
    COST_OM,
    COST_UPFRONT,
    ENERGY_PRODUCTION,
    TOTAL_FLOW,
    ENERGY_CONSUMPTION,
    ENERGY_CONVERSION,
    ENERGY_STORAGE,
    LCOE_ASSET,
    OUTPUT_POWER,
    INPUT_POWER,
    STORAGE_CAPACITY,
    COST_REPLACEMENT,
    SIMULATION_RESULTS,
    FLOW,
    SPECIFIC_REPLACEMENT_COSTS_INSTALLED,
    SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED,
)


class MissingParametersForEconomicEvaluation(UserWarning):
    "Warning if one or more parameters are missing for economic post-processing  of an asset"
    pass


def get_costs(dict_asset, economic_data):
    r"""
    Calculates economic KPI of the asset handed to the function

    Parameters
    ----------
    dict_asset: dict
        Asset to be evaluated.
        Warning messages in place in case that the asset should not be evaluated.

    economic_data: dict
        Economic data of the project

    Returns
    -------
    Updated dict_asset with following KPI:
    - COST_INVESTMENT
    - COST_UPFRONT
    - COST_REPLACEMENT
    - COST_TOTAL
    - COST_OM
    - COST_DISPATCH
    - COST_OPERATIONAL_TOTAL
    - ANNUITY_TOTAL
    - ANNUITY_OM

    Tested with:
    - test_all_cost_info_parameters_added_to_dict_asset()
    - Test_Economic_KPI.test_benchmark_Economic_KPI_C2_E2()

    """

    logging.debug("Calculating costs of asset %s", dict_asset[LABEL])

    # helper for developing get_costs() and E modules
    if not isinstance(dict_asset, dict):
        logging.warning(
            f"Function E2.get_costs() is used on {dict_asset}, eventhough it is not a dict. Check loops in E modules."
        )

    # helper for developing get_costs() and E modules
    if dict_asset[LABEL] in [ECONOMIC_DATA, SIMULATION_SETTINGS, SIMULATION_RESULTS]:
        logging.warning(
            f"Function E2.get_costs() is used on {dict_asset[LABEL]}, eventhough it should not be applied to it. Check loops in E modules."
        )

    # Testing, if the dict_asset includes all parameters necessary for the proceeding evaluation
    all_list_in_dict(
        dict_asset,
        [
            LIFETIME_SPECIFIC_COST,
            OPTIMIZED_ADD_CAP,
            DEVELOPMENT_COSTS,
            SPECIFIC_COSTS,
            LIFETIME_PRICE_DISPATCH,
            FLOW,
        ],
    )

    # Part of the investment costs to be paid upfront at t=0
    costs_investment_upfront = calculate_costs_upfront_investment(
        capacity=dict_asset[OPTIMIZED_ADD_CAP][VALUE],
        specific_cost=dict_asset[SPECIFIC_COSTS][VALUE],
        development_costs=dict_asset[DEVELOPMENT_COSTS][VALUE],
    )

    dict_asset.update(
        {COST_UPFRONT: {VALUE: costs_investment_upfront, UNIT: economic_data[CURR]}}
    )

    # Part of the investment costs to be paid due to replacements
    costs_replacement = calculate_costs_replacement(
        specific_replacement_of_initial_capacity=dict_asset[
            SPECIFIC_REPLACEMENT_COSTS_INSTALLED
        ][VALUE],
        specific_replacement_of_optimized_capacity=dict_asset[
            SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED
        ][VALUE],
        initial_capacity=dict_asset[INSTALLED_CAP][VALUE],
        optimized_capacity=dict_asset[OPTIMIZED_ADD_CAP][VALUE],
    )

    dict_asset.update(
        {COST_REPLACEMENT: {VALUE: costs_replacement, UNIT: economic_data[CURR]}}
    )

    # Total investment costs including investments into the asset, replacement costs and development costs
    costs_investment_lifetime = calculate_total_capital_costs(
        upfront=dict_asset[COST_UPFRONT][VALUE],
        replacement=dict_asset[COST_REPLACEMENT][VALUE],
    )

    dict_asset.update(
        {COST_INVESTMENT: {VALUE: costs_investment_lifetime, UNIT: economic_data[CURR]}}
    )

    # Operation and management expenditures over the project lifetime
    operation_and_management_expenditures = calculate_operation_and_management_expenditures(
        specific_om_cost=dict_asset[LIFETIME_SPECIFIC_COST_OM][VALUE],
        installed_capacity=dict_asset[INSTALLED_CAP][VALUE],
        optimized_add_capacity=dict_asset[OPTIMIZED_ADD_CAP][VALUE],
    )
    dict_asset.update(
        {
            COST_OM: {
                VALUE: operation_and_management_expenditures,
                UNIT: economic_data[CURR],
            }
        }
    )

    # Dispatch expenditures of the asset over the project lifetime
    if isinstance(dict_asset.get(OUTFLOW_DIRECTION, None), list):
        costs_dispatch = 0
        for bus in dict_asset[OUTFLOW_DIRECTION]:
            costs_dispatch += calculate_dispatch_expenditures(
                dispatch_price=dict_asset[LIFETIME_PRICE_DISPATCH][VALUE],
                flow=dict_asset[FLOW][bus],
                asset=dict_asset[LABEL],
            )
    else:
        costs_dispatch = calculate_dispatch_expenditures(
            dispatch_price=dict_asset[LIFETIME_PRICE_DISPATCH][VALUE],
            flow=dict_asset[FLOW],
            asset=dict_asset[LABEL],
        )

    dict_asset.update(
        {COST_DISPATCH: {VALUE: costs_dispatch, UNIT: economic_data[CURR]}}
    )

    # Total operational expenditures over the lifetime
    total_operational_expenditures = calculate_total_operational_expenditures(
        dict_asset[COST_OM][VALUE], dict_asset[COST_DISPATCH][VALUE]
    )
    dict_asset.update({COST_OPERATIONAL_TOTAL: {VALUE: total_operational_expenditures}})

    # Total costs of the assets, capital and operational
    total_asset_costs_over_lifetime = calculate_total_asset_costs_over_lifetime(
        dict_asset[COST_INVESTMENT][VALUE], dict_asset[COST_OPERATIONAL_TOTAL][VALUE]
    )
    dict_asset.update(
        {
            COST_TOTAL: {
                VALUE: total_asset_costs_over_lifetime,
                UNIT: economic_data[CURR],
            }
        }
    )

    dict_asset.update(
        {
            ANNUITY_TOTAL: {
                VALUE: dict_asset[COST_TOTAL][VALUE] * economic_data[CRF][VALUE],
                UNIT: CURR + "/" + UNIT_YEAR,
            },
            ANNUITY_OM: {
                VALUE: dict_asset[COST_OPERATIONAL_TOTAL][VALUE]
                * economic_data[CRF][VALUE],
                UNIT: CURR + "/" + UNIT_YEAR,
            },
        }
    )


def calculate_total_asset_costs_over_lifetime(
    costs_investment, cost_operational_expenditures
):
    r"""
    Calculate costs of an asset over whole lifetime

    Parameters
    ----------
    costs_investment: float
        Investment costs over whole lifetime

    cost_operational_expenditures: float
        Operation and management as well as dispatch expenditures over whole lifetime

    Returns
    -------
    total_asset_costs_over_lifetime: float
        costs of an asset over whole lifetime, including upfront investment costs, development costs, replacement costs, operation and management expenditures, dispatch expenditures
    """
    total_asset_costs_over_lifetime = costs_investment + cost_operational_expenditures
    return total_asset_costs_over_lifetime


def calculate_dispatch_expenditures(dispatch_price, flow, asset):
    r"""
    Calculate the expenditures connected to an asset due to its dispatch

    Parameters
    ----------
    dispatch_price: float, int or pd.Series
        Dispatch price of an asset (variable costs), ie. how much has to be paid for each unit of dispatch
        Raises error if type does not match
        a) lifetime_price_dispatch (taking into account all years of operation)
        b) price_dispatch (taking into account one year of operation)

    flow: pd.Series
        Dispatch of the asset

    asset: str
        Label of the asset

    Returns
    -------
    a) Total dispatch expenditures of an asset
    b) Annual dispatch expenditures of an asset
    """

    if isinstance(dispatch_price, float) or isinstance(dispatch_price, int):
        # Dispatch price is a scalar
        dispatch_expenditures = dispatch_price * sum(flow)
    elif isinstance(dispatch_price, pd.Series):
        # Dispatch price is defined as a timeseries
        dispatch_expenditures = sum(dispatch_price * flow)
    elif isinstance(dispatch_price, list):
        # Dispatch price is defined as a list, ie. the asset has multiple flows
        dispatch_expenditures = 0
        for list_price in dispatch_price:
            partial_dispatch_expenditures = calculate_dispatch_expenditures(
                list_price, flow, asset + " (list entry)"
            )
            dispatch_expenditures += partial_dispatch_expenditures
    else:
        raise TypeError(
            f"The dispatch price of asset {asset} is neither float, list nor pd.Series but {type(dispatch_price)}."
            f"Please adapt E2.calculate_dispatch_costs() to evaluate the dispatch_expenditures of the asset."
        )

    return dispatch_expenditures


def calculate_costs_upfront_investment(specific_cost, capacity, development_costs):
    r"""
    Calculate investment costs of an asset
    Depending on the specific_cost provided,
    either the total asset's lifetime investment costs or the upfront investment costs are calculated,

    Parameters
    ----------
    specific_cost: float
        a) Specific per-unit investment costs of an asset over its lifetime, including all replacement costs
        b) Specific per-unit investment costs of an asset in year 0

    capacity: float
        Capacity to be installed

    development_costs: float
        Fix development costs, ie. an expense not related to the capacity that is installed. Could be planning costs of the asset.

    Returns
    -------
    costs_investment: float
        a) Total investment costs of an asset over its lifetime, including all replacement costs
        b) Upfront investment costs in year 0

    """
    costs_upfront_investment = specific_cost * capacity + development_costs
    return costs_upfront_investment


def calculate_total_capital_costs(upfront, replacement):
    r"""
    Calculate total capital expenditures

    Parameters
    ----------
    upfront: float
        Upfront investments at t=0, including development costs

    replacement: float
        Replacement costs of pre-installed and new assets


    Returns
    -------
    cost_total_investment: float
        Total capital costs
    """
    cost_total_investment = upfront + replacement
    return cost_total_investment


def calculate_costs_replacement(
    specific_replacement_of_initial_capacity,
    specific_replacement_of_optimized_capacity,
    initial_capacity,
    optimized_capacity,
):
    r"""
    Calculate (the present value of) the replacement costs over the project lifetime

    Parameters
    ----------
    specific_replacement_of_initial_capacity: float
        Per-unit replacement costs of an asset that was pre-existing at the location

    specific_replacement_of_optimized_capacity: float
        Per-unit replacement costs of an asset that is to be installed

    initial_capacity: float
        Initial capacity installed

    optimized_capacity: float
        Additional capacity to be installed, as optimized

    Returns
    -------
    costs_replacements: float
        Aggregated replacement costs over the project lifetime
    """
    costs_replacements = (
        specific_replacement_of_initial_capacity * initial_capacity
        + specific_replacement_of_optimized_capacity * optimized_capacity
    )
    return costs_replacements


def calculate_operation_and_management_expenditures(
    specific_om_cost, installed_capacity, optimized_add_capacity
):
    r"""
    Calculate operation and management expenditures

    Parameters
    ----------
    specific_om_cost: float
        a) specific operation and management costs per unit in year 0
        b) specific operation and management costs per unit for the whole project lifetime

    installed_capacity: float
        Capacity installed initially

    optimized_add_capacity: float
        Capacity installed within the optimization scenario

    Returns
    -------
    costs_operation_and_management: float
        a) Operation and management expenditures in year 0
        b) Total operation and management expenditures over the project lifetime
    """
    costs_operation_and_management = specific_om_cost * (
        installed_capacity + optimized_add_capacity
    )
    return costs_operation_and_management


def calculate_total_operational_expenditures(
    operation_and_management_expenditures, dispatch_expenditures
):
    r"""
    Calculate total expenditures of an asset (operational costs)

    Parameters
    ----------
    operation_and_management_expenditures: float
        a) operation and management expenditures per annum for the installed capacity
        b) operation and management expenditures for whole project lifetime for the installed capacity

    dispatch_expenditures: float
        a) dispatch expenditures per annum for the installed capacity
        b) dispatch expenditures for whole project lifetime for the installed capacity

    Returns
    -------
    total_operational_expenditures: float
        a) total operational expenditures per annum for installed capacity
        b) total operational expenditures for whole project lifetime for installed capacity
    """
    total_operational_expenditures = (
        operation_and_management_expenditures + dispatch_expenditures
    )
    return total_operational_expenditures


def all_list_in_dict(dict_asset, list):
    r"""
    Checks if all items of a list are withing the keys of a dictionary

    Parameters
    ----------
    dict_asset: dict
        Dict with the keys to be evaluated

    list: list
        List of keys (parameter in strings) that should be in dict

    Returns
    -------
    boolean: bool
        True: All items in keys of the dict
        False: At least one item is not in keys of the dict
    """
    boolean = all([name in dict_asset for name in list]) is True
    if boolean is False:
        missing_parameters = []
        for name in list:
            if name not in dict_asset:
                missing_parameters.append(name)
        missing_parameters = ", ".join(map(str, missing_parameters))
        raise MissingParametersForEconomicEvaluation(
            f"Asset {dict_asset[LABEL]} is missing parameters for the economic evaluation: {missing_parameters}."
            f"These parameters are needed for E2.get_costs(). Please check the E modules."
        )
    return boolean


def lcoe_assets(dict_asset, asset_group):
    r"""
    Calculates the levelized cost of electricity (lcoe) of each asset. [Follow this link for information](docs/MVS_Outputs.rst)

    Parameters
    ----------
    dict_asset: dict
        Dictionary defining an asset

    asset_group: str
        Defining to which asset group the asset belongs

    Returns
    -------
    Updates the asset dictionary with the calculated LCOE_ASSET.
    Storages have four values LCOE_ASSET: One for the overall storage including all costs, and one each for the components.

    Notes
    -----

    .. math::

        LCOE\_ASSET = \frac{A}{ E_{throughput} } \\
        \textrm{If } E_{throughput} = 0, LCOE\_ASSET = 0

    """

    lcoe_a = 0

    if asset_group == ENERGY_STORAGE:
        if dict_asset[OUTPUT_POWER][TOTAL_FLOW][VALUE] > 0:
            storage_annuity = (
                dict_asset[INPUT_POWER][ANNUITY_TOTAL][VALUE]
                + dict_asset[OUTPUT_POWER][ANNUITY_TOTAL][VALUE]
                + dict_asset[STORAGE_CAPACITY][ANNUITY_TOTAL][VALUE]
            )
            lcoe_a = storage_annuity / dict_asset[OUTPUT_POWER][TOTAL_FLOW][VALUE]

        for component in [INPUT_POWER, OUTPUT_POWER]:
            if dict_asset[component][TOTAL_FLOW][VALUE] > 0:
                lcoe_a_component = (
                    dict_asset[component][ANNUITY_TOTAL][VALUE]
                    / dict_asset[component][TOTAL_FLOW][VALUE]
                )
                dict_asset[component].update(
                    {LCOE_ASSET: {VALUE: lcoe_a_component, UNIT: CURR + "/kWh"}}
                )
                if component == INPUT_POWER:
                    lcoe_a_component = (
                        dict_asset[STORAGE_CAPACITY][ANNUITY_TOTAL][VALUE]
                        / dict_asset[component][TOTAL_FLOW][VALUE]
                    )
                    dict_asset[STORAGE_CAPACITY].update(
                        {LCOE_ASSET: {VALUE: lcoe_a_component, UNIT: CURR + "/kWh"}}
                    )
            else:
                dict_asset[component].update(
                    {LCOE_ASSET: {VALUE: 0, UNIT: CURR + "/kWh"}}
                )
                if component == INPUT_POWER:
                    dict_asset[STORAGE_CAPACITY].update(
                        {LCOE_ASSET: {VALUE: 0, UNIT: CURR + "/kWh"}}
                    )

    elif dict_asset[TOTAL_FLOW][VALUE] > 0:
        lcoe_a = dict_asset[ANNUITY_TOTAL][VALUE] / dict_asset[TOTAL_FLOW][VALUE]

    dict_asset.update({LCOE_ASSET: {VALUE: lcoe_a, UNIT: CURR + "/kWh"}})
