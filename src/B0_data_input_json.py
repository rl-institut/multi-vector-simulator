import json


def load_json(path_input_file):
    """Opens and reads json input file and parses it to dict of input parameters.

    :param path_input_file:
    :return: dict of all input parameters
    """
    with open(path_input_file) as json_file:
        dict_values = json.load(json_file)
    return dict_values
