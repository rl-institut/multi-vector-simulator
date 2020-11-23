import os
import shutil
import pandas as pd

from _constants import TEST_REPO_PATH

from multi_vector_simulator.utils.helpers import find_value_by_key
from multi_vector_simulator.utils.constants_json_strings import (
    LABEL,
    ENERGY_PROVIDERS,
    ENERGY_PRODUCTION,
)


def test_shutil_remove_folder_recursively():
    df = pd.DataFrame(columns=["A", "B"])
    folder_name = "a_folder"
    file_name = "a_file"
    path_folder = os.path.join(TEST_REPO_PATH, folder_name)
    os.makedirs(path_folder)
    path_file = os.path.join(path_folder, file_name)
    df.to_csv(path_file)
    assert os.path.exists(path_file)
    assert os.path.exists(path_folder)
    shutil.rmtree(path_folder)
    assert os.path.exists(path_file) is False
    assert os.path.exists(path_folder) is False


def test_find_value_by_key_no_key_apperance():
    A_LABEL = "a_label"
    dict_values = {ENERGY_PRODUCTION: {"asset": {LABEL: A_LABEL}}}
    result = find_value_by_key(data=dict_values, target=UNIT)
    assert (
        result is None
    ), f"The key {UNIT} does not exist in dict_values but a value {result} is returned instead of None."


def test_find_value_by_key_single_key_apperance():
    ASSET = "asset"
    A_LABEL = "a_label"
    dict_values = {ENERGY_PRODUCTION: {ASSET: {LABEL: A_LABEL}}}
    result = find_value_by_key(data=dict_values, target=LABEL)
    assert isinstance(
        result, str
    ), f"The key {A_LABEL} only exists once, but its value {A_LABEL} is not provided. Instead, result is {result}."
    assert (
        result == A_LABEL
    ), f"The value of the searched key should have been {A_LABEL}, but is {result}."


def test_find_value_by_key_multiple_key_apperance():
    ASSET = "asset"
    A_LABEL = "a_label"
    dict_values = {
        ENERGY_PRODUCTION: {ASSET: {LABEL: A_LABEL}},
        ENERGY_PROVIDERS: {ASSET: {LABEL: A_LABEL}},
    }
    result = find_value_by_key(data=dict_values, target=LABEL)
    assert isinstance(
        result, list
    ), f"The key {LABEL} appears twice in dict_values. Still, no list of occurrences is provided, but {result}."
    expected_output = [A_LABEL, A_LABEL]
    assert (
        result == expected_output
    ), f"Not all key duplicates ({expected_output}) were identified, but {result}."
