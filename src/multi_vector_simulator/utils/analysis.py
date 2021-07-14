import json
import logging
from oemof.tools import logger

logger.define_logging(
    logpath=".", logfile="log", file_level=logging.INFO, screen_level="INFO",
)

from multi_vector_simulator.utils.constants_json_strings import (
    KPI,
    KPI_COST_MATRIX,
    KPI_SCALAR_MATRIX,
    KPI_SCALARS_DICT,
    COST_TOTAL,
    COST_UPFRONT,
    COST_OM,
    ANNUITY_TOTAL,
    ANNUITY_OM,
    RENEWABLE_FACTOR,
    DEGREE_OF_AUTONOMY,
    TOTAL_EMISSIONS,
    TOTAL_EXCESS,
    TOTAL_RENEWABLE_GENERATION_IN_LES,
    LCOeleq,
    SUFFIX_ELECTRICITY_EQUIVALENT,
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
    JSON_WITH_RESULTS,
    JSON_FILE_EXTENSION,
)
import os
import pandas as pd
import shutil
import glob
import logging
import matplotlib.pyplot as plt

FILE_NAME_SCALARS = "scalars"
FILE_NAME_TIMESERIES = "timeseries_all_busses"
PARAMETER = "senstivity_parameter"
SCENARIO_OUTPUT_PATH = "scenario_output_path"
VALUES = "values"
EXPERIMENT_OUTPUT_PATHS = "scenario_output_path"
WORKING_DIR = "working_dir"

dict_result_paths = {}


def check_for_directory_and_create(directory, overwrite):
    if not os.path.isdir(directory):
        os.mkdir(directory)
        logging.debug(f"Created empty directory {directory}.")
    elif os.path.isdir(directory) and overwrite is True:
        shutil.rmtree(directory)
        os.mkdir(directory)
        logging.info(
            f"Path {directory} existed. It was removed and replaced by an empty directory."
        )
    else:
        raise FileExistsError(
            f"Path {directory} already exists. Either set {overwrite} to True, or define a different output path."
        )
    return


def create_loop_output_structure(
    outputs_directory, scenario_name, variable_name, dict_result_paths, overwrite
):
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

    check_for_directory_and_create(outputs_directory, overwrite)

    # defines scenario folder and loop_output_directory
    scenario_folder = os.path.join(outputs_directory, scenario_name)
    # creates scenario folder if it doesn't exist yet
    check_for_directory_and_create(scenario_folder, overwrite)

    dict_result_paths.update(
        {
            scenario_name: {
                PARAMETER: variable_name,
                SCENARIO_OUTPUT_PATH: scenario_folder,
                VALUES: [],
                EXPERIMENT_OUTPUT_PATHS: [],
            }
        }
    )

    #  defines loop output directory in scenario_folder
    loop_output_directory = os.path.join(
        scenario_folder, "loop_outputs_" + str(variable_name)
    )

    # checks if loop_output_directory already exists, otherwise create it
    check_for_directory_and_create(loop_output_directory, overwrite)

    # create two folder in loop_output_directories for FOLDER_NAME_SCALARS and FOLDER_NAME_TIMESERIES
    path_to_folder_with_scalar_results = os.path.join(
        loop_output_directory, FILE_NAME_SCALARS
    )
    check_for_directory_and_create(path_to_folder_with_scalar_results, overwrite)

    path_to_folder_with_timeseries_results = os.path.join(
        loop_output_directory, FILE_NAME_TIMESERIES
    )
    check_for_directory_and_create(path_to_folder_with_timeseries_results, overwrite)

    return loop_output_directory


def determine_variable_name_value_vector(variable_name, start, stop, step):
    number_of_steps = (stop - start) / step

    if number_of_steps.is_integer() is False:
        logging.warning(
            f"With the chosen start {start}, stop {stop} and step {step} of {variable_name}, the number of steps between start and stop is uneven."
        )
        number_of_steps = round(number_of_steps + 0.5) + 1
    else:
        number_of_steps = round(number_of_steps + 0.5)

    value_vector = [start + i * step for i in range(0, number_of_steps)]
    logging.info(f"The {variable_name} will be set to following values: {value_vector}")
    return value_vector


def clone_input_dir_into_working_dir(
    original_input_directory, original_outputs_directory, overwrite
):
    """
    Creates a working directory folder and clones inputs into that folder

    The working directory folder is changed in order to produce the experiments within the loop. This should not change the initial input files.

    Parameters
    ----------
    original_input_directory: <os.path>
        Path to input directory

    original_outputs_directory: <os.path>
        Path to output directory

    Returns
    -------
    working_directory_path: <os.path>
        Path to the newly created working directory

    """
    working_directory_path = os.path.join(original_outputs_directory, WORKING_DIR)
    shutil.copytree(original_input_directory, working_directory_path)
    logging.debug(
        f"Created working directory {working_directory_path} and copied the original input file from {original_input_directory}"
    )
    return working_directory_path


def adapt_input_csv_files(
    csv_filename,
    variable_name,
    variable_column,
    value,
    experiment_name,
    working_directory_path,
):
    """

    Parameters
    ----------
    csv_filename
    variable_name
    variable_column
    value
    experiment_name
    working_directory_path

    Returns
    -------

    """
    # change variable value and save this value to csv
    csv_file = pd.read_csv(csv_filename, index_col=0)
    csv_file.loc[[variable_name], [variable_column]] = value
    csv_file.to_csv(csv_filename)
    # adapt parameter 'scenario_name' in 'project_data.csv'.
    add_parameter_to_mvs_file(
        input_path=working_directory_path,
        mvs_filename="project_data.csv",
        mvs_row="scenario_name",
        mvs_column="project_data",
        pvcompare_parameter=experiment_name,
        warning=True,
    )
    return


def loop_mvs(
    variable_name,
    variable_column,
    csv_file_variable,
    start,
    stop,
    step,
    scenario_name,
    original_input_directory=DEFAULT_INPUT_PATH,
    original_outputs_directory=DEFAULT_OUTPUT_PATH,
    overwrite=False,
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

    original_input_directory: str or None
        Default: `user_inputs_mvs_directory = DEFAULT_INPUT_PATH`

    original_outputs_directory: str or None
        Path to output directory.
        Default: `outputs_directory = DEFAULT_OUTPUT_PATH`

    Returns
    -------

    """

    loop_output_directory = create_loop_output_structure(
        original_outputs_directory,
        scenario_name,
        variable_name,
        dict_result_paths,
        overwrite,
    )

    working_directory_path = clone_input_dir_into_working_dir(
        original_input_directory, original_outputs_directory, overwrite
    )

    csv_filename = os.path.join(working_directory_path, CSV_ELEMENTS, csv_file_variable)

    value_vector = determine_variable_name_value_vector(
        variable_name, start, stop, step
    )

    for value in value_vector:
        dict_result_paths[scenario_name][VALUES].append(value)
        experiment_name = (
            scenario_name
            + "_"
            + variable_column
            + "_"
            + variable_name
            + "_"
            + str(value)
        )

        adapt_input_csv_files(
            csv_filename,
            variable_name,
            variable_column,
            value,
            experiment_name,
            working_directory_path,
        )

        # define experiment_output_directory for every looping step
        experiment_output_directory = os.path.join(
            original_outputs_directory, scenario_name, experiment_name,
        )
        dict_result_paths[scenario_name][EXPERIMENT_OUTPUT_PATHS].append(
            experiment_output_directory
        )

        # apply mvs for every looping step
        main(
            path_input_folder=working_directory_path,
            path_output_folder=experiment_output_directory,
            input_type="csv",
            overwrite=overwrite,
            save_png=True,
            display_output="warning",
        )

        for excel_file in [FILE_NAME_SCALARS, FILE_NAME_TIMESERIES]:
            name_excel_file = excel_file + ".xlsx"
            new_name_excel_file = (
                excel_file + "_" + variable_name + "_" + str(value) + ".xlsx"
            )
            src_dir = os.path.join(experiment_output_directory, name_excel_file)
            dst_dir = os.path.join(
                loop_output_directory, excel_file, new_name_excel_file
            )
            shutil.copy(src_dir, dst_dir)

    # Remove working directory
    shutil.rmtree(working_directory_path)

    postprocessing_kpi(
        variable_name=variable_name,
        variable_value_vector=dict_result_paths[scenario_name][VALUES],
        output_path_vector=dict_result_paths[scenario_name][EXPERIMENT_OUTPUT_PATHS],
        output_path_summary=loop_output_directory,
    )


def add_parameter_to_mvs_file(
    input_path, mvs_filename, mvs_row, mvs_column, pvcompare_parameter, warning=True,
):
    r"""
    Overwrites a value from a file in 'mvs_inputs/csv_elements' with a user input.
    Parameters
    ----------
    input_path: str or None
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

    filename = os.path.join(input_path, "csv_elements", mvs_filename)
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
    variable_name, variable_value_vector, output_path_vector, output_path_summary
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
    original_outputs_directory: str
        output directory

    Returns
        Saves new sheet in output excel file
    """

    KEY_INTEREST_KPI = [
        COST_TOTAL,
        COST_UPFRONT,
        COST_OM,
        ANNUITY_TOTAL,
        ANNUITY_OM,
        RENEWABLE_FACTOR,
        DEGREE_OF_AUTONOMY,
        TOTAL_EMISSIONS,
        TOTAL_EXCESS + SUFFIX_ELECTRICITY_EQUIVALENT,
        TOTAL_RENEWABLE_GENERATION_IN_LES,
        LCOeleq,
    ]

    senstivitiy_data = pd.DataFrame(index=KEY_INTEREST_KPI)

    diesel_fuel_consumption = "Annual_diesel_fuel_consumption_in_l"
    diesel_fuel_expenses = "Annual_diesel_fuel_expenses_in_USD"
    capacity_h2_electrolyzer = "Capacity_H2_electrolyzer_in_kgH2"
    capacity_h2_tank = "Capacit_H2_tank_in_kgH2"
    capacity_fuel_cell = "Capacity_fuel_cell_in_kW"
    json_parameter_paths = {
        diesel_fuel_consumption: ("energyProduction", "Diesel", "total_flow", "value",),
        diesel_fuel_expenses: ("energyProduction", "Diesel", "annuity_om", "value"),
        capacity_h2_electrolyzer: (
            "energyConversion",
            "Electrolyzer",
            "optimizedAddCap",
            "value",
        ),
        capacity_fuel_cell: (
            "energyConversion",
            "Fuel cell",
            "optimizedAddCap",
            "value",
        ),
        capacity_h2_tank: (
            "energyStorage",
            "H2 storage",
            "storage capacity",
            "optimizedAddCap",
            "value",
        ),
    }

    other_scalars = pd.DataFrame(index=json_parameter_paths.keys())

    for item in range(0, len(output_path_vector)):
        output_json = os.path.join(
            output_path_vector[item], JSON_WITH_RESULTS + JSON_FILE_EXTENSION
        )
        json = load_json(output_json)
        sensitivity_results = [json[KPI][KPI_SCALARS_DICT][i] for i in KEY_INTEREST_KPI]
        senstivitiy_data[variable_value_vector[item]] = sensitivity_results
        logging.info(
            f"Gathered simulation results (KPIS) from {variable_name}={variable_value_vector[item]}, output folder {output_path_vector[item]}"
        )

        other_scalars = get_asset_results(
            json, json_parameter_paths, other_scalars, variable_value_vector[item]
        )
        logging.info(
            f"Gathered simulation results (assets) from {variable_name}={variable_value_vector[item]}, output folder {output_path_vector[item]}"
        )

    senstivitiy_data = senstivitiy_data.transpose()

    for kpi in KEY_INTEREST_KPI:
        plot_data = pd.Series(senstivitiy_data[kpi], index=senstivitiy_data.index)
        plot_data.plot()
        plt.xlabel(variable_name)
        plt.ylabel(kpi)
        plt.savefig(
            os.path.join(output_path_summary, f"{variable_name}_effect_on_{kpi}.png")
        )
        plt.close()

    senstivitiy_data.to_csv(output_path_summary + "kpi_summary.csv")

    other_scalars = other_scalars.transpose()

    for scalar in other_scalars.columns:
        plot_data = pd.Series(other_scalars[scalar], index=other_scalars.index)
        plot_data.plot()
        plt.xlabel(variable_name)
        plt.ylabel(scalar)
        plt.savefig(
            os.path.join(output_path_summary, f"{variable_name}_effect_on_{scalar}.png")
        )
        plt.close()

    other_scalars.to_csv(output_path_summary + "other_scalars_summary.csv")


def get_asset_results(json, parameters, df, value):
    results = []
    for key in parameters:
        key_value = get_nested_value(json, parameters[key])
        results.append(key_value)
    df[value] = results
    return df


"""
loop_mvs(
    variable_name="energy_price",
    variable_column="Electricity_grid_DSO",
    csv_file_variable="energyProviders.csv",
    start=0.1,
    stop=0.2,
    step=0.1,
    scenario_name="energy_price_variablity",
    original_input_directory="tests/inputs",
    original_outputs_directory="sensitivity_outputs",
    overwrite=True,
)
"""
loop_mvs(
    variable_name="dispatch_price",
    variable_column="Diesel",
    csv_file_variable="energyProduction.csv",
    start=0.8,
    stop=0.9,
    step=0.1,
    scenario_name="diesel_price",
    original_input_directory="Aysen/two_storages",
    original_outputs_directory="Aysen_diesel_price",
    overwrite=True,
)
loop_mvs(
    variable_name="H2_storage_tank",
    variable_column="specific_costs",
    csv_file_variable="H2_storage_tank.csv",
    start=2300,
    stop=2400,
    step=100,
    scenario_name="H2_tank_costs",
    original_input_directory="Aysen/two_storages",
    original_outputs_directory="Aysen_H2_tank_costs",
    overwrite=True,
)
