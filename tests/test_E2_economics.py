import src.E2_economics as E2

def test_all_cost_info_parameters_added_to_dict_values():
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

