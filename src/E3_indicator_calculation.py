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
import logging

from src.constants import DEFAULT_WEIGHTS_ENERGY_CARRIERS
from src.constants import PROJECT_DATA
from src.constants_json_strings import (
    VALUE,
    LABEL,
    ECONOMIC_DATA,
    SIMULATION_SETTINGS,
    ENERGY_CONVERSION,
    ENERGY_PRODUCTION,
    ENERGY_PROVIDERS,
    ENERGY_CONSUMPTION,
    CONNECTED_FEEDIN_SINK,
    CRF,
    SECTORS,
    EXCESS,
    AUTO_SINK,
    ENERGY_VECTOR,
    KPI,
    KPI_SCALARS_DICT,
    KPI_UNCOUPLED_DICT,
    KPI_COST_MATRIX,
    LCOE_ASSET,
    COST_TOTAL,
    TOTAL_FLOW,
    TIMESERIES_TOTAL,
    RENEWABLE_ASSET_BOOL,
    RENEWABLE_SHARE_DSO,
    DSO_CONSUMPTION,
    TOTAL_RENEWABLE_GENERATION_IN_LES,
    TOTAL_NON_RENEWABLE_GENERATION_IN_LES,
    TOTAL_RENEWABLE_ENERGY_USE,
    TOTAL_NON_RENEWABLE_ENERGY_USE,
RENEWABLE_SHARE,
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

    Notes
    -----

    The totals are calculated for following parameters:
    - costs_total
    - costs_om_total
    - costs_investment_over_lifetime
    - costs_upfront_in_year_zero
    - costs_dispatch
    - costs_cost_om
    - annuity_total
    - annuity_om

    The levelized_cost_of_energy_of_asset are dropped from the list,
    as they do not hold any actual meaning for the whole energy system.
    The LCOE of the energy system is calculated seperately.

    """
    for column in dict_values[KPI][KPI_COST_MATRIX].columns:
        if column not in [LABEL, LCOE_ASSET]:
            dict_values[KPI][KPI_SCALARS_DICT].update(
                {column: dict_values[KPI][KPI_COST_MATRIX][column].sum()}
            )
    return


def total_demand_each_sector(dict_values):
    """
    Calculation of the total demand of each sector

    Parameters
    ----------
    dict_values :
        dict with all project input data and results up to E0

    Returns
    -------
    Updated KPI_SCALARS_DICT with
    - total demand of each energy carrier (original unit)
    - total demand of each energy carrier (electricity equivalent) 
    - total demand in electricity equivalent
    """

    # Define empty dict to gather the total demand of each energy carrier
    total_demand_dict = {}
    for sector in dict_values[PROJECT_DATA][SECTORS]:
        total_demand_dict.update({sector: 0})

    # determine all dso feedin sinks that should not be evaluated for the total demand
    dso_feedin_sinks = []
    for dso in dict_values[ENERGY_PROVIDERS]:
        dso_feedin_sinks.append(
            dict_values[ENERGY_PROVIDERS][dso][CONNECTED_FEEDIN_SINK]
        )

    # Loop though energy consumption assets to determine those that are demand
    for consumption_asset in dict_values[ENERGY_CONSUMPTION]:
        # Do not process feedin sinks but only demands
        if (
            consumption_asset not in dso_feedin_sinks
            and consumption_asset
            not in dict_values[SIMULATION_SETTINGS][EXCESS + AUTO_SINK]
        ):
            # get name of energy carrier
            energy_carrier = dict_values[ENERGY_CONSUMPTION][consumption_asset][
                ENERGY_VECTOR
            ]
            # check if energy carrier in total_demand dict
            # (might be unnecessary, check where dict_values[PROJECT_DATA][SECTORS] are defined)
            if energy_carrier not in total_demand_dict:
                logging.error(
                    f"Energy vector {energy_carrier} not in known energy sectors. Please double check."
                )
            else:
                total_demand_dict.update(
                    {
                        energy_carrier: total_demand_dict[energy_carrier]
                        + dict_values[ENERGY_CONSUMPTION][consumption_asset][
                            TOTAL_FLOW
                        ][VALUE]
                    }
                )

    # Write total demand per energy carrier as well as its electricity equivalent to dict_values
    total_demand_label = "total demand"
    total_demand_electricity_equivalent = 0
    for energy_carrier in total_demand_dict:
        energy_carrier_label = label_total_demand_energy_carrier(energy_carrier)
        # Define total demand of electricity carrier in original unit
        dict_values[KPI][KPI_SCALARS_DICT].update(
            {energy_carrier_label: total_demand_dict[energy_carrier]}
        )
        # Define total energy carrier demand in electricity equivalent
        dict_values[KPI][KPI_SCALARS_DICT].update(
            {
                add_suffix_electricity_equivalent(
                    energy_carrier_label
                ): total_demand_dict[energy_carrier]
                * DEFAULT_WEIGHTS_ENERGY_CARRIERS[energy_carrier][VALUE]
            }
        )
        # Add to total demand in electricity equivalent
        total_demand_electricity_equivalent += dict_values[KPI][KPI_SCALARS_DICT][
            add_suffix_electricity_equivalent(energy_carrier_label)
        ]
    # Define total demand in electricity equivalent
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {
            add_suffix_electricity_equivalent(
                total_demand_label
            ): total_demand_electricity_equivalent
        }
    )
    return


def label_total_demand_energy_carrier(energy_carrier):
    label = f"Total demand of {energy_carrier}"
    return label


def add_suffix_electricity_equivalent(label):
    label = label + "_electricity_equivalent"
    return label


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
            TOTAL_RENEWABLE_GENERATION_IN_LES: renewable_origin.copy(),
            TOTAL_NON_RENEWABLE_GENERATION_IN_LES: non_renewable_origin.copy(),
        }
    )

    for DSO in dict_values[ENERGY_PROVIDERS]:
        sector = dict_values[ENERGY_PROVIDERS][DSO][ENERGY_VECTOR]

        # Get source connected to the specific DSO in question
        DSO_source_name = DSO + DSO_CONSUMPTION

        # Add renewable share of energy consumption from DSO to the renewable origin (total)
        renewable_origin[sector] += (
            dict_values[ENERGY_PRODUCTION][DSO_source_name][TOTAL_FLOW][VALUE]
            * dict_values[ENERGY_PROVIDERS][DSO][RENEWABLE_SHARE_DSO][VALUE]
        )

        non_renewable_origin[sector] += dict_values[ENERGY_PRODUCTION][DSO_source_name][
            TOTAL_FLOW
        ][VALUE] * (1 - dict_values[ENERGY_PROVIDERS][DSO][RENEWABLE_SHARE_DSO][VALUE])

    dict_values[KPI][KPI_UNCOUPLED_DICT].update(
        {
            TOTAL_RENEWABLE_ENERGY_USE: renewable_origin,
            TOTAL_NON_RENEWABLE_ENERGY_USE: non_renewable_origin,
        }
    )

    for sector_specific_kpi in [
        TOTAL_RENEWABLE_GENERATION_IN_LES,
        TOTAL_NON_RENEWABLE_GENERATION_IN_LES,
        TOTAL_RENEWABLE_ENERGY_USE,
        TOTAL_NON_RENEWABLE_ENERGY_USE,
    ]:
        weighting_for_sector_coupled_kpi(dict_values, sector_specific_kpi)

    logging.info("Calculated renewable share of the LES.")
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
    dict_renewable_share = {}
    for sector in dict_values[PROJECT_DATA][SECTORS]:
        total_res = dict_values[KPI][KPI_UNCOUPLED_DICT][TOTAL_RENEWABLE_ENERGY_USE][
            sector
        ]
        total_non_res = dict_values[KPI][KPI_UNCOUPLED_DICT][
            TOTAL_NON_RENEWABLE_ENERGY_USE
        ][sector]
        dict_renewable_share.update(
            {sector: equation_renewable_share(total_res, total_non_res)}
        )
    dict_values[KPI][KPI_UNCOUPLED_DICT].update({RENEWABLE_SHARE: dict_renewable_share})

    total_res = dict_values[KPI][KPI_SCALARS_DICT][TOTAL_RENEWABLE_ENERGY_USE]
    total_non_res = dict_values[KPI][KPI_SCALARS_DICT][TOTAL_NON_RENEWABLE_ENERGY_USE]
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {RENEWABLE_SHARE: equation_renewable_share(total_res, total_non_res)}
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


def add_levelized_cost_of_energy_carriers(dict_values):
    r"""
    Adds levelized costs of all energy carriers and overall system to the scalar KPI.
    
    Parameters
    ----------
    dict_values: dict
        All simulation inputs and results

    Returns
    -------
    Updates KPI_SCALAR_DICT
    """
    # Abbreviate costs accessed
    NPC = dict_values[KPI][KPI_SCALARS_DICT][COST_TOTAL]

    # Get total demand in electricity equivalent
    total_demand_electricity_equivalent = dict_values[KPI][KPI_SCALARS_DICT][
        add_suffix_electricity_equivalent("total demand")
    ]

    # Loop through all energy carriers
    for energy_carrier in dict_values[PROJECT_DATA][SECTORS]:
        # Get energy carrier specific values
        energy_carrier_label = label_total_demand_energy_carrier(energy_carrier)
        total_flow_energy_carrier_eleq = dict_values[KPI][KPI_SCALARS_DICT][
            energy_carrier_label
        ]
        total_flow_energy_carrier = dict_values[KPI][KPI_SCALARS_DICT][
            add_suffix_electricity_equivalent(energy_carrier_label)
        ]
        # Calculate LCOE of energy carrier
        (
            lcoe_energy_carrier,
            attributed_costs,
        ) = equation_levelized_cost_of_energy_carrier(
            cost_total=NPC,
            crf=dict_values[ECONOMIC_DATA][CRF][VALUE],
            total_flow_energy_carrier_eleq=total_flow_energy_carrier_eleq,
            total_flow_energy_carrier=total_flow_energy_carrier,
            total_demand_electricity_equivalent=total_demand_electricity_equivalent,
        )

        # Update dict_values with ATTRIBUTED_COSTS and LCOE_energy_carrier
        dict_values[KPI][KPI_SCALARS_DICT].update(
            {
                f"Attributed costs of {energy_carrier}": attributed_costs,
                f"Levelized costs of energy equivalent of {energy_carrier}": lcoe_energy_carrier,
            }
        )
        logging.debug(
            f"Determined LCOE of energy carrier {energy_carrier}: {round(lcoe_energy_carrier, 2)}"
        )

    # Total demand
    lcoe_energy_carrier, attributed_costs = equation_levelized_cost_of_energy_carrier(
        cost_total=NPC,
        crf=dict_values[ECONOMIC_DATA][CRF][VALUE],
        total_flow_energy_carrier_eleq=total_demand_electricity_equivalent,
        total_flow_energy_carrier=total_demand_electricity_equivalent,
        total_demand_electricity_equivalent=total_demand_electricity_equivalent,
    )
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {f"Levelized costs of energy equivalent": lcoe_energy_carrier}
    )
    logging.debug(f"Determined LCOE of energy: {round(lcoe_energy_carrier, 2)}")
    logging.info("Calculated LCOE of the energy system.")
    return


def equation_levelized_cost_of_energy_carrier(
    cost_total,
    crf,
    total_flow_energy_carrier_eleq,
    total_demand_electricity_equivalent,
    total_flow_energy_carrier,
):
    r"""
    Calculates LCOE of each energy carrier of the system.

    Based on distributing the NPC of the energy system over the total weighted energy demand of the local energy system.
    This avoids that a conversion asset has to be defined as being used for a specific sector only,
    or that an energy production asset (eg. electricity) which is mainly used for powering energy conversion assets for another energy carrier (eg. H2)
    are increasing the costs of the first energy carrier (electricity),
    eventhough the costs should be attributed to the costs of the end-use of generation.

    Parameters
    ----------
    cost_total: float

    crf: float

    total_flow_energy_carrier_eleq: float

    total_demand_electricity_equivalent: float

    total_flow_energy_carrier:float

    Returns
    -------
        lcoe_energy_carrier: float
            Levelized costs of an energy carrier in a sector coupled system
    
        attributed_costs: float
            Costs attributed to a specific energy carrier

    Notes
    -----
    Please refer to the conference paper presented at the CIRED Workshop Berlin (see readthedocs) for more detail.

    The costs attributed to an energy carrier are calculated from the ratio of electricity equivalent of the energy carrier demand in focus to the electricity equivalent of the total demand:

    .. math: attributed costs = NPC \cdot \frac{Total electricity equivalent of energy carrier demand}{Total electricity equivalent of demand}

    The LCOE sets these attributed costs in relation to the energy carrier demand (in its original unit):

    .. math: LCOE energy carrier = \frac{attributed costs \cdot CRF}{total energy carrier demand}

    """
    attributed_costs = 0

    if total_demand_electricity_equivalent > 0:
        attributed_costs = (
            cost_total
            * total_flow_energy_carrier_eleq
            / total_demand_electricity_equivalent
        )

    if total_flow_energy_carrier > 0:
        lcoe_energy_carrier = attributed_costs * crf / total_flow_energy_carrier
    return lcoe_energy_carrier, attributed_costs


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
