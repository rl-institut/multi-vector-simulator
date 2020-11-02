import copy
import json
import os

import numpy as np
import pandas as pd

from multi_vector_simulator.utils.constants_json_strings import (
    START_DATE,
    PERIODS,
    END_DATE,
    EVALUATED_PERIOD,
    TIME_INDEX,
    TIMESTEP,
    UNIT_MINUTE,
    VALUE,
)

from multi_vector_simulator.utils.constants import (
    CSV_FNAME,
    INPUTS_COPY,
    PATHS_TO_PLOTS,
    DICT_PLOTS,
    DATA_TYPE_JSON_KEY,
    TYPE_DATETIMEINDEX,
    TYPE_SERIES,
    TYPE_NDARRAY,
    TYPE_DATAFRAME,
    TYPE_TIMESTAMP,
    SIMULATION_SETTINGS,
    PATH_INPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
    PATH_OUTPUT_FOLDER_INPUTS,
)

"""
This module is used to open a json file and parse it as a dict all input parameters for the energy 
system.

If the user does not give the input parameters "path_input_folder", "path_output_folder" or "path_output_folder_inputs", they are replaced by the default values.

It will be an interface to the EPA.
"""


def convert_from_json_to_special_types(a_dict, prev_key=None):
    """Convert the field values of the mvs result json file which are not simple types.

    The function is recursive to explore all nested levels

    Parameters
    ----------
    a_dict: variable
        In the recursion, this is either a dict (moving down one nesting level) or a field value
    prev_key: str
        The previous key of the dict in the recursive loop
    Returns
    The original dictionary, with the serialized instances of pandas.Series,
    pandas.DatetimeIndex, pandas.DataFrame, numpy.array converted back to their original form
    -------

    """

    answer = a_dict
    if isinstance(a_dict, dict):
        # the a_dict argument is a dictionary not containing the special type key,
        # therefore we dive deeper in the nesting level
        if DATA_TYPE_JSON_KEY not in a_dict:
            answer = {}
            for k in a_dict:
                answer[k] = convert_from_json_to_special_types(a_dict[k], prev_key=k)
        else:
            # the a_dict is a dictionary containing the special type key,
            # therefore we apply the conversion if this type is listed below

            # find the special type value
            data_type = a_dict.pop(DATA_TYPE_JSON_KEY)

            if TYPE_DATAFRAME in data_type:
                # pandas.DataFrame
                a_dict = json.dumps(a_dict)
                answer = pd.read_json(a_dict, orient="split")
            elif TYPE_DATETIMEINDEX in data_type:
                # pandas.DatetimeIndex
                a_dict = json.dumps(a_dict)
                answer = pd.read_json(a_dict, orient="split")
                answer = pd.to_datetime(answer.index)

                answer.freq = answer.inferred_freq
            elif TYPE_SERIES in data_type:
                # pandas.Series
                # extract the name of the series in case it was a tuple
                name = a_dict.pop("name")

                # reconvert the dict to a json for conversion to pandas Series
                a_dict = json.dumps(a_dict)
                answer = pd.read_json(a_dict, orient="split", typ="series")

                # if the name was a tuple it was converted to a list via json serialization
                if isinstance(name, list):
                    name[0] = tuple(name[0])
                    name = tuple(name)

                if name is not None:
                    answer.name = name

            elif TYPE_TIMESTAMP in data_type:
                answer = pd.Timestamp(a_dict[VALUE])
            elif TYPE_NDARRAY in data_type:
                # numpy.array
                answer = np.array(a_dict[VALUE])

    return answer


def convert_from_special_types_to_json(o):
    """This converts all data stored in dict_values that is not compatible with the
    json format to a format that is compatible.

    Parameters
    ----------
    o :
        Any type. Object to be converted to json-storable value.

    Returns
    -------
    type
        json-storable value.

    """
    if isinstance(o, np.int64):
        answer = int(o)
    elif isinstance(o, bool) or isinstance(o, str):
        answer = o
    elif isinstance(o, pd.DatetimeIndex):
        answer = {DATA_TYPE_JSON_KEY: TYPE_DATETIMEINDEX, VALUE: o.values.tolist()}
    elif isinstance(o, pd.Timestamp):
        answer = {DATA_TYPE_JSON_KEY: TYPE_TIMESTAMP, VALUE: str(o)}
    elif isinstance(o, pd.Series):
        answer = {DATA_TYPE_JSON_KEY: TYPE_SERIES, VALUE: o.to_list()}
    elif isinstance(o, np.ndarray):
        answer = {DATA_TYPE_JSON_KEY: TYPE_NDARRAY, VALUE: o.tolist()}
    elif isinstance(o, pd.DataFrame):
        answer = {DATA_TYPE_JSON_KEY: TYPE_DATAFRAME}
        answer.update(json.loads(o.to_json(orient="split")))
    else:
        raise TypeError(
            "An error occurred when converting the simulation data (dict_values) to json, as the type is not recognized: \n"
            "Type: " + str(type(o)) + " \n "
            "Value(s): " + str(o) + "\n"
            "Please edit function CO_data_processing.dataprocessing.store_as_json."
        )

    return answer


def retrieve_date_time_info(simulation_settings):
    """
    Updates simulation settings by all time-related parameters.
    - START_DATE
    - END_DATE
    - TIME_INDEX
    - PERIODS

    Parameters
    ----------
    simulation_settings: dict
        Simulation parameters of the input data

    Returns
    -------
    Update simulation_settings by start date, end date, timeindex, and number of simulation periods


    Notes
    -----
    Function tested with test_retrieve_datetimeindex_for_simulation()
    """
    simulation_settings.update(
        {START_DATE: pd.to_datetime(simulation_settings[START_DATE])}
    )
    simulation_settings.update(
        {
            END_DATE: simulation_settings[START_DATE]
            + pd.DateOffset(days=simulation_settings[EVALUATED_PERIOD][VALUE], hours=-1)
        }
    )
    # create time index used for initializing oemof simulation
    simulation_settings.update(
        {
            TIME_INDEX: pd.date_range(
                start=simulation_settings[START_DATE],
                end=simulation_settings[END_DATE],
                freq=str(simulation_settings[TIMESTEP][VALUE]) + UNIT_MINUTE,
            )
        }
    )

    simulation_settings.update({PERIODS: len(simulation_settings[TIME_INDEX])})


def load_json(
    path_input_file, path_input_folder=None, path_output_folder=None, move_copy=False
):
    """Opens and reads json input file and parses it to dict of input parameters.

    Parameters
    ----------

    path_input_file: str
        The path to the json file created from csv files
    path_input_folder : str, optional
        The path to the directory where the input CSVs/JSON files are located.
        Default: 'inputs/'.
    path_output_folder : str, optional
        The path to the directory where the results of the simulation such as
        the plots, time series, results JSON files are saved by MVS E-Lands.
        Default: 'MVS_outputs/'
    move_copy: bool, optional
        if this is set to True, the path_input_file will be moved to the path_output_folder
        Default: False

    Returns
    -------

    dict of all input parameters of the MVS E-Lands simulation
    """
    with open(path_input_file) as json_file:
        dict_values = json.load(json_file)

    dict_values = convert_from_json_to_special_types(dict_values)

    # The user specified a value
    if path_input_folder is not None:
        dict_values[SIMULATION_SETTINGS][PATH_INPUT_FOLDER] = path_input_folder

    # The user specified a value
    if path_output_folder is not None:
        dict_values[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER] = path_output_folder
        dict_values[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER_INPUTS] = os.path.join(
            path_output_folder, INPUTS_COPY
        )

    # Move the json file created from csv to the copy of the input folder in the output folder
    if move_copy is True:
        os.replace(
            path_input_file,
            os.path.join(
                dict_values[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER_INPUTS], CSV_FNAME,
            ),
        )

    # add default value if the field PATHS_TO_PLOTS is not already present
    if PATHS_TO_PLOTS not in dict_values:
        dict_values.update(copy.deepcopy(DICT_PLOTS))
    return dict_values
