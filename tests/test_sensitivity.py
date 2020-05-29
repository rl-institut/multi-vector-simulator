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

