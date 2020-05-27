import logging

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
        dict_asset["label"]
        in [
            "settings",
            "economic_data",
            "electricity_demand",
            "simulation_settings",
            "simulation_results",
        ]
    ):
        logging.debug("Calculating costs of asset %s", dict_asset["label"])
        costs_total = 0
        cost_om = 0
        # Calculation of connected parameters:
        if (
            all_list_in_dict(
                dict_asset, ["lifetime_capex_var", "capex_fix", "optimizedAddCap"]
            )
            == True
            and dict_asset["optimizedAddCap"]["value"] > 0
        ):
            # total investments including fix prices
            costs_investment = (
                dict_asset["optimizedAddCap"]["value"]
                * dict_asset["lifetime_capex_var"]["value"]
                + dict_asset["capex_fix"]["value"]
            )
            costs_total = add_costs_and_total(
                dict_asset, "costs_investment", costs_investment, costs_total
            )

        if (
            all_list_in_dict(dict_asset, ["capex_var", "capex_fix", "optimizedAddCap"])
            == True
            and dict_asset["optimizedAddCap"]["value"] > 0
        ):
            # investments including fix prices, only upfront costs at t=0
            costs_upfront = (
                dict_asset["optimizedAddCap"]["value"]
                + dict_asset["capex_var"]["value"]
                + dict_asset["capex_fix"]["value"]
            )
            costs_total = add_costs_and_total(
                dict_asset, "costs_upfront", costs_upfront, costs_total
            )

        if (
            all_list_in_dict(dict_asset, ["annual_total_flow", "lifetime_opex_var"])
            == True
        ):
            costs_opex_var = (
                dict_asset["lifetime_opex_var"]["value"]
                * dict_asset["annual_total_flow"]["value"]
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
                dict_asset["price"]["value"] * dict_asset["annual_total_flow"]["value"]
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
                    "installedCap",
                    "optimizedAddCap",
                ],
            )
            == True
        ):
            cap = dict_asset["installedCap"]["value"]
            if "optimizedAddCap" in dict_asset:
                cap += dict_asset["optimizedAddCap"]["value"]

            costs_opex_fix = dict_asset["lifetime_opex_fix"]["value"] * cap
            costs_total = add_costs_and_total(
                dict_asset, "costs_opex_fix", costs_opex_fix, costs_total
            )
            cost_om = add_costs_and_total(
                dict_asset, "costs_opex_fix", costs_opex_fix, cost_om
            )

        dict_asset.update(
            {
                "costs_total": {"value": costs_total, "unit": "currency"},
                "costs_om": {"value": cost_om, "unit": "currency"},
            }
        )

        dict_asset.update(
            {
                "annuity_total": {
                    "value": dict_asset["costs_total"]["value"]
                    * economic_data["crf"]["value"],
                    "unit": "currency/year",
                },
                "annuity_om": {
                    "value": dict_asset["costs_om"]["value"]
                    * economic_data["crf"]["value"],
                    "unit": "currency/year",
                },
            }
        )
    return


def add_costs_and_total(dict_asset, name, value, total_costs):
    total_costs += value
    dict_asset.update({name: {"value": value}})
    return total_costs


def all_list_in_dict(dict_asset, list):
    boolean = all([name in dict_asset for name in list]) == True
    return boolean
