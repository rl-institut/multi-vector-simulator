"""
Convert csv files to json file as input for the simulation.

The default input csv files are stored in "/inputs/elements/csv".
Otherwise their path is provided by the user.

The user can change parameters of the simulation of of the energy system in the csv files.

Storage: The "energyStorage.csv" contains information about all storages.
For each storage there needs to be another file named exactly after each storage-column in the
"energyStorage.csv" file. For the default file this is "storage_01", "storage_02" etc.
Please stick to this convention.

The function "create_input_json()" reads all csv files that are stored
in the given input folder (input_directory) and creates one json input file for mvs_tool.
"""

import os
import json
import logging
import pandas as pd

ALLOWED_FILES = (
    "fixcost",
    "simulation_settings",
    "project_data",
    "economic_data",
    "energyConversion",
    "energyProduction",
    "energyStorage",
    "energyProviders",
    "energyConsumption",
)


def create_input_json(
    input_directory,
    output_filename="autogenerated_json_input_file.json",
    pass_back=True,
):
    """
    Convert csv files to json file as input for the simulation.

    Looks at all csv-files in `input_directory` and compile the information they contain
    into a json file. The json file is then saved within the `input_directory`
    with the filename `output_filename`.
    While reading the csv files, it is checked, whether all required parameters
    for each component are provided. Missing parameters will return a warning message.

    :param input_directory: str
        path of the directory where the input csv files can be found
    :param output_filename: str
        path of the output file with file extension (it should be .json)
    :param pass_back: binary
        if pass_back=True: the final json dict is returned. Otherwise it is
        only saved

    :return: None or dict
    """

    logging.info(
        "loading and converting all csv's from %s" % input_directory + " into one json"
    )

    input_json = {}
    # hardcoded required lists of parameters for the creation of json files according csv file

    # hardcorded list of necessary csv files
    required_files_list = [
        "energyConsumption",
        "simulation_settings",
        "project_data",
        "economic_data",
    ]
    parameterlist = {}

    # Hardcoded list of parameters for each of the csv files.
    parameterlist.update(
        {
            "energyConsumption": [
                "dsm",
                "file_name",
                "label",
                "type_asset",
                "type_oemof",
                "energyVector",
                # "inflow_direction",
                "unit",
            ]
        }
    )
    parameterlist.update(
        {
            "energyConversion": [
                "age_installed",
                "capex_fix",
                "capex_var",
                "efficiency",
                "inflow_direction",
                "installedCap",
                "label",
                "lifetime",
                "opex_fix",
                "opex_var",
                "optimizeCap",
                "outflow_direction",
                "type_oemof",
                "energyVector",
                "unit",
            ]
        }
    )
    parameterlist.update(
        {
            "energyStorage": [
                "inflow_direction",
                "label",
                "optimizeCap",
                "outflow_direction",
                "type_oemof",
                "storage_filename",
                "energyVector",
            ]
        }
    )
    parameterlist.update(
        {
            "energyProduction": [
                "age_installed",
                "capex_fix",
                "capex_var",
                "file_name",
                "installedCap",
                "label",
                "lifetime",
                "opex_fix",
                "opex_var",
                "optimizeCap",
                "outflow_direction",
                "type_oemof",
                "unit",
                "energyVector",
            ]
        }
    )
    parameterlist.update(
        {
            "energyProviders": [
                "energy_price",
                "feedin_tariff",
                "inflow_direction",
                "label",
                "optimizeCap",
                "outflow_direction",
                "peak_demand_pricing",
                "peak_demand_pricing_period",
                "type_oemof",
                "energyVector",
            ]
        }
    )
    parameterlist.update(
        {
            "fixcost": [
                "age_installed",
                "capex_fix",
                "capex_var",
                "label",
                "lifetime",
                "opex_fix",
                "opex_var",
            ]
        }
    )
    parameterlist.update(
        {
            "simulation_settings": [
                "evaluated_period",
                "label",
                "oemof_file_name",
                "output_lp_file",
                "restore_from_oemof_file",
                "plot_nx_graph",
                "start_date",
                "store_oemof_results",
                "timestep",
            ]
        }
    )
    parameterlist.update(
        {
            "project_data": [
                "country",
                "label",
                "latitude",
                "longitude",
                "project_id",
                "project_name",
                "scenario_id",
                "scenario_name",
            ]
        }
    )
    parameterlist.update(
        {
            "economic_data": [
                "currency",
                "discount_factor",
                "label",
                "project_duration",
                "tax",
            ]
        }
    )

    # Read all csv files from path input directory
    list_assets = []
    for f in os.listdir(input_directory):
        filename = str(f[:-4])
        if filename in parameterlist.keys():
            list_assets.append(filename)
            parameters = parameterlist[filename]
            single_dict = create_json_from_csv(
                input_directory, filename, parameters=parameters
            )
            input_json.update(single_dict)
        elif "storage_" in filename:
            list_assets.append(filename)
            # TODO
            pass
        else:
            logging.error(
                "The file %s" % f + " is not recognized as input file for mvs "
                "check %s",
                input_directory + "for correct " "file names.",
            )

    # check if all required files are available
    extra = list(set(list_assets) ^ set(ALLOWED_FILES))

    for i in extra:
        if i in required_files_list:
            logging.error(
                "Required input file %s is missing! Please add it"
                "into %s." % (i, os.path.join(input_directory))
            )
        elif i in ALLOWED_FILES:
            logging.debug(
                "No %s" % i + ".csv file found. This is an " "accepted option."
            )
        elif "storage_" in i:
            pass
        else:
            logging.debug(
                "File %s" % i + ".csv is an unknown filename and"
                " will not be processed."
            )

    # store generated json file to file in input_directory.
    # This json will be used in the simulation.
    with open(os.path.join(input_directory, output_filename), "w") as outfile:
        json.dump(input_json, outfile, skipkeys=True, sort_keys=True, indent=4)
    logging.info(
        "Json file created successully from csv's and stored into "
        "%s" % os.path.join(input_directory, output_filename) + "\n"
    )
    logging.debug("Json created successfully from csv.")
    if pass_back:
        return outfile.name


def create_json_from_csv(input_directory, filename, parameters):

    """
    One csv file is loaded and it's parameters are checked. The csv file is
    then converted to a dictionary; the name of the csv file is used as the
    main key of the dictionary. Exceptions are made for the files
    ["economic_data", "project", "project_data", "simulation_settings"], here
    no main key is added. Another exception is made for the file
    "energyStorage". When this file is processed, the according "storage_"
    files (names of the "storage_"-columns in "energyStorage" are called and
    added to the energyStorage Dictionary.


    :param input_directory: str
        path of the directory where the input csv files can be found
    :param filename: str
        name of the inputfile that is transformed into a json, without
        extension
    :param parameters: list
        List of parameters names that are required
    :return: dict
        the converted dictionary
    """

    logging.debug("Loading input data from csv: %s", filename)

    df = pd.read_csv(
        os.path.join(input_directory, "%s.csv" % filename),
        sep=",",
        header=0,
        index_col=0,
    )

    # check parameters
    extra = list(set(parameters) ^ set(df.index))
    if len(extra) > 0:
        for i in extra:
            if i in parameters:
                logging.error(
                    "In the file %s.csv" % filename
                    + " the parameter "
                    + str(i)
                    + " is missing. "
                    "check %s",
                    input_directory + " for correct parameter names.",
                )
            else:
                logging.error(
                    "In the file %s.csv" % filename
                    + " the parameter "
                    + str(i)
                    + " is not recognized. \n"
                    "check %s",
                    input_directory + " for correct parameter names.",
                )

    # convert csv to json
    single_dict2 = {}
    single_dict = {}
    asset_name_string = ""
    if len(df.columns) == 1:
        logging.debug(
            "No %s" % filename + " assets are added because all "
            "columns of the csv file are empty."
        )

    for column in df:
        if column != "unit":
            column_dict = {}
            for i, row in df.iterrows():
                if i == "label":
                    asset_name_string = asset_name_string + row[column] + ", "

                # Find type of input value (csv file is read into df as an object)
                if isinstance(row[column], str) and (
                    "[" in row[column] or "]" in row[column]
                ):
                    if "[" not in row[column] or "]" not in row[column]:
                        logging.warning(
                            "In file %s, asset %s for parameter %s either '[' or ']' is missing.",
                            filename,
                            column,
                            i,
                        )
                    else:
                        # Define list of efficiencies by efficiency,factor,"[1;2]"
                        value_string = row[column].replace("[", "").replace("]", "")
                        value_list = value_string.split(";")
                        for item in range(0, len(value_list)):
                            column_dict = conversion(
                                filename, column_dict, row, i, column, value_list[item],
                            )
                            if row["unit"] != "str":
                                if "value" in column_dict[i]:
                                    # if wrapped in list is a scalar
                                    value_list[item] = column_dict[i]["value"]
                                else:
                                    # if wrapped in list is a dictionary (ie. timeseries)
                                    value_list[item] = column_dict[i]

                            else:
                                # if wrapped in list is a string
                                value_list[item] = column_dict[i]

                        if row["unit"] != "str":
                            column_dict.update(
                                {i: {"value": value_list, "unit": row["unit"]}}
                            )
                        else:
                            column_dict.update({i: value_list})
                        logging.info(
                            "Parameter %s of asset %s is defined as a list.", i, column,
                        )
                else:
                    column_dict = conversion(
                        filename, column_dict, row, i, column, row[column]
                    )

            single_dict.update({column: column_dict})
            # add exception for energyStorage
            if filename == "energyStorage":
                storage_dict = add_storage(column, input_directory)
                single_dict[column].update(storage_dict)

    logging.info(
        "From file %s following assets are added to the energy " "system: %s",
        filename,
        asset_name_string[:-2],
    )

    # add exception for single dicts
    if filename in [
        "economic_data",
        "project_data",
        "simulation_settings",
    ]:
        return single_dict
    elif "storage_" in filename:
        return single_dict
    else:
        single_dict2.update({filename: single_dict})
        return single_dict2
    return


def conversion(filename, column_dict, row, i, column, value):
    if isinstance(value, str) and ("{" in value or "}" in value):
        # if parameter defined as dictionary
        # example: input,str,"{'file_name':'pv_gen_merra2_2014_eff1_tilt40_az180.csv','header':'kW','unit':'kW'}"
        # todo this would not include [value, dict] eg. for multiple busses with one fix and one timeseries efficiency
        if "{" not in value or "}" not in value:
            logging.warning(
                "In file %s, asset %s for parameter %s either '{' or '}' is missing.",
                filename,
                column,
                i,
            )
        else:
            dict_string = value.replace("'", '"')
            value_dict = json.loads(dict_string)
            column_dict.update({i: value_dict})
            logging.info(
                "Parameter %s of asset %s is defined as a timeseries.", i, column
            )

    elif row["unit"] == "str":
        column_dict.update({i: value})

    else:
        if row["unit"] == "bool":
            if value in ["True", "true", "t"]:
                value = True
            elif value in ["False", "false", "F"]:
                value = False
            else:
                logging.warning(
                    "Parameter %s of asset %s is not a boolean value "
                    "(True/T/true or False/F/false."
                )
        else:
            if value == "None":
                value = None
            else:
                try:
                    value = int(value)
                except:
                    value = float(value)

        column_dict.update({i: {"value": value, "unit": row["unit"]}})
    return column_dict


def add_storage(storage_filename, input_directory):

    """
    loads the csv of a the specific storage listed as column in
    "energyStorage.csv", checks for complete set of parameters and creates a
    json dictionary.
    :param storage_filename: str
        name of storage, given by the column name in "energyStorage.csv
    :param input_directory: str
        path of the input directory
    :return: dict
        dictionary containing the storage parameters
    """

    if not os.path.exists(os.path.join(input_directory, "%s.csv" % storage_filename)):
        logging.error("The storage file %s.csv" % storage_filename + " is missing!")
    else:
        parameters = [
            "age_installed",
            "capex_fix",
            "capex_var",
            "crate",
            "efficiency",
            "installedCap",
            "label",
            "lifetime",
            "opex_fix",
            "opex_var",
            "soc_initial",
            "soc_max",
            "soc_min",
            "unit",
        ]
        single_dict = create_json_from_csv(
            input_directory, filename=storage_filename, parameters=parameters
        )
        return single_dict
