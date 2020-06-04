import src.E2_economics as E2
from src.constants_json_strings import (
    UNIT,
    CURR,
    C_DEVELOPMENT,
    C_SPECIFIC,
    P_DISPATCH,
    VALUE,
    LABEL,
    INSTALLED_CAP,
    LIFETIME_CAPEX_VAR,
    CRF,
    LIFETIME_OPEX_FIX,
    LIFETIME_OPEX_VAR,
    ANNUAL_TOTAL_FLOW,
    OPTIMIZED_ADD_CAP,
    ANNUITY_OM
)

dict_asset = {
    LABEL: "DSO_feedin_sink",
    P_DISPATCH: {VALUE: -0.4, UNIT: "currency/kWh"},
    C_SPECIFIC: {VALUE: 0, UNIT: "currency/kW"},
    INSTALLED_CAP: {VALUE: 0.0, UNIT: UNIT},
    C_DEVELOPMENT: {VALUE: 0, UNIT: CURR},
    LIFETIME_CAPEX_VAR: {VALUE: 0.0, UNIT: "currency/kW"},
    LIFETIME_OPEX_FIX: {VALUE: 0.0, UNIT: "currency/ye"},
    LIFETIME_OPEX_VAR: {VALUE: -5.505932460595773, UNIT: "?"},
    ANNUAL_TOTAL_FLOW: {VALUE: 0.0, UNIT: "kWh"},
    OPTIMIZED_ADD_CAP: {VALUE: 0, UNIT: "?"},
}

dict_economic = {
    CRF: {VALUE: 0.07264891149004721, UNIT: "?"},
}


def test_all_cost_info_parameters_added_to_dict_asset():
    """Tests whether the function get_costs is adding all the calculated costs to dict_asset."""
    E2.get_costs(dict_asset, dict_economic)
    for k in (
        "costs_p_dispatch",
        "costs_cost_om",
        "costs_total",
        "costs_om",
        "annuity_total",
        ANNUITY_OM,
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
    list_true = ["annual_total_flow", OPTIMIZED_ADD_CAP]
    boolean = E2.all_list_in_dict(dict_asset, list_true)
    assert boolean is True


def test_all_list_in_dict_fails_due_to_not_included_keys():
    """Tests whether looking for list items in dict_asset is plausible."""
    list_false = ["flow", OPTIMIZED_ADD_CAP]
    boolean = E2.all_list_in_dict(dict_asset, list_false)
    assert boolean is False
