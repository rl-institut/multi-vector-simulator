r"""
Module E3 - Indicator calculation
==================================

In module E3 the technical KPI are evaluated:
- calculate renewable share
- calculate degree of autonomy (DA)
- calculate degree of net zero energy (NZE)
- calculate total generation of each asset and total_internal_generation
- calculate total feedin electricity equivalent
- calculate energy flows between sectors
- calculate degree of sector coupling
- calculate onsite energy fraction (OEF)
- calculate onsite energy matching (OEM)
"""
import logging

from multi_vector_simulator.utils.constants import DEFAULT_WEIGHTS_ENERGY_CARRIERS
from multi_vector_simulator.utils.constants import PROJECT_DATA
from multi_vector_simulator.utils.constants_json_strings import (
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
    LES_ENERGY_VECTOR_S,
    EXCESS,
    AUTO_SINK,
    ENERGY_VECTOR,
    KPI,
    KPI_SCALARS_DICT,
    KPI_UNCOUPLED_DICT,
    KPI_COST_MATRIX,
    KPI_SCALAR_MATRIX,
    LCOE_ASSET,
    COST_TOTAL,
    TOTAL_FLOW,
    RENEWABLE_ASSET_BOOL,
    RENEWABLE_SHARE_DSO,
    DSO_CONSUMPTION,
    DSO_FEEDIN,
    DSO_CONSUMPTION,
    TOTAL_RENEWABLE_GENERATION_IN_LES,
    TOTAL_NON_RENEWABLE_GENERATION_IN_LES,
    TOTAL_GENERATION_IN_LES,
    TOTAL_RENEWABLE_ENERGY_USE,
    TOTAL_NON_RENEWABLE_ENERGY_USE,
    RENEWABLE_FACTOR,
    RENEWABLE_SHARE_OF_LOCAL_GENERATION,
    TOTAL_DEMAND,
    TOTAL_EXCESS,
    TOTAL_FEEDIN,
    TOTAL_CONSUMPTION_FROM_PROVIDERS,
    SUFFIX_ELECTRICITY_EQUIVALENT,
    LCOeleq,
    ATTRIBUTED_COSTS,
    DEGREE_OF_SECTOR_COUPLING,
    DEGREE_OF_AUTONOMY,
    ONSITE_ENERGY_FRACTION,
    ONSITE_ENERGY_MATCHING,
    EMISSION_FACTOR,
    TOTAL_EMISSIONS,
    SPECIFIC_EMISSIONS_ELEQ,
    UNIT,
    UNIT_SPECIFIC_EMISSIONS,
    UNIT_EMISSIONS,
    DEGREE_OF_NZE,
)


def all_totals(dict_values):
    """Calculate sum of all cost parameters

    Parameters
    ----------

    dict_values :
        dict all input parameters and results up to E0

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


def total_demand_and_excess_each_sector(dict_values):
    """
    Calculation of the total demand and total excess of each sector

    Both in original energy carrier unit and electricity equivalent

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
    - total excess of each energy carrier (original unit)
    - total excess of each energy carrier (electricity equivalent)
    - total excess in electricity equivalent

    Notes
    -----
    Tested with
    - test_add_levelized_cost_of_energy_carriers_one_sector()
    - test_add_levelized_cost_of_energy_carriers_two_sectors()
    - TestTechnicalKPI.renewable_factor_and_renewable_share_of_local_generation()
    """

    # Define empty dict to gather the total demand of each energy carrier
    total_demand_dict = {}
    total_excess_dict = {}
    for sector in dict_values[PROJECT_DATA][LES_ENERGY_VECTOR_S]:
        total_demand_dict.update({sector: 0})
        total_excess_dict.update({sector: 0})

    # determine all dso feedin sinks that should not be evaluated for the total demand
    dso_feedin_sinks = []
    for dso in dict_values[ENERGY_PROVIDERS]:
        dso_feedin_sinks.append(
            dict_values[ENERGY_PROVIDERS][dso][CONNECTED_FEEDIN_SINK]
        )

    # Loop though energy consumption assets to determine those that are demand
    for consumption_asset in dict_values[ENERGY_CONSUMPTION]:
        # Do not process feedin sinks neither for excess nor for demands
        if consumption_asset not in dso_feedin_sinks:
            # get name of energy carrier
            energy_carrier = dict_values[ENERGY_CONSUMPTION][consumption_asset][
                ENERGY_VECTOR
            ]
            # check if energy carrier in total_demand dict
            # (might be unnecessary, check where dict_values[PROJECT_DATA][LES_ENERGY_VECTOR_S] are defined)
            if energy_carrier not in total_demand_dict:
                logging.error(
                    f'Energy vector "{energy_carrier}" of asset {consumption_asset} not in known energy sectors. Please double check.'
                )
                total_demand_dict.update({energy_carrier: {}})

            # Evaluate excess
            if (
                consumption_asset
                in dict_values[SIMULATION_SETTINGS][EXCESS + AUTO_SINK]
            ):
                total_excess_dict.update(
                    {
                        energy_carrier: total_excess_dict[energy_carrier]
                        + dict_values[ENERGY_CONSUMPTION][consumption_asset][
                            TOTAL_FLOW
                        ][VALUE]
                    }
                )
            # Evaluate demands
            else:
                total_demand_dict.update(
                    {
                        energy_carrier: total_demand_dict[energy_carrier]
                        + dict_values[ENERGY_CONSUMPTION][consumption_asset][
                            TOTAL_FLOW
                        ][VALUE]
                    }
                )

    # Append total demand in electricity equivalent to kpi
    calculate_electricity_equivalent_for_a_set_of_aggregated_values(
        dict_values, total_demand_dict, kpi_name=TOTAL_DEMAND
    )

    # Append total excess in electricity equivalent to kpi
    calculate_electricity_equivalent_for_a_set_of_aggregated_values(
        dict_values, total_excess_dict, kpi_name=TOTAL_EXCESS
    )


def calculate_electricity_equivalent_for_a_set_of_aggregated_values(
    dict_values, dict_of_aggregated_flows, kpi_name
):
    r"""
    Calculates the electricity equivalent for a dict of aggregated flows and writes it to the KPI

    Parameters
    ----------
    dict_values: dict
        All simulation parameters

    dict_of_aggregated_flows: dict
        Dict of aggragated flows, with keys of energy carriers.

    kpi_name: str
        Name of the KPI to write to the results

    Returns
    -------
    Updated dict_values.
    """

    # For totalling aggregated electricity equivalents
    total_electricity_equivalent = 0

    # Write total demand per energy carrier as well as its electricity equivalent to dict_values
    for energy_carrier in dict_of_aggregated_flows:
        # Define total aggregated flow of energy carrier in original unit
        dict_values[KPI][KPI_SCALARS_DICT].update(
            {kpi_name + energy_carrier: dict_of_aggregated_flows[energy_carrier]}
        )
        # Define total aggregated flow of energy carrier in electricity equivalent
        dict_values[KPI][KPI_SCALARS_DICT].update(
            {
                kpi_name
                + energy_carrier
                + SUFFIX_ELECTRICITY_EQUIVALENT: dict_of_aggregated_flows[
                    energy_carrier
                ]
                * DEFAULT_WEIGHTS_ENERGY_CARRIERS[energy_carrier][VALUE]
            }
        )
        # Add to total aggregated flow in electricity equivalent
        total_electricity_equivalent += dict_values[KPI][KPI_SCALARS_DICT][
            kpi_name + energy_carrier + SUFFIX_ELECTRICITY_EQUIVALENT
        ]

    # Define total aggregated flow in electricity equivalent
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {kpi_name + SUFFIX_ELECTRICITY_EQUIVALENT: total_electricity_equivalent}
    )

    logging.info(
        f"The {kpi_name+SUFFIX_ELECTRICITY_EQUIVALENT} of the LES is: {round(total_electricity_equivalent)} kWheleq."
    )

    return total_electricity_equivalent


def add_total_renewable_and_non_renewable_energy_origin(dict_values):
    """Identifies all renewable generation assets and summs up their total generation to total renewable generation

    Parameters
    ----------
    dict_values :
        dict with all project input data and results up to E0

    Returns
    -------
    type
        Updated dict_values with total internal/overall renewable and non-renewable energy origin

    Notes
    -----
    Tested with
    - test_total_renewable_and_non_renewable_origin_of_each_sector()
    """
    dict_values[KPI].update({KPI_UNCOUPLED_DICT: {}})

    renewable_origin = {}
    non_renewable_origin = {}
    for sector in dict_values[PROJECT_DATA][LES_ENERGY_VECTOR_S]:
        renewable_origin.update({sector: 0})
        non_renewable_origin.update({sector: 0})

    # Aggregate the total generation of non renewable and renewable energy in the LES
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

    # Aggregate the total use of non renewable and renewable energy at DSO level
    for dso in dict_values[ENERGY_PROVIDERS]:
        sector = dict_values[ENERGY_PROVIDERS][dso][ENERGY_VECTOR]

        # Get source connected to the specific DSO in question
        DSO_source_name = dso + DSO_CONSUMPTION

        # Add renewable share of energy consumption from DSO to the renewable origin (total)
        renewable_origin[sector] += (
            dict_values[ENERGY_PRODUCTION][DSO_source_name][TOTAL_FLOW][VALUE]
            * dict_values[ENERGY_PROVIDERS][dso][RENEWABLE_SHARE_DSO][VALUE]
        )

        non_renewable_origin[sector] += dict_values[ENERGY_PRODUCTION][DSO_source_name][
            TOTAL_FLOW
        ][VALUE] * (1 - dict_values[ENERGY_PROVIDERS][dso][RENEWABLE_SHARE_DSO][VALUE])

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
    # calculate total generation, renewable + non-renewable
    dict_values[KPI][KPI_SCALARS_DICT][TOTAL_GENERATION_IN_LES] = (
        dict_values[KPI][KPI_SCALARS_DICT][TOTAL_RENEWABLE_GENERATION_IN_LES]
        + dict_values[KPI][KPI_SCALARS_DICT][TOTAL_NON_RENEWABLE_GENERATION_IN_LES]
    )

    logging.info("Calculated renewable share of the LES.")


def add_renewable_share_of_local_generation(dict_values):
    """Determination of renewable share of local energy production

        Parameters
    ----------
    dict_values :
        dict with all project information and results, after applying add_total_renewable_and_non_renewable_energy_origin
    sector :
        Sector for which renewable share is being calculated

    Returns
    -------
    type
        updated dict_values with renewable share of each sector as well as the system-wide KPI

    Notes
    -----
    Updates the KPI with RENEWABLE_SHARE_OF_LOCAL_GENERATION for each sector as well as system-wide KPI.

    Tested with
    * test_renewable_share_of_local_generation_one_sector()
    * test_renewable_share_of_local_generation_two_sectors()
    * TestTechnicalKPI.renewable_factor_and_renewable_share_of_local_generation()
    """

    dict_renewable_share = {}
    for sector in dict_values[PROJECT_DATA][LES_ENERGY_VECTOR_S]:
        # Defines the total renewable energy as the renewable production within the LES
        total_res = dict_values[KPI][KPI_UNCOUPLED_DICT][
            TOTAL_RENEWABLE_GENERATION_IN_LES
        ][sector]
        # Defines the total non-renewable energy as the non-renewable production within the LES
        total_non_res = dict_values[KPI][KPI_UNCOUPLED_DICT][
            TOTAL_NON_RENEWABLE_GENERATION_IN_LES
        ][sector]
        # Calculates the renewable factor for the current sector
        dict_renewable_share.update(
            {sector: equation_renewable_share(total_res, total_non_res)}
        )
    # Updates the KPI matrix for the individual sectors
    dict_values[KPI][KPI_UNCOUPLED_DICT].update(
        {RENEWABLE_SHARE_OF_LOCAL_GENERATION: dict_renewable_share}
    )

    # Calculation of the system-wide renewable factor
    total_res = dict_values[KPI][KPI_SCALARS_DICT][TOTAL_RENEWABLE_GENERATION_IN_LES]
    total_non_res = dict_values[KPI][KPI_SCALARS_DICT][
        TOTAL_NON_RENEWABLE_GENERATION_IN_LES
    ]

    # Updates the system-wide KPI matrix
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {
            RENEWABLE_SHARE_OF_LOCAL_GENERATION: equation_renewable_share(
                total_res, total_non_res
            )
        }
    )


def add_renewable_factor(dict_values):
    """Determination of renewable share of one sector

    Parameters
    ----------
    dict_values :
        dict with all project information and results, after applying add_total_renewable_and_non_renewable_energy_origin

    Returns
    -------
    type
        updated dict_values with renewable factor of each sector as well as system-wide indicator

    Notes
    -----
    Updates the KPI with RENEWABLE_FACTOR for each sector as well as system-wide KPI.


    Tested with
    - test_renewable_factor_one_sector
    - test_renewable_factor_two_sectors
    - TestTechnicalKPI.renewable_factor_and_renewable_share_of_local_generation()
    """
    dict_renewable_share = {}
    # Loops though the sectors
    for sector in dict_values[PROJECT_DATA][LES_ENERGY_VECTOR_S]:
        # Defines the total renewable energy as the renewable influx into the system (generation and consumption)
        total_res = dict_values[KPI][KPI_UNCOUPLED_DICT][TOTAL_RENEWABLE_ENERGY_USE][
            sector
        ]
        # Defines the total non-renewable energy as the non-renewable influx into the system (generation and consumption)
        total_non_res = dict_values[KPI][KPI_UNCOUPLED_DICT][
            TOTAL_NON_RENEWABLE_ENERGY_USE
        ][sector]
        # Calculates the renewable factor for the current sector
        dict_renewable_share.update(
            {sector: equation_renewable_share(total_res, total_non_res)}
        )
    # Updates the KPI matrix for the individual sectors
    dict_values[KPI][KPI_UNCOUPLED_DICT].update(
        {RENEWABLE_FACTOR: dict_renewable_share}
    )

    # Calculation of the system-wide renewable factor
    total_res = dict_values[KPI][KPI_SCALARS_DICT][TOTAL_RENEWABLE_ENERGY_USE]
    total_non_res = dict_values[KPI][KPI_SCALARS_DICT][TOTAL_NON_RENEWABLE_ENERGY_USE]
    # Updates the system-wide KPI matrix
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {RENEWABLE_FACTOR: equation_renewable_share(total_res, total_non_res)}
    )


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

    Notes
    -----
    Used both to calculate RENEWABLE_FACTOR and RENEWABLE_SHARE_OF_LOCAL_GENERATION.

    Equation:

    .. math::
            RES = \frac{total_res}{total_non_res + total_res}


    The renewable share is relative to generation, but not consumption of energy, the renewable share can not be larger 1.
    If there is no generation or consumption from a DSO within an energyVector and supply is solely reached by energy conversion from another vector, the renewable share is defined to be zero.

    * renewable share = 1 - all energy in the energy system is of renewable origin
    * renewable share < 1 - part of the energy in the system is of renewable origin
    * renewable share = 0 - no energy is of renewable origin


    Tested with:
    - test_renewable_share_equation_no_generation()
    - test_renewable_share_equation_below_1()
    - test_renewable_share_equation_is_0()
    - test_renewable_share_equation_is_1()
    """

    if total_res + total_non_res > 0:
        renewable_share = total_res / (total_non_res + total_res)
    else:
        renewable_share = 0
    return renewable_share


def add_degree_of_autonomy(dict_values):
    """
    Determines degree of autonomy and adds KPI to dict_values

    Parameters
    ----------
    dict_values: dict
        dict with all project information and results,
        after applying total_renewable_and_non_renewable_energy_origin and
        total_demand_and_excess_each_sector

    Returns
    -------
    None
        updated dict_values with the degree of autonomy

    Tested with
    - test_add_degree_of_autonomy()
    """

    total_consumption_from_energy_provider = dict_values[KPI][KPI_SCALARS_DICT][
        TOTAL_CONSUMPTION_FROM_PROVIDERS + SUFFIX_ELECTRICITY_EQUIVALENT
    ]
    total_demand = dict_values[KPI][KPI_SCALARS_DICT][
        TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT
    ]

    degree_of_autonomy = equation_degree_of_autonomy(
        total_consumption_from_energy_provider, total_demand
    )

    dict_values[KPI][KPI_SCALARS_DICT].update({DEGREE_OF_AUTONOMY: degree_of_autonomy})

    logging.debug(
        f"Calculated the {DEGREE_OF_AUTONOMY}: {round(degree_of_autonomy, 2)}"
    )
    logging.info(f"Calculated the {DEGREE_OF_AUTONOMY} of the LES.")


def equation_degree_of_autonomy(total_consumption_from_energy_provider, total_demand):
    """
    Calculates the degree of autonomy (DA).

    The degree of autonomy describes the relation of how much demand is supplied by local generation (as opposed to
    grid conumption) compared to the total demand of the system.

    Parameters
    ----------
    total_consumption_from_energy_provider: float
        total energy consumption from providers

    total_demand: float
        total demand

    Returns
    -------
    float
        degree of autonomy

    .. math::
        DA &=\frac{\sum_i {E_{demand} (i) \cdot w_i} - \sum_{i} {E_{consumption,provider,j} (j) \cdot w_j}}{\sum_i {E_{demand} (i) \cdot w_i}}

    A DA = 0 : Demand is fully supplied by DSO consumption
    DA = 1 : System is autonomous, ie. no DSO consumption is necessary

    Notice: As above, we apply a weighting based on Electricity Equivalent.

    Tested with
    - test_equation_degree_of_autonomy()
    """
    degree_of_autonomy = (
        total_demand - total_consumption_from_energy_provider
    ) / total_demand

    return degree_of_autonomy


def add_degree_of_net_zero_energy(dict_values):
    """
    Determines degree of net zero energy (NZE) and adds KPI to dict_values.

    Parameters
    ----------
    dict_values: dict
        dict with all project information and results,
        after applying total_renewable_and_non_renewable_energy_origin and
        total_demand_and_excess_each_sector

    Returns
    -------
    None
        updated dict_values with the degree of net zero energy

    Notes
    -----
    As for other KPI, we apply a weighting based on Electricity Equivalent.

    Tested with
    - test_add_degree_of_net_zero_energy()
    """

    total_renewable_generation = dict_values[KPI][KPI_SCALARS_DICT][
        TOTAL_RENEWABLE_GENERATION_IN_LES
    ]

    total_demand = dict_values[KPI][KPI_SCALARS_DICT][
        TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT
    ]

    total_excess = dict_values[KPI][KPI_SCALARS_DICT][
        TOTAL_EXCESS + SUFFIX_ELECTRICITY_EQUIVALENT
    ]

    degree_of_nze = equation_degree_of_net_zero_energy(
        total_renewable_generation, total_demand, total_excess
    )

    dict_values[KPI][KPI_SCALARS_DICT].update({DEGREE_OF_NZE: degree_of_nze})

    logging.debug(f"Calculated the {DEGREE_OF_NZE}: {round(degree_of_nze, 2)}")
    logging.info(f"Calculated the {DEGREE_OF_NZE} of the LES.")


def equation_degree_of_net_zero_energy(
    total_renewable_generation, total_demand, total_excess
):
    """
    Calculates the degree of net zero energy (NZE).

    In NZE systems import and export of energy is allowed while the balance over one
    year should be zero. If more energy is exported than imported it is plus-energy system.

    Parameters
    ----------
    total_renewable_generation: float
        total internal renewable generation of energy
    total_demand: float
        total demand
    total_excess: float
        Total Excess energy

    Returns
    -------
    float
        degree of net zero energy

    Notes
    -----

    .. math::
        Degree of NZE &=\frac{\sum_{i} {E_{RE\_generation,i} \cdot w_i - E_{excess, i} \cdot w_i}}{\sum_i {E_{demand, i} \cdot w_i}}

    Degree of NZE = 1 : System is a net zero energy system,
    Degree of NZE > 1 : system is a plus-energy system,
    Degree of NZE < 1 : system does not reach net zero balance, indicates by how much it fails to do so

    Tested with
    - test_equation_degree_of_net_zero_energy()

    """
    degree_of_nze = (total_renewable_generation - total_excess) / total_demand

    return degree_of_nze


def add_degree_of_sector_coupling(dict_values):
    r"""
    Determines the aggregated flows in between the sectors and the Degree of Sector Coupling.

    Takes into account the value of different energy carriers.

    Parameters
    ----------
    dict_values: dict
        dictionary with all project inputs and results, specifically the energyConversion assets and the outputs.

    Returns
    -------
    Energy equivalent of total conversion flows:

    .. math::
        E_{conversion,eq} = \sum_{i}{E_{conversion} (i) \cdot w_i}
        with i are conversion assets

    """
    # todo actually only flows that transform an energy carrier from one energy vector to the next should be added
    # maybe energyBusses helps?
    total_flow_of_energy_conversion_equivalent = 0
    for asset in dict_values[ENERGY_CONVERSION]:
        sector = dict_values[ENERGY_CONVERSION][asset][ENERGY_VECTOR]
        total_flow_of_energy_conversion_equivalent += (
            dict_values[ENERGY_CONVERSION][asset][TOTAL_FLOW][VALUE]
            * DEFAULT_WEIGHTS_ENERGY_CARRIERS[sector][VALUE]
        )

    dict_values[KPI][KPI_SCALARS_DICT].update(
        {"total_energy_conversion_flow": total_flow_of_energy_conversion_equivalent}
    )
    logging.debug("Determined total energy conversion flow in electricity equivalent.")

    # Calculate degree of sector coupling
    degree_of_sector_coupling = equation_degree_of_sector_coupling(
        total_flow_of_energy_conversion_equivalent,
        dict_values[KPI][KPI_SCALARS_DICT][
            TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT
        ],
    )
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {DEGREE_OF_SECTOR_COUPLING: degree_of_sector_coupling}
    )
    logging.debug(
        f"Calculated the {DEGREE_OF_SECTOR_COUPLING}: {round(degree_of_sector_coupling)}"
    )
    logging.info(f"Calculated the {DEGREE_OF_SECTOR_COUPLING} for the LES.")
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
    float
        Degree of sector coupling based on conversion flows and energy demands in electricity equivalent.

    .. math::
       DSC=\frac{\sum_{i,j}{E_{conversion} (i,j)⋅w_i}}{\sum_i {E_{demand} (i)⋅w_i}}

        with i,j \epsilon [Electricity,H2…]

    """
    degree_of_sector_coupling = (
        total_flow_of_energy_conversion_equivalent / total_demand_equivalent
    )
    return degree_of_sector_coupling


def add_total_feedin_electricity_equivalent(dict_values):
    """
    Determines the total grid feed-in with weighting of electricity equivalent.

    Parameters
    ----------
    dict_values: dict
        dict with all project information and results

    Returns
    -------
    None
        updated dict_values with KPI : total feedin

    Tested with
    - test_add_total_feedin_electricity_equivalent()
    """

    total_feedin_dict = {}
    # Get source connected to the specific DSO in question
    for dso in dict_values[ENERGY_PROVIDERS]:
        # load total flow into the dso sink
        feedin_sink = str(dso + DSO_FEEDIN + AUTO_SINK)
        energy_carrier = dict_values[ENERGY_CONSUMPTION][feedin_sink][ENERGY_VECTOR]
        total_feedin_dict.update({energy_carrier: {}})
        total_feedin_dict.update(
            {
                energy_carrier: dict_values[ENERGY_CONSUMPTION][feedin_sink][
                    TOTAL_FLOW
                ][VALUE]
            }
        )

    # Append total feedin in electricity equivalent to kpi
    calculate_electricity_equivalent_for_a_set_of_aggregated_values(
        dict_values, total_feedin_dict, kpi_name=TOTAL_FEEDIN
    )


def add_total_consumption_from_provider_electricity_equivalent(dict_values):
    """
    Determines the total consumption from energy providers with weighting of electricity equivalent.

    Parameters
    ----------
    dict_values: dict
        dict with all project information and results

    Returns
    -------
    None
        updated dict_values with KPI :
        - TOTAL_CONSUMPTION_FROM_PROVIDERS + electricity,
        - TOTAL_CONSUMPTION_FROM_PROVIDERS + electricity + SUFFIX_ELECTRICITY_EQUIVALENT
        - TOTAL_CONSUMPTION_FROM_PROVIDERS + SUFFIX_ELECTRICITY_EQUIVALENT

    Notes
    -----
    Tested with:
    - E3.test_add_total_consumption_from_provider_electricity_equivalent()
    """

    total_consumption_dict = {}
    # Get source connected to the specific DSO in question
    for dso in dict_values[ENERGY_PROVIDERS]:
        # load total flow into the dso sink
        consumption_source = str(dso + DSO_CONSUMPTION)
        energy_carrier = dict_values[ENERGY_PRODUCTION][consumption_source][
            ENERGY_VECTOR
        ]
        total_consumption_dict.update({energy_carrier: {}})
        total_consumption_dict.update(
            {
                energy_carrier: dict_values[ENERGY_PRODUCTION][consumption_source][
                    TOTAL_FLOW
                ][VALUE]
            }
        )

    # Append total feedin in electricity equivalent to kpi
    calculate_electricity_equivalent_for_a_set_of_aggregated_values(
        dict_values, total_consumption_dict, kpi_name=TOTAL_CONSUMPTION_FROM_PROVIDERS
    )


def add_onsite_energy_fraction(dict_values):
    """
    Determines onsite energy fraction (OEF), i.e. self-consumption, and adds KPI to dict_values

    Parameters
    ----------
    dict_values: dict
        dict with all project information and results
        after applying total_renewable_and_non_renewable_energy_origin
    
    Returns
    -------
    None
        updated dict_values with onsite energy fraction KPI

    Tested with
    - test_add_onsite_energy_fraction()
    """

    total_generation = dict_values[KPI][KPI_SCALARS_DICT][TOTAL_GENERATION_IN_LES]

    total_feedin = dict_values[KPI][KPI_SCALARS_DICT][
        TOTAL_FEEDIN + SUFFIX_ELECTRICITY_EQUIVALENT
    ]

    # calculate onsite energy fraction
    onsite_energy_fraction = equation_onsite_energy_fraction(
        total_generation, total_feedin
    )

    # save KPI  onsite energy fraction into KPI_SCALARS_DICT
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {ONSITE_ENERGY_FRACTION: onsite_energy_fraction}
    )
    logging.debug(
        f"Calculated the {ONSITE_ENERGY_FRACTION}: {round(onsite_energy_fraction, 2)}"
    )
    logging.info(f"Calculated the {ONSITE_ENERGY_FRACTION} of the LES.")


def equation_onsite_energy_fraction(total_generation, total_feedin):
    """
    Calculates onsite energy fraction (OEF), i.e. self-consumption.

    OEF describes the fraction of all locally generated energy that is consumed
    by the system itself.

    Parameters
    ----------
    total_generation: float
        Energy equivalent of total generation flows
    total_feedin: float
        Total feed into the grid

    Returns
    -------
        float
            Onsite energy fraction.

    .. math::
            OEF &=\frac{\sum_{i} {E_{generation} (i) \cdot w_i} - E_{gridfeedin}(i) \cdot w_i}{\sum_{i} {E_{generation} (i) \cdot w_i}}

            &OEF \epsilon \text{[0,1]}

    Tested with
    - test_equation_onsite_energy_fraction()
    """

    if total_generation != 0:
        onsite_energy_fraction = (total_generation - total_feedin) / total_generation
    else:
        # TODO find a better way to deal with this
        onsite_energy_fraction = 0
        logging.warning(
            "The total local energy generation is zero, therefore the onsite energy fraction cannot be calculated and is set to 0"
        )

    return onsite_energy_fraction


def add_onsite_energy_matching(dict_values):
    """
    Determines onsite energy matching (OEM), i.e. self-sufficiency, and adds KPI to dict_values

    Parameters
    ----------
    dict_values: dict
        dict with all project information and results
        after applying total_renewable_and_non_renewable_energy_origin and
        total_demand_and_excess_each_sector and
        add_onsite_energy_fraction
    
    Returns
    -------
    None
        updated dict_values with onsite energy matching KPI

    Tested with
    - test_add_onsite_energy_matching()
    """

    total_generation = dict_values[KPI][KPI_SCALARS_DICT][TOTAL_GENERATION_IN_LES]

    total_feedin = dict_values[KPI][KPI_SCALARS_DICT][
        TOTAL_FEEDIN + SUFFIX_ELECTRICITY_EQUIVALENT
    ]

    total_excess = dict_values[KPI][KPI_SCALARS_DICT][
        TOTAL_EXCESS + SUFFIX_ELECTRICITY_EQUIVALENT
    ]

    total_demand = dict_values[KPI][KPI_SCALARS_DICT][
        TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT
    ]

    # calculate onsite energy matching
    onsite_energy_matching = equation_onsite_energy_matching(
        total_generation, total_feedin, total_excess, total_demand
    )
    # save KPI onsite energy matching to KPI Scalars
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {ONSITE_ENERGY_MATCHING: onsite_energy_matching}
    )
    logging.debug(
        f"Calculated the {ONSITE_ENERGY_MATCHING}: {round(onsite_energy_matching, 2)}"
    )
    logging.info(f"Calculated the {ONSITE_ENERGY_MATCHING} of the LES.")


def equation_onsite_energy_matching(
    total_generation, total_feedin, total_excess, total_demand
):
    """
    Calculates onsite energy matching (OEM), i.e. self-sufficiency.

    OEM describes the fraction of the total demand that can be
    covered by the locally generated energy.

    Parameters
    ----------
    total_generation: float
        Energy equivalent of total conversion flows
    total_feedin: float
        Total feed into the grid
    total_excess: float
        Total Excess energy
    total_demand: float
        Total demand

    Returns
    -------
    Onsite energy matching.

    .. math::
            OEM &=\frac{\sum_{i} {E_{generation} (i) \cdot w_i} - E_{gridfeedin}(i) \cdot w_i - E_{excess}(i) \cdot w_i}{\sum_i {E_{demand} (i) \cdot w_i}}

            &OEM \epsilon \text{[0,1]}

    Tested with
    - test_equation_onsite_energy_matching()
    """
    onsite_energy_matching = (
        total_generation - total_feedin - total_excess
    ) / total_demand
    return onsite_energy_matching


def calculate_emissions_from_flow(dict_asset):
    r"""
    Calculates the total emissions of the asset in 'dict_asset' in kg per year.

    Parameters
    ----------
    dict_asset : dict
        Contains information about the asset.

    Notes
    -----
    Tested with:
    - E3.test_calculate_emissions_from_flow()
    - E3.test_calculate_emissions_from_flow_zero_emissions

    Returns
    -------
    None
        Updated `dict_asset` with TOTAL_EMISSIONS of the asset in kgCO2eq/a (UNIT_EMISSIONS).

    """
    emissions = dict_asset[TOTAL_FLOW][VALUE] * dict_asset[EMISSION_FACTOR][VALUE]
    dict_asset.update({TOTAL_EMISSIONS: {VALUE: emissions, UNIT: UNIT_EMISSIONS}})


def add_total_emissions(dict_values):
    r"""
    Calculates the total emission of the energy system in kgCO2eq/a and adds KPI to `dict_values`.

    Parameters
    ----------
    dict_values: dict
        All simulation inputs and results

    Returns
    -------
    None
        Updated `dict_values` with TOTAL_EMISSIONS of the energy system in kgCO2eq/a
        (UNIT_EMISSIONS).

    Notes
    -----

    Tested with:
    - E3.test_add_total_emissions()

    """
    # sum up emissions of all assets [kgCO2eq/a]
    emissions = dict_values[KPI][KPI_SCALAR_MATRIX][TOTAL_EMISSIONS].sum()  # data frame
    dict_values[KPI][KPI_SCALARS_DICT].update({TOTAL_EMISSIONS: emissions})
    logging.debug(
        f"Calculated the {TOTAL_EMISSIONS}: {round(emissions, 2)} {UNIT_EMISSIONS}."
    )
    logging.info(f"Calculated the {TOTAL_EMISSIONS} ({UNIT_EMISSIONS}) of the LES.")


def add_specific_emissions_per_electricity_equivalent(dict_values):
    r"""
    Calculates the specific emissions of the energy system per kWheleq and adds KPI to `dict_values`.

    Parameters
    ----------
    dict_values: dict
        All simulation inputs and results including TOTAL_EMISSIONS calculated in
        `E3.calculate_emissions_from_flow`.

    Notes
    -----
    This funtion is run after `E3.calculate_emissions_from_flow`.

    Tested with:
    - E3.test_add_specific_emissions_per_electricity_equivalent()

    Returns
    -------
    None
        Updated `dict_values` with SPECIFIC_EMISSIONS_ELEQ in kgCO2eq/kWheleq (UNIT_SPECIFIC_EMISSIONS).

    """
    # emissions per kWheleq
    emissions_kWheleq = (
        dict_values[KPI][KPI_SCALARS_DICT][TOTAL_EMISSIONS]
        / dict_values[KPI][KPI_SCALARS_DICT][
            TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT
        ]
    )
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {SPECIFIC_EMISSIONS_ELEQ: emissions_kWheleq}
    )
    logging.debug(
        f"Calculated the {SPECIFIC_EMISSIONS_ELEQ}: {round(emissions_kWheleq, 2)} {UNIT_SPECIFIC_EMISSIONS}."
    )
    logging.info(
        f"Calculated the {SPECIFIC_EMISSIONS_ELEQ} ({UNIT_SPECIFIC_EMISSIONS}) of the LES."
    )


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
        TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT
    ]

    # Loop through all energy carriers
    for energy_carrier in dict_values[PROJECT_DATA][LES_ENERGY_VECTOR_S]:
        # Get energy carrier specific values
        energy_carrier_label = TOTAL_DEMAND + energy_carrier
        total_flow_energy_carrier_eleq = dict_values[KPI][KPI_SCALARS_DICT][
            energy_carrier_label
        ]
        total_flow_energy_carrier = dict_values[KPI][KPI_SCALARS_DICT][
            energy_carrier_label + SUFFIX_ELECTRICITY_EQUIVALENT
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
                ATTRIBUTED_COSTS + energy_carrier: attributed_costs,
                LCOeleq + energy_carrier: lcoe_energy_carrier,
            }
        )
        logging.debug(
            f"Determined {LCOeleq} {energy_carrier}: {round(lcoe_energy_carrier, 2)}"
        )

    # Total demand
    lcoe_energy_carrier, attributed_costs = equation_levelized_cost_of_energy_carrier(
        cost_total=NPC,
        crf=dict_values[ECONOMIC_DATA][CRF][VALUE],
        total_flow_energy_carrier_eleq=total_demand_electricity_equivalent,
        total_flow_energy_carrier=total_demand_electricity_equivalent,
        total_demand_electricity_equivalent=total_demand_electricity_equivalent,
    )
    dict_values[KPI][KPI_SCALARS_DICT].update({LCOeleq: lcoe_energy_carrier})
    logging.debug(f"Determined {LCOeleq}: {round(lcoe_energy_carrier, 2)}")
    logging.info("Calculated LCOE of the energy system.")


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

    .. math:: attributed costs = NPC \cdot \frac{Total electricity equivalent of energy carrier demand}{Total electricity equivalent of demand}

    The LCOE sets these attributed costs in relation to the energy carrier demand (in its original unit):

    .. math:: LCOE energy carrier = \frac{attributed costs \cdot CRF}{total energy carrier demand}

    Tested with:
    - test_equation_levelized_cost_of_energy_carrier_total_demand_electricity_equivalent_larger_0_total_flow_energy_carrier_larger_0()
    - test_equation_levelized_cost_of_energy_carrier_total_demand_electricity_equivalent_larger_0_total_flow_energy_carrier_is_0()
    - test_equation_levelized_cost_of_energy_carrier_total_demand_electricity_equivalent_is_0_total_flow_energy_carrier_is_0()
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
    else:
        lcoe_energy_carrier = 0
    return lcoe_energy_carrier, attributed_costs


def weighting_for_sector_coupled_kpi(dict_values, kpi_name):
    """Calculates the weighted kpi for a specific kpi_name both for a single sector and system-wide

    Parameters
    ----------
    dict_values :
        dict with all project information and results, including KPI_UNCOUPLED_DICT with the specifc kpi_name in question
    kpi_name :
        str with the kpi which should be weighted

    Returns
    -------
    type
        Append specific KPI that describes sector-coupled system to dict_values[KPI][KPI_SCALARS_DICT]
        Appends specific KPI in energy equivalent to each sector to dict_values[KPI][KPI_UNCOUPLED_DICT]
    """
    total_energy_equivalent = 0
    dict_energy_equivalents_per_sector = {}

    for sector in dict_values[PROJECT_DATA][LES_ENERGY_VECTOR_S]:
        if sector in DEFAULT_WEIGHTS_ENERGY_CARRIERS:
            energy_equivalent = (
                dict_values[KPI][KPI_UNCOUPLED_DICT][kpi_name][sector]
                * DEFAULT_WEIGHTS_ENERGY_CARRIERS[sector][VALUE]
            )
            total_energy_equivalent += energy_equivalent
            dict_energy_equivalents_per_sector.update({sector: energy_equivalent})
        else:
            raise ValueError(
                f"The electricity equivalent value of energy carrier {sector} is not defined. "
                f"Please add this information to the variable DEFAULT_WEIGHTS_ENERGY_CARRIERS in constants.py."
            )

    # Describes the energy equivalent of the kpi in question, eg. the renewable generation, so that comparison is easier
    dict_values[KPI][KPI_UNCOUPLED_DICT].update(
        {kpi_name + SUFFIX_ELECTRICITY_EQUIVALENT: dict_energy_equivalents_per_sector}
    )
    # Describes system wide total of the energy equivalent of the kpi
    dict_values[KPI][KPI_SCALARS_DICT].update({kpi_name: total_energy_equivalent})
