import src.C2_economic_functions as e_functions

project_life = 20
wacc = 0.1
# investment_t0, lifetime, tax

def test_annuity_factor_calculation():
    """
    Tests whether the MVS is correctly calculating the annuity factor
    Returns
    -------

    """
    AF = e_functions.annuity_factor(project_life, wacc)
    assert AF == 8.51356


def test_crf():
    """
    Tests whether the MVS is correctly calculating the capital recovery factor
    Returns
    -------

    """
    CRF = e_functions.crf(project_life, wacc)
    assert CRF == 0.11746

def test_capex_from_investment():


def test_annuity():
    """
    Tests whether the MVS is correctly calculating the annuity value
    Returns
    -------

    """

def test_present_value_from_annuity():
    """
    Tests whether the MVS is correctly calculating the present value
    Returns
    -------

    """

def test_fuel_price_present_value():


