"""
Module A1 - Csv to json
=======================

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

from multi_vector_simulator.utils.constants import (
    CSV_FNAME,
    CSV_SEPARATORS,
    REQUIRED_CSV_FILES,
    REQUIRED_CSV_PARAMETERS,
    SIMULATION_SETTINGS,
    ECONOMIC_DATA,
    PROJECT_DATA,
    CONSTRAINTS,
    ENERGY_BUSSES,
    ENERGY_CONSUMPTION,
    ENERGY_CONVERSION,
    ENERGY_PRODUCTION,
    ENERGY_PROVIDERS,
    STORAGE_FILENAME,
    TYPE_BOOL,
    TYPE_STR,
    TYPE_NONE,
    KNOWN_EXTRA_PARAMETERS,
    WARNING_TEXT,
    REQUIRED_IN_CSV_ELEMENTS,
    DEFAULT_VALUE,
    HEADER,
    FIX_COST,
)
from multi_vector_simulator.utils.constants_json_strings import (
    LABEL,
    SPECIFIC_COSTS_OM,
    DEVELOPMENT_COSTS,
    SPECIFIC_COSTS,
    AGE_INSTALLED,
    LIFETIME,
    INSTALLED_CAP,
    EFFICIENCY,
    INPUT_POWER,
    OUTPUT_POWER,
    C_RATE,
    DISPATCH_PRICE,
    SOC_INITIAL,
    SOC_MAX,
    SOC_MIN,
    THERM_LOSSES_REL,
    THERM_LOSSES_ABS,
    STORAGE_CAPACITY,
    FILENAME,
    UNIT,
    VALUE,
    ENERGY_STORAGE,
)


from multi_vector_simulator.utils.exceptions import (
    MissingParameterError,
    CsvParsingError,
    WrongStorageColumn,
    MissingCsvEndingError,
)


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
            if filename in [PROJECT_DATA, ECONOMIC_DATA, SIMULATION_SETTINGS]:
                # use filename as label
                single_dict[filename][LABEL] = filename
            elif filename in [
                ENERGY_BUSSES,
                ENERGY_CONSUMPTION,
                ENERGY_CONVERSION,
                ENERGY_PRODUCTION,
                ENERGY_PROVIDERS,
                FIX_COST,
            ]:
                # use column names as labels, replace underscores and capitalize
                for key, item in single_dict[filename].items():
                    item[LABEL] = key
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
        f"Json file created successfully from csv's and stored into {output_filename}\n"
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
    ["economic_data", "project", "project_data", "simulation_settings", "constraints"], here
    no main key is added. Another exception is made for the file
    "energyStorage". When this file is processed, the according "storage"
    files (names of the "storage" columns in "energyStorage" are called and
    added to the energyStorage Dictionary.

    Parameters
    ----------
    input_directory : str
        path of the directory where the input csv files can be found
    filename : str
        name of the input file that is transformed into a json, without
        extension
    parameters : list
        List of parameters names that are required

    asset_is_a_storage : bool
        default value is False. If the function is called by
        add_storage_components() the
        parameter is set to True

    Returns
    -------
    dict
        the converted dictionary

    Notes
    -----
    Tested with:
    - test_default_values_storage_without_thermal_losses()
    - test_default_values_storage_with_thermal_losses()
    """

    logging.debug("Loading input data from csv: %s", filename)

    parameters = REQUIRED_CSV_PARAMETERS.get(filename, parameters)

    if parameters is None:
        raise MissingParameterError(
            f"No parameters were provided to extract from the file {filename}.csv \n"
            f"Please check {input_directory} for correct parameter names."
        )

    # allow different separators for csv files, take the first one which works
    seperator_unknown = True

    idx = 0
    while seperator_unknown is True and idx < len(CSV_SEPARATORS):

        try:
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

        except pd.errors.ParserError:
            logging.warning(
                f"The file {filename} is not separated by {CSV_SEPARATORS[idx]} or has a formatting problem somewhere"
            )
            seperator_unknown = True
            idx = idx + 1

    if seperator_unknown is True:
        raise CsvParsingError(
            "The csv file {} has a separator for values which is not one of the "
            "following: {}. The file was therefore unparsable".format(
                os.path.join(input_directory, f"{filename}.csv"), CSV_SEPARATORS
            )
        )

    # check for wrong or missing required parameters
    missing_parameters = []
    wrong_parameters = []
    if asset_is_a_storage is False:
        extra = list(set(parameters) ^ set(df.index))
        if len(extra) > 0:
            for i in extra:
                if i in parameters:
                    missing_parameters.append(i)
                else:
                    if i not in KNOWN_EXTRA_PARAMETERS:
                        wrong_parameters.append(i)

    if len(wrong_parameters) > 0:
        parameter_string = ", ".join(map(str, parameters))
        logging.warning(
            f"The parameter {i} in the file "
            f"{os.path.join(input_directory,filename)}.csv is not expected. "
            f"Expected parameters are: {str(parameter_string)}"
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
                    extra = [
                        SOC_INITIAL,
                        SOC_MAX,
                        SOC_MIN,
                        THERM_LOSSES_REL,
                        THERM_LOSSES_ABS,
                    ]
                elif column == INPUT_POWER or column == OUTPUT_POWER:
                    extra = [C_RATE, DISPATCH_PRICE]
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
                    if i == THERM_LOSSES_REL:
                        logging.debug(
                            f"You are not using the parameter {THERM_LOSSES_REL}, which allows considering relative thermal energy losses (Values: Float). This is an advanced setting that most users can ignore."
                        )
                        # Set 0 as default parameter for losses in storage capacity
                        losses = pd.DataFrame(
                            data={
                                "": THERM_LOSSES_REL,
                                df_copy.columns[0]: ["factor"],
                                df_copy.columns[1]: [0],
                            }
                        )
                        losses = losses.set_index("")
                        # Append missing parameter to dataframe
                        df_copy = pd.concat([df_copy, losses])
                    elif i == THERM_LOSSES_ABS:
                        logging.debug(
                            f"You are not using the parameter {THERM_LOSSES_ABS}, which allows considering relative thermal energy losses (Values: Float). This is an advanced setting that most users can ignore."
                        )
                        # Set 0 as default parameter for losses in storage capacity
                        losses = pd.DataFrame(
                            data={
                                "": THERM_LOSSES_ABS,
                                df_copy.columns[0]: ["kWh"],
                                df_copy.columns[1]: [0],
                            }
                        )
                        losses = losses.set_index("")
                        # Append missing parameter to dataframe
                        df_copy = pd.concat([df_copy, losses])
                    else:
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
                            DISPATCH_PRICE,
                            SOC_INITIAL,
                            SOC_MAX,
                            SOC_MIN,
                            THERM_LOSSES_REL,
                            THERM_LOSSES_ABS,
                        ]:
                            logging.warning(
                                f"The storage parameter {i} of the file "
                                f"{os.path.join(input_directory,filename)}.csv "
                                f"is not recognized. It will not be "
                                "considered in the simulation."
                            )

                            df_copy.loc[[i], [column]] = "NaN"

                        elif pd.isnull(df_copy.at[i, column]) is False:
                            logging.warning(
                                f"The storage parameter {i} in column "
                                f" {column} of the file {filename}.csv should "
                                "be set to NaN. It will not be considered in the "
                                "simulation"
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
                        logging.warning(
                            f"In file {filename}.csv the parameter {i}"
                            f" in column {column} is NaN. Please insert a value "
                            "of 0 or int. For this "
                            "simulation the value is set to 0 "
                            "automatically."
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
                storage_file_name = check_storage_file_is_csv(
                    df.loc[STORAGE_FILENAME][column]
                )
                storage_dict = add_storage_components(
                    storage_file_name, input_directory, single_dict[column][LABEL],
                )
                single_dict[column].update(storage_dict)

    logging.debug(
        "From file %s following assets are added to the energy system: %s",
        filename,
        asset_name_string[:-2],
    )

    # add exception for single dicts
    if filename in [
        ECONOMIC_DATA,
        PROJECT_DATA,
        SIMULATION_SETTINGS,
        CONSTRAINTS,
    ]:
        return single_dict
    elif asset_is_a_storage is True:
        return single_dict
    else:
        single_dict2 = {}
        single_dict2.update({filename: single_dict})
        return single_dict2


def check_storage_file_is_csv(storage_file):
    r"""
    Checks that the storage file name defined in `energyStorage.csv` has ending `.csv`.

    Parameters
    ----------
    storage_file: str
        Defined storage file name

    Returns
    -------

    If test fails: MissingCsvEndingError(ValueError), else:

    storage_file: str
        Storage file name without ending '.csv'

    """
    if storage_file[-4:] == ".csv":
        storage_file = storage_file[:-4]
    else:
        raise MissingCsvEndingError(
            f"The storage file defined as input in {ENERGY_STORAGE} does not end with '.csv' but is only {storage_file}. Please add the file ending."
        )
    return storage_file


def conversion(value, asset_dict, row, param, asset, filename=""):
    r"""
    This function converts the input given in the csv to the dict used in the MVS.

    When using json files, they are already provided parsed like this functions output.

    Parameters
    ----------
    value: Misc.
        Value to be parsed

    asset_dict: dict
        Dict of asset that is to be filled with data

    row:
    param: str
        Parameter that is currently parsed

    asset
    filename

    Returns
    -------
    """
    if pd.isnull(value):
        logging.error(
            f"Parameter {param} of asset {asset} (group: {filename}) is missing. "
            f"The simulation may continue, but errors during execution or in the results can be expected."
        )

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
            if (
                FILENAME in asset_dict[param]
                and HEADER in asset_dict[param]
                and UNIT in asset_dict[param]
            ):
                logging.info(
                    f"Parameter {param} of asset {asset} is defined as a timeseries."
                )
            else:
                logging.warning(
                    f"Parameter {param} of asset {asset} is defined as a dict, "
                    f"bus does not inlude parameters {FILENAME}, {HEADER} and {UNIT} to make the input complete "
                    f"and result in a timeseries."
                )

            # todo: this should result in reading the csv and writing a pd.Series to the param

    # If unit should be a string
    elif row[UNIT] == TYPE_STR:
        asset_dict.update({param: value})

    else:
        # If unit should be a bool
        if row[UNIT] == TYPE_BOOL:
            if value in [True, "TRUE", "True", "true", "T", "t", "1"]:
                value = True
            elif value in [False, "FALSE", "False", "false", "F", "f", "0"]:
                value = False
            else:
                logging.warning(
                    f"Parameter {param} of asset {asset} is not a boolean value "
                    "(True/T/true or False/F/false)."
                )
        else:
            if value == TYPE_NONE or value is None:
                value = None
            else:
                try:
                    value = float(value)
                    if value.is_integer() is True:
                        value = int(value)
                except:
                    value = int(value)
        asset_dict.update({param: {VALUE: value, UNIT: row[UNIT]}})
    return asset_dict


def add_storage_components(storage_filename, input_directory, storage_label):
    r"""
    Creates json dict from storage csv.

    Loads the csv of a the specific storage listed as column in
    "energyStorage.csv", checks for complete set of parameters, adds a label and creates
    a json dictionary.

    Parameters
    ----------
    storage_filename: str
        file name excl. extension, given by the parameter 'file_name` in "energyStorage.csv
    input_directory: str
        path to the input directory where `storage_filename` is located
    storage_label: str
        Label of storage

    Notes
    -----
    Tested with:
    - test_add_storage_components_label_correctly_added()

    Returns
    -------
    dict
        dictionary containing the storage parameters
    """
    if not os.path.exists(os.path.join(input_directory, f"{storage_filename}.csv")):
        logging.error(f"The storage file {storage_filename}.csv is missing!")
    else:
        # hardcoded parameter list of common parameters in all columns
        parameters = [
            AGE_INSTALLED,
            DEVELOPMENT_COSTS,
            SPECIFIC_COSTS,
            EFFICIENCY,
            INSTALLED_CAP,
            LIFETIME,
            SPECIFIC_COSTS_OM,
            UNIT,
        ]
        single_dict = create_json_from_csv(
            input_directory,
            filename=storage_filename,
            parameters=parameters,
            asset_is_a_storage=True,
        )
        # add labels to storage
        for key, item in single_dict.items():
            item[LABEL] = " ".join([storage_label, key])
        return single_dict
