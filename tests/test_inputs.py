import os
import shutil
import pytest
import mock

import src.A0_initialization as initializing

from .constants import REPO_PATH


class TestClass:

    output_path = os.path.join('.', 'tests', 'MVS_outputs')

    def setup_method(self):
        print('setup')
        os.mkdir(self.output_path)
        os.mkdir(os.path.join(self.output_path, 'dummy'))

    def test_create_output_path_ask_to_overwrite_existing_no(self):
        with mock.patch('builtins.input', return_value="no"):
            with pytest.raises(FileExistsError):
                initializing.check_output_directory(os.path.join(self.output_path), overwrite=False)
            assert os.path.exists(self.output_path)

    def test_create_output_path_ask_overwrite_existing_yes(self):
        with mock.patch('builtins.input', return_value="yes"):
            initializing.check_output_directory(os.path.join(self.output_path), overwrite=False)
            assert os.path.exists(self.output_path)


    def test_create_output_path_existing_yes(self):
        initializing.check_output_directory(os.path.join(self.output_path), overwrite=True)
        assert os.path.exists(self.output_path)


    def teardown_method(self):
        shutil.rmtree(self.output_path, ignore_errors=True)


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
