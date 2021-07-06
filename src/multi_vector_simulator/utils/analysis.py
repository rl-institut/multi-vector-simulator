import json
import logging
from oemof.tools import logger

logger.define_logging(
    logpath=".",
    logfile="log",
    file_level=logging.DEBUG,
    screen_level="DEBUG",
)

from multi_vector_simulator.utils.constants_json_strings import KPI, KPI_COST_MATRIX, KPI_SCALAR_MATRIX

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
            #try:

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
                    if KPI_COST_MATRIX in output_param or KPI_SCALAR_MATRIX in output_param:
                        # Get corresponding matrix
                        matrix = sim_output_json[output_param[0]][output_param[1]]
                        # Only get row with relevant asset
                        matrix = matrix[(matrix == output_param[3]).any(axis=1)]
                        # Make sure there is only one asset with string output_param[3]
                        if len(matrix.index) > 1:
                            logging.warning(f"The matrix with asset {output_param[3]} has multiple rows: {matrix}")
                        # Get parameter value for the asset from the matrix
                        output_parameters[output_param] = matrix[output_param[2]]

                    # For others, the output can be identified following the json structure.
                    else:
                        output_param = split_nested_path(output_param)
                        output_parameters[output_param] = get_nested_value(
                            sim_output_json, output_param
                    )
                answer.append(output_parameters)
            #except:
            #    logging.warning(f"The sensitivity did not work.")
            #    answer.append(None)
    print({"parameters": param_values, "outputs": answer})
    return {"parameters": param_values, "outputs": answer}

import pvcompare.main as main
import pvcompare.constants as constants
import os
import pandas as pd
import numpy as np
import shutil
import glob
import matplotlib.pyplot as plt
import logging


def create_loop_output_structure(outputs_directory, scenario_name, variable_name):
    """
    Defines the path of the loop_output_directory.

    Parameters
    ----------
    outputs_directory: str
        Path to output directory.
        Default: constants.DEFAULT_OUTPUTS_DIRECTORY.
    scenario_name: str
        Name of the Scenario. The name should follow the scheme:
        "Scenario_A1", "Scenario_A2", "Scenario_B1" etc.
    variable_name: str
        name of the variable that is atapted in each loop.

    Returns
    -------
    str
        path of the loop_output_directory.
    """

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

    # create two folder in loop_output_directories for "scalars" and "timeseries"
    os.mkdir(os.path.join(loop_output_directory, "scalars"))
    os.mkdir(os.path.join(loop_output_directory, "timeseries"))

    return loop_output_directory


def loop_pvcompare(
    scenario_name,
    latitude,
    longitude,
    years,
    storeys,
    country,
    loop_type,
    loop_dict=None,
    pv_setup=None,
    user_inputs_mvs_directory=None,
    outputs_directory=None,
    user_inputs_pvcompare_directory=None,
):
    """
    Starts multiple *pvcompare* simulations with a range of values for a
    specific loop type.

    The loop type corresponds to a variable or a set of
    variables that is/are changed in each loop.The
    results, stored in two excel sheets, are copied into `loop_output_directory`.

    Parameters
    ----------
    scenario_name: str
        Name of the Scenario. The name should follow the scheme:
        "Scenario_A1", "Scenario_A2", "Scenario_B1" etc.
    latitude: float
        latitude of the location
    longitude: foat
        longitude of the location
    years: list
        year(s) of simulation
    storeys: int
        number of storeys
    country: str
        country of location
    loop_type: str
        possible values: 'location', 'year', 'storeys', 'technology', 'hp_temp'.
        Defines the variable or variables that are changed with each loop.
    loop_dict: dict
        For location, the form of the dict should be: {"step1": ["country", "lat", "lon"], "step2": ["country", "lat", "lon"], etc}.
        For technology, the form of the dict should be: {"step1": "si", "step2": "cpv", "step3": "psi"}
        For year/storeys/hp_temp, the form of the dict should be: {"start": "1", "stop": "10", "step": "2"}
    pv_setup: dict or None
        If `pv_setup` is None, it is loaded from the `input_directory/pv_setup.cvs`.
        Default: None.
    user_inputs_mvs_directory: str or None
        Default: `user_inputs_mvs_directory = constants.DEFAULT_USER_INPUTS_MVS_DIRECTORY`
    outputs_directory: str or None
        Path to output directory.
        Default: `outputs_directory = constants.DEFAULT_OUTPUTS_DIRECTORY`
    user_inputs_pvcompare_directory: str or None
        If None, `constants.DEFAULT_USER_INPUTS_PVCOMPARE_DIRECTORY` is used
        as user_input_directory. Default: None.

    Returns
    -------
        None
    """
    # checks of outputs_directory and user_inputs_mvs_directory is None
    if user_inputs_mvs_directory == None:
        user_inputs_mvs_directory = constants.DEFAULT_USER_INPUTS_MVS_DIRECTORY
    if outputs_directory == None:
        outputs_directory = constants.DEFAULT_OUTPUTS_DIRECTORY
    if user_inputs_pvcompare_directory == None:
        user_inputs_pvcompare_directory = (
            constants.DEFAULT_USER_INPUTS_PVCOMPARE_DIRECTORY
        )

    loop_output_directory = create_loop_output_structure(
        outputs_directory=outputs_directory,
        scenario_name=scenario_name,
        variable_name=loop_type,
    )

    for year in years:
        if loop_type is "location":
            for key in loop_dict:
                country = loop_dict[key][0]
                latitude = loop_dict[key][1]
                longitude = loop_dict[key][2]

                single_loop_pvcompare(
                    scenario_name=scenario_name,
                    storeys=storeys,
                    country=country,
                    latitude=latitude,
                    longitude=longitude,
                    year=year,
                    user_inputs_pvcompare_directory=user_inputs_pvcompare_directory,
                    user_inputs_mvs_directory=user_inputs_mvs_directory,
                    outputs_directory=outputs_directory,
                    plot=False,
                    pv_setup=pv_setup,
                    loop_output_directory=loop_output_directory,
                    step=str(latitude) + "_" + str(longitude),
                    loop_type=loop_type,
                )

        elif loop_type is "year":

            year = loop_dict["start"]
            while year <= loop_dict["stop"]:

                single_loop_pvcompare(
                    scenario_name=scenario_name,
                    storeys=storeys,
                    country=country,
                    latitude=latitude,
                    longitude=longitude,
                    year=year,
                    user_inputs_pvcompare_directory=user_inputs_pvcompare_directory,
                    user_inputs_mvs_directory=user_inputs_mvs_directory,
                    outputs_directory=outputs_directory,
                    plot=False,
                    pv_setup=pv_setup,
                    loop_output_directory=loop_output_directory,
                    step=year,
                    loop_type=loop_type,
                )
                year = year + loop_dict["step"]

        elif loop_type is "storeys":

            number_of_storeys = loop_dict["start"]
            while number_of_storeys <= loop_dict["stop"]:

                single_loop_pvcompare(
                    scenario_name=scenario_name,
                    storeys=number_of_storeys,
                    country=country,
                    latitude=latitude,
                    longitude=longitude,
                    year=year,
                    user_inputs_pvcompare_directory=user_inputs_pvcompare_directory,
                    user_inputs_mvs_directory=user_inputs_mvs_directory,
                    outputs_directory=outputs_directory,
                    plot=False,
                    pv_setup=pv_setup,
                    loop_output_directory=loop_output_directory,
                    step=number_of_storeys,
                    loop_type=loop_type,
                )

                number_of_storeys = number_of_storeys + loop_dict["step"]

        elif loop_type is "technology":

            for key in loop_dict:
                technology = loop_dict[key]

                data_path = os.path.join(
                    user_inputs_pvcompare_directory, "pv_setup.csv"
                )
                # load input parameters from pv_setup.csv
                pv_setup = pd.read_csv(data_path)
                for i, row in pv_setup.iterrows():
                    pv_setup.at[i, "technology"] = technology
                pv_setup.to_csv(data_path, index=False)

                single_loop_pvcompare(
                    scenario_name=scenario_name,
                    storeys=storeys,
                    country=country,
                    latitude=latitude,
                    longitude=longitude,
                    year=year,
                    user_inputs_pvcompare_directory=user_inputs_pvcompare_directory,
                    user_inputs_mvs_directory=user_inputs_mvs_directory,
                    outputs_directory=outputs_directory,
                    plot=False,
                    pv_setup=None,
                    loop_output_directory=loop_output_directory,
                    step=technology,
                    loop_type=loop_type,
                )

        elif loop_type is "hp_temp":
            temp_high = loop_dict["start"]

            data_path = os.path.join(
                user_inputs_pvcompare_directory, "heat_pumps_and_chillers.csv"
            )
            while temp_high <= loop_dict["stop"]:
                # load input parameters from pv_setup.csv
                hp_file = pd.read_csv(data_path, index_col=0)
                hp_file.at["heat_pump", "temp_high"] = temp_high
                hp_file.to_csv(data_path)

                single_loop_pvcompare(
                    scenario_name=scenario_name,
                    storeys=storeys,
                    country=country,
                    latitude=latitude,
                    longitude=longitude,
                    year=year,
                    user_inputs_pvcompare_directory=user_inputs_pvcompare_directory,
                    user_inputs_mvs_directory=user_inputs_mvs_directory,
                    outputs_directory=outputs_directory,
                    plot=False,
                    pv_setup=pv_setup,
                    loop_output_directory=loop_output_directory,
                    step=temp_high,
                    loop_type=loop_type,
                )
                temp_high = temp_high + loop_dict["step"]

    logging.info("starting postprocessing KPI")
    postprocessing_kpi(
        scenario_name=scenario_name,
        variable_name=loop_type,
        outputs_directory=outputs_directory,
    )


def single_loop_pvcompare(
    scenario_name,
    storeys,
    country,
    latitude,
    longitude,
    year,
    user_inputs_pvcompare_directory,
    user_inputs_mvs_directory,
    outputs_directory,
    plot,
    pv_setup,
    loop_output_directory,
    loop_type,
    step,
):
    """

    Parameters
    ----------
    scenario_name: str
        name of the scenario.
    storeys: int
        number of storeys
    country: str
        country name
    latitude: float
        latitude of the location
    longitude: foat
        longitude of the location
    year: int
        year
    user_inputs_pvcompare_directory: str or None
        If None, `constants.DEFAULT_USER_INPUTS_PVCOMPARE_DIRECTORY` is used
        as user_input_directory. Default: None.
    user_inputs_mvs_directory: str or None
        Default: `user_inputs_mvs_directory = constants.DEFAULT_USER_INPUTS_MVS_DIRECTORY`
    outputs_directory: str or None
        Path to output directory.
        Default: `outputs_directory = constants.DEFAULT_OUTPUTS_DIRECTORY`
    plot: bool
        default: False
    loop_output_directory: str
        output directory defined in 'pvcompare.outputs.create_loop_output_structure()'.
    loop_type: str
        possible values: 'location', 'year', 'storeys', 'technology', 'hp_temp'.
        Defines the variable or variables that are changed with each loop.
    step: str or int
        Gradation of the loop variable.

    Returns
    -------
        None
    """

    main.apply_pvcompare(
        storeys=storeys,
        country=country,
        latitude=latitude,
        longitude=longitude,
        year=year,
        user_inputs_pvcompare_directory=user_inputs_pvcompare_directory,
        user_inputs_mvs_directory=user_inputs_mvs_directory,
        plot=plot,
        pv_setup=pv_setup,
    )

    # define mvs_output_directory for every looping step
    mvs_output_directory = os.path.join(
        outputs_directory,
        scenario_name,
        "mvs_outputs_loop_" + str(loop_type) + "_" + str(year) + "_" + str(step),
    )

    main.apply_mvs(
        scenario_name,
        user_inputs_mvs_directory=user_inputs_mvs_directory,
        mvs_output_directory=mvs_output_directory,
        outputs_directory=outputs_directory,
    )

    excel_file1 = "scalars.xlsx"
    new_excel_file1 = "scalars_" + str(year) + "_" + str(step) + ".xlsx"
    src_dir = os.path.join(mvs_output_directory, excel_file1)
    dst_dir = os.path.join(loop_output_directory, "scalars", new_excel_file1)
    shutil.copy(src_dir, dst_dir)

    excel_file2 = "timeseries_all_busses.xlsx"
    new_excel_file2 = (
        "timeseries_all_busses_" + "_" + str(year) + "_" + str(step) + ".xlsx"
    )
    src_dir = os.path.join(mvs_output_directory, excel_file2)
    dst_dir = os.path.join(loop_output_directory, "timeseries", new_excel_file2)
    shutil.copy(src_dir, dst_dir)


def loop_mvs(
    latitude,
    longitude,
    years,
    storeys,
    country,
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
    latitude: float
        latitude of the location
    longitude: foat
        longitude of the location
    years: list
        year(s) for simulation
    storeys:int
        number of storeys
    country: str
        country of location
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
        Default: `user_inputs_mvs_directory = constants.DEFAULT_USER_INPUTS_MVS_DIRECTORY`
    outputs_directory: str or None
        Path to output directory.
        Default: `outputs_directory = constants.DEFAULT_OUTPUTS_DIRECTORY`

    Returns
    -------

    """

    if outputs_directory is None:
        outputs_directory = constants.DEFAULT_OUTPUTS_DIRECTORY
    loop_output_directory = create_loop_output_structure(
        outputs_directory, scenario_name, variable_name
    )
    # define filename of variable that should be looped over
    if user_inputs_mvs_directory is None:
        user_inputs_mvs_directory = constants.DEFAULT_USER_INPUTS_MVS_DIRECTORY
    csv_filename = os.path.join(
        user_inputs_mvs_directory, "csv_elements", csv_file_variable
    )

    # loop over years
    for year in years:
        # apply pvcompare
        main.apply_pvcompare(
            latitude=latitude,
            longitude=longitude,
            year=year,
            storeys=storeys,
            country=country,
            user_inputs_mvs_directory=user_inputs_mvs_directory,
        )

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
                "mvs_outputs_loop_"
                + str(variable_name)
                + "_"
                + str(year)
                + "_"
                + str(i),
            )

            # apply mvs for every looping step
            main.apply_mvs(
                scenario_name=scenario_name,
                mvs_output_directory=mvs_output_directory,
                user_inputs_mvs_directory=user_inputs_mvs_directory,
                outputs_directory=outputs_directory,
            )

            # copy excel sheets to loop_output_directory
            number_digits = len(str(stop)) - len(str(i))

            if number_digits == 0:
                j = str(i)
            elif number_digits == 1:
                j = "0" + str(i)
            elif number_digits == 2:
                j = "00" + str(i)
            elif number_digits == 3:
                j = "000" + str(i)
            elif number_digits == 4:
                j = "0000" + str(i)

            excel_file1 = "scalars.xlsx"
            new_excel_file1 = "scalars_" + str(year) + "_" + str(j) + ".xlsx"
            src_dir = os.path.join(mvs_output_directory, excel_file1)
            dst_dir = os.path.join(loop_output_directory, "scalars", new_excel_file1)
            shutil.copy(src_dir, dst_dir)

            excel_file2 = "timeseries_all_busses.xlsx"
            new_excel_file2 = (
                "timeseries_all_busses_" + str(year) + "_" + str(j) + ".xlsx"
            )
            src_dir = os.path.join(mvs_output_directory, excel_file2)
            dst_dir = os.path.join(loop_output_directory, "timeseries", new_excel_file2)
            shutil.copy(src_dir, dst_dir)

            # add another step
            i = i + step
    logging.info("starting postprocessing KPI")
    postprocessing_kpi(
        scenario_name=scenario_name,
        variable_name=variable_name,
        outputs_directory=outputs_directory,
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
        outputs_directory = constants.DEFAULT_OUTPUTS_DIRECTORY
        scenario_folder = os.path.join(outputs_directory, scenario_name)
    else:
        scenario_folder = os.path.join(outputs_directory, scenario_name)
        if not os.path.isdir(scenario_folder):
            logging.warning(f"The scenario folder {scenario_name} does not exist.")
    if user_inputs_pvcompare_directory == None:
        user_inputs_pvcompare_directory = (
            constants.DEFAULT_USER_INPUTS_PVCOMPARE_DIRECTORY
        )

    # Get stratified TES inputs
    strat_tes_inputs = os.path.join(
        user_inputs_pvcompare_directory, "stratified_thermal_storage.csv"
    )
    if os.path.exists(strat_tes_inputs):
        strat_tes = pd.read_csv(strat_tes_inputs, index_col=0)
        heat_capacity = 4195.52
        density = 971.803
        temp_h = strat_tes.at["temp_h", "var_value"]
        temp_c = strat_tes.at["temp_c", "var_value"]
        diameter = strat_tes.at["diameter", "var_value"]

    # Get number of households in simulation
    building_params = pd.read_csv(
        os.path.join(user_inputs_pvcompare_directory, "building_parameters.csv"),
        index_col=0,
    )

    # Calculate the toal number of households
    # and hence obtain number of plants in simulation by assuming
    # that every household has one plant
    total_number_households = (
        float(building_params.at["number of houses", "value"])
        * float(building_params.at["number of storeys", "value"])
        * (float(building_params.at["population per storey", "value"]) / 4)
    )

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
        glob.glob(os.path.join(loop_output_directory, "scalars", "*.xlsx"))
    ):
        # read sheets of scalars
        scalars = pd.read_excel(filepath_s, sheet_name=None)

        file_sheet1 = scalars["cost_matrix"]
        file_sheet2 = scalars["scalar_matrix"]
        file_sheet2.index = file_sheet2["label"]
        file_sheet3 = scalars["scalars"]
        file_sheet3.index = file_sheet3.iloc[:, 0]
        file_sheet4 = scalars["KPI individual sectors"]

        # get variable value from filepath
        split_path = filepath_s.split("_")
        get_year = split_path[::-1][1]
        get_step = split_path[::-1][0]
        ending = str(get_year) + "_" + str(get_step)

        # load timeseries_all_busses
        for filepath_t in list(
            glob.glob(os.path.join(loop_output_directory, "timeseries", "*.xlsx"))
        ):
            heat_exists = False
            if filepath_t.endswith(ending) is True:
                # add heat demand to electricty demand it heat demand exists
                timeseries = pd.read_excel(filepath_t, sheet_name="Electricity bus")
                if "Heat pump" in timeseries.columns:
                    heat_exists = True
                    electricity_demand = (
                        timeseries["Electricity demand"] + timeseries["Heat pump"]
                    )
                    timeseries["Electricity demand"] = electricity_demand
                    with pd.ExcelWriter(filepath_t, mode="a") as writer:
                        timeseries.to_excel(writer, sheet_name="Electricity bus")
                    logging.info(
                        f"The timeseries_all_flows file {filepath_t} has been overwritten with the new electricity demand."
                    )
                else:
                    electricity_demand = timeseries["Electricity demand"]

                if heat_exists == True:
                    timeseries_heat = pd.read_excel(filepath_t, sheet_name="Heat bus")
                    if "TES output power" in timeseries_heat:
                        # Calculate maximum capacity, nominal capacity and height
                        # of one storage unit
                        maximal_tes_capacity = file_sheet2.at[
                            "TES storage capacity", "optimizedAddCap"
                        ]
                        # There is 15 % of unused storage volume according to
                        # https://op.europa.eu/en/publication-detail/-/publication/312f0f62-dfbd-11e7-9749-01aa75ed71a1/language-en
                        # The nominal storage capacity is hence the maximum storage capacity multiplied by 1.15
                        nominal_storage_capacity = maximal_tes_capacity * 1.15
                        # Calculate volume of TES using oemof-thermal's equations
                        # in stratified_thermal_storage.py
                        volume = (
                            maximal_tes_capacity
                            * 1000
                            / (heat_capacity * density * (temp_h - temp_c) * (1 / 3600))
                        )
                        # Calculate height of TES using oemof-thermal's equations
                        # in stratified_thermal_storage.py
                        height = volume / (0.25 * np.pi * diameter ** 2)
                        file_sheet3.at[
                            "Installed capacity per TES", "Unnamed: 0"
                        ] = "Installed capacity per TES"
                        # Divide total capacity through number of households = number of plants
                        file_sheet3.at["Installed capacity per TES", 0] = (
                            maximal_tes_capacity / total_number_households
                        )
                        file_sheet3.at[
                            "Installed nominal capacity per TES", "Unnamed: 0"
                        ] = "Installed nominal capacity per TES"
                        # Divide total nominal capacity through number of households = number of plants
                        file_sheet3.at["Installed nominal capacity per TES", 0] = (
                            nominal_storage_capacity / total_number_households
                        )
                        file_sheet3.at[
                            "Height of each TES", "Unnamed: 0"
                        ] = "Height of each TES"
                        # Divide total height of all TES through number of households = number of plants
                        file_sheet3.at["Height of each TES", 0] = (
                            height / total_number_households
                        )
                    if "Heat pump" in timeseries_heat.columns:
                        # Calculate maximum capacity of one heat pump unit and write to scalars
                        maximal_hp_capacity = max(timeseries_heat["Heat pump"])
                        file_sheet3.at[
                            "Installed capacity per heat pump", "Unnamed: 0"
                        ] = "Installed capacity per heat pump"
                        # Divide total capacity through number of households = number of plants
                        file_sheet3.at["Installed capacity per heat pump", 0] = (
                            maximal_hp_capacity / total_number_households
                        )

        # recalculate KPI
        file_sheet2.at["Electricity demand", "total_flow"] = sum(electricity_demand) * (
            -1
        )
        file_sheet3.at["Total_demandElectricity", 0] = sum(electricity_demand) * (-1)
        file_sheet3.at["Degree of NZE", 0] = (
            1
            + (
                file_sheet3.at["Total_feedinElectricity", 0]
                - file_sheet3.at[
                    "Total_consumption_from_energy_provider_electricity_equivalent", 0
                ]
            )
            / file_sheet3.at["Total_demandElectricity", 0]
        )
        file_sheet3.at["Degree of autonomy", 0] = (
            file_sheet3.at["Total_demandElectricity", 0]
            - file_sheet3.at["Total_consumption_from_energy_providerElectricity", 0]
        ) / file_sheet3.at["Total_demandElectricity", 0]
        file_sheet3.at["Onsite energy fraction", 0] = (
            file_sheet3.at["Total internal renewable generation", 0]
            - file_sheet3.at["Total_feedinElectricity", 0]
            - file_sheet3.at["Total_excessElectricity", 0]
        ) / file_sheet3.at["Total internal renewable generation", 0]

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
