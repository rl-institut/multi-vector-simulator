import logging

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
    COST_OM_TOTAL,
    COST_INVESTMENT,
    COST_DISPATCH,
    COST_OM_FIX,
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
SIMULATION_RESULTS
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
            costs_investment = (
                dict_asset[OPTIMIZED_ADD_CAP][VALUE]
                * dict_asset[LIFETIME_SPECIFIC_COST][VALUE]
                + dict_asset[DEVELOPMENT_COSTS][VALUE]
            )
            costs_total = add_costs_and_total(
                dict_asset, COST_INVESTMENT, costs_investment, costs_total
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
            costs_upfront = calculate_costs_upfront(
                capacity=dict_asset[OPTIMIZED_ADD_CAP][VALUE],
                specific_costs = dict_asset[SPECIFIC_COSTS][VALUE],
                development_costs= dict_asset[DEVELOPMENT_COSTS][VALUE]
            )
            costs_total = add_costs_and_total(
                dict_asset, COST_UPFRONT, costs_upfront, costs_total
            )
        else:
            dict_asset.update({COST_UPFRONT: {VALUE: 0.0}})

        if (
            all_list_in_dict(dict_asset, [ANNUAL_TOTAL_FLOW, LIFETIME_PRICE_DISPATCH])
            is True
        ):
            costs_price_dispatch = (
                dict_asset[LIFETIME_PRICE_DISPATCH][VALUE]
                * dict_asset[ANNUAL_TOTAL_FLOW][VALUE]
            )
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

def calculate_costs_upfront(specific_costs, capacity, development_costs):
    r"""
    Calculate upfront costs of an investment, ie. the investment in year 0.

    Parameters
    ----------
    specific_costs: float
        Specific per-unit investment costs of an asset

    capacity: float
        Capacity to be installed

    development_costs: float
        Fix development costs, ie. an expense not related to the capacity that is installed. Could be planning costs of the plant.

    Returns
    -------
    costs_upfront: float
        Upfront investment costs in year 0

    """
    costs_upfront = specific_costs * capacity + development_costs
    return costs_upfront

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
