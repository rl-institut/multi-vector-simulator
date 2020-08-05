from pytest import approx

import src.C2_economic_functions as C2

project_life = 20
discount_factor = 0.1
investment_t0 = 220000
tax = 0.15
# please do not change project_life and lifetime as this will affect CAPEX calculations that depend on the number of investments
lifetime = {
    "equal project life": project_life,
    "smaller project life": project_life - 5,
    "bigger project life": project_life + 15,
}
present_value = 295000
crf = 0.12
annuity = 35400
annuity_factor = 1 / 0.12
exp_capex_equal_project_life = 253000
exp_capex_smaller_project_life = 307564.336
exp_capex_bigger_project_life = 236882.783
fuel_keys = {
    "fuel_price": 1.3,
    "fuel_price_change_annual": 0,
}


def test_annuity_factor():
    """

    Tests whether the MVS is correctly calculating the annuity factor
    """
    AF = C2.annuity_factor(project_life, discount_factor)
    assert AF == 1 / discount_factor - 1 / (
        discount_factor * (1 + discount_factor) ** project_life
    )


def test_crf():
    """

    Tests whether the MVS is correctly calculating the capital recovery factor
    """
    CRF = C2.crf(project_life, discount_factor)
    assert CRF == (discount_factor * (1 + discount_factor) ** project_life) / (
        (1 + discount_factor) ** project_life - 1
    )


def test_capex_from_investment_lifetime_equals_project_life():
    """

    Tests whether the MVS is correctly calculating the capital expenditure of the project if the lifetime is equal to project_life
    """
    CAPEX = C2.capex_from_investment(
        investment_t0,
        lifetime["equal project life"],
        project_life,
        discount_factor,
        tax,
    )
    assert round(CAPEX, 7) == exp_capex_equal_project_life


def test_capex_from_investment_lifetime_smaller_than_project_life():
    """

    Tests whether the MVS is correctly calculating the capital expenditure of the project if the lifetime is smaller than project_life
    """
    CAPEX = C2.capex_from_investment(
        investment_t0,
        lifetime["smaller project life"],
        project_life,
        discount_factor,
        tax,
    )
    assert CAPEX == approx(exp_capex_smaller_project_life, rel=1e-3)


def test_capex_from_investment_lifetime_bigger_than_project_life():
    """

    Tests whether the MVS is correctly calculating the capital expenditure of the project if the lifetime is bigger than project_life
    """
    CAPEX = C2.capex_from_investment(
        investment_t0,
        lifetime["bigger project life"],
        project_life,
        discount_factor,
        tax,
    )
    assert CAPEX == approx(exp_capex_bigger_project_life, rel=1e-3)


def test_annuity():
    """

    Tests whether the MVS is correctly calculating the annuity value
    """
    A = C2.annuity(present_value, crf)
    assert A == present_value * crf


def test_present_value_from_annuity():
    """

    Tests whether the MVS is correctly calculating the present value
    """
    PV_from_annuity = C2.present_value_from_annuity(annuity, annuity_factor)
    assert PV_from_annuity == annuity * annuity_factor


def test_fuel_price_present_value_without_fuel_price_change():
    """

    Tests whether the MVS is correctly calculating the present value of the fuel price over the lifetime of the project without fuel price change
    """
    C2.fuel_price_present_value(fuel_keys)
    assert fuel_keys["fuel_price"] == 1.3


def test_simulation_annuity_week():
    simulation_annuity = C2.simulation_annuity(365, 7)
    assert simulation_annuity == 7


def test_simulation_annuity_year():
    simulation_annuity = C2.simulation_annuity(365, 365)
    assert simulation_annuity == 365

