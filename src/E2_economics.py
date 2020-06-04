import logging

from src.constants_json_strings import (
    UNIT,
    VALUE,
    ECONOMIC_DATA,
    CURR,
    LABEL,
    C_DEVELOPMENT,
    C_SPECIFIC,
    INSTALLED_CAP,
    SIMULATION_SETTINGS,
    LIFETIME_CAPEX_VAR,
    CRF,
    LIFETIME_OPEX_FIX,
    LIFETIME_OPEX_VAR,
    ANNUAL_TOTAL_FLOW,
    OPTIMIZED_ADD_CAP,
    ANNUITY_OM
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
                dict_asset, [LIFETIME_CAPEX_VAR, C_DEVELOPMENT, OPTIMIZED_ADD_CAP]
            )
            is True
            and dict_asset[OPTIMIZED_ADD_CAP][VALUE] > 0
        ):
            # total investments including fix prices
            costs_investment = (
                dict_asset[OPTIMIZED_ADD_CAP][VALUE]
                * dict_asset[LIFETIME_CAPEX_VAR][VALUE]
                + dict_asset[C_DEVELOPMENT][VALUE]
            )
            costs_total = add_costs_and_total(
                dict_asset, "costs_investment", costs_investment, costs_total
            )

        if (
            all_list_in_dict(dict_asset, [C_SPECIFIC, C_DEVELOPMENT, OPTIMIZED_ADD_CAP])
            is True
            and dict_asset[OPTIMIZED_ADD_CAP][VALUE] > 0
        ):
            # investments including fix prices, only upfront costs at t=0
            costs_upfront = (
                dict_asset[OPTIMIZED_ADD_CAP][VALUE]
                + dict_asset[C_SPECIFIC][VALUE]
                + dict_asset[C_DEVELOPMENT][VALUE]
            )
            costs_total = add_costs_and_total(
                dict_asset, "costs_upfront", costs_upfront, costs_total
            )

        if all_list_in_dict(dict_asset, [ANNUAL_TOTAL_FLOW, LIFETIME_OPEX_VAR]) is True:
            costs_p_dispatch = (
                dict_asset[LIFETIME_OPEX_VAR][VALUE]
                * dict_asset[ANNUAL_TOTAL_FLOW][VALUE]
            )
            costs_total = add_costs_and_total(
                dict_asset, "costs_p_dispatch", costs_p_dispatch, costs_total
            )
            cost_om = add_costs_and_total(
                dict_asset, "costs_p_dispatch", costs_p_dispatch, cost_om
            )

        # todo actually, price is probably not the label, but p_dispatch
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
                    LIFETIME_OPEX_VAR,
                    INSTALLED_CAP,
                    OPTIMIZED_ADD_CAP,
                ],
            )
            is True
        ):
            cap = dict_asset[INSTALLED_CAP][VALUE]
            if OPTIMIZED_ADD_CAP in dict_asset:
                cap += dict_asset[OPTIMIZED_ADD_CAP][VALUE]

            costs_cost_om = dict_asset[LIFETIME_OPEX_FIX][VALUE] * cap
            costs_total = add_costs_and_total(
                dict_asset, "costs_cost_om", costs_cost_om, costs_total
            )
            cost_om = add_costs_and_total(
                dict_asset, "costs_cost_om", costs_cost_om, cost_om
            )

        dict_asset.update(
            {
                "costs_total": {VALUE: costs_total, UNIT: CURR},
                "costs_om": {VALUE: cost_om, UNIT: CURR},
            }
        )

        dict_asset.update(
            {
                "annuity_total": {
                    VALUE: dict_asset["costs_total"][VALUE] * economic_data[CRF][VALUE],
                    UNIT: "currency/year",
                },
                ANNUITY_OM: {
                    VALUE: dict_asset["costs_om"][VALUE] * economic_data[CRF][VALUE],
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
