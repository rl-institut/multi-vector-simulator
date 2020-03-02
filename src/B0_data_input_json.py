import os
import json

"""
This model is used to open and a json file and parse it as a dict all input parameters for the energy 
system.

It will be an interface to the EPA.
"""


def load_json(
    path_input_file, path_input_folder=None, path_output_folder=None,
):
    """Opens and reads json input file and parses it to dict of input parameters.

    :param path_input_file:
    :param path_input_folder:
    :param path_output_folder:
    :return: dict of all input parameters
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
            path_output_folder, "inputs"
        )

    return dict_values
