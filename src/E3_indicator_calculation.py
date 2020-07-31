r"""
Module E3 indicator calculation
-------------------------------

In module E3 the technical KPI are evaluated:
- calculate renewable share
- calculate degree of autonomy
- calculate total generation of each asset
- calculate energy flows between sectors
- calculate degree of autonomy me
- calculate degree of sector coupling
"""

from src.constants import DEFAULT_WEIGHTS_ENERGY_CARRIERS
from src.constants import PROJECT_DATA
from src.constants_json_strings import (
    VALUE,
    LABEL,
    ENERGY_CONVERSION,
    ENERGY_PRODUCTION,
    ENERGY_PROVIDERS,
    SECTORS,
    ENERGY_VECTOR,
    KPI,
    KPI_SCALARS_DICT,
    KPI_UNCOUPLED_DICT,
    KPI_COST_MATRIX,
    TOTAL_FLOW,
    RENEWABLE_ASSET_BOOL,
    RENEWABLE_SHARE_DSO,
    CONNECTED_CONSUMPTION_SOURCES,
)


def all_totals(dict_values):
    """Calculate sum of all cost parameters

    Parameters
    ----------
    dict_values :
        dict all input parameters and restults up to E0

    Returns
    -------
    type
        List of all total cost parameters for the project

    """
    for column in dict_values[KPI][KPI_COST_MATRIX].columns:
        if column != LABEL:
            dict_values[KPI][KPI_SCALARS_DICT].update(
                {column: dict_values[KPI][KPI_COST_MATRIX][column].sum()}
            )
    return


def total_demand_each_sector(dict_values):
    """

    Parameters
    ----------
    dict_values :
        dict with all project input data and results up to E0

    Returns
    -------

    """
    return


def total_renewable_and_non_renewable_energy_origin(dict_values):
    """Identifies all renewable generation assets and summs up their total generation to total renewable generation

    Parameters
    ----------
    dict_values :
        dict with all project input data and results up to E0

    Returns
    -------
    type
        Updated dict_values with total internal/overall renewable and non-renewable energy origin

    """
    dict_values[KPI].update({KPI_UNCOUPLED_DICT: {}})

    renewable_origin = {}
    non_renewable_origin = {}
    for sector in dict_values[PROJECT_DATA][SECTORS]:
        renewable_origin.update({sector: 0})
        non_renewable_origin.update({sector: 0})

    for asset in dict_values[ENERGY_PRODUCTION]:
        if RENEWABLE_ASSET_BOOL in dict_values[ENERGY_PRODUCTION][asset]:
            sector = dict_values[ENERGY_PRODUCTION][asset][ENERGY_VECTOR]
            if (
                dict_values[ENERGY_PRODUCTION][asset][RENEWABLE_ASSET_BOOL][VALUE]
                is True
            ):
                renewable_origin[sector] += dict_values[ENERGY_PRODUCTION][asset][
                    TOTAL_FLOW
                ][VALUE]
            else:
                non_renewable_origin[sector] += dict_values[ENERGY_PRODUCTION][asset][
                    TOTAL_FLOW
                ][VALUE]

    dict_values[KPI][KPI_UNCOUPLED_DICT].update(
        {
            "Total internal renewable generation": renewable_origin.copy(),
            "Total internal non-renewable generation": non_renewable_origin.copy(),
        }
    )

    for DSO in dict_values[ENERGY_PROVIDERS]:
        sector = dict_values[ENERGY_PROVIDERS][DSO][ENERGY_VECTOR]
        for DSO_source in dict_values[ENERGY_PROVIDERS][DSO][
            CONNECTED_CONSUMPTION_SOURCE
        ]:
            renewable_origin[sector] += (
                dict_values[ENERGY_PRODUCTION][DSO_source][TOTAL_FLOW][VALUE]
                * dict_values[ENERGY_PROVIDERS][DSO][RENEWABLE_SHARE_DSO][VALUE]
            )
            non_renewable_origin[sector] += dict_values[ENERGY_PRODUCTION][DSO_source][
                TOTAL_FLOW
            ][VALUE] * (
                1 - dict_values[ENERGY_PROVIDERS][DSO][RENEWABLE_SHARE_DSO][VALUE]
            )

    dict_values[KPI][KPI_UNCOUPLED_DICT].update(
        {
            "Total renewable energy use": renewable_origin,
            "Total non-renewable energy use": non_renewable_origin,
        }
    )

    for sector_specific_kpi in [
        "Total internal renewable generation",
        "Total internal non-renewable generation",
        "Total renewable energy use",
        "Total non-renewable energy use",
    ]:
        weighting_for_sector_coupled_kpi(dict_values, sector_specific_kpi)

    return


def renewable_share(dict_values):
    """Determination of renewable share of one sector

    Parameters
    ----------
    dict_values :
        dict with all project information and results, after applying total_renewable_and_non_renewable_energy_origin
    sector :
        Sector for which renewable share is being calculated

    Returns
    -------
    type
        updated dict_values with renewable share of a specific sector

    """
    kpi_name = "Renewable share"
    dict_renewable_share = {}
    for sector in dict_values[PROJECT_DATA][SECTORS]:
        total_res = dict_values[KPI][KPI_UNCOUPLED_DICT]["Total renewable energy use"][
            sector
        ]
        total_non_res = dict_values[KPI][KPI_UNCOUPLED_DICT][
            "Total non-renewable energy use"
        ][sector]
        dict_renewable_share.update(
            {sector: equation_renewable_share(total_res, total_non_res)}
        )
    dict_values[KPI][KPI_UNCOUPLED_DICT].update({kpi_name: dict_renewable_share})

    total_res = dict_values[KPI][KPI_SCALARS_DICT]["Total renewable energy use"]
    total_non_res = dict_values[KPI][KPI_SCALARS_DICT]["Total non-renewable energy use"]
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {kpi_name: equation_renewable_share(total_res, total_non_res)}
    )
    return


def equation_renewable_share(total_res, total_non_res):
    """Calculates the renewable share

    Parameters
    ----------
    total_res :
        Renewable generation of a system

    total_non_res :
        Non-renewable generation of a system

    Returns
    -------
    type
        Renewable share

    .. math::
            RES = \frac{total_res}{total_non_res + total_res}

            =\frac{\sum_i {E_{RES,generation} (i)⋅w_i}}{\sum_j {E_{generation}(j)⋅w_j}+\sum_k {E_{grid} (k)}}

            with i \epsilon [PV,Geothermal,…]

            and j \epsilon [generation assets 1,2,…]

            and  k \epsilon [DSO 1,2…]

        renewable share = 1 - all energy in the energy system is of renewable origin
        renewable share < 1 - part of the energy in the system is of renewable origin
        renewable share = 0 - no energy is of renewable origin

        As for now this is relative to generation, but not consumption of energy, the renewable share can not be larger 1. If in future however the renewable share is calculated relative to the energy consumption, a renewable share larger 1 is possible in case of overly high renewable gerneation within the system that is later fed into the DSO grid.
        If there is no generation or consumption from a DSO withing an energyVector and supply is solely reached by energy conversion from another vector, the renewable share is defined to be zero.

    """
    if total_res + total_non_res > 0:
        renewable_share = total_res / (total_non_res + total_res)
    else:
        renewable_share = 0
    return renewable_share


def equation_degree_of_autonomy():
    return degree_of_autonomy


def assert_aggregated_flows_of_energy_conversion_equivalent(dict_values):
    """
    Determines the aggregated flows in between the sectors, taking into account the value of different energy carriers.
    This will be used to calculate the degree of sector coupling at the pilot sites.

    Parameters
    ----------
    dict_values: dict
        dictionary with all project inputs and results, specifically the energyConversion assets and the outputs.

    Returns
    -------
    Energy equivalent of total conversion flows:

    .. math:: E_{conversion,eq} = \sum_{i}{E_{conversion} (i)⋅w_i}

            with i are conversion assets

    """
    total_flow_of_energy_conversion_equivalent = 0
    for asset in dict_values[ENERGY_CONVERSION]:
        sector = dict_values[ENERGY_CONVERSION][asset][ENERGY_VECTOR]
        total_flow_of_energy_conversion_equivalent += (
            dict_values[ENERGY_CONVERSION][asset]["total_aggregated_flow"]
            * DEFAULT_WEIGHTS_ENERGY_CARRIERS[sector][VALUE]
        )

    dict_values[KPI][KPI_SCALARS_DICT].update(
        {
            "total_energy_conversion_flow": total_flow_of_energy_conversion_equivalent
        }  # needs units!
    )
    return total_flow_of_energy_conversion_equivalent


def equation_degree_of_sector_coupling(
    total_flow_of_energy_conversion_equivalent, total_demand_equivalent
):
    """Calculates degree of sector coupling.

    Parameters
    ----------
    total_flow_of_energy_conversion_equivalent: float
        Energy equivalent of total conversion flows

    total_demand_equivalent: float
        Energy equivalent of total energy demand

    Returns
    -------
    Degree of sector coupling based on conversion flows and energy demands in electricity equivalent.

    .. math::
       DSC=\frac{\sum_{i,j}{E_{conversion} (i,j)⋅w_i}}{\sum_i {E_{demand} (i)⋅w_i}}

        with i,j \epsilon [Electricity,H2…]

    """
    degree_of_sector_coupling = (
        total_flow_of_energy_conversion_equivalent / total_demand_equivalent
    )
    return degree_of_sector_coupling


def equation_onsite_energy_fraction():
    return onsite_energy_fraction


def equation_onsite_energy_matching():
    return onsite_energy_matching


def equation_co2_emissions(dict_values):
    co2_emissions = 0
    for asset in dict_values[ENERGY_PRODUCTION]:
        co2_emissions += (
            dict_values[ENERGY_PRODUCTION][asset]["total_aggregated_flow"][VALUE]
            * dict_values[ENERGY_PRODUCTION][asset]["emissionFactor"][VALUE]
        )
    return co2_emissions


def weighting_for_sector_coupled_kpi(dict_values, kpi_name):
    """Calculates the weighted kpi for a specific kpi_name

    Parameters
    ----------
    dict_values :
        dict with all project information and results, including KPI_UNCOUPLED_DICT with the specifc kpi_name in question
    kpi_name :
        str with the kpi which should be weighted

    Returns
    -------
    type
        Specific KPI that describes sector-coupled system

    """
    energy_equivalent = 0

    for sector in dict_values[PROJECT_DATA][SECTORS]:
        if sector in DEFAULT_WEIGHTS_ENERGY_CARRIERS:
            energy_equivalent += (
                dict_values[KPI][KPI_UNCOUPLED_DICT][kpi_name][sector]
                * DEFAULT_WEIGHTS_ENERGY_CARRIERS[sector][VALUE]
            )
        else:
            raise ValueError(
                f"The electricity equivalent value of energy carrier {sector} is not defined. "
                f"Please add this information to the variable DEFAULT_WEIGHTS_ENERGY_CARRIERS in constants.py."
            )

        dict_values[KPI][KPI_SCALARS_DICT].update({kpi_name: energy_equivalent})
    return
