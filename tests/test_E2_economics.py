import src.E2_economics as E2

dict_asset = {
    "label": "DSO_feedin_sink",
    "opex_var": {"value": -0.4, "unit": "currency/kWh"},
    "capex_var": {"value": 0, "unit": "currency/kW"},
    "installedCap": {"value": 0.0, "unit": "unit"},
    "capex_fix": {"value": 0, "unit": "currency"},
    "lifetime_capex_var": {"value": 0.0, "unit": "currency/kW"},
    "lifetime_opex_fix": {"value": 0.0, "unit": "currency/ye"},
    "lifetime_opex_var": {"value": -5.505932460595773, "unit": "?"},
    "annual_total_flow": {"value": 0.0, "unit": "kWh"},
    "optimizedAddCap": {"value": 0, "unit": "?"},
}

dict_economic = {
    "crf": {"value": 0.07264891149004721, "unit": "?"},
}


def test_all_cost_info_parameters_added_to_dict_values():

    E2.economics.get_costs(dict_asset, dict_economic)
    for k in (
        "costs_opex_var",
        "costs_opex_fix",
        "costs_total",
        "costs_om",
        "annuity_total",
        "annuity_om",
    ):
        assert k in dict_asset


def test_add_costs_and_total():
    total_costs = 10000
    new_cost = 5000
    total_costs = E2.add_costs_and_total(dict_asset, "new_cost", new_cost, total_costs)
    assert total_costs == new_cost + total_costs


def test_all_list_in_dict():
    list_true = ["annual_total_flow", "optimizedAddCap"]
    boolean = E2.all_list_in_dict(dict_asset, list_true)
    assert boolean == True

    list_false = ["flow", "optimizedAddCap"]
    boolean = E2.all_list_in_dict(dict_asset, list_false)
    assert boolean == False
