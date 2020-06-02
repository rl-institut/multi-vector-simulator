import src.E2_economics as E2
from src.constants_json_strings import UNIT, CURR

dict_asset = {
    "label": "DSO_feedin_sink",
    "opex_var": {"value": -0.4, UNIT: "currency/kWh"},
    "capex_var": {"value": 0, UNIT: "currency/kW"},
    "installedCap": {"value": 0.0, UNIT: UNIT},
    "capex_fix": {"value": 0, UNIT: CURR},
    "lifetime_capex_var": {"value": 0.0, UNIT: "currency/kW"},
    "lifetime_opex_fix": {"value": 0.0, UNIT: "currency/ye"},
    "lifetime_opex_var": {"value": -5.505932460595773, UNIT: "?"},
    "annual_total_flow": {"value": 0.0, UNIT: "kWh"},
    "optimizedAddCap": {"value": 0, UNIT: "?"},
}

dict_economic = {
    "crf": {"value": 0.07264891149004721, UNIT: "?"},
}


def test_all_cost_info_parameters_added_to_dict_asset():
    """Tests whether the function get_costs is adding all the calculated costs to dict_asset."""
    E2.get_costs(dict_asset, dict_economic)
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
    """Tests if new costs are adding to current costs correctly and if dict_asset is being updated accordingly."""
    current_costs = 10000
    new_cost = 5000
    total_costs = E2.add_costs_and_total(
        dict_asset, "new_cost", new_cost, current_costs
    )
    assert total_costs == new_cost + current_costs
    assert "new_cost" in dict_asset


def test_all_list_in_dict_passes_as_all_keys_included():
    """Tests whether looking for list items in dict_asset is plausible."""
    list_true = ["annual_total_flow", "optimizedAddCap"]
    boolean = E2.all_list_in_dict(dict_asset, list_true)
    assert boolean == True


def test_all_list_in_dict_fails_due_to_not_included_keys():
    """Tests whether looking for list items in dict_asset is plausible."""
    list_false = ["flow", "optimizedAddCap"]
    boolean = E2.all_list_in_dict(dict_asset, list_false)
    assert boolean == False
