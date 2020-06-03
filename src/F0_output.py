import json
import logging
import os

import numpy
import pandas as pd

import src.F1_plotting as F1_plots
import src.F2_autoreport as autoreport
from src.constants import (
    TYPE_DATETIMEINDEX,
    TYPE_SERIES,
    TYPE_DATAFRAME,
    TYPE_TIMESTAMP,
    SIMULATION_SETTINGS,
    PROJECT_DATA,
    SECTORS,
    LABEL,
    PATH_OUTPUT_FOLDER,
)

r"""
Module F0 Output
================
The model F0 output defines all functions that store evaluation results to file.
- Aggregate demand profiles to a total demand profile
- Plot all energy flows for both 14 and 365 days for each energy bus
- Store timeseries of all energy flows to excel (one sheet = one energy bus)
- Execute function: plot optimised capacities as a barchart (F1)
- Execute function: plot all annuities as a barchart (F1)
- Store scalars/KPI to excel
- Process dictionary so that it can be stored to Json
- Store dictionary to Json
"""


def evaluate_dict(dict_values, path_pdf_report=None):
    """This is the main function of F0. It calls all functions that prepare the simulation output, ie. Storing all simulation output into excellent files, bar charts, and graphs.

    Parameters
    ----------
    dict_values :
        dict Of all input and output parameters up to F0
    path_pdf_report : (str)
        if provided, generate a pdf report of the simulation to the given path

    Returns
    -------
    type
        NA

    """

    logging.info(
        "Summarizing simulation results to results_timeseries and results_scalars_assets."
    )

    for sector in dict_values[PROJECT_DATA][SECTORS]:
        sector_name = dict_values[PROJECT_DATA][SECTORS][sector]

        logging.info("Aggregating flows for the %s sector.", sector_name)

        # Plot flows for one sector for the 14 first days
        F1_plots.flows(
            dict_values,
            dict_values[SIMULATION_SETTINGS],
            dict_values[PROJECT_DATA],
            dict_values["optimizedFlows"][sector_name + " bus"],
            sector,
            14,
        )

        # Plot flows for one sector for a year
        F1_plots.flows(
            dict_values,
            dict_values[SIMULATION_SETTINGS],
            dict_values[PROJECT_DATA],
            dict_values["optimizedFlows"][sector_name + " bus"],
            sector,
            365,
        )

        """
        ###
        # Aggregation of demand profiles to total demand
        ###
        This would store demands are twice - as total demand as well as individual demand!

        # Initialize
        total_demand = pd.Series(
            [0 for i in dict_values[SIMULATION_SETTINGS][TIME_INDEX]],
            index=dict_values[SIMULATION_SETTINGS][TIME_INDEX],
        )

        # Add demands (exclude excess)
        for asset in dict_values[ENERGY_CONSUMPTION]:
            # key "energyVector" not included in excess sinks, ie. this filters them out from demand.
            if ENERGY_VECTOR in dict_values[ENERGY_CONSUMPTION][asset].keys() \
                    and dict_values[ENERGY_CONSUMPTION][asset][ENERGY_VECTOR] == sector_name:
                total_demand = (
                    total_demand + dict_values[ENERGY_CONSUMPTION][asset]["flow"]
                )

        # todo this should actually link to C0: helpers.bus_suffix
        dict_values["optimizedFlows"][sector_name + " bus"][
            "Total demand " + sector_name
        ] = total_demand
        """

    # storing all flows to exel.
    store_timeseries_all_busses_to_excel(dict_values)

    # plot optimal capacities if there are optimized assets
    plot_optimized_capacities(dict_values)

    # plot annuity, first-investment and om costs
    plot_piecharts_of_costs(dict_values)

    # Write everything to file with multipe tabs
    store_scalars_to_excel(dict_values)

    store_as_json(
        dict_values,
        dict_values[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER],
        "json_with_results",
    )

    # generate a pdf report
    if path_pdf_report is not None:
        app = autoreport.create_app(dict_values)
        autoreport.print_pdf(app, path_pdf_report=path_pdf_report)
        logging.info(
            "Generating PDF report of the simulation: {}".format(path_pdf_report)
        )


def plot_piecharts_of_costs(dict_values):
    """
    Kicks of plotting piecharts of different cost paramameters (ie. annuity and total cost, potentially in the future LCOE)
    Parameters
    ----------
    dict_values : dict
        all simulation input and output data up to this point

    Returns
    -------
    Pie charts for various parameters.
    """

    # Annuity costs plot (only plot if there are values with cost over 0)
    F1_plots.evaluate_cost_parameter(dict_values, "annuity_total", "annuity")

    # First-investment costs plot (only plot if there are values with cost over 0)
    F1_plots.evaluate_cost_parameter(
        dict_values, "costs_investment", "upfront_investment_costs"
    )

    # O&M costs plot (only plot if there are values with cost over 0)
    F1_plots.evaluate_cost_parameter(
        dict_values, "costs_om", "operation_and_maintenance_costs"
    )
    return


def plot_optimized_capacities(dict_values):
    """This function determinants whether or not any capacities are added to the optimal system and calls the function plotting those capacities as a bar chart.

    Parameters
    ----------
    dict_values :
        dict Of all input and output parameters up to F0

    Returns
    -------
    type
        Bar chart of capacities

    """

    show_optimal_capacities = False
    for element in dict_values["kpi"]["scalar_matrix"]["optimizedAddCap"].values:
        if element > 0:
            show_optimal_capacities = True

    if show_optimal_capacities is True:
        F1_plots.capacities(
            dict_values,
            dict_values[SIMULATION_SETTINGS],
            dict_values[PROJECT_DATA],
            dict_values["kpi"]["scalar_matrix"][LABEL],
            dict_values["kpi"]["scalar_matrix"]["optimizedAddCap"],
        )
    return show_optimal_capacities


def store_scalars_to_excel(dict_values):
    """All output data that is a scalar is storage to an excellent file tab. This could for example be economical data or technical data.

    Parameters
    ----------
    dict_values :
        dict Of all input and output parameters up to F0

    Returns
    -------
    type
        Excel file with scalar data

    """
    results_scalar_output_file = "/scalars" + ".xlsx"
    with pd.ExcelWriter(
        dict_values[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER]
        + results_scalar_output_file
    ) as open_file:  # doctest: +SKIP
        for kpi_set in dict_values["kpi"]:
            if isinstance(dict_values["kpi"][kpi_set], dict):
                data = pd.DataFrame([dict_values["kpi"][kpi_set]]).to_excel(
                    open_file, sheet_name=kpi_set
                )
            else:
                dict_values["kpi"][kpi_set].to_excel(open_file, sheet_name=kpi_set)
            logging.info(
                "Saved scalar results to: %s, tab %s.",
                results_scalar_output_file,
                kpi_set,
            )
    return


def store_timeseries_all_busses_to_excel(dict_values):
    """This function plots the energy flows of each single bus and the energy system and saves it as PNG and additionally as a tab and an Excel sheet.

    Parameters
    ----------
    dict_values :
        dict Of all input and output parameters up to F0

    Returns
    -------
    type
        Plots and excel with all timeseries of each bus

    """

    timeseries_output_file = "/timeseries_all_busses" + ".xlsx"
    with pd.ExcelWriter(
        dict_values[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER] + timeseries_output_file
    ) as open_file:  # doctest: +SKIP
        for bus in dict_values["optimizedFlows"]:
            dict_values["optimizedFlows"][bus].to_excel(open_file, sheet_name=bus)
            F1_plots.flows(
                dict_values,
                dict_values[SIMULATION_SETTINGS],
                dict_values[PROJECT_DATA],
                dict_values["optimizedFlows"][bus],
                bus,
                365,
            )

    logging.info("Saved flows at busses to: %s.", timeseries_output_file)
    return


def convert(o):
    """This converts all data stored in dict_values that is not compatible with the json format to a format that is compatible.

    Parameters
    ----------
    o :
        Any type. Object to be converted to json-storable value.

    Returns
    -------
    type
        json-storable value.

    """
    if isinstance(o, numpy.int64):
        answer = int(o)
    # todo this actually drops the date time index, which could be interesting
    elif isinstance(o, pd.DatetimeIndex):
        answer = o.to_frame().to_json(orient="split")
        answer = "{}{}".format(TYPE_DATETIMEINDEX, answer)
    elif isinstance(o, pd.Timestamp):
        answer = str(o)
        answer = "{}{}".format(TYPE_TIMESTAMP, answer)
    # todo this also drops the timeindex, which is unfortunate.
    elif isinstance(o, pd.Series):
        answer = o.to_json(orient="split")
        answer = "{}{}".format(TYPE_SERIES, answer)
    elif isinstance(o, numpy.ndarray):
        answer = json.dumps({"array": o.tolist()})
    elif isinstance(o, pd.DataFrame):
        answer = o.to_json(orient="split")
        answer = "{}{}".format(TYPE_DATAFRAME, answer)
    else:
        raise TypeError(
            "An error occurred when converting the simulation data (dict_values) to json, as the type is not recognized: \n"
            "Type: " + str(type(o)) + " \n "
            "Value(s): " + str(o) + "\n"
            "Please edit function CO_data_processing.dataprocessing.store_as_json."
        )

    return answer


def store_as_json(dict_values, output_folder=None, file_name=None):
    """Converts dict_values to JSON format and saves dict_values as a JSON file or return json

    Parameters
    ----------
    dict_values : (dict)
        dict to be stored as json
    output_folder : (path)
        Folder into which json should be stored
        Default None
    file_name : (str)
        Name of the file the json should be stored as
        Default None

    Returns
    -------
    If file_name is provided, the json variable converted from the dict_values is saved under
    this file_name, otherwise the json variable is returned
    """
    json_data = json.dumps(
        dict_values, skipkeys=False, sort_keys=True, default=convert, indent=4
    )
    if file_name is not None:
        file_path = os.path.abspath(os.path.join(output_folder, file_name + ".json"))
        myfile = open(file_path, "w")

        myfile.write(json_data)
        myfile.close()
        logging.info(
            "Converted and stored processed simulation data to json: %s", file_path
        )
        answer = file_path
    else:
        answer = json_data

    return answer
