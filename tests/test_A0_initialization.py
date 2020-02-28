import os
import sys
import shutil
import pytest
import mock
import argparse

import src.A0_initialization as initializing
from mvs_eland_tool.mvs_eland_tool import main

from .constants import REPO_PATH, CSV_ELEMENTS, INPUTS_COPY


class TestProcessUserArguments:

    output_path = os.path.join(".", "tests", "MVS_outputs")
    input_path = os.path.join("tests", "inputs")
    fake_input_path = os.path.join("tests", "fake_inputs")

    def test_input_folder_is_copied_in_output_within_folder_named_input(self):
        pass
        # initializing.get_user_input(path_output_folder=self.output_path)
        # assert os.path.exists(self.output_path)

    def test_input_folder_not_existing_raise_filenotfound_error(self):
        pass
        # with pytest.raises(NotADirectoryError):
        #     initializing.get_user_input(
        #         path_input_file=self.fake_input_path,
        #         path_output_folder=self.output_path,
        #     )

    def test_if_json_opt_and_no_json_file_in_input_folder_raise_filenotfound_error(
        self,
    ):
        pass
        # with pytest.raises(FileNotFoundError):
        #     initializing.get_user_input(
        #         path_input_file=os.path.join(self.input_path, "not_existing.json"),
        #         path_output_folder=self.output_path,
        #         overwrite=True,
        #     )

    def test_if_json_opt_and_more_than_one_json_file_in_input_folder_raise_fileexists_error(
        self,
    ):
        pass
        # with pytest.raises(FileNotFoundError):
        #     initializing.get_user_input(
        #         path_input_file=os.path.join(self.input_path, "not_existing.json"),
        #         path_output_folder=self.output_path,
        #         overwrite=True,
        #     )

    def test_if_json_opt_path_input_file_set_to_path_input_folder(self):
        """Check that the path_input_file is <path_input_folder>

            in module A1_csv_to_json this will be transformed into a .json file
        """
        pass

    def test_if_csv_opt_and_csv_elements_folder_not_in_input_folder_raise_filenotfound_error(
        self,
    ):
        pass
        # with pytest.raises(FileNotFoundError):
        #     initializing.get_user_input(
        #         path_input_file=os.path.join(self.input_path, "not_existing.json"),
        #         path_output_folder=self.output_path,
        #         overwrite=True,
        #     )

    def test_if_csv_opt_path_input_file_set_to_path_input_folder_mvs_csv_config_dot_json(
        self,
    ):
        """Check that the path_input_file is <path_input_folder>/mvs_csv_config.json """
        pass

    def test_if_log_opt_display_output_is_set_with_correct_value(self):
        pass

    def test_if_path_output_folder_exists_raise_fileexists_error(self):
        """The error message should advice the user to use -f option to force overwrite"""
        pass

    def test_if_f_opt_preexisting_path_output_folder_should_be_replaced(self):
        pass

    def teardown_method(self):
        pass
        # if os.path.exists(self.output_path):
        #     shutil.rmtree(self.output_path, ignore_errors=True)


def test_check_input_path_posix():
    """Verify the code works on both windows and linux path systems"""
    if os.name == "posix":
        folder = initializing.check_input_directory(
            "{}/inputs/working_example.json".format(REPO_PATH)
        )
    else:
        folder = initializing.check_input_directory(
            "{}\\inputs\\working_example.json".format(REPO_PATH)
        )

    assert folder == os.path.join(REPO_PATH, "inputs")


OUTPUT_PATH = os.path.join(".", "tests", "other")


class TestCommandLineInput:

    parser = initializing.create_parser()

    def test_input_json_file(self):
        parsed = self.parser.parse_args(["-json", "input_file"])
        assert parsed.path_input_file == "input_file"

    def test_input_csv_file(self):
        parsed = self.parser.parse_args(["-csv", "input_file"])
        assert parsed.path_input_file == os.path.join("input_file", CSV_ELEMENTS)

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
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
