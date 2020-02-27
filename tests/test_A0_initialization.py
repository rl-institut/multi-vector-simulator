import os
import sys
import shutil
import pytest
import mock
import argparse

import src.A0_initialization as initializing
from mvs_eland_tool.mvs_eland_tool import main

from .constants import REPO_PATH

OUTPUT_PATH = os.path.join(".", "tests", "other")


class TestOutputPath:

    output_path = os.path.join(".", "tests", "MVS_outputs")

    def setup_method(self):

        os.mkdir(self.output_path)
        os.mkdir(os.path.join(self.output_path, "dummy"))

    def test_create_output_path_ask_to_overwrite_existing_no(self):
        with mock.patch("builtins.input", return_value="no"):
            with pytest.raises(FileExistsError):
                initializing.check_output_directory(
                    os.path.join(self.output_path), overwrite=False
                )
            assert os.path.exists(self.output_path)
            assert os.path.exists(os.path.join(self.output_path, "dummy"))

    def test_create_output_path_ask_overwrite_existing_yes(self):
        with mock.patch("builtins.input", return_value="yes"):
            initializing.check_output_directory(
                os.path.join(self.output_path), overwrite=False
            )
            assert os.path.exists(self.output_path)
            assert not os.path.exists(os.path.join(self.output_path, "dummy"))

    def test_create_output_path_existing_yes(self):
        initializing.check_output_directory(
            os.path.join(self.output_path), overwrite=True
        )
        assert os.path.exists(self.output_path)
        assert not os.path.exists(os.path.join(self.output_path, "dummy"))

    def teardown_method(self):
        shutil.rmtree(self.output_path, ignore_errors=True)


class TestUserInput:

    output_path = os.path.join(".", "tests", "MVS_outputs")
    input_path = os.path.join("tests", "inputs")
    fake_input_path = os.path.join("tests", "fake_inputs")

    def test_user_input_path_folder_copy_in_output(self):
        initializing.get_user_input(path_output_folder=self.output_path)
        assert os.path.exists(self.output_path)

    def test_user_input_path_input_folder_not_existing(self):
        with pytest.raises(NotADirectoryError):
            initializing.get_user_input(
                path_input_file=self.fake_input_path,
                path_output_folder=self.output_path,
            )

    def test_user_input_path_input_file_not_existing(self):
        with pytest.raises(FileNotFoundError):
            initializing.get_user_input(
                path_input_file=os.path.join(self.input_path, "not_existing.json"),
                path_output_folder=self.output_path,
                overwrite=True,
            )

    def teardown_method(self):
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path, ignore_errors=True)


def test_check_input_path_posix():
    if os.name == "posix":
        folder = initializing.check_input_directory(
            "{}/inputs/working_example.json".format(REPO_PATH)
        )
    else:
        folder = initializing.check_input_directory(
            "{}\\inputs\\working_example.json".format(REPO_PATH)
        )

    assert folder == os.path.join(REPO_PATH, "inputs")


class TestCommandLineInput:

    parser = initializing.create_parser()

    def test_input_file(self):
        parsed = self.parser.parse_args(["-i", "input_file"])
        assert parsed.path_input_file == "input_file"

    def test_output_folder(self):
        parsed = self.parser.parse_args(["-o", "output_folder"])
        assert parsed.path_output_folder == "output_folder"

    def test_overwrite_false_by_default(self):
        parsed = self.parser.parse_args([])
        assert parsed.overwrite is False

    def test_overwrite_activation(self):
        parsed = self.parser.parse_args(["-f"])
        assert parsed.overwrite is True

    def test_log_assignation(self):
        parsed = self.parser.parse_args(["-log", "debug"])
        assert parsed.display_output == "debug"

    def test_log_default(self):
        parsed = self.parser.parse_args([])
        assert parsed.display_output == "info"

    def test_log_not_accepting_other_choices(self):
        with pytest.raises(SystemExit) as argparse_error:
            parsed = self.parser.parse_args(["-log", "something"])
        assert str(argparse_error.value) == "2"

    # this ensure that the test is only ran if explicitly executed,
    # ie not when the `pytest` command alone it called
    @pytest.mark.skipif(
        "tests/test_inputs.py" not in sys.argv, reason="requires python3.3"
    )
    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argparse.Namespace(path_output_folder=OUTPUT_PATH),
    )
    def test_user_defined_output_path(self, mock_args):
        main()
        assert os.path.exists(OUTPUT_PATH)

    def teardown_method(self):
        shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
