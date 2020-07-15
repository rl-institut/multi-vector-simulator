import logging

from src.constants_json_strings import (
    UNIT,
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
            "settings",
            ECONOMIC_DATA,
            "electricity_demand",
            SIMULATION_SETTINGS,
            "simulation_results",
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

        if (
            all_list_in_dict(
                dict_asset, [SPECIFIC_COSTS, DEVELOPMENT_COSTS, OPTIMIZED_ADD_CAP]
            )
            is True
            and dict_asset[OPTIMIZED_ADD_CAP][VALUE] > 0
        ):
            # investments including fix prices, only upfront costs at t=0
            costs_upfront = (
                dict_asset[OPTIMIZED_ADD_CAP][VALUE]
                + dict_asset[SPECIFIC_COSTS][VALUE]
                + dict_asset[DEVELOPMENT_COSTS][VALUE]
            )
            costs_total = add_costs_and_total(
                dict_asset, COST_UPFRONT, costs_upfront, costs_total
            )

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
                    UNIT: "currency/year",
                },
                ANNUITY_OM: {
                    VALUE: dict_asset[COST_OM_TOTAL][VALUE] * economic_data[CRF][VALUE],
                    UNIT: "currency/year",
                },
            }
        )
    return


def add_costs_and_total(dict_asset, name, value, total_costs):
    total_costs += value
    dict_asset.update({name: {VALUE: value}})
    return total_costs


def all_list_in_dict(dict_asset, list):
    boolean = all([name in dict_asset for name in list]) is True
    return boolean


def lcoe_assets(dict_values):
    """
    Calculates the levelized cost of electricity (lcoe) of each asset
    Parameters
    ----------
    dict_values

    Returns
    -------

    """
    asset_group_list = [
        ENERGY_CONSUMPTION,
        ENERGY_CONVERSION,
        ENERGY_PRODUCTION,
    ]
    for asset_group in asset_group_list:
        for asset in dict_values[asset_group]:
            if asset_group == "ENERGY_CONSUMPTION":
                dict_values[asset_group][asset].update({LCOE_ASSET: 0})
            elif dict_values[asset_group][asset][TOTAL_FLOW][VALUE] == 0.0:
                dict_values[asset_group][asset].update({LCOE_ASSET: None})
            else:
                lcoe_a = (
                    dict_values[asset_group][asset][ANNUITY_TOTAL][VALUE]
                    / dict_values[asset_group][asset][TOTAL_FLOW][VALUE]
                )
                dict_values[asset_group][asset].update({LCOE_ASSET: lcoe_a})

    for asset in dict_values[ENERGY_STORAGE]:
        if dict_values[ENERGY_STORAGE][asset]["output power"][TOTAL_FLOW][VALUE] == 0:
            dict_values[ENERGY_STORAGE][asset].update({LCOE_ASSET: None})
        else:
            storage_annuity = (
                dict_values[ENERGY_STORAGE][asset]["input power"][ANNUITY_TOTAL][VALUE]
                + dict_values[ENERGY_STORAGE][asset]["output power"][ANNUITY_TOTAL][
                    VALUE
                ]
                + dict_values[ENERGY_STORAGE][asset]["storage capacity"][ANNUITY_TOTAL][
                    VALUE
                ]
            )
            lcoe_a = (
                storage_annuity
                / dict_values[ENERGY_STORAGE][asset]["output power"][TOTAL_FLOW][VALUE]
            )
            dict_values[ENERGY_STORAGE][asset].update({LCOE_ASSET: lcoe_a})
    return
