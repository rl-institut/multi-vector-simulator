import os
import pytest
import mock

import src.A0_initialization as initializing

from .constants import REPO_PATH

# def test_create_output_path():
#
#     with mock.patch('builtins.input', return_value="yes"):
#         initializing.check_output_directory(os.path.join('test_func'), False)
#         assert os.path.exists('test_func')


def test_check_input_path_posix():
    if os.name == "posix":
        folder, file = initializing.check_input_directory(
            "{}/inputs/working_example.json".format(REPO_PATH)
        )
    else:
        folder, file = initializing.check_input_directory(
            "{}\\inputs\\working_example.json".format(REPO_PATH)
        )

    assert folder == os.path.join(REPO_PATH, "inputs")
    assert file == "working_example.json"
