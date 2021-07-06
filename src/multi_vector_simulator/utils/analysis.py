import json
import logging
from oemof.tools import logger

logger.define_logging(
    logpath=".", logfile="log", file_level=logging.DEBUG, screen_level="DEBUG",
)

from multi_vector_simulator.utils.constants_json_strings import (
    KPI,
    KPI_COST_MATRIX,
    KPI_SCALAR_MATRIX,
)

from multi_vector_simulator.utils import (
    get_nested_value,
    set_nested_value,
    split_nested_path,
)
from multi_vector_simulator.server import run_simulation
from multi_vector_simulator.B0_data_input_json import (
    load_json,
    convert_from_json_to_special_types,
)


def single_param_variation_analysis(
    param_values, json_input, json_path_to_param_value, json_path_to_output_value=None
):
    r"""Run mvs simulations by varying one of the input parameters to access output's sensitivity

    Parameters
    ----------
    param_values: list of values (type can vary)
    json_input: path or dict
        input parameters for the multi-vector simulation
    json_path_to_param_value: tuple or str
        succession of keys which lead the value of the parameter to vary in the json_input dict
        potentially nested structure. The order of keys is to be read from left to right. In the
        case of str, each key should be separated by a `.` or a `,`.
    json_path_to_output_value: tuple of tuple or str, optional
        collection of succession of keys which lead the value of an output parameter of interest in
        the json dict of the simulation's output. The order of keys is to be read from left to
        right. In the case of str, each key should be separated by a `.` or a `,`.

    Returns
    -------
    The simulation output json matched to the list of variied parameter values
    """

    # Process the argument json_input based on its type
    if isinstance(json_input, str):
        # load the file if it is a path
        simulation_input = load_json(json_input)
    elif isinstance(json_input, dict):
        # this is already a json variable
        simulation_input = json_input
    else:
        simulation_input = None
        logging.error(
            f"Simulation input `{json_input}` is neither a file path, nor a json dict. "
            f"It can therefore not be processed."
        )
    param_path_tuple = split_nested_path(json_path_to_param_value)
    answer = []
    if simulation_input is not None:
        for param_val in param_values:
            # modify the value of the parameter before running a new simulation
            modified_input = set_nested_value(
                simulation_input, param_val, param_path_tuple
            )
            # run a simulation with next value of the variable parameter and convert the result to
            # mvs special json type
            # try:

            sim_output_json = run_simulation(
                modified_input, display_output="error", epa_format=False
            )

            if json_path_to_output_value is None:
                answer.append(sim_output_json)
            else:
                output_parameters = {}
                # for each of the output parameter path, add the value located under this path in
                # the final json dict, that could also be applied to the full json dict as
                # post-processing
                for output_param in json_path_to_output_value:
                    # For KPI_COST_MATRIX and KPI_SCALAR_MATRIX items of a pd.DataFrame need to be accessed
                    if (
                        KPI_COST_MATRIX in output_param
                        or KPI_SCALAR_MATRIX in output_param
                    ):
                        # Get corresponding matrix
                        matrix = sim_output_json[output_param[0]][output_param[1]]
                        # Only get row with relevant asset
                        matrix = matrix[(matrix == output_param[3]).any(axis=1)]
                        # Make sure there is only one asset with string output_param[3]
                        if len(matrix.index) > 1:
                            logging.warning(
                                f"The matrix with asset {output_param[3]} has multiple rows: {matrix}"
                            )
                        # Get parameter value for the asset from the matrix
                        output_parameters[output_param] = matrix[output_param[2]]

                    # For others, the output can be identified following the json structure.
                    else:
                        output_param = split_nested_path(output_param)
                        output_parameters[output_param] = get_nested_value(
                            sim_output_json, output_param
                        )
                answer.append(output_parameters)
            # except:
            #    logging.warning(f"The sensitivity did not work.")
            #    answer.append(None)
    print({"parameters": param_values, "outputs": answer})
    return {"parameters": param_values, "outputs": answer}


from multi_vector_simulator.cli import main
from multi_vector_simulator.utils.constants import (
    DEFAULT_INPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    CSV_ELEMENTS,
)
import os
import pandas as pd
import numpy as np
import shutil
import glob
import logging

FOLDER_NAME_SCALARS = "scalars"
FOLDER_NAME_TIMESERIES = "timeseries"


def create_loop_output_structure(outputs_directory, scenario_name, variable_name):
    """
    Defines the path of the loop_output_directory.

    Parameters
    ----------
    outputs_directory: str
        Path to output directory.
        Default: DEFAULT_OUTPUT_PATH

    scenario_name: str
        Name of the Scenario. The name should follow the scheme:
        "Scenario_A1", "Scenario_A2", "Scenario_B1" etc.

    variable_name: str
        name of the variable that is adapted in each loop.

    Returns
    -------
    str
        path of the loop_output_directory.
    """

    if not os.path.isdir(outputs_directory):
        os.mkdir(outputs_directory)

    # defines scenario folder and loop_output_directory
    scenario_folder = os.path.join(outputs_directory, scenario_name)
    # creates scenario folder if it doesn't exist yet
    if not os.path.isdir(scenario_folder):
        # create scenario folder
        os.mkdir(scenario_folder)

    #  defines loop output directory in scenario_folder
    loop_output_directory = os.path.join(
        scenario_folder, "loop_outputs_" + str(variable_name)
    )

    # checks if loop_output_directory already exists, otherwise create it
    if os.path.isdir(loop_output_directory):
        raise NameError(
            f"The loop output directory {loop_output_directory} "
            f"already exists. Please "
            f"delete the existing folder or rename {scenario_name}."
        )
    else:
        os.mkdir(loop_output_directory)

    # create two folder in loop_output_directories for FOLDER_NAME_SCALARS and FOLDER_NAME_TIMESERIES
    os.mkdir(os.path.join(loop_output_directory, FOLDER_NAME_SCALARS))
    os.mkdir(os.path.join(loop_output_directory, FOLDER_NAME_TIMESERIES))

    return loop_output_directory


def loop_mvs(
    variable_name,
    variable_column,
    csv_file_variable,
    start,
    stop,
    step,
    scenario_name,
    user_inputs_mvs_directory=None,
    outputs_directory=None,
):
    """
    Starts multiple MVS simulations with a range of values for a specific parameter.

    This function applies :py:func:`~.main.apply_pvcompare`, one time. After that
     :py:func:`~.main.apply_mvs` is executed in a loop.
     Before each loop a specific variable value is changed. The
    results, stored in two excel sheets, are copied into `loop_output_directory`.

    Parameters
    ----------

    variable_name: str
        name of the variable that is atapted in each loop

    variable_column: str
        name of the  variable column in the csv file

    csv_file_variable: str
        name of the csv file the variable is saved in

    start: int
        first value of the variable

    stop: int
        last value of the variable. notice that stop > start

    step: int
        step of increase

    scenario_name: str
        Name of the Scenario. The name should follow the scheme:
        "Scenario_A1", "Scenario_A2", "Scenario_B1" etc.

    user_inputs_mvs_directory: str or None
        Default: `user_inputs_mvs_directory = DEFAULT_INPUT_PATH`

    outputs_directory: str or None
        Path to output directory.
        Default: `outputs_directory = DEFAULT_OUTPUT_PATH`

    Returns
    -------

    """

    if outputs_directory is None:
        outputs_directory = DEFAULT_OUTPUT_PATH
    loop_output_directory = create_loop_output_structure(
        outputs_directory, scenario_name, variable_name
    )
    # define filename of variable that should be looped over
    if user_inputs_mvs_directory is None:
        user_inputs_mvs_directory = DEFAULT_INPUT_PATH
    csv_filename = os.path.join(
        user_inputs_mvs_directory, CSV_ELEMENTS, csv_file_variable
    )

    # todo
    # loop over the variable
    i = start
    while i <= stop:
        # change variable value and save this value to csv
        csv_file = pd.read_csv(csv_filename, index_col=0)
        csv_file.loc[[variable_name], [variable_column]] = i
        csv_file.to_csv(csv_filename)

        # define mvs_output_directory for every looping step
        mvs_output_directory = os.path.join(
            outputs_directory,
            scenario_name,
            "mvs_outputs_loop_" + str(variable_name) + "_" + str(i),
        )

        # apply mvs for every looping step
        apply_mvs(
            scenario_name=scenario_name,
            mvs_output_directory=mvs_output_directory,
            user_inputs_mvs_directory=user_inputs_mvs_directory,
            outputs_directory=outputs_directory,
        )

        excel_file1 = "scalars.xlsx"
        new_excel_file1 = "scalars_" + variable_name + "_" + str(i) + ".xlsx"
        src_dir = os.path.join(mvs_output_directory, excel_file1)
        dst_dir = os.path.join(
            loop_output_directory, FOLDER_NAME_SCALARS, new_excel_file1
        )
        shutil.copy(src_dir, dst_dir)

        excel_file2 = "timeseries_all_busses.xlsx"
        new_excel_file2 = (
            "timeseries_all_busses_" + variable_name + "_" + str(i) + ".xlsx"
        )
        src_dir = os.path.join(mvs_output_directory, excel_file2)
        dst_dir = os.path.join(
            loop_output_directory, FOLDER_NAME_TIMESERIES, new_excel_file2
        )
        shutil.copy(src_dir, dst_dir)

        # add another step
        i = i + step
    # postprocessing_kpi(
    #    scenario_name=scenario_name,
    #    variable_name=variable_name,
    #    outputs_directory=outputs_directory,
    # )


def apply_mvs(
    scenario_name,
    user_inputs_mvs_directory=None,
    outputs_directory=None,
    mvs_output_directory=None,
):
    r"""
    Starts the energy system optimization with MVS and stores results.
    Parameters
    ----------
    scenario_name: str
        Name of the Scenario.
    user_inputs_mvs_directory: str or None
        Path to input directory containing files that describe the energy
        system and that are an input to MVS. If None,
        `DEFAULT_INPUT_PATH` is used.
        Default: None.
    outputs_directory: str
        Path to output directory where results are saved in case `mvs_output_directory`
        is None. If None, `DEFAULT_OUTPUT_PATH` is used.
        Default: None.
    mvs_output_directory: str or None
        Path to output directory where results are saved. If None, it is filled in
        automatically according to `outputs_directory` and `scenario_name`:
        'outputs_directory/scenario_name/mvs_output'.
        Default: None.
    Returns
    -------
        Stores simulation results in directory according to `outputs_directory` and `scenario_name` in 'outputs_directory/scenario_name/mvs_outputs'.
    """

    if user_inputs_mvs_directory is None:
        user_inputs_mvs_directory = DEFAULT_INPUT_PATH
    if outputs_directory is None:
        outputs_directory = DEFAULT_OUTPUT_PATH
    if not os.path.isdir(outputs_directory):
        os.mkdir(outputs_directory)

    scenario_folder = os.path.join(outputs_directory, scenario_name)
    if mvs_output_directory is None:
        mvs_output_directory = os.path.join(scenario_folder, "mvs_outputs")
    # check if output folder exists, if not: create it
    if not os.path.isdir(scenario_folder):
        # create output folder
        os.mkdir(scenario_folder)
    # check if mvs_output_directory already exists. If yes, raise error
    if os.path.isdir(mvs_output_directory):
        raise NameError(
            f"The mvs output directory {mvs_output_directory} "
            f"already exists. Please delete the folder or "
            f"rename 'scenario_name' to create a different scenario "
            f"folder."
        )

    # adapt parameter 'scenario_name' in 'project_data.csv'.
    add_scenario_name_to_project_data(user_inputs_mvs_directory, scenario_name)

    main(
        path_input_folder=user_inputs_mvs_directory,
        path_output_folder=mvs_output_directory,
        input_type="csv",
        overwrite=True,
        save_png=True,
        display_output="warning",
    )


def add_scenario_name_to_project_data(user_inputs_mvs_directory, scenario_name):
    r"""
    Matches user input `scenario_name` with `scenario_name` in 'project_data.csv'.
    If user input `scenario_name` is different to the parameter in
    'project_data.csv', a warning is returned and 'project_data.csv' is
    overwritten.
    Parameters
    ----------
    user_inputs_mvs_directory: str or None
        Path to MVS specific input directory. If None,
        `DEFAULT_INPUT_PATH` is used.
        Default: None.
    scenario_name: str
        Name of the Scenario.
    Returns
    -------
    None
    """
    add_parameter_to_mvs_file(
        user_inputs_mvs_directory=user_inputs_mvs_directory,
        mvs_filename="project_data.csv",
        mvs_row="scenario_name",
        mvs_column="project_data",
        pvcompare_parameter=scenario_name,
        warning=True,
    )


def add_parameter_to_mvs_file(
    user_inputs_mvs_directory,
    mvs_filename,
    mvs_row,
    mvs_column,
    pvcompare_parameter,
    warning=True,
):
    r"""
    Overwrites a value from a file in 'mvs_inputs/csv_elements' with a user input.
    Parameters
    ----------
    user_inputs_mvs_directory: str or None
        Path to MVS specific input directory. If None,
        `DEFAULT_INPUT_PATH` is used.
        Default: None.
    mvs_filename: str
        Name of the mvs-csv file.
    mvs_row: str
        Row name of the value in `mvs_filename`.
    mvs_column: str
        Column name of the value in `mvs_filename`.
    pvcompare_parameter: str
        Parameter that should be added to the mvs_csv file.
    warning: bool
        If True, a warning is returned that the parameter with the name
        `mvs_row` is overwritten.
    Returns
    ------
    None
    """
    if user_inputs_mvs_directory == None:
        user_inputs_mvs_directory = DEFAULT_INPUT_PATH

    filename = os.path.join(user_inputs_mvs_directory, "csv_elements", mvs_filename)
    # load mvs_csv_file
    mvs_file = pd.read_csv(filename, index_col=0)

    if warning is True:
        if mvs_file.at[mvs_row, mvs_column] != pvcompare_parameter:
            logging.warning(
                f"The parameter {pvcompare_parameter} differs from "
                f"the parameter {mvs_row} in {mvs_filename} and thus will "
                f"be overwritten."
            )

    mvs_file.loc[[mvs_row], [mvs_column]] = pvcompare_parameter
    mvs_file.to_csv(filename)
    logging.info(
        f"The parameter {mvs_row} has been added to the "
        f"mvs input file {mvs_filename}."
    )


def postprocessing_kpi(
    scenario_name,
    variable_name,
    user_inputs_pvcompare_directory=None,
    outputs_directory=None,
):
    """
    Overwrites all output excel files "timeseries_all_flows.xlsx" and "scalars.xlsx"
    in loop output directory of a scenario with modified KPI's.
    1) Creates new sheet "Electricity bus1" with the column
    Electricity demand = Electricity demand + Heat pump.
    2) Creates new sheets in scalars.xlsx with KPI's adjusted to the new demand.

    Parameters
    ----------------
    scenario_name: str
        scenario name
    user_inputs_pvcompare_directory: str
        pvcompare inputs directory
    outputs_directory: str
        output directory

    Returns
        Saves new sheet in output excel file
    """
    if outputs_directory == None:
        outputs_directory = DEFAULT_OUTPUT_PATH
        scenario_folder = os.path.join(outputs_directory, scenario_name)
    else:
        scenario_folder = os.path.join(outputs_directory, scenario_name)
        if not os.path.isdir(scenario_folder):
            logging.warning(f"The scenario folder {scenario_name} does not exist.")

    # # loop over all loop output folders with variable name
    loop_output_directory = os.path.join(
        scenario_folder, "loop_outputs_" + str(variable_name)
    )
    if not os.path.isdir(loop_output_directory):
        logging.warning(
            f"The loop output folder {loop_output_directory} does not exist. "
            f"Please check the variable_name"
        )
    # parse through scalars folder and read in all excel sheets
    for filepath_s in list(
        glob.glob(os.path.join(loop_output_directory, FOLDER_NAME_SCALARS, "*.xlsx"))
    ):
        # read sheets of scalars
        scalars = pd.read_excel(filepath_s, sheet_name=None)

        file_sheet1 = scalars["cost_matrix"]
        file_sheet2 = scalars["scalar_matrix"]
        file_sheet2.index = file_sheet2["label"]
        file_sheet3 = scalars["scalars"]
        file_sheet3.index = file_sheet3.iloc[:, 0]
        file_sheet4 = scalars["KPI individual sectors"]

        # save excel sheets
        with pd.ExcelWriter(filepath_s, mode="a") as writer:
            file_sheet1.to_excel(writer, sheet_name="cost_matrix", index=None)
            file_sheet2.to_excel(writer, sheet_name="scalar_matrix", index=None)
            file_sheet3.to_excel(writer, sheet_name="scalars", index=None)
            file_sheet4.to_excel(
                writer, sheet_name="KPI individual sectors", index=None
            )
        logging.info(
            f"Scalars file sheet {filepath_s} has been overwritten with new KPI's"
        )


loop_mvs(
    variable_name="energy_price",
    variable_column="Electricity_grid_DSO",
    csv_file_variable="energyProviders.csv",
    start=0.1,
    stop=0.5,
    step=0.1,
    scenario_name="energy_price_variablity",
    user_inputs_mvs_directory="tests/inputs",
    outputs_directory="sensitivity_outputs",
)
