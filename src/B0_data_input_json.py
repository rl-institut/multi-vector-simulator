import os
import json
import numpy as np
import pandas as pd

from src.constants import (
    CSV_FNAME,
    INPUTS_COPY,
    PATHS_TO_PLOTS,
    DICT_PLOTS,
    TYPE_DATETIMEINDEX,
    TYPE_SERIES,
    TYPE_DATAFRAME,
    TYPE_TIMESTAMP,
)

"""
This module is used to open a json file and parse it as a dict all input parameters for the energy 
system.

If the user does not give the input parameters "path_input_folder", "path_output_folder" or "path_output_folder_inputs", they are replaced by the default values.

It will be an interface to the EPA.
"""


def convert_special_types(a_dict, prev_key=None):
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

    if isinstance(a_dict, dict):
        # the a_dict argument is a dictionary, therefore we dive deeper in the nesting level
        answer = {}
        for k in a_dict:
            answer[k] = convert_special_types(a_dict[k], prev_key=k)

    else:
        # the a_dict argument is not a dictionary, therefore we check if is one the serialized type
        # pandas.Series, pandas.DatetimeIndex, pandas.DataFrame, numpy.array
        answer = a_dict
        if isinstance(a_dict, str):
            if TYPE_DATAFRAME in a_dict:
                a_dict = a_dict.replace(TYPE_DATAFRAME, "")
                # pandas.DataFrame
                answer = pd.read_json(a_dict, orient="split")
            elif TYPE_DATETIMEINDEX in a_dict:
                # pandas.DatetimeIndex
                a_dict = a_dict.replace(TYPE_DATETIMEINDEX, "")
                answer = pd.read_json(a_dict, orient="split")
                answer = pd.to_datetime(answer.index)
                answer.freq = answer.inferred_freq
            elif TYPE_SERIES in a_dict:
                # pandas.Series
                a_dict = a_dict.replace(TYPE_SERIES, "")
                # extract the name of the series in case it was a tuple
                a_dict = json.loads(a_dict)
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

            elif TYPE_TIMESTAMP in a_dict:
                a_dict = a_dict.replace(TYPE_TIMESTAMP, "")
                answer = pd.Timestamp(a_dict)
            elif "array" in a_dict:
                # numpy.array
                answer = np.array(json.loads(a_dict)["array"])

    return answer


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

    dict_values = convert_special_types(dict_values)

    # The user specified a value
    if path_input_folder is not None:
        dict_values["simulation_settings"]["path_input_folder"] = path_input_folder

    # The user specified a value
    if path_output_folder is not None:
        dict_values["simulation_settings"]["path_output_folder"] = path_output_folder
        dict_values["simulation_settings"]["path_output_folder_inputs"] = os.path.join(
            path_output_folder, INPUTS_COPY
        )

    # Move the json file created from csv to the copy of the input folder in the output folder
    if move_copy is True:
        os.replace(
            path_input_file,
            os.path.join(
                dict_values["simulation_settings"]["path_output_folder_inputs"],
                CSV_FNAME,
            ),
        )

    # add default value if the field PATHS_TO_PLOTS is not already present
    if PATHS_TO_PLOTS not in dict_values:
        dict_values.update(DICT_PLOTS)
    return dict_values
