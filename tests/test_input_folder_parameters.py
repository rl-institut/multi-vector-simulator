import os
import pytest

from src.utils import find_input_folders, compare_input_parameters_with_reference
from src.constants import REPO_PATH
from .constants import (
    TEST_REPO_PATH,
    JSON_EXT,
    CSV_EXT,
    JSON_FNAME,
    MISSING_PARAMETERS_KEY,
    EXTRA_PARAMETERS_KEY,
)

TEST_INPUT_FOLDERS = find_input_folders(REPO_PATH)


@pytest.mark.parametrize("input_folder", TEST_INPUT_FOLDERS)
def test_input_folder_csv_files_have_required_parameters(input_folder):
    """
        Browse all folders which contains a {CSV_ELEMENTS} folder (defined as csv input folders)
        and verify the csv files they contain have all required parameters.
        For the special folder 'input_template', it is also tested that it does not have any
        extra parameters besides the required ones
    """
    comparison = compare_input_parameters_with_reference(input_folder, ext=CSV_EXT)
    assert MISSING_PARAMETERS_KEY not in comparison
    # TODO: after merging #384, compare with the EXTRA_CSV_PARAMETERS dict
    # if "input_template" in input_folder:
    #     assert EXTRA_PARAMETERS_KEY not in comparison


@pytest.mark.parametrize("input_folder", TEST_INPUT_FOLDERS)
def test_input_folder_json_file_have_required_parameters(input_folder):
    """
        Browse all folders which contains a {CSV_ELEMENTS} folder and a {JSON_FNAME} json file
        (defined as json input folders) and verify that this json file have all required
        parameters
    """
    if os.path.exists(os.path.join(input_folder, JSON_FNAME)):
        comparison = compare_input_parameters_with_reference(input_folder, ext=JSON_EXT)
        assert MISSING_PARAMETERS_KEY not in comparison
