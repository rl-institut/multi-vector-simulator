import os
import json

from src.constants import CSV_FNAME, INPUTS_COPY

"""
This module is used to open a json file and parse it as a dict all input parameters for the energy 
system.

If the user does not give the input parameters "path_input_folder", "path_output_folder" or "path_output_folder_inputs", they are replaced by the default values.

It will be an interface to the EPA.
"""


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

    return dict_values
