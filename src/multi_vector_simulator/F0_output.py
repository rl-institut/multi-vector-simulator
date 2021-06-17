"""
Module F0 - Output
==================

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


import json
import logging
import os

import pandas as pd

from multi_vector_simulator.B0_data_input_json import convert_from_special_types_to_json
from multi_vector_simulator.E1_process_results import get_units_of_cost_matrix_entries
import multi_vector_simulator.F1_plotting as F1_plots

try:
    import multi_vector_simulator.F2_autoreport as autoreport

    AUTOREPORT = True
except ModuleNotFoundError:
    logging.warning("The reporting feature is disabled")
    AUTOREPORT = False

from multi_vector_simulator.utils.constants import (
    SIMULATION_SETTINGS,
    PATH_OUTPUT_FOLDER,
    OUTPUT_FOLDER,
    LOGFILE,
    PATHS_TO_PLOTS,
)

from multi_vector_simulator.utils.constants import (
    JSON_WITH_RESULTS,
    JSON_FILE_EXTENSION,
)
from multi_vector_simulator.utils.constants_json_strings import (
    UNIT,
    KPI,
    OPTIMIZED_FLOWS,
    DEMANDS,
    RESOURCES,
    LES_ENERGY_VECTOR_S,
    KPI_SCALARS_DICT,
    KPI_SCALAR_MATRIX,
    KPI_COST_MATRIX,
    PROJECT_DATA,
    ECONOMIC_DATA,
    SIMULATION_RESULTS,
    LOGS,
    ERRORS,
    WARNINGS,
    FIX_COST,
    ENERGY_BUSSES,
)


def evaluate_dict(dict_values, path_pdf_report=None, path_png_figs=None):
    """This is the main function of F0. It calls all functions that prepare the simulation output, ie. Storing all simulation output into excellent files, bar charts, and graphs.

    Parameters
    ----------
    dict_values :
        dict Of all input and output parameters up to F0

    path_pdf_report : (str)
        if provided, generate a pdf report of the simulation to the given path

    path_png_figs : (str)
        if provided, generate png figures of the simulation's results to the given path

    Returns
    -------
    type
        NA

    """

    logging.info(
        "Summarizing simulation results to results_timeseries and results_scalars_assets."
    )

    parse_simulation_log(
        path_log_file=os.path.join(
            dict_values[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER], LOGFILE
        ),
        dict_values=dict_values,
    )

    # storing all flows to exel.
    store_timeseries_all_busses_to_excel(dict_values)

    # Write everything to file with multiple tabs
    store_scalars_to_excel(dict_values)

    store_as_json(
        dict_values,
        dict_values[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER],
        JSON_WITH_RESULTS,
    )

    # generate png figures
    if path_png_figs is not None:
        # plot demand timeseries
        F1_plots.plot_timeseries(
            dict_values, data_type=DEMANDS, file_path=path_png_figs
        )
        # plot demand timeseries for the first 2 weeks only
        F1_plots.plot_timeseries(
            dict_values, data_type=DEMANDS, max_days=14, file_path=path_png_figs
        )

        # plot supply timeseries
        F1_plots.plot_timeseries(
            dict_values, data_type=RESOURCES, file_path=path_png_figs
        )
        # plot supply timeseries for the first 2 weeks only
        F1_plots.plot_timeseries(
            dict_values, data_type=RESOURCES, max_days=14, file_path=path_png_figs
        )

        # plot power flows in the energy system
        F1_plots.plot_instant_power(dict_values, file_path=path_png_figs)

        # plot optimal capacities if there are optimized assets
        F1_plots.plot_optimized_capacities(dict_values, file_path=path_png_figs)

        # plot annuity, first-investment and om costs
        F1_plots.plot_piecharts_of_costs(dict_values, file_path=path_png_figs)

    # generate a pdf report
    if path_pdf_report is not None:
        app = autoreport.create_app(dict_values)
        autoreport.print_pdf(app, path_pdf_report=path_pdf_report)
        logging.info(
            "Generating PDF report of the simulation: {}".format(path_pdf_report)
        )


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
        for kpi_set in dict_values[KPI]:
            if isinstance(dict_values[KPI][kpi_set], dict):
                data = pd.DataFrame([dict_values[KPI][kpi_set]])
            else:
                data = dict_values[KPI][kpi_set]

            # Transpose results and add units to the entries
            if kpi_set == KPI_SCALARS_DICT:
                data = data.transpose()
                units_cost_kpi = get_units_of_cost_matrix_entries(
                    dict_values[ECONOMIC_DATA], dict_values[KPI][kpi_set]
                )
                data[UNIT] = units_cost_kpi

            data.to_excel(open_file, sheet_name=kpi_set)
            logging.debug(
                "Saved scalar results to: %s, tab %s.",
                results_scalar_output_file,
                kpi_set,
            )


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
        for bus in dict_values[OPTIMIZED_FLOWS]:
            dict_values[OPTIMIZED_FLOWS][bus].to_excel(open_file, sheet_name=bus)

    logging.debug("Saved flows at busses to: %s.", timeseries_output_file)


def parse_simulation_log(path_log_file, dict_values):
    """Gather a log file with several log messages, this function gathers them all and inputs them into the dict with
    all input and output parameters up to F0

    Parameters
    ----------
    path_log_file: str/None
        path to the mvs log file
        Default: None

    dict_values :
        dict Of all input and output parameters up to F0

    Returns
    -------
    Updates the results dictionary with the log messages of the simulation

    Notes
    -----
    This function is tested with:
    - test_F0_output.TestLogCreation.test_parse_simulation_log

    """
    # Dictionaries to gather non-fatal warning and error messages that appear during the simulation

    error_dict, warning_dict = {}, {}

    if path_log_file is None:
        path_log_file = os.path.join(OUTPUT_FOLDER, LOGFILE)

    with open(path_log_file) as log_messages:
        log_messages = log_messages.readlines()

    i = j = 0

    # Loop through the list of lines of the log file to check for the relevant log messages and gather them in dicts
    for line in log_messages:
        if "ERROR" in line:
            i = i + 1
            substrings = line.split(" - ")
            message_string = substrings[-1]
            error_dict.update({i: message_string})
        elif "WARNING" in line:
            j = j + 1
            substrings = line.split(" - ")
            message_string = substrings[-1]
            warning_dict.update({j: message_string})

    log_dict = {ERRORS: error_dict, WARNINGS: warning_dict}

    dict_values[SIMULATION_RESULTS].update({LOGS: log_dict})


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
        dict_values,
        skipkeys=False,
        sort_keys=True,
        default=convert_from_special_types_to_json,
        indent=4,
    )
    if file_name is not None:
        file_path = os.path.abspath(os.path.join(output_folder, file_name + ".json"))

        if os.path.exists(os.path.dirname(file_path)):
            myfile = open(file_path, "w")

            myfile.write(json_data)
            myfile.close()
            logging.info(
                "Converted and stored processed simulation data to json: %s", file_path
            )
            answer = file_path
        else:
            answer = None
    else:
        answer = json_data

    return answer
