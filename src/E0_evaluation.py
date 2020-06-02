import logging

import oemof.outputlib as outputlib
import pandas as pd

from src.constants_json_strings import (
    UNIT,
    ENERGY_CONVERSION,
    ENERGY_CONSUMPTION,
    ENERGY_PRODUCTION,
    ENERGY_BUSSES,
)

import src.E1_process_results as process_results
import src.E2_economics as economics
import src.E3_indicator_calculation as indicators

r"""
Module E0 evaluation
====================

Module E0 evaluates the oemof results and calculates the KPI
- define dictionary entry for kpi matrix
- define dictionary entry for cost matrix
- store all results to matrix
"""


def evaluate_dict(dict_values, results_main, results_meta):
    """

    Parameters
    ----------
    dict_values: dict
        simulation parameters
    results_main: DataFrame
        oemof simulation results as output by outputlib.processing.results()
    results_meta: DataFrame
        oemof simulation meta information as output by outputlib.processing.meta_results()

    Returns
    -------

    """
    dict_values.update(
        {
            "kpi": {
                "cost_matrix": pd.DataFrame(
                    columns=[
                        "label",
                        "costs_total",
                        "costs_om",
                        "costs_investment",
                        "costs_upfront",
                        "costs_opex_var",
                        "costs_opex_fix",
                        "annuity_total",
                        "annuity_om",
                    ]
                ),
                "scalar_matrix": pd.DataFrame(
                    columns=[
                        "label",
                        "optimizedAddCap",
                        "total_flow",
                        "annual_total_flow",
                        "peak_flow",
                        "average_flow",
                    ]
                ),
                "scalars": {},
            }
        }
    )
    bus_data = {}
    # Store all information related to busses in bus_data
    for bus in dict_values[ENERGY_BUSSES]:
        # Read all energy flows from busses
        bus_data.update({bus: outputlib.views.node(results_main, bus)})

    # Evaluate timeseries and store to a large DataFrame for each bus:
    process_results.get_timeseries_per_bus(dict_values, bus_data)

    # Store all information related to storages in bus_data, as storage capacity acts as a bus
    for storage in dict_values["energyStorage"]:
        bus_data.update(
            {
                dict_values["energyStorage"][storage]["label"]: outputlib.views.node(
                    results_main, dict_values["energyStorage"][storage]["label"],
                )
            }
        )
        process_results.get_storage_results(
            dict_values["simulation_settings"],
            bus_data[dict_values["energyStorage"][storage]["label"]],
            dict_values["energyStorage"][storage],
        )

        # hardcoded list of names in storage_01.csv
        for storage_item in ["storage capacity", "input power", "output power"]:
            economics.get_costs(
                dict_values["energyStorage"][storage][storage_item],
                dict_values["economic_data"],
            )
            store_result_matrix(
                dict_values["kpi"], dict_values["energyStorage"][storage][storage_item]
            )

        if (
            dict_values["energyStorage"][storage]["input_bus_name"]
            in dict_values["optimizedFlows"].keys()
        ) or (
            dict_values["energyStorage"][storage]["output_bus_name"]
            in dict_values["optimizedFlows"].keys()
        ):
            bus_name = dict_values["energyStorage"][storage]["input_bus_name"]
            timeseries_name = (
                dict_values["energyStorage"][storage]["label"]
                + " ("
                + str(
                    round(
                        dict_values["energyStorage"][storage]["storage capacity"][
                            "optimizedAddCap"
                        ]["value"],
                        1,
                    )
                )
                + dict_values["energyStorage"][storage]["storage capacity"][
                    "optimizedAddCap"
                ][UNIT]
                + ") SOC"
            )

            dict_values["optimizedFlows"][bus_name][timeseries_name] = dict_values[
                "energyStorage"
            ][storage]["timeseries_soc"]

    for asset in dict_values[ENERGY_CONVERSION]:
        process_results.get_results(
            dict_values["simulation_settings"],
            bus_data,
            dict_values[ENERGY_CONVERSION][asset],
        )
        economics.get_costs(
            dict_values[ENERGY_CONVERSION][asset], dict_values["economic_data"]
        )
        store_result_matrix(dict_values["kpi"], dict_values[ENERGY_CONVERSION][asset])

    for group in [ENERGY_PRODUCTION, ENERGY_CONSUMPTION]:
        for asset in dict_values[group]:
            process_results.get_results(
                dict_values["simulation_settings"], bus_data, dict_values[group][asset],
            )
            economics.get_costs(dict_values[group][asset], dict_values["economic_data"])
            store_result_matrix(dict_values["kpi"], dict_values[group][asset])

    indicators.all_totals(dict_values)

    # Processing further KPI
    indicators.total_renewable_and_non_renewable_energy_origin(dict_values)
    indicators.renewable_share(dict_values)

    logging.info("Evaluating optimized capacities and dispatch.")
    return


def store_result_matrix(dict_kpi, dict_asset):
    """Storing results to vector and then result matrix for saving it in csv.

    Parameters
    ----------
    dict_kpi
    dict_asset

    Returns
    -------

    """

    round_to_comma = 5

    for kpi_storage in ["cost_matrix", "scalar_matrix"]:
        asset_result_dict = {}
        for key in dict_kpi[kpi_storage].columns.values:
            # Check if called value is in oemof results -> Remember: check if pandas index has certain index: pd.object.index.contains(key)
            if key in dict_asset:
                if isinstance(dict_asset[key], str):
                    asset_result_dict.update({key: dict_asset[key]})
                else:
                    asset_result_dict.update(
                        {key: round(dict_asset[key]["value"], round_to_comma)}
                    )

        asset_result_df = pd.DataFrame([asset_result_dict])

        dict_kpi.update(
            {kpi_storage: dict_kpi[kpi_storage].append(asset_result_df, sort=False)}
        )
    return
