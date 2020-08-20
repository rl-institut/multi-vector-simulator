import logging
import pandas as pd
import warnings

from src.constants_json_strings import (
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
    LIFETIME_SPECIFIC_COST,
    CRF,
    LIFETIME_SPECIFIC_COST_OM,
    LIFETIME_PRICE_DISPATCH,
    ANNUAL_TOTAL_FLOW,
    OPTIMIZED_ADD_CAP,
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
SIMULATION_RESULTS,
FLOW
)

r"""
Module E3 economic processing
-----------------------------
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

class UnexpectedValueError(UserWarning):
    """Exception raised for value errors during economic post-processing"""
    pass


class MissingParametersForEconomicEvaluation(UserWarning):
    "Warning if one or more parameters are missing for economic post-processing  of an asset"
    pass

def get_costs(dict_asset, economic_data):
    if isinstance(dict_asset, dict) and not (
        dict_asset[LABEL]
        in [
            ECONOMIC_DATA,
            SIMULATION_SETTINGS,
            SIMULATION_RESULTS,
        ]
    ):
        logging.debug("Calculating costs of asset %s", dict_asset[LABEL])
        costs_total = 0
        cost_om = 0
        # Calculation of connected parameters:
        if (
            all_list_in_dict(
                dict_asset,
                [LIFETIME_SPECIFIC_COST, DEVELOPMENT_COSTS, OPTIMIZED_ADD_CAP],
            )
            is True
            and dict_asset[OPTIMIZED_ADD_CAP][VALUE] > 0
        ):
            # total investments including fix prices
            costs_investment_lifetime = calculate_costs_investment(
                specific_cost=dict_asset[LIFETIME_SPECIFIC_COST][VALUE],
                capacity=dict_asset[OPTIMIZED_ADD_CAP][VALUE], 
                development_costs=dict_asset[DEVELOPMENT_COSTS][VALUE])
            
            costs_total = add_costs_and_total(
                dict_asset, COST_INVESTMENT, costs_investment_lifetime, costs_total
            )
        else:
            dict_asset.update({COST_INVESTMENT: {VALUE: 0.0}})

        if (
            all_list_in_dict(
                dict_asset, [SPECIFIC_COSTS, DEVELOPMENT_COSTS, OPTIMIZED_ADD_CAP]
            )
            is True
            and dict_asset[OPTIMIZED_ADD_CAP][VALUE] > 0
        ):
            # investments including fix prices, only upfront costs at t=0
            costs_investment_upfront = calculate_costs_investment(
                capacity=dict_asset[OPTIMIZED_ADD_CAP][VALUE],
                specific_cost = dict_asset[SPECIFIC_COSTS][VALUE],
                development_costs= dict_asset[DEVELOPMENT_COSTS][VALUE]
            )
            costs_total = add_costs_and_total(
                dict_asset, COST_UPFRONT, costs_investment_upfront, costs_total
            )
        else:
            dict_asset.update({COST_UPFRONT: {VALUE: 0.0}})

        if (
            all_list_in_dict(dict_asset, [FLOW, LIFETIME_PRICE_DISPATCH])
            is True
        ):
            costs_price_dispatch = calculate_dispatch_expenditures(
                dispatch_price=dict_asset[LIFETIME_PRICE_DISPATCH][VALUE],
                flow=dict_asset[FLOW],
                asset=dict_asset[LABEL])

            costs_total = add_costs_and_total(
                dict_asset, COST_DISPATCH, costs_price_dispatch, costs_total
            )
            cost_om = add_costs_and_total(
                dict_asset, COST_DISPATCH, costs_price_dispatch, cost_om
            )

        # todo actually, price is probably not the label, but dispatch_price
        if all_list_in_dict(dict_asset, ["price", ANNUAL_TOTAL_FLOW]) is True:
            costs_energy = (
                dict_asset["price"][VALUE] * dict_asset[ANNUAL_TOTAL_FLOW][VALUE]
            )
            cost_om = add_costs_and_total(
                dict_asset, "costs_energy", costs_energy, cost_om
            )

        if (
            all_list_in_dict(
                dict_asset,
                [
                    ANNUAL_TOTAL_FLOW,
                    LIFETIME_PRICE_DISPATCH,
                    INSTALLED_CAP,
                    OPTIMIZED_ADD_CAP,
                ],
            )
            is True
        ):
            cap = dict_asset[INSTALLED_CAP][VALUE]
            if OPTIMIZED_ADD_CAP in dict_asset:
                cap += dict_asset[OPTIMIZED_ADD_CAP][VALUE]

            costs_cost_om = dict_asset[LIFETIME_SPECIFIC_COST_OM][VALUE] * cap
            costs_total = add_costs_and_total(
                dict_asset, COST_OM_FIX, costs_cost_om, costs_total
            )
            cost_om = add_costs_and_total(
                dict_asset, COST_OM_FIX, costs_cost_om, cost_om
            )

        dict_asset.update(
            {
                COST_TOTAL: {VALUE: costs_total, UNIT: CURR},
                COST_OM_TOTAL: {VALUE: cost_om, UNIT: CURR},
            }
    # Testing, if the dict_asset includes all parameters necessary for the proceeding evaluation
    all_list_in_dict(dict_asset, [LIFETIME_SPECIFIC_COST, OPTIMIZED_ADD_CAP, DEVELOPMENT_COSTS, SPECIFIC_COSTS])

        )

        dict_asset.update(
            {
                ANNUITY_TOTAL: {
                    VALUE: dict_asset[COST_TOTAL][VALUE] * economic_data[CRF][VALUE],
                    UNIT: CURR + "/" + UNIT_YEAR,
                },
                ANNUITY_OM: {
                    VALUE: dict_asset[COST_OM_TOTAL][VALUE] * economic_data[CRF][VALUE],
                    UNIT: CURR + "/" + UNIT_YEAR,
                },
            }
        )
    return

def calculate_dispatch_expenditures(dispatch_price, flow, asset):
    r"""
    Calculated the expenditures connected to an asset due to its dispatch

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
        dispatch_expenditures= dispatch_price * sum(flow)
    elif isinstance(dispatch_price, pd.Series):
        dispatch_expenditures = sum(dispatch_price*flow)
    else:
        raise UnexpectedValueError(
            f"The dispatch price of asset {asset} is neither float nor pd.Series but {type(dispatch_price)}."
            f"Please adapt E2.calculate_dispatch_costs() to evaluate the dispatch_expenditures of the asset.")

    return dispatch_expenditures

def calculate_costs_investment(specific_cost, capacity, development_costs):
    r"""
    Calculate investment costs of an asset
    Depending on the specific_cost provided,
    either the total lifetime investment costs or the upfront investment costs are calculated,

    Parameters
    ----------
    specific_cost: float
        a) Specific per-unit investment costs of an asset over its lifetime, including all replacement costs
        b) Specific per-unit investment costs of an asset in year 0

    capacity: float
        Capacity to be installed

    development_costs: float
        Fix development costs, ie. an expense not related to the capacity that is installed. Could be planning costs of the plant.

    Returns
    -------
    costs_investment: float
        a) Total investment costs of an asset over its lifetime, including all replacement costs
        b) Upfront investment costs in year 0

    """
    costs_investment = specific_cost * capacity + development_costs
    return costs_investment

def calculate_costs_replacement(costs_investment, costs_upfront):
    r"""
    Calculates (the present value of) the replacement costs over the project lifetime

    Parameters
    ----------
    costs_investment: float
        Investment costs over project lifetime

    costs_upfront: float
        Upfront investment costs in year 0

    Returns
    -------
    costs_replacements: float
        Aggregated replacement costs over the project lifetime
    """
    costs_replacements = costs_investment - costs_upfront
    return costs_replacements

def calculate_operation_and_management_expenditures(specific_om_cost, capacity):
    r"""
    Calculates operation and management expenditures

    Parameters
    ----------
    specific_om_cost: float
        a) specific operation and management costs per unit in year 0
        b) specific operation and management costs per unit for the whole project lifetime

    capacity: float
        Capacity installed

    Returns
    -------
    costs_operation_and_management: float
        a) Operation and management expenditures in year 0
        b) Total operation and management expenditures over the project lifetime
    """
    costs_operation_and_management = specific_om_cost * capacity
    return costs_operation_and_management

def calculate_total_operational_expenditures(operation_and_management_expenditures, dispatch_expenditures):
    r"""
    Calculated total expenditures of an asset (operational costs)

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
    total_operatinal_expenditures: float
        a) total operational expenditures per annum for installed capacity
        b) total operational expenditures for whole project lifetime for installed capacity
    """
    total_operatinal_expenditures = operation_and_management_expenditures + dispatch_expenditures
    return total_operatinal_expenditures

def add_costs_and_total(dict_asset, name, value, total_costs):
    total_costs += value
    dict_asset.update({name: {VALUE: value}})
    return total_costs


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
            if name in dict_asset:
                pass
            else:
                missing_parameters.append(name)
        missing_parameters = ', '.join(map(str, missing_parameters))
        raise MissingParametersForEconomicEvaluation(
            f"Asset {dict_asset[LABEL]} is missing parameters for the economic evaluation: {missing_parameters}."
            f"These parameters are needed for E2.get_costs(). Please check the E modules.")
    return boolean


def lcoe_assets(dict_asset, asset_group):
    """
    Calculates the levelized cost of electricity (lcoe) of each asset. [Follow this link for information](docs/MVS_Outputs.rst)
    Parameters
    ----------
    dict_asset: dict
        Dictionary defining an asset

    asset_group: str
        Defining to which asset group the asset belongs

    Returns
    -------

    """

    if asset_group == ENERGY_CONSUMPTION:
        dict_asset.update({LCOE_ASSET: {VALUE: 0, UNIT: "currency/kWh"}})

    elif asset_group == ENERGY_STORAGE:
        if dict_asset[OUTPUT_POWER][TOTAL_FLOW][VALUE] == 0:
            dict_asset.update({LCOE_ASSET: {VALUE: None, UNIT: "currency/kWh"}})
        else:
            storage_annuity = (
                dict_asset[INPUT_POWER][ANNUITY_TOTAL][VALUE]
                + dict_asset[OUTPUT_POWER][ANNUITY_TOTAL][VALUE]
                + dict_asset[STORAGE_CAPACITY][ANNUITY_TOTAL][VALUE]
            )
            lcoe_a = storage_annuity / dict_asset[OUTPUT_POWER][TOTAL_FLOW][VALUE]
            dict_asset.update({LCOE_ASSET: {VALUE: lcoe_a, UNIT: "currency/kWh"}})

    elif dict_asset[TOTAL_FLOW][VALUE] == 0.0:
        dict_asset.update({LCOE_ASSET: {VALUE: None, UNIT: "currency/kWh"}})
    else:
        lcoe_a = dict_asset[ANNUITY_TOTAL][VALUE] / dict_asset[TOTAL_FLOW][VALUE]
        dict_asset.update({LCOE_ASSET: {VALUE: lcoe_a, UNIT: "currency/kWh"}})

    return
