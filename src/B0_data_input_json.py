import json


def load_json(path_input_file):
    """

    :param path_input_file:
    :return:
    """
    with open(path_input_file) as json_file:
        dict_values = json.load(json_file)
    return dict_values
