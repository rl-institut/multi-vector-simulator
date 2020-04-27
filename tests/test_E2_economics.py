import src.E2_economics as E2


dict_asset = {
    "lifetime_capex_var": {"value": 10, "unit": "year"},
    "capex_fix": {"value": 16000, "unit": "currency"},
    "optimizedAddCap": {"value": 7000, "unit": "currency"},
    "capex_var": {"value": 4000, "unit": "currency/unit"},
    "annual_total_flow": {"value": 50000, "unit": "kWh"},
    "lifetime_opex_var": {"value": 10, "unit": "year"},
    "price": {"value": 2, "unit": "currency"},
    "installedCap": {"value": 1000, "unit": "kWh"},
    "lifetime_opex_fix": {"value": 10, "unit": "year"},
}

dict_asset_test = {
    "lifetime_capex_var": {"value": 10, "unit": "year"},
    "capex_fix": {"value": 16000, "unit": "currency"},
    "optimizedAddCap": {"value": 7000, "unit": "currency"},
    "capex_var": {"value": 4000, "unit": "currency/unit"},
    "annual_total_flow": {"value": 50000, "unit": "kWh"},
    "lifetime_opex_var": {"value": 10, "unit": "year"},
    "price": {"value": 2, "unit": "currency"},
    "installedCap": {"value": 1000, "unit": "kWh"},
    "lifetime_opex_fix": {"value": 10, "unit": "year"},
    "costs_investment": {"value": 86000},
    "costs_upfront": {"value": 27000},
    "costs_opex_var": {"value": 500000},
    "costs_energy": {"value": 100000},
    "costs_opex_fix": {"value": 80000},
    "costs_total": {"value": 693000, "unit": "currency"},
    "cost_om": {"value": 680000, "unit": "currency"},
    "annuity_total": {"value": 83160.0, "unit": "currency/year"},
    "annuity_om": {"value": 81600.0, "unit": "currency/year"},
}

economic_data = {"crf": {"value": 0.12}}

cost = 10000
total_costs = 5000
Dict_2 = {}
Dict_3 = {
    "value_0": 0,
    "value_1": 1,
    "value_2": 2,
}
list_test_true = ["value_0", "value_1", "value_2"]
list_test_false = ["value_4", "value_5"]


def test_get_costs():

    """

    Returns
    -------

    """
    E2.get_costs(dict_asset, economic_data)
    assert dict_asset == dict_asset_test


def test_add_costs_and_total():
    """

    Returns
    -------

    """
    Total_Costs = E2.add_costs_and_total(Dict_2, "cost", cost, total_costs)
    assert Total_Costs == cost + total_costs


def test_all_list_in_dict_true():
    """

    Returns
    -------

    """
    Boolean = E2.all_list_in_dict(Dict_3, list_test_true)
    assert Boolean == True


def test_all_list_in_dict_true():
    """

    Returns
    -------

    """
    Boolean = E2.all_list_in_dict(Dict_3, list_test_false)
    assert Boolean == False
