"""
Helper functions
================

Util functions that are useful throughout the MVS

Including:
- find_valvue_by_key(): Finds value of a key in a nested dictionary.
"""

import os


def find_value_by_key(data, target, result=None):
    """
    Finds value of a key in a nested dictionary.

    Parameters
    ----------
    data: dict
        Dict to be searched for target key

    target: str
        Key for which the value should be found in data

    result: None, value or list
        Only provided if function loops in itself

    Returns
    -------
    value if the key is only once in data
    list of values if it appears multiple times.
    """
    # check each item-value pair in the level
    for k, v in data.items():
        # if target in keys of level
        if k == target:
            if result is None:
                result = v
            elif isinstance(result, list):
                # Expands list of key finds
                result.append(v)
            else:
                # creates list for multiple key finds
                previous_result = result
                result = []
                result.append(previous_result)
                result.append(v)
        # Check next level for target
        if isinstance(v, dict):
            result = find_value_by_key(data=v, target=target, result=result)
    return result


def translates_epa_strings_to_mvs_readable(folder_name, file_name):
    """
    This function translates the json file generated by the EPA to a file readable by the MVS.
    This is necessary as there are some parameter names whose string representative differs in both tools.

    Parameters
    ----------
    folder_name: path
        Path to the folder with the json file
    file_name: json file name with extension
        Json to be converted

    Returns
    -------
    Stores converted json file to current dict

    Usage:
        `import multi_vector_simulator.utils.helpers as helpers`
        `helpers.translates_epa_strings_to_mvs_readable("./epa_benchmark", "epa_benchmark.json-original")`
    """
    import json
    from multi_vector_simulator.utils.data_parser import convert_epa_params_to_mvs

    with open(os.path.join(folder_name, file_name)) as json_file:
        epa_dict = json.load(json_file)

    dict_values = convert_epa_params_to_mvs(epa_dict)

    with open(os.path.join(folder_name, "mvs_config.json"), "w") as json_file:
        json.dump(dict_values, json_file, indent=4)


def get_item_if_list(list_or_float, index):
    if isinstance(list_or_float, list):
        answer = list_or_float[index]
    else:
        answer = list_or_float
    return answer


def get_length_if_list(list_or_float):
    if isinstance(list_or_float, list):
        answer = len(list_or_float)
    else:
        answer = 0
    return answer
