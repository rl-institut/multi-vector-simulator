import os
import shutil

import mock
import pytest

import multi_vector_simulator.A0_initialization as A0

from multi_vector_simulator.utils.constants import INPUT_FOLDER, OUTPUT_FOLDER

from multi_vector_simulator.cli import main
from _constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    TEST_REPO_PATH,
    CSV_ELEMENTS,
    INPUTS_COPY,
    JSON_FNAME,
    JSON_PATH,
    JSON_EXT,
    CSV_FNAME,
    CSV_EXT,
    DEFAULT_INPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    PDF_REPORT,
    REPORT_FOLDER,
    PATH_INPUT_FILE,
)

PARSER = A0.mvs_arg_parser()


class TestProcessUserArguments:

    test_in_path = os.path.join(TEST_REPO_PATH, INPUT_FOLDER)
    test_out_path = os.path.join(TEST_REPO_PATH, OUTPUT_FOLDER)
    fake_input_path = os.path.join(TEST_REPO_PATH, "fake_inputs")

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            ["-f", "-log", "warning", "-i", test_in_path, "-o", test_out_path]
        ),
    )
    def test_input_folder_is_copied_in_output_within_folder_named_input(self, m_args):
        A0.process_user_arguments()
        assert os.path.exists(os.path.join(self.test_out_path, INPUTS_COPY))

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            ["-f", "-log", "warning", "-i", fake_input_path, "-o", test_out_path]
        ),
    )
    def test_input_folder_not_existing_raise_filenotfound_error(self, m_args):
        with pytest.raises(FileNotFoundError):
            A0.process_user_arguments()

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(["-f", "-log", "warning", "-ext", JSON_EXT]),
    )
    def test_if_json_opt_and_no_json_file_in_input_folder_raise_filenotfound_error(
        self, m_args, tmpdir
    ):
        """provide a temporary dir with no .json in it"""
        with pytest.raises(FileNotFoundError):
            A0.process_user_arguments(path_input_folder=tmpdir)

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            ["-f", "-log", "warning", "-i", fake_input_path, "-ext", JSON_EXT]
        ),
    )
    def test_if_json_opt_and_more_than_one_json_file_in_input_folder_raise_fileexists_error(
        self, m_args
    ):
        # create a folder with two json files
        os.mkdir(self.fake_input_path)
        with open(os.path.join(self.fake_input_path, JSON_FNAME), "w") as of:
            of.write("something")
        with open(os.path.join(self.fake_input_path, "file2.json"), "w") as of:
            of.write("something")
        with pytest.raises(FileExistsError):
            A0.process_user_arguments()

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(["-f", "-log", "warning", "-ext", CSV_EXT]),
    )
    def test_if_csv_opt_and_csv_elements_folder_not_in_input_folder_raise_filenotfound_error(
        self, m_args, tmpdir
    ):
        with pytest.raises(FileNotFoundError):
            A0.process_user_arguments(path_input_folder=tmpdir)

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            [
                "-f",
                "-log",
                "warning",
                "-i",
                fake_input_path,
                "-ext",
                CSV_EXT,
                "-o",
                test_out_path,
            ]
        ),
    )
    def test_if_csv_opt_path_input_file_set_to_path_input_folder_mvs_csv_config_dot_json(
        self, m_args, tmpdir
    ):
        """Check that the path_input_file is <path_input_folder>/mvs_csv_config.json"""
        os.mkdir(self.fake_input_path)
        os.mkdir(os.path.join(self.fake_input_path, CSV_ELEMENTS))
        user_inputs = A0.process_user_arguments()
        assert user_inputs[PATH_INPUT_FILE] == os.path.join(
            self.fake_input_path, CSV_ELEMENTS, CSV_FNAME
        )

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            ["-f", "-log", "warning", "-i", test_in_path, "-o", test_out_path]
        ),
    )
    def test_if_log_opt_display_output_is_set_with_correct_value(self, m_args):
        A0.process_user_arguments()
        # TODO check the logging level
        assert 1

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            ["-log", "warning", "-i", test_in_path, "-o", test_out_path]
        ),
    )
    def test_if_path_output_folder_exists_raise_fileexists_error(self, m_args):
        """The error message should advice the user to use -f option to force overwrite"""
        if os.path.exists(self.test_out_path) is False:
            os.mkdir(self.test_out_path)
        with pytest.raises(FileExistsError):
            A0.process_user_arguments()

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            ["-f", "-log", "warning", "-i", test_in_path, "-o", test_out_path]
        ),
    )
    def test_if_f_opt_preexisting_path_output_folder_should_be_replaced(self, m_args):
        if os.path.exists(self.test_out_path) is False:
            os.mkdir(self.test_out_path)
        some_file = os.path.join(self.test_out_path, "a_file.txt")
        with open(some_file, "w") as of:
            of.write("something")
        A0.process_user_arguments()
        assert os.path.exists(some_file) is False

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            [
                "-f",
                "-log",
                "warning",
                "-i",
                test_in_path,
                "-o",
                os.path.join(test_out_path, "recursive_folder"),
            ]
        ),
    )
    def test_if_path_output_folder_recursive_create_full_path(self, m_args):
        A0.process_user_arguments()
        assert os.path.exists(os.path.join(self.test_out_path, "recursive_folder"))

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            ["-f", "-log", "warning", "-i", test_in_path, "-o", test_out_path, "-pdf"]
        ),
    )
    def test_if_pdf_opt_the_key_path_pdf_report_exists_in_user_inputs(self, m_args):
        user_inputs = A0.process_user_arguments()
        assert user_inputs["path_pdf_report"] == os.path.join(
            self.test_out_path, REPORT_FOLDER, PDF_REPORT
        )
        assert "path_png_figs" not in user_inputs.keys()

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            ["-f", "-log", "warning", "-i", test_in_path, "-o", test_out_path]
        ),
    )
    def test_if_no_pdf_opt_the_key_path_pdf_report_does_not_exist_in_user_inputs(
        self, m_args
    ):
        user_inputs = A0.process_user_arguments()
        assert "path_pdf_report" not in user_inputs.keys()

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            ["-f", "-log", "warning", "-i", test_in_path, "-o", test_out_path, "-png"]
        ),
    )
    def test_if_png_pdf_not_active(self, m_args):
        user_inputs = A0.process_user_arguments()
        assert "path_png_figs" in user_inputs.keys()
        assert "path_pdf_report" not in user_inputs.keys()

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            [
                "-f",
                "-log",
                "warning",
                "-i",
                test_in_path,
                "-o",
                test_out_path,
                "-png",
                "-pdf",
            ]
        ),
    )
    def test_if_both_pdf_and_png_opt_raises_no_error(self, m_args):
        user_inputs = A0.process_user_arguments()
        assert "path_png_figs" in user_inputs.keys()
        assert "path_pdf_report" in user_inputs.keys()

    def teardown_method(self):
        if os.path.exists(self.test_out_path):
            shutil.rmtree(self.test_out_path, ignore_errors=True)
        if os.path.exists(self.fake_input_path):
            shutil.rmtree(self.fake_input_path, ignore_errors=True)


def test_check_input_path_posix():
    """Verify the code works on both windows and linux path systems"""
    if os.name == "posix":
        folder = A0.check_input_folder("{}/inputs/".format(TEST_REPO_PATH), JSON_EXT)
    else:
        folder = A0.check_input_folder("{}\\inputs\\".format(TEST_REPO_PATH), JSON_EXT)

    assert folder == os.path.join(JSON_PATH)


TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "other")


class TestCommandLineInput:

    parser = A0.mvs_arg_parser()

    def test_input_folder(self):
        parsed = self.parser.parse_args(["-i", "input_folder"])
        assert parsed.path_input_folder == "input_folder"

    def test_default_input_folder(self):
        parsed = self.parser.parse_args([])
        assert parsed.path_input_folder == DEFAULT_INPUT_PATH

    def test_input_json_ext(self):
        parsed = self.parser.parse_args(["-ext", JSON_EXT])
        assert parsed.input_type == JSON_EXT

    def test_input_csv_ext(self):
        parsed = self.parser.parse_args(["-ext", CSV_EXT])
        assert parsed.input_type == CSV_EXT

    def test_default_input_type(self):
        parsed = self.parser.parse_args([])
        assert parsed.input_type == JSON_EXT

    def test_ext_not_accepting_other_choices(self):
        with pytest.raises(SystemExit) as argparse_error:
            parsed = self.parser.parse_args(["-ext", "something"])
        assert str(argparse_error.value) == "2"

    def test_output_folder(self):
        parsed = self.parser.parse_args(["-o", "output_folder"])
        assert parsed.path_output_folder == "output_folder"

    def test_default_output_folder(self):
        parsed = self.parser.parse_args([])
        assert parsed.path_output_folder == DEFAULT_OUTPUT_PATH

    def test_overwrite_false_by_default(self):
        parsed = self.parser.parse_args([])
        assert parsed.overwrite is False

    def test_overwrite_activation(self):
        parsed = self.parser.parse_args(["-f"])
        assert parsed.overwrite is True

    def test_pdf_report_false_by_default(self):
        parsed = self.parser.parse_args([])
        assert parsed.pdf_report is False

    def test_pdf_report_activation(self):
        parsed = self.parser.parse_args(["-pdf"])
        assert parsed.pdf_report is True

    def test_png_activation(self):
        parsed = self.parser.parse_args(["-png"])
        assert parsed.save_png is True

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
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            [
                "-f",
                "-log",
                "warning",
                "-i",
                os.path.join(TEST_REPO_PATH, INPUT_FOLDER),
                "-o",
                TEST_OUTPUT_PATH,
            ]
        ),
    )
    def test_user_defined_output_path(self, mock_args):
        main()
        assert os.path.exists(TEST_OUTPUT_PATH)

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
