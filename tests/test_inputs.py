import os
import pytest
import mock

import src.A0_initialization as initializing


def test_create_output_path():

    with mock.patch('builtins.input', return_value="yes"):
        initializing.check_output_directory(os.path.join('test_func'), False)
        assert os.path.exists('test_func')


def test_check_input_path_posix():
    folder, file = initializing.check_input_directory(".inputs/working_example.json")
    assert folder == "inputs"
    assert file == "working_example.json"


def test_check_input_path_windows():
    folder, file = initializing.check_input_directory(".inputs\\working_example.json")
    assert folder == "inputs"
    assert file == "working_example.json"