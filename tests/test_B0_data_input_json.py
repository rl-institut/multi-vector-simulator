import os

from .constants import JSON_PATH

import src.B0_data_input_json as data_input


def test_load_json_overwrite_output_folder_from_json():
    dict_values = data_input.load_json(JSON_PATH, path_output_folder="test")
    assert dict_values["simulation_settings"]["path_output_folder"] == "test"
    assert dict_values["simulation_settings"][
        "path_output_folder_inputs"
    ] == os.path.join("test", "inputs")


def test_load_json_overwrite_input_folder_from_json():
    dict_values = data_input.load_json(JSON_PATH, path_input_folder="test")
    assert dict_values["simulation_settings"]["path_input_folder"] == "test"
