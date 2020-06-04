# todo check whether this is the most recent version
# - there were some project costs included wrongly,
# and something with the replacement costs
"""
Module C2 performs the economic pre-processing of MVS' input parameters.
It includes basic economic formulas.

Functionalities:
- Calculate annuity factor
- calculate crf depending on year
- calculate specific lifetime capex, considering replacement costs and residual value of the asset
- calculate annuity from present costs
- calculate present costs based on annuity
- calculate effective fuel price cost, in case there is a annual fuel price change (this functionality still has to be checked in this module)
"""

from src.constants_json_strings import CRF

# annuity factor to calculate present value of cash flows
def annuity_factor(project_life, wacc):
    """
    Calculates the annuity factor, which in turn in used to calculate the present value of annuities (instalments)

    :param project_life: time period over which the costs of the system occur
    :param wacc: weighted average cost of capital, which is the after-tax average cost of various capital sources
    :return: financial value "annuity factor". Dividing a present cost by tha annuity factor returns its annuity, multiplying an annuity with the annuity factor returns its present value
    """
    # discount_rate was replaced here by wacc
    annuity_factor = 1 / wacc - 1 / (wacc * (1 + wacc) ** project_life)
    return annuity_factor


# accounting factor to translate present value to annual cash flows
def crf(project_life, wacc):
    """
    Calculates the capital recovery ratio used to determine the present value of a series of equal payments (annuity)

    :param project_life: time period over which the costs of the system occur
    :param wacc: weighted average cost of capital, which is the after-tax average cost of various capital sources
    :return: capital recovery factor, a ratio used to calculate the present value of an annuity
    """
    crf = (wacc * (1 + wacc) ** project_life) / ((1 + wacc) ** project_life - 1)
    return crf


def capex_from_investment(investment_t0, lifetime, project_life, wacc, tax):
    """
    Calculates the capital expenditures, also known as CapEx. CapEx represent the total funds used to acquire or upgrade an asset

    :param investment_t0: first investment at the beginning of the project made at year 0
    :param lifetime: time period over which investments and re-investments can occur. can be equal to, longer or shorter than project_life
    :param project_life: time period over which the costs of the system occur
    :param wacc: weighted average cost of capital, which is the after-tax average cost of various capital sources
    :param tax: compulsory financial charge paid to the government
    :return: capital expenditure for an asset over project lifetime
    """
    # [quantity, investment, installation, weight, lifetime, om, first_investment]
    if project_life == lifetime:
        number_of_investments = 1
    else:
        number_of_investments = int(round(project_life / lifetime + 0.5))
    # costs with quantity and import tax at t=0
    first_time_investment = investment_t0 * (1 + tax)

    for count_of_replacements in range(0, number_of_investments):
        # Very first investment is in year 0
        if count_of_replacements == 0:
            capex = first_time_investment
        else:
            # replacements taking place in year = number_of_replacement * lifetime
            if count_of_replacements * lifetime != project_life:
                capex = capex + first_time_investment / (
                    (1 + wacc) ** (count_of_replacements * lifetime)
                )

    # Subtraction of component value at end of life with last replacement (= number_of_investments - 1)
    if number_of_investments * lifetime > project_life:
        last_investment = first_time_investment / (
            (1 + wacc) ** ((number_of_investments - 1) * lifetime)
        )
        linear_depreciation_last_investment = last_investment / lifetime
        capex = capex - linear_depreciation_last_investment * (
            number_of_investments * lifetime - project_life
        )

    return capex


def annuity(present_value, crf):
    """
    Calculates the annuity which is a fixed stream of payments incurred by investments in assets

    :param present_value: current equivalent value of a set of future cash flows for an asset
    :param crf: ratio used to calculate the present value of an annuity
    :return: annuity, i.e. payment made at equal intervals
    """
    annuity = present_value * crf
    return annuity


def present_value_from_annuity(annuity, annuity_factor):
    """
    Calculates the present value of future instalments from an annuity

    :param annuity: payment made at equal intervals
    :param annuity_factor: financial value
    :return: present value of future payments from an annuity
    """
    present_value = annuity * annuity_factor
    return present_value


def fuel_price_present_value(economics,):
    """
    Calculates the present value of the fuel price over the lifetime of the project, taking into consideration the annual price change

    :param economics: dict with fuel data values
    :return: present value of the fuel price over the lifetime of the project
    """
    cash_flow_fuel_l = 0
    fuel_price_i = economics["fuel_price"]
    # todo check this calculation again!
    if economics["fuel_price_change_annual"] == 0:
        economics.update({"price_fuel": fuel_price_i})
    else:
        for i in range(0, economics["project_lifetime"]):
            cash_flow_fuel_l += fuel_price_i / (1 + economics["wacc"]) ** (i)
            fuel_price_i = fuel_price_i * (1 + economics["fuel_price_change_annual"])
        economics.update({"price_fuel": cash_flow_fuel_l * economics[CRF]})


def simulation_annuity(annuity, days):
    """
    Scaling annuity to timeframe
    Updating all annuities above to annuities "for the timeframe", so that optimization is based on more adequate
    costs. Includes project_cost_annuity, distribution_grid_cost_annuity, maingrid_extension_cost_annuity for
    consistency eventhough these are not used in optimization.

    Parameters
    ----------
    annuity
    days

    Returns
    -------

    """
    simulation_annuity = annuity / 365 * days
    return simulation_annuity
