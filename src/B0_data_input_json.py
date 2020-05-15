import os
import json
import numpy as np
import pandas as pd

from src.constants import CSV_FNAME, INPUTS_COPY
from src.constants import (
    PLOTS_BUSSES,
    PATHS_TO_PLOTS,
    PLOTS_DEMANDS,
    PLOTS_RESOURCES,
    PLOTS_NX,
    PLOTS_PERFORMANCE,
    PLOTS_COSTS,
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
            if "index" in a_dict and "column" in a_dict:
                # pandas.DatetimeIndex or pandas.DataFrame
                answer = pd.read_json(a_dict, orient="split")
            elif "index" in a_dict and "name" in a_dict:
                # pandas.Series
                answer = pd.read_json(a_dict, orient="split", typ="series")
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

    dict_values.update(
        {
            PATHS_TO_PLOTS: {
                PLOTS_BUSSES: [],
                PLOTS_DEMANDS: [],
                PLOTS_RESOURCES: [],
                PLOTS_NX: [],
                PLOTS_PERFORMANCE: [],
                PLOTS_COSTS: [],
            }
        }
    )
    return dict_values
