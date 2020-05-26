import src.E2_economics as E2

def test_all_cost_info_parameters_added_to_dict_values():
    dict_asset = {
        "type_oemof": "sink",
        "label": "DSO_feedin_sink",
        "input_direction": "Electricity (DSO)",
        "input_bus_name": "Electricity (DSO) bus",
        "lifetime": {"value": 30, "unit": "year"},
        "opex_var": {"value": -0.4, "unit": "currency/kWh"},
        "capex_var": {"value": 0, "unit": "currency/kW"},
        "optimizeCap": {"value": False, "unit": "bool"},
        "unit": "?",
        "installedCap": {"value": 0.0, "unit": "unit"},
        "capex_fix": {"value": 0, "unit": "currency"},
        "opex_fix": {"value": 0, "unit": "currency/year"},
        "lifetime_capex_var": {"value": 0.0, "unit": "currency/kW"},
        "annuity_capex_opex_var": {"value": 0.0, "unit": "currency/kW/a"},
        "lifetime_opex_fix": {"value": 0.0, "unit": "currency/ye"},
        "lifetime_opex_var": {"value": -5.505932460595773, "unit": "?"},
        "simulation_annuity": {"value": 0.0, "unit": "currency/unit/simulation period"},
        "total_flow": {"value": 0.0, "unit": "kWh"},
        "annual_total_flow": {"value": 0.0, "unit": "kWh"},
        "peak_flow": {"value": 0.0, "unit": "kW"},
        "average_flow": {"value": 0.0, "unit": "kW"},
        "optimizedAddCap": {"value": 0, "unit": "?"},
    }

    dict_economic = {
        "currency": "NOK",
        "discount_factor": {"unit": "factor", "value": 0.06},
        "label": "economic_data",
        "project_duration": {"unit": "year", "value": 30},
        "tax": {"unit": "factor", "value": 0.0},
        "annuity_factor": {"value": 13.76483115148943, "unit": "?"},
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

