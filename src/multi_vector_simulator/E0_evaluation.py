"""
Module E0 - evaluation
======================

Module E0 evaluates the oemof results and calculates the KPI
- define dictionary entry for kpi matrix
- define dictionary entry for cost matrix
- store all results to matrix
"""

import logging

import oemof.solph as solph
import pandas as pd

import multi_vector_simulator.E1_process_results as E1
import multi_vector_simulator.E2_economics as E2
import multi_vector_simulator.E3_indicator_calculation as E3

import multi_vector_simulator.E4_verification as E4

from multi_vector_simulator.utils.constants import SOC

from multi_vector_simulator.utils.constants_json_strings import (
    UNIT,
    ENERGY_CONVERSION,
    ENERGY_CONSUMPTION,
    ENERGY_PRODUCTION,
    ENERGY_STORAGE,
    ENERGY_BUSSES,
    VALUE,
    SIMULATION_SETTINGS,
    ECONOMIC_DATA,
    INPUT_POWER,
    OUTPUT_POWER,
    STORAGE_CAPACITY,
    INFLOW_DIRECTION,
    OUTFLOW_DIRECTION,
    KPI,
    KPI_COST_MATRIX,
    KPI_SCALAR_MATRIX,
    KPI_SCALARS_DICT,
    OPTIMIZED_FLOWS,
    LABEL,
    INSTALLED_CAP,
    TIMESERIES_SOC,
    KPI_UNCOUPLED_DICT,
    CONSTRAINTS,
    MAXIMUM_EMISSIONS,
    NET_ZERO_ENERGY,
    MINIMAL_DEGREE_OF_AUTONOMY,
    MINIMAL_RENEWABLE_FACTOR,
    RENEWABLE_FACTOR,
    DEGREE_OF_AUTONOMY,
    FIX_COST,
    OPTIMIZED_ADD_CAP,
    LIFETIME_PRICE_DISPATCH,
    FLOW,
    COST_DISPATCH,
)

from multi_vector_simulator.utils.constants_output import (
    KPI_COST_MATRIX_ENTRIES,
    KPI_SCALAR_MATRIX_ENTRIES,
)


def evaluate_dict(dict_values, results_main, results_meta):
    """
    Processes all simulation outputs by evaluating oemof results, asset capacities and dispatch as well as all KPIs.

    Parameters
    ----------
    dict_values: dict
        simulation parameters

    results_main: DataFrame
        oemof simulation results as output by processing.results()

    results_meta: DataFrame
        oemof simulation meta information as output by processing.meta_results()

    Returns
    -------

    Notes
    -----

    Tested with:
    - test_E0.evaluation.test_evaluate_dict_append_new_fields()
    - test_E0.evaluation.test_evaluate_dict_important_fields_in_output_dict()
    - test_E0.evaluation.test_evaluate_dict_fields_values_in_output_dict_are_dataframes()
    """

    initalize_kpi(dict_values)

    bus_data = {}
    # Store all information related to busses in bus_data
    for bus in dict_values[ENERGY_BUSSES]:
        # Read all energy flows from busses
        bus_data.update({bus: solph.views.node(results_main, bus)})

    logging.info("Evaluating optimized capacities and dispatch.")
    # Evaluate timeseries and store to a large DataFrame for each bus:
    E1.get_timeseries_per_bus(dict_values, bus_data)

    # Store all information related to storages in bus_data, as storage capacity acts as a bus
    for storage in dict_values[ENERGY_STORAGE]:
        bus_data.update(
            {
                dict_values[ENERGY_STORAGE][storage][LABEL]: solph.views.node(
                    results_main, dict_values[ENERGY_STORAGE][storage][LABEL],
                )
            }
        )
        E1.get_storage_results(
            dict_values[SIMULATION_SETTINGS],
            bus_data[dict_values[ENERGY_STORAGE][storage][LABEL]],
            dict_values[ENERGY_STORAGE][storage],
        )

        for storage_item in [STORAGE_CAPACITY, INPUT_POWER, OUTPUT_POWER]:
            E2.get_costs(
                dict_values[ENERGY_STORAGE][storage][storage_item],
                dict_values[ECONOMIC_DATA],
            )

        E2.lcoe_assets(dict_values[ENERGY_STORAGE][storage], ENERGY_STORAGE)
        for storage_item in [STORAGE_CAPACITY, INPUT_POWER, OUTPUT_POWER]:
            store_result_matrix(
                dict_values[KPI], dict_values[ENERGY_STORAGE][storage][storage_item]
            )

        if (
            dict_values[ENERGY_STORAGE][storage][INFLOW_DIRECTION]
            in dict_values[OPTIMIZED_FLOWS].keys()
        ) or (
            dict_values[ENERGY_STORAGE][storage][OUTFLOW_DIRECTION]
            in dict_values[OPTIMIZED_FLOWS].keys()
        ):
            bus_name = dict_values[ENERGY_STORAGE][storage][INFLOW_DIRECTION]
            inflow_direction = dict_values[ENERGY_STORAGE][storage][INFLOW_DIRECTION]
            timeseries_name = (
                dict_values[ENERGY_STORAGE][storage][LABEL]
                + " ("
                + str(
                    round(
                        dict_values[ENERGY_STORAGE][storage][STORAGE_CAPACITY][
                            OPTIMIZED_ADD_CAP
                        ][VALUE]
                        + dict_values[ENERGY_STORAGE][storage][STORAGE_CAPACITY][
                            INSTALLED_CAP
                        ][VALUE],
                        1,
                    )
                )
                + dict_values[ENERGY_STORAGE][storage][STORAGE_CAPACITY][
                    OPTIMIZED_ADD_CAP
                ][UNIT]
                + f") {SOC}"
            )

            dict_values[OPTIMIZED_FLOWS][inflow_direction][
                timeseries_name
            ] = dict_values[ENERGY_STORAGE][storage][TIMESERIES_SOC]

    for group in [ENERGY_CONVERSION, ENERGY_PRODUCTION, ENERGY_CONSUMPTION]:
        for asset in dict_values[group]:
            E1.get_results(
                settings=dict_values[SIMULATION_SETTINGS],
                bus_data=bus_data,
                dict_asset=dict_values[group][asset],
                asset_group=group,
            )
            E2.get_costs(dict_values[group][asset], dict_values[ECONOMIC_DATA])
            E2.lcoe_assets(dict_values[group][asset], group)
            if group == ENERGY_PRODUCTION:
                E3.calculate_emissions_from_flow(dict_values[group][asset])
            store_result_matrix(dict_values[KPI], dict_values[group][asset])

    # Add fix project costs
    process_fixcost(dict_values)

    logging.info("Evaluating key performance indicators of the system")
    E3.all_totals(dict_values)
    E3.total_demand_and_excess_each_sector(dict_values)
    E3.add_total_feedin_electricity_equivalent(dict_values)
    E3.add_total_consumption_from_provider_electricity_equivalent(dict_values)
    E3.add_levelized_cost_of_energy_carriers(dict_values)
    E3.add_total_renewable_and_non_renewable_energy_origin(dict_values)
    E3.add_renewable_share_of_local_generation(dict_values)
    E3.add_renewable_factor(dict_values)
    # E3.add_degree_of_sector_coupling(dict_values) feature not finished
    E3.add_onsite_energy_fraction(dict_values)
    E3.add_onsite_energy_matching(dict_values)
    E3.add_degree_of_autonomy(dict_values)
    E3.add_degree_of_net_zero_energy(dict_values)
    E3.add_total_emissions(dict_values)
    E3.add_specific_emissions_per_electricity_equivalent(dict_values)

    # Tests and checks
    logging.info("Running validity checks.")

    if MINIMAL_RENEWABLE_FACTOR in dict_values[CONSTRAINTS]:
        E4.minimal_constraint_test(
            dict_values, MINIMAL_RENEWABLE_FACTOR, RENEWABLE_FACTOR
        )

    if MINIMAL_DEGREE_OF_AUTONOMY in dict_values[CONSTRAINTS]:
        E4.minimal_constraint_test(
            dict_values, MINIMAL_DEGREE_OF_AUTONOMY, DEGREE_OF_AUTONOMY
        )
    if MAXIMUM_EMISSIONS in dict_values[CONSTRAINTS]:
        E4.maximum_emissions_test(dict_values)

    if NET_ZERO_ENERGY in dict_values[CONSTRAINTS]:
        E4.net_zero_energy_constraint_test(dict_values)

    E4.detect_excessive_excess_generation_in_bus(dict_values)
    E4.verify_state_of_charge(dict_values)

    # Format KPI about energy generation into a pd.DataFrame
    dict_values[KPI][KPI_UNCOUPLED_DICT] = pd.DataFrame.from_dict(
        dict_values[KPI][KPI_UNCOUPLED_DICT], orient="index"
    )


def store_result_matrix(dict_kpi, dict_asset, fix_cost=False):
    """
    Storing results to vector and then result matrix for saving it in csv.
    Defined value types: Str, bool, None, dict (with key "VALUE"), else (int, float)

    Parameters
    ----------
    dict_kpi: dict
        dictionary with the two kpi groups (costs and scalars), which are pd.DF

    dict_asset: dict
        all information known for a specific asset

    fix_cost: Boolean
        If fix_cost is True, then no new row is added to KPI_SCALAR_MATRIX, as there are no KPI to update.
        Costs in KPI_COST_MATRIX however are added.

    Returns
    -------
    Updated dict_kpi DF, with new row of kpis of the specific asset.


    """

    round_to_comma = 5

    for kpi_storage in [KPI_COST_MATRIX, KPI_SCALAR_MATRIX]:
        if fix_cost == True and kpi_storage == KPI_SCALAR_MATRIX:
            pass
        else:
            asset_result_dict = {}
            for key in dict_kpi[kpi_storage].columns.values:
                # Check if called value is in oemof results -> Remember: check if pandas index has certain index: pd.object.index.contains(key)
                if key in dict_asset:
                    if isinstance(dict_asset[key], str):
                        asset_result_dict.update({key: dict_asset[key]})
                    elif isinstance(dict_asset[key], bool):
                        asset_result_dict.update({key: dict_asset[key]})
                    elif dict_asset[key] is None:
                        asset_result_dict.update({key: None})
                    elif isinstance(dict_asset[key], dict):
                        if VALUE in dict_asset[key].keys():
                            if dict_asset[key][VALUE] is not None:
                                asset_result_dict.update(
                                    {key: round(dict_asset[key][VALUE], round_to_comma)}
                                )
                    else:
                        asset_result_dict.update(
                            {key: round(dict_asset[key], round_to_comma)}
                        )

            asset_result_df = pd.DataFrame([asset_result_dict])

            dict_kpi.update(
                {
                    kpi_storage: pd.concat(
                        [dict_kpi[kpi_storage], asset_result_df], ignore_index=True
                    )
                }
            )


def initalize_kpi(dict_values):
    r"""
    Adds basic structure of KPI to dict_values to gather them later on.

    Parameters
    ----------
    dict_values: dict
        All simulation data, but without any results

    Returns
    -------
    Updated dict_values with KPI structure, made up from KPI_COST_MATRIX, KPI_SCALAR_MATRIX and KPI_SCALARS_DICT.

    """
    dict_values.update(
        {
            KPI: {
                KPI_COST_MATRIX: pd.DataFrame(columns=KPI_COST_MATRIX_ENTRIES),
                KPI_SCALAR_MATRIX: pd.DataFrame(columns=KPI_SCALAR_MATRIX_ENTRIES),
                KPI_SCALARS_DICT: {},
            }
        }
    )


def process_fixcost(dict_values):
    r"""
    Adds fix costs of the project to the economic evaluation of the energy system.

    Parameters
    ----------
    dict_values: dict
        All simulation data with inputs and results of the assets

    Returns
    -------
    Updated dict_values with costs attributed in dict values also appended to the dict_values[KPI] (scalar results)

    Notes
    -----

    Function is tested with:
    - test_E0_evaluation.test_process_fixcost()
    """
    for asset in dict_values[FIX_COST]:
        # Add parameters that are needed for E2.get_costs()
        dict_values[FIX_COST][asset].update(
            {
                OPTIMIZED_ADD_CAP: {VALUE: 1},
                INSTALLED_CAP: {VALUE: 0},
                LIFETIME_PRICE_DISPATCH: {VALUE: 0},
                FLOW: pd.Series([0, 0]),
            }
        )

        E2.get_costs(dict_values[FIX_COST][asset], dict_values[ECONOMIC_DATA])
        # Remove all parameters that were added before and the KPI that do not apply
        for key in [
            OPTIMIZED_ADD_CAP,
            LIFETIME_PRICE_DISPATCH,
            INSTALLED_CAP,
            FLOW,
            COST_DISPATCH,
        ]:
            dict_values[FIX_COST][asset].pop(key)
        store_result_matrix(
            dict_values[KPI], dict_values[FIX_COST][asset], fix_cost=True
        )
