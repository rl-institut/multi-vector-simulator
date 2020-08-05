import pandas as pd

import pytest

from src.constants import TYPE_STR, UNIT_HOUR
from src.constants_json_strings import DISPATCH_PRICE, VALUE, UNIT, LIFETIME_PRICE_DISPATCH, PROJECT_DURATION, ANNUITY_FACTOR, CRF, DISCOUNTFACTOR, TAX
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
    assert CAPEX == pytest.approx(exp_capex_smaller_project_life, rel=1e-3)


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
    assert CAPEX == pytest.approx(exp_capex_bigger_project_life, rel=1e-3)


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


# Tests connected to LIFETIME_PRICE_DISPATCH

economic_data = {
    PROJECT_DURATION: {VALUE: project_life},
    ANNUITY_FACTOR: {VALUE: annuity_factor},
    CRF: {VALUE: crf},
    DISCOUNTFACTOR: {VALUE: discount_factor},
    TAX: {VALUE: tax},
}

def test_determine_lifetime_price_dispatch_as_int():
    dict_asset = {DISPATCH_PRICE: {VALUE: 1},
                  UNIT: "kW"}
    C2.determine_lifetime_price_dispatch(dict_asset, economic_data)
    assert LIFETIME_PRICE_DISPATCH in dict_asset.keys()
    assert isinstance(dict_asset[LIFETIME_PRICE_DISPATCH][VALUE], float) or isinstance(
        dict_asset[LIFETIME_PRICE_DISPATCH][VALUE], int
    )
    assert dict_asset[LIFETIME_PRICE_DISPATCH][VALUE] == 1 * annuity_factor


def test_determine_lifetime_price_dispatch_as_float():
    dict_asset = {DISPATCH_PRICE: {VALUE: 1.5},
                  UNIT: UNIT}
    C2.determine_lifetime_price_dispatch(dict_asset, economic_data)
    assert LIFETIME_PRICE_DISPATCH in dict_asset.keys()
    assert isinstance(dict_asset[LIFETIME_PRICE_DISPATCH][VALUE], float)
    assert dict_asset[LIFETIME_PRICE_DISPATCH][VALUE] == 1.5 * annuity_factor
    assert dict_asset[LIFETIME_PRICE_DISPATCH][UNIT] == UNIT + "/" + UNIT_HOUR


def test_determine_lifetime_price_dispatch_as_list():
    dict_asset = {DISPATCH_PRICE: {VALUE: [1.0, 1.0]},
                  UNIT: UNIT}
    C2.determine_lifetime_price_dispatch(dict_asset, economic_data)
    assert LIFETIME_PRICE_DISPATCH in dict_asset.keys()
    assert isinstance(dict_asset[LIFETIME_PRICE_DISPATCH][VALUE], list)
    assert dict_asset[LIFETIME_PRICE_DISPATCH][VALUE] == [1 * annuity_factor, 1 * annuity_factor]

TEST_START_TIME = "2020-01-01 00:00"
TEST_PERIODS = 3
VALUES = [0, 1, 2]

pandas_DatetimeIndex = pd.date_range(
    start=TEST_START_TIME, periods=TEST_PERIODS, freq="60min"
)
pandas_Series = pd.Series(VALUES, index=pandas_DatetimeIndex)

def test_determine_lifetime_price_dispatch_as_timeseries():
    dict_asset = {DISPATCH_PRICE: {VALUE: pandas_Series},
                  UNIT: UNIT}
    C2.determine_lifetime_price_dispatch(dict_asset, economic_data)
    assert LIFETIME_PRICE_DISPATCH in dict_asset.keys()
    assert isinstance(dict_asset[LIFETIME_PRICE_DISPATCH][VALUE], pd.Series)
    assert dict_asset[LIFETIME_PRICE_DISPATCH][VALUE][0] == 0*annuity_factor
    assert dict_asset[LIFETIME_PRICE_DISPATCH][VALUE][1] == 1*annuity_factor
    assert dict_asset[LIFETIME_PRICE_DISPATCH][VALUE][2] == 2*annuity_factor


def test_determine_lifetime_price_dispatch_as_list_with_pdSeries():
    dict_asset = {DISPATCH_PRICE: {VALUE: [1.0, pandas_Series]},
                  UNIT: UNIT}
    C2.determine_lifetime_price_dispatch(dict_asset, economic_data)
    assert LIFETIME_PRICE_DISPATCH in dict_asset.keys()
    assert isinstance(dict_asset[LIFETIME_PRICE_DISPATCH][VALUE], list)
    assert dict_asset[LIFETIME_PRICE_DISPATCH][VALUE][0] == 1 * annuity_factor
    assert dict_asset[LIFETIME_PRICE_DISPATCH][VALUE][1][0] == 0*annuity_factor
    assert dict_asset[LIFETIME_PRICE_DISPATCH][VALUE][1][1] == 1*annuity_factor
    assert dict_asset[LIFETIME_PRICE_DISPATCH][VALUE][1][2] == 2*annuity_factor

def test_determine_lifetime_price_dispatch_is_other():
    dict_asset = {DISPATCH_PRICE: {VALUE: TYPE_STR},
                  UNIT: UNIT}
    with pytest.raises(ValueError):
        C2.determine_lifetime_price_dispatch(dict_asset, economic_data)