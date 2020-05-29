"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""
import copy
import logging
import os

from mvs_eland_tool import run_simulation
from src.B0_data_input_json import load_json
from tests.constants import JSON_PATH, TEST_REPO_PATH

TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "MVS_outputs_simulation")


def set_nested_value(dct, value, keys):
    r"""Set a value within a nested dict structure given the path within the dict

    Parameters
    ----------
    dct: dict
        the (potentially nested) dict from which we want to get a value
    value: variable type
        value to assign within the dict
    keys: tuple
        Tuple containing the succession of keys which lead to the value within the nested dict

    Returns"
    -------
    The value under the path within the (potentially nested) dict
    """
    if isinstance(keys, tuple) is True:
        answer = copy.deepcopy(dct)
        if len(keys) > 1:
            answer[keys[0]] = set_nested_value(dct[keys[0]], value, keys[1:])
        elif len(keys) == 1:
            answer[keys[0]] = value
        else:
            raise ValueError(
                "The tuple argument 'keys' from set_nested_value() should not be empty"
            )
    else:
        raise TypeError("The argument 'keys' from set_nested_value() should be a tuple")
    return answer


def get_nested_value(dct, keys):
    r"""Get a value from a succession of keys within a nested dict structure

    Parameters
    ----------
    dct: dict
        the (potentially nested) dict from which we want to get a value
    keys: tuple
        Tuple containing the succession of keys which lead to the value within the nested dict

    Returns
    -------
    The value under the path within the (potentially nested) dict
    """
    if isinstance(keys, tuple) is True:
        if len(keys) > 1:
            answer = get_nested_value(dct[keys[0]], keys[1:])
        elif len(keys) == 1:
            answer = dct[keys[0]]
        else:
            raise ValueError(
                "The tuple argument 'keys' from get_nested_value() should not be empty"
            )
    else:
        raise TypeError("The argument 'keys' from get_nested_value() should be a tuple")
    return answer


def split_nested_path(path):
    r"""Separate a single-string path in a nested dict in a list of keys


    Parameters
    ----------
    path: str or tuple
        path within a nested dict which is expressed as a str of a succession of keys separated by
        a `.` or a `,`. The order of keys is to be read from left to right.

    Returns
    -------
    Tuple containing the succession of keys which lead to the value within the nested dict

    """
    SEPARATORS = (".", ",")
    keys_list = None
    if isinstance(path, str):
        separator_count = 0
        keys_separator = None
        for separator in SEPARATORS:
            if separator in path:
                if path.count(separator) > 0:
                    if separator_count > 0:
                        raise ValueError(
                            f"The separator of the nested dict's path is not unique"
                        )
                    separator_count = path.count(separator)
                    keys_separator = separator
        if keys_separator is not None:
            keys_list = tuple(path.split(keys_separator))
    elif isinstance(path, tuple):
        keys_list = path
    else:
        raise TypeError("The argument path is not str type")

    return keys_list


def single_param_variation_analysis(
    param_values, json_input, json_path_to_param_value, json_path_to_output_value=None
):
    r"""Run mvs simulations by varying one of the input parameters ta access output's sensitivity

    Parameters
    ----------
    param_values: list of values (type can vary)
    json_input: path or dict
        input parameters for the mvs_eland simulation
    json_path_to_param_value: tuple or str
        succession of keys which lead the value of the parameter to vary in the json_input dict
        potentially nested structure. The order of keys is to be read from left to right. In the
        case of str, each key should be separated by a `.` or a `,`.
    json_path_to_output_value: tuple or str, optional
        succession of keys which lead the value of an output parameter of interest in the json
        dict of the simulation's output. The order of keys is to be read from left to right. In the
        case of str, each key should be separated by a `.` or a `,`.

    Returns
    -------
    The simulation output json matched to the list of variied parameter values
    """

    if isinstance(json_input, str):
        # load the file if it is a path
        with open(json_input) as fp:
            simulation_input = load_json(json_input)
    elif isinstance(json_input, dict):
        # this is already a json variable
        simulation_input = json_input
    else:
        simulation_input = None
        logging.error(
            f"Simulation input `{json_input}` is neither a file path, nor a json dict. "
            f"It can therefor not be processed."
        )
    param_path_tuple = split_nested_path(json_path_to_param_value)
    answer = []
    if simulation_input is not None:
        for param_val in param_values:
            # modify the value of the parameter before running a new simulation
            modified_input = set_nested_value(
                simulation_input, param_val, param_path_tuple
            )
            # run a simulation with next value of the variable parameter
            sim_output_json = run_simulation(modified_input, display_output="error")

            if json_path_to_output_value is None:
                answer.append(sim_output_json)
            else:
                # TODO specific output params
                pass

    return {"parameters": param_values, "outputs": answer}


if __name__ == "__main__":
    single_param_variation_analysis(
        [1, 2, 3, 4, 5, 6, 7],
        JSON_PATH,
        ("simulation_settings", "evaluated_period", "value"),
    )
