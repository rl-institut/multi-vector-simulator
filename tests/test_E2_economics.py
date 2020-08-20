import pandas as pd
import pytest

import src.E2_economics as E2

from src.constants_json_strings import (
    UNIT,
    CURR,
    DEVELOPMENT_COSTS,
    SPECIFIC_COSTS,
    DISPATCH_PRICE,
    VALUE,
    LABEL,
    INSTALLED_CAP,
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
    COST_DISPATCH,
    COST_OM_FIX,
    LCOE_ASSET,
    ENERGY_CONSUMPTION,
    ENERGY_CONVERSION,
    ENERGY_PRODUCTION,
    ENERGY_STORAGE,
    TOTAL_FLOW,
)

dict_asset = {
    LABEL: "DSO_feedin_sink",
    DISPATCH_PRICE: {VALUE: -0.4, UNIT: "currency/kWh"},
    SPECIFIC_COSTS: {VALUE: 0, UNIT: "currency/kW"},
    INSTALLED_CAP: {VALUE: 0.0, UNIT: UNIT},
    DEVELOPMENT_COSTS: {VALUE: 0, UNIT: CURR},
    LIFETIME_SPECIFIC_COST: {VALUE: 0.0, UNIT: "currency/kW"},
    LIFETIME_SPECIFIC_COST_OM: {VALUE: 0.0, UNIT: "currency/ye"},
    LIFETIME_PRICE_DISPATCH: {VALUE: -5.505932460595773, UNIT: "?"},
    ANNUAL_TOTAL_FLOW: {VALUE: 0.0, UNIT: "kWh"},
    OPTIMIZED_ADD_CAP: {VALUE: 0, UNIT: "?"},
}

dict_economic = {
    CRF: {VALUE: 0.07264891149004721, UNIT: "?"},
}

dict_values = {
    ENERGY_PRODUCTION: {
        "PV": {ANNUITY_TOTAL: {VALUE: 50000}, TOTAL_FLOW: {VALUE: 470000}}
    },
    ENERGY_CONVERSION: {
        "inverter": {ANNUITY_TOTAL: {VALUE: 15000}, TOTAL_FLOW: {VALUE: 0}}
    },
    ENERGY_CONSUMPTION: {
        "demand": {ANNUITY_TOTAL: {VALUE: 0}, TOTAL_FLOW: {VALUE: 40000}}
    },
    ENERGY_STORAGE: {
        "battery_1": {
            "input power": {ANNUITY_TOTAL: {VALUE: 1000}, TOTAL_FLOW: {VALUE: 1000}},
            "output power": {
                ANNUITY_TOTAL: {VALUE: 30000},
                TOTAL_FLOW: {VALUE: 240000},
            },
            "storage capacity": {
                ANNUITY_TOTAL: {VALUE: 25000},
                TOTAL_FLOW: {VALUE: 200000},
            },
        },
        "battery_2": {
            "input power": {ANNUITY_TOTAL: {VALUE: 1000}, TOTAL_FLOW: {VALUE: 1000}},
            "output power": {ANNUITY_TOTAL: {VALUE: 30000}, TOTAL_FLOW: {VALUE: 0}},
            "storage capacity": {
                ANNUITY_TOTAL: {VALUE: 25000},
                TOTAL_FLOW: {VALUE: 200000},
            },
        },
    },
}

exp_lcoe_pv = 50000 / 470000
exp_lcoe_demand = 0
exp_lcoe_battery_1 = (1000 + 30000 + 25000) / 240000


def test_all_cost_info_parameters_added_to_dict_asset():
    """Tests whether the function get_costs is adding all the calculated costs to dict_asset."""
    E2.get_costs(dict_asset, dict_economic)
    for k in (
        COST_DISPATCH,
        COST_OM_FIX,
        COST_TOTAL,
        COST_OM_TOTAL,
        ANNUITY_TOTAL,
        ANNUITY_OM,
    ):
        assert k in dict_asset

def test_calculate_costs_replacement():
    cost_replacement = E2.calculate_costs_replacement(costs_investment=700, costs_upfront=500)
    assert cost_replacement == 200

def test_calculate_costs_investment():
    costs = E2.calculate_costs_investment(specific_cost=100, capacity=5, development_costs=200)
    assert costs == 700

asset = "an_asset"
flow = pd.Series([1,1,1])
def test_calculate_annual_dispatch_expenditures_float():
    dispatch_expenditure = E2.calculate_dispatch_expenditures(dispatch_price=1, flow=flow, asset=asset)
    assert dispatch_expenditure == 3

def test_calculate_annual_dispatch_expenditures_pd_Series():
    dispatch_price = pd.Series([1, 2, 3])
    dispatch_expenditure = E2.calculate_dispatch_expenditures(dispatch_price, flow, asset)
    assert dispatch_expenditure == 6

def test_calculate_annual_dispatch_expenditures_else():
    with pytest.raises(E2.UnexpectedValueError):
            E2.calculate_dispatch_expenditures([1, 2], flow, asset)

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


def test_calculation_of_lcoe_of_asset_total_flow_is_0():
    """Tests if LCOE is set to None with TOTAL_FLOW of asset is 0"""
    for group in [ENERGY_CONVERSION, ENERGY_STORAGE]:
        for asset in dict_values[group]:
            E2.lcoe_assets(dict_values[group][asset], group)
    assert dict_values[ENERGY_CONVERSION]["inverter"][LCOE_ASSET][VALUE] is None
    assert dict_values[ENERGY_STORAGE]["battery_2"][LCOE_ASSET][VALUE] is None


def test_calculation_of_lcoe_asset_storage_flow_not_0_provider_flow_not_0():
    """Tests whether the LCOE is correctly calculated for each asset in the different asset groups"""
    for group in [ENERGY_PRODUCTION, ENERGY_CONSUMPTION, ENERGY_STORAGE]:
        for asset in dict_values[group]:
            E2.lcoe_assets(dict_values[group][asset], group)
    assert dict_values[ENERGY_PRODUCTION]["PV"][LCOE_ASSET][VALUE] == exp_lcoe_pv
    assert (
        dict_values[ENERGY_CONSUMPTION]["demand"][LCOE_ASSET][VALUE] == exp_lcoe_demand
    )
    assert (
        dict_values[ENERGY_STORAGE]["battery_1"][LCOE_ASSET][VALUE]
        == exp_lcoe_battery_1
    )
