import logging
from src.constants_json_strings import (
    UNIT,
    VALUE,
    ECONOMIC_DATA,
    CURR,
    LABEL,
    OPEX_VAR,
    OPEX_FIX,
    CAPEX_FIX,
    CAPEX_VAR,
    INSTALLED_CAP,
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
            "simulation_settings",
            "simulation_results",
        ]
    ):
        logging.debug("Calculating costs of asset %s", dict_asset[LABEL])
        costs_total = 0
        cost_om = 0
        # Calculation of connected parameters:
        if (
            all_list_in_dict(
                dict_asset, ["lifetime_capex_var", CAPEX_FIX, "optimizedAddCap"]
            )
            == True
            and dict_asset["optimizedAddCap"][VALUE] > 0
        ):
            # total investments including fix prices
            costs_investment = (
                dict_asset["optimizedAddCap"][VALUE]
                * dict_asset["lifetime_capex_var"][VALUE]
                + dict_asset[CAPEX_FIX][VALUE]
            )
            costs_total = add_costs_and_total(
                dict_asset, "costs_investment", costs_investment, costs_total
            )

        if (
            all_list_in_dict(dict_asset, [CAPEX_VAR, CAPEX_FIX, "optimizedAddCap"])
            == True
            and dict_asset["optimizedAddCap"][VALUE] > 0
        ):
            # investments including fix prices, only upfront costs at t=0
            costs_upfront = (
                dict_asset["optimizedAddCap"][VALUE]
                + dict_asset[CAPEX_VAR][VALUE]
                + dict_asset[CAPEX_FIX][VALUE]
            )
            costs_total = add_costs_and_total(
                dict_asset, "costs_upfront", costs_upfront, costs_total
            )

        if (
            all_list_in_dict(dict_asset, ["annual_total_flow", "lifetime_opex_var"])
            == True
        ):
            costs_opex_var = (
                dict_asset["lifetime_opex_var"][VALUE]
                * dict_asset["annual_total_flow"][VALUE]
            )
            costs_total = add_costs_and_total(
                dict_asset, "costs_opex_var", costs_opex_var, costs_total
            )
            cost_om = add_costs_and_total(
                dict_asset, "costs_opex_var", costs_opex_var, cost_om
            )

        # todo actually, price is probably not the label, but opex_var
        if all_list_in_dict(dict_asset, ["price", "annual_total_flow"]) == True:
            costs_energy = (
                dict_asset["price"][VALUE] * dict_asset["annual_total_flow"][VALUE]
            )
            cost_om = add_costs_and_total(
                dict_asset, "costs_energy", costs_energy, cost_om
            )

        if (
            all_list_in_dict(
                dict_asset,
                [
                    "annual_total_flow",
                    "lifetime_opex_var",
                    INSTALLED_CAP,
                    "optimizedAddCap",
                ],
            )
            == True
        ):
            cap = dict_asset[INSTALLED_CAP][VALUE]
            if "optimizedAddCap" in dict_asset:
                cap += dict_asset["optimizedAddCap"][VALUE]

            costs_opex_fix = dict_asset["lifetime_opex_fix"][VALUE] * cap
            costs_total = add_costs_and_total(
                dict_asset, "costs_opex_fix", costs_opex_fix, costs_total
            )
            cost_om = add_costs_and_total(
                dict_asset, "costs_opex_fix", costs_opex_fix, cost_om
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
                    VALUE: dict_asset["costs_total"][VALUE]
                    * economic_data["crf"][VALUE],
                    UNIT: "currency/year",
                },
                "annuity_om": {
                    VALUE: dict_asset["costs_om"][VALUE] * economic_data["crf"][VALUE],
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
    boolean = all([name in dict_asset for name in list]) == True
    return boolean
