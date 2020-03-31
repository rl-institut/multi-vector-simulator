import src.C2_economic_functions as e_functions

project_life = 20
wacc = 0.1
investment_t0 = 220000
tax = 0.15
lifetime = [20, 15]
present_value = 295000
fuel_keys = {
    "fuel_price": 1.3,
    "fuel_price_change_annual": 0,
    "project_lifetime": project_life,
    "wacc": wacc
}


def test_annuity_factor():
    """

    Tests whether the MVS is correctly calculating the annuity factor
    """
    AF = e_functions.annuity_factor(project_life, wacc)
    assert AF == 1 / 0.1 - 1 / (0.1 * (1 + 0.1) ** 20)


def test_crf():
    """

    Tests whether the MVS is correctly calculating the capital recovery factor
    """
    CRF = e_functions.crf(project_life, wacc)
    assert CRF == (0.1 * (1 + 0.1) ** 20) / ((1 + 0.1) ** 20 - 1)


def test_capex_from_investment(lifetime):
    """

    Tests whether the MVS is correctly calculating the capital expenditure of the project
    """
    for years in lifetime:
        if years == project_life:
            CAPEX = e_functions.capex_from_investment(investment_t0, years, project_life,wacc,tax)
            assert CAPEX == 220000*(1+0.15)
        else:
            CAPEX = e_functions.capex_from_investment(investment_t0, years, project_life, wacc, tax)
            first_investment = 220000*(1+0.15)
            assert CAPEX == first_investment + first_investment / (1 + 0.1) ** (15 * 1) + first_investment \
                   + first_investment / (1 + 0.1) ** (15 * 1) + first_investment / (1 + 0.1) ** (15 * 2) \
                   - ((first_investment / ((1 + 0.1) ** 15)) / 15) * (2 * 15 - 20)


def test_annuity():
    """

    Tests whether the MVS is correctly calculating the annuity value
    """
    CRF = e_functions.crf(project_life, wacc)
    A = e_functions.annuity(present_value,CRF)
    assert A == 295000 * ((0.1 * (1 + 0.1) ** 20) / ((1 + 0.1) ** 20 - 1))


def test_present_value_from_annuity():
    """

    Tests whether the MVS is correctly calculating the present value
    """
    A = e_functions.annuity(present_value, CRF)
    AF = e_functions.annuity_factor(project_life, wacc)
    PV_from_annuity = e_functions.present_value_from_annuity(A, AF)
    assert PV_from_annuity == 295000 * ((0.1 * (1 + 0.1) ** 20) / ((1 + 0.1) ** 20 - 1)) * (1 / 0.1 - 1 / (0.1 * (1 + 0.1) ** 20))


def test_fuel_price_present_value(economics):
    """

    Tests whether the MVS is correctly calculating the present value of the fuel price over the lifetime of the project
    """
    PV_fuel_price = e_functions.fuel_price_present_value(fuel_keys)
    assert PV_fuel_price == 1.3

    fuel_keys["fuel_price_change_annual"] = 0.008
    fuel_keys["crf"] = e_functions.crf(project_life, wacc)
    PV_fuel_price = e_functions.fuel_price_present_value(fuel_keys)
    # still not sure how not to use float number in assert
    assert PV_fuel_price == 13.06049955 * ((0.1 * (1 + 0.1) ** 20) / ((1 + 0.1) ** 20 - 1))
