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

Functions of this module (that need to be tested)
- read all necessary input files (`REQUIRED_CSV_FILES`) from input folder
- display error message if `CSV_FNAME` already in input folder
- read all parameters in from csv files
- parse parameter that is given as a timeseries with input file name and header
- parse parameter that is given as a list
- check that parameter that is given as a list results and subsequent other parameters to be given
  as list e.g. if we have two output flows in conversion assets there should be two efficiencies
  to operational costs (this is not implemented in code yet)
- only necessary parameters should be transferred to json dict, error message with additonal parameters
- parse data from csv according to intended types - string, boolean, float, int, dict, list!
"""

import json
import logging
import os
import warnings

import pandas as pd

from src.constants import (
    CSV_FNAME,
    CSV_SEPARATORS,
    REQUIRED_CSV_FILES,
    REQUIRED_CSV_PARAMETERS,
    SIMULATION_SETTINGS,
    ECONOMIC_DATA,
    PROJECT_DATA,
    STORAGE_FILENAME,
    TYPE_BOOL,
    TYPE_STR,
    TYPE_NONE,
)
from src.constants_json_strings import (
    LABEL,
    P_DISPATCH,
    C_OM,
    COST_DEVELOPMENT,
    C_SPECIFIC,
    AGE_INSTALLED,
    LIFETIME,
    INSTALLED_CAP,
    EFFICIENCY,
    INPUT_POWER,
    OUTPUT_POWER,
    C_RATE,
    P_DISPATCH,
    SOC_INITIAL,
    SOC_MAX,
    SOC_MIN,
    STORAGE_CAPACITY,
    MAXIMUM_CAP,
)
from src.constants_json_strings import UNIT, VALUE, ENERGY_STORAGE


class MissingParameterError(ValueError):
    """Exception raised for missing parameters of a csv input file."""

    pass


class WrongParameterWarning(UserWarning):
    """Exception raised for errors in the parameters of a csv input file."""

    pass


class CsvParsingError(ValueError):
    """Exception raised for errors in the parameters of a csv input file."""

    pass


class WrongStorageColumn(ValueError):
    """Exception raised for wrong column name in "storage_xx" input file."""

    pass


def create_input_json(
    input_directory, pass_back=True,
):
    """Convert csv files to json file as input for the simulation.

    Looks at all csv-files in `input_directory` and compile the information they contain
    into a json file. The json file is then saved within the `input_directory`
    with the filename `CSV_FNAME`.
    While reading the csv files, it is checked, whether all required parameters
    for each component are provided. Missing parameters will return a warning message.

    Parameters
    ----------
    input_directory, str
        path of the directory where the input csv files can be found
    pass_back, bool, optional
        if True the final json dict is returned. Otherwise it is only saved
    Returns
    -------
        None or dict
    """

    logging.info(
        "loading and converting all csv's from %s" % input_directory + " into one json"
    )

    output_filename = os.path.join(input_directory, CSV_FNAME)

    if os.path.exists(output_filename):
        raise FileExistsError(
            f"The mvs json config file {CSV_FNAME} already exists in the input "
            f"folder {input_directory}. This is likely due to an aborted "
            f"previous run. Please make sure no such file is located within "
            f"the folder prior to run a new simulation"
        )

    input_json = {}

    # Read all csv files from path input directory
    list_assets = []
    for f in os.listdir(input_directory):
        filename = str(f[:-4])
        if filename in REQUIRED_CSV_FILES:
            list_assets.append(filename)
            single_dict = create_json_from_csv(input_directory, filename)
            input_json.update(single_dict)
        elif "storage_" in filename:
            list_assets.append(filename)
            # TODO
            pass

    # check if all required files are available
    extra = list(set(list_assets) ^ set(REQUIRED_CSV_FILES))

    missing_csv_files = []
    for i in extra:
        if i in REQUIRED_CSV_FILES:
            missing_csv_files.append(i)
        elif "storage_" in i:
            pass
        else:
            logging.error(
                f"File {i}.csv is an unknown filename and will not be processed."
            )

    if len(missing_csv_files) > 0:
        raise FileNotFoundError(
            f"Required input files {missing_csv_files} are missing! Please add them "
            f"into {input_directory}. The required files are {REQUIRED_CSV_FILES}"
        )
    # store generated json file to file in input_directory.
    # This json will be used in the simulation.
    with open(output_filename, "w") as outfile:
        json.dump(input_json, outfile, skipkeys=True, sort_keys=True, indent=4)
    logging.info(
        f"Json file created successully from csv's and stored into {output_filename}\n"
    )
    logging.debug("Json created successfully from csv.")
    if pass_back:
        return outfile.name


def create_json_from_csv(
    input_directory, filename, parameters=None, asset_is_a_storage=False
):

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
        name of the input file that is transformed into a json, without
        extension
    :param parameters: list
        List of parameters names that are required
    :param asset_is_a_storage : bool
        default value is False. If the function is called by
        add_storage_components() the
        parameter is set to True
    :return: dict
        the converted dictionary
    """

    logging.debug("Loading input data from csv: %s", filename)

    parameters = REQUIRED_CSV_PARAMETERS.get(filename, parameters)

    if parameters is None:
        raise MissingParameterError(
            f"No parameters were provided to extract from the file file {filename}.csv \n"
            f"Please check {input_directory} for correct parameter names."
        )

    # allow different separators for csv files, take the first one which works
    seperator_unknown = True

    idx = 0
    while seperator_unknown is True and idx < len(CSV_SEPARATORS):
        df = pd.read_csv(
            os.path.join(input_directory, "{}.csv".format(filename)),
            sep=CSV_SEPARATORS[idx],
            header=0,
            index_col=0,
        )

        if len(df.columns) > 0:
            seperator_unknown = False
        else:
            idx = idx + 1

    if seperator_unknown is True:
        raise CsvParsingError(
            "The csv file {} has a separator for values which is not one of the "
            "following: {}. The file was therefore unparsable".format(
                os.path.join(input_directory, f"{filename}.csv"), CSV_SEPARATORS
            )
        )

    # check wether parameter maximumCap is availavle
    # TODO in next version: add maximumCap to hardcoded parameter list in constants.py
    # TODO create this as a function, so that in future also new parameters can be added
    list_of_new_parameters = {
        MAXIMUM_CAP: "allows setting a maximum capacity for an asset that is being capacity optimized (Values: None/Float). ",
        "renewableAsset": "allows defining a energyProduction asset as either renewable (True) or non-renewable (False) source. ",
        "renewable_share": "allows defining the renewable share of the DSO supply (Values: Float). ",
    }

    for new_parameter in list_of_new_parameters:
        if new_parameter in df.index:
            parameters.append(new_parameter)
        else:
            # todo this message should only be displayed in case that the parameter is actually supposed to be applied to each of the files. For maxCap, this is also not valid, eg. it should not be added to economic_data
            logging.warning(
                f"You are not using the parameter {new_parameter} for asset group {filename}, which "
                + list_of_new_parameters[new_parameter]
                + "In the upcoming version of the MVS, this parameter will be required."
            )

    # check parameters
    missing_parameters = []
    wrong_parameters = []
    if asset_is_a_storage is False:
        extra = list(set(parameters) ^ set(df.index))
        if len(extra) > 0:
            for i in extra:
                if i in parameters:
                    missing_parameters.append(i)
                else:
                    wrong_parameters.append(i)

    if len(missing_parameters) > 0 or len(parameters) == 0:
        raise MissingParameterError(
            f"In the file {filename}.csv the parameter {i} is missing. \n"
            f"Please check {input_directory} for correct parameter names."
        )
    elif len(wrong_parameters) > 0:
        warnings.warn(
            WrongParameterWarning(
                f"The parameter {i} in the file"
                f"{os.path.join(input_directory,filename)}.csv is not expected. \n"
                f"Expected parameters are {parameters}"
            )
        )
        # ignore the wrong parameter which is in the csv but not required by the parameters list
        df = df.drop(wrong_parameters)

    # convert csv to json
    single_dict = {}
    asset_name_string = ""
    if len(df.columns) == 1:
        logging.debug(
            "No %s" % filename + " assets are added because all "
            "columns of the csv file are empty."
        )
    df_copy = df.copy()
    for column in df_copy:
        if column != UNIT:
            column_dict = {}
            # the storage columns are checked for the right parameters,
            # Nan values that are not needed are deleted
            if asset_is_a_storage is True:
                # check if all three columns are available
                if len(df_copy.columns) < 4 or len(df_copy.columns) > 4:
                    logging.error(
                        f"The file {filename}.csv requires "
                        f"three columns, you have inserted {len(df_copy.columns)}"
                        "columns."
                    )
                # add column specific parameters
                if column == STORAGE_CAPACITY:
                    extra = [SOC_INITIAL, SOC_MAX, SOC_MIN]
                elif column == INPUT_POWER or column == OUTPUT_POWER:
                    extra = [C_RATE, P_DISPATCH]
                else:
                    raise WrongStorageColumn(
                        f"The column name {column} in The file {filename}.csv"
                        " is not valid. Please use the column names: "
                        "'storage capacity', 'input power' and "
                        "'output power'."
                    )
                column_parameters = parameters + extra
                # check if required parameters are missing
                for i in set(column_parameters) - set(df_copy.index):
                    raise MissingParameterError(
                        f"In file {filename}.csv the parameter {i}"
                        f" in column {column} is missing."
                    )
                for i in df_copy.index:
                    if i not in column_parameters:
                        # check if not required parameters are set to Nan and
                        # if not, set them to Nan
                        if i not in [
                            C_RATE,
                            P_DISPATCH,
                            SOC_INITIAL,
                            SOC_MAX,
                            SOC_MIN,
                        ]:
                            warnings.warn(
                                WrongParameterWarning(
                                    f"The storage parameter {i} of the file "
                                    f"{os.path.join(input_directory,filename)}.csv "
                                    f"is not recognized. It will not be "
                                    "considered in the simulation."
                                )
                            )
                            df_copy.loc[[i], [column]] = "NaN"

                        elif pd.isnull(df_copy.at[i, column]) is False:
                            warnings.warn(
                                WrongParameterWarning(
                                    f"The storage parameter {i} in column "
                                    f" {column} of the file {filename}.csv should "
                                    "be set to NaN. It will not be considered in the "
                                    "simulation"
                                )
                            )
                            df_copy.loc[[i], [column]] = "NaN"
                        else:
                            logging.debug(
                                f"In file {filename}.csv the parameter {str(i)}"
                                f" in column {column} is NaN. This is correct; "
                                f"the parameter will not be considered."
                            )
                    # check if all other values have a value unequal to Nan
                    elif pd.isnull(df_copy.at[i, column]) is True:
                        warnings.warn(
                            WrongParameterWarning(
                                f"In file {filename}.csv the parameter {i}"
                                f" in column {column} is NaN. Please insert a value "
                                "of 0 or int. For this "
                                "simulation the value is set to 0 "
                                "automatically."
                            )
                        )

                        df_copy.loc[[i], [column]] = 0
                # delete not required rows in column
                df = df_copy[df_copy[column].notna()]

            for param, row in df.iterrows():
                if param == LABEL:
                    asset_name_string = asset_name_string + row[column] + ", "

                # Find type of input value (csv file is read into df as an object)
                if isinstance(row[column], str) and (
                    "[" in row[column] or "]" in row[column]
                ):
                    if "[" not in row[column] or "]" not in row[column]:
                        logging.warning(
                            f"In file {filename}, asset {column} for parameter {param} either '[' "
                            f"or ']' is missing."
                        )
                    else:
                        # Define list of efficiencies by efficiency,factor,"[1,2]"
                        value_string = row[column].replace("[", "").replace("]", "")

                        # find the separator used for the list amongst the CSV_SEPARATORS
                        list_separator = None
                        separator_count = 0
                        for separator in CSV_SEPARATORS:
                            if separator in value_string:
                                if value_string.count(separator) > separator_count:
                                    if separator_count > 0:
                                        raise ValueError(
                                            f"The separator of the list for the "
                                            f"parameter {param} is not unique"
                                        )
                                    separator_count = value_string.count(separator)
                                    list_separator = separator

                        value_list = value_string.split(list_separator)

                        for item in range(0, len(value_list)):
                            column_dict = conversion(
                                value_list[item].strip(),
                                column_dict,
                                row,
                                param=param,
                                asset=column,
                                filename=filename,
                            )
                            if row[UNIT] != TYPE_STR:
                                if VALUE in column_dict[param]:
                                    # if wrapped in list is a scalar
                                    value_list[item] = column_dict[param][VALUE]
                                else:
                                    # if wrapped in list is a dictionary (ie. timeseries)
                                    value_list[item] = column_dict[param]

                            else:
                                # if wrapped in list is a string
                                value_list[item] = column_dict[param]

                        if row[UNIT] != TYPE_STR:
                            column_dict.update(
                                {param: {VALUE: value_list, UNIT: row[UNIT]}}
                            )
                        else:
                            column_dict.update({param: value_list})
                        logging.info(
                            f"Parameter {param} of asset {column} is defined as a list."
                        )
                else:
                    column_dict = conversion(
                        row[column],
                        column_dict,
                        row,
                        param=param,
                        asset=column,
                        filename=filename,
                    )

            single_dict.update({column: column_dict})
            # add exception for energyStorage
            if filename == ENERGY_STORAGE:
                storage_dict = add_storage_components(
                    df.loc[STORAGE_FILENAME][column][:-4], input_directory
                )
                single_dict[column].update(storage_dict)

    logging.info(
        "From file %s following assets are added to the energy system: %s",
        filename,
        asset_name_string[:-2],
    )

    # add exception for single dicts
    if filename in [
        ECONOMIC_DATA,
        PROJECT_DATA,
        SIMULATION_SETTINGS,
    ]:
        return single_dict
    elif asset_is_a_storage is True:
        return single_dict
    else:
        single_dict2 = {}
        single_dict2.update({filename: single_dict})
        return single_dict2
    return


def conversion(value, asset_dict, row, param, asset, filename=""):
    if isinstance(value, str) and ("{" in value or "}" in value):
        # if parameter defined as dictionary
        # example: input,str,"{'file_name':'pv_gen_merra2_2014_eff1_tilt40_az180.csv','header':'kW','unit':'kW'}"
        # todo this would not include [value, dict] eg. for multiple busses with one fix and one timeseries efficiency
        if "{" not in value or "}" not in value:
            logging.warning(
                f"In file {filename}, asset {asset} for parameter {param} either '{{' or '}}' is "
                f"missing."
            )
        else:
            dict_string = value.replace("'", '"')
            asset_dict.update({param: json.loads(dict_string)})
            logging.info(
                f"Parameter {param} of asset {asset} is defined as a timeseries."
            )

    elif row[UNIT] == TYPE_STR:
        asset_dict.update({param: value})

    else:
        if row[UNIT] == TYPE_BOOL:
            if value in ["True", "true", "T", "t", "1"]:
                value = True
            elif value in ["False", "false", "F", "f", "0"]:
                value = False
            else:
                logging.warning(
                    f"Parameter {param} of asset {asset} is not a boolean value "
                    "(True/T/true or False/F/false)."
                )
        else:
            if value == TYPE_NONE:
                value = None
            else:
                try:
                    value = int(value)
                except:
                    value = float(value)

        asset_dict.update({param: {VALUE: value, UNIT: row[UNIT]}})
    return asset_dict


def add_storage_components(storage_filename, input_directory):

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

    if not os.path.exists(os.path.join(input_directory, f"{storage_filename}.csv")):
        logging.error(f"The storage file {storage_filename}.csv is missing!")
    else:
        # hardcoded parameterlist of common parameters in all columns
        parameters = [
            AGE_INSTALLED,
            COST_DEVELOPMENT,
            C_SPECIFIC,
            EFFICIENCY,
            INSTALLED_CAP,
            LABEL,
            LIFETIME,
            C_OM,
            UNIT,
        ]
        single_dict = create_json_from_csv(
            input_directory,
            filename=storage_filename,
            parameters=parameters,
            asset_is_a_storage=True,
        )
        return single_dict
