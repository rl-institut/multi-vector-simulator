import src.E2_economics as E2
from src.constants_json_strings import (
    UNIT,
    CURR,
    CAPEX_FIX,
    CAPEX_VAR,
    OPEX_VAR,
    VALUE,
    LABEL,
    INSTALLED_CAP,
)

dict_asset = {
    LABEL: "DSO_feedin_sink",
    OPEX_VAR: {VALUE: -0.4, UNIT: "currency/kWh"},
    CAPEX_VAR: {VALUE: 0, UNIT: "currency/kW"},
    INSTALLED_CAP: {VALUE: 0.0, UNIT: UNIT},
    CAPEX_FIX: {VALUE: 0, UNIT: CURR},
    "lifetime_capex_var": {VALUE: 0.0, UNIT: "currency/kW"},
    "lifetime_opex_fix": {VALUE: 0.0, UNIT: "currency/ye"},
    "lifetime_opex_var": {VALUE: -5.505932460595773, UNIT: "?"},
    "annual_total_flow": {VALUE: 0.0, UNIT: "kWh"},
    "optimizedAddCap": {VALUE: 0, UNIT: "?"},
}

dict_economic = {
    "crf": {VALUE: 0.07264891149004721, UNIT: "?"},
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
    assert boolean is True


def test_all_list_in_dict_fails_due_to_not_included_keys():
    """Tests whether looking for list items in dict_asset is plausible."""
    list_false = ["flow", "optimizedAddCap"]
    boolean = E2.all_list_in_dict(dict_asset, list_false)
    assert boolean is False
