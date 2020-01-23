import json


def load_json(user_input):
    """

    :param user_input:
    :return:
    """
    with open(user_input["path_input_file"]) as json_file:
        dict_values = json.load(json_file)
    return dict_values
