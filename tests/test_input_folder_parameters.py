import os
import pytest

from mvs_eland.utils.constants import REPO_PATH, EXTRA_CSV_PARAMETERS
from _constants import (
    TEMPLATE_INPUT_FOLDER,
    JSON_EXT,
    CSV_EXT,
    JSON_FNAME,
    MISSING_PARAMETERS_KEY,
    EXTRA_PARAMETERS_KEY,
)
from mvs_eland.utils import (
    find_csv_input_folders,
    find_json_input_folders,
    compare_input_parameters_with_reference,
)

TEST_CSV_INPUT_FOLDERS = find_csv_input_folders(REPO_PATH)
TEST_JSON_INPUT_FOLDERS = find_json_input_folders(REPO_PATH)


@pytest.mark.parametrize("input_folder", TEST_CSV_INPUT_FOLDERS)
def test_input_folder_csv_files_have_required_parameters(input_folder):
    """
    Browse all folders which contains a {CSV_ELEMENTS} folder (defined as csv input folders)
    and verify the csv files they contain have all required parameters.
    For the special folder 'input_template', it is also tested that it does not have any
    extra parameters besides the required ones
    """
    comparison = compare_input_parameters_with_reference(input_folder, ext=CSV_EXT)
    if MISSING_PARAMETERS_KEY not in comparison:
        assert True
    else:
        for k in comparison[MISSING_PARAMETERS_KEY].keys():
            for el in comparison[MISSING_PARAMETERS_KEY][k]:
                assert (
                    el in EXTRA_CSV_PARAMETERS
                ), f"Key {el} is not in {EXTRA_PARAMETERS_KEY}, but is in {MISSING_PARAMETERS_KEY} in the folder {input_folder}."

    if TEMPLATE_INPUT_FOLDER in input_folder:
        if EXTRA_PARAMETERS_KEY in comparison:
            for k in comparison[EXTRA_PARAMETERS_KEY].keys():
                for el in comparison[EXTRA_PARAMETERS_KEY][k]:
                    assert el in EXTRA_CSV_PARAMETERS
        else:
            assert True


@pytest.mark.parametrize("input_folder", TEST_JSON_INPUT_FOLDERS)
def test_input_folder_json_file_have_required_parameters(input_folder):
    """
    Browse all folders which contains a {CSV_ELEMENTS} folder and a {JSON_FNAME} json file
    (defined as json input folders) and verify that this json file have all required
    parameters
    """
    if os.path.exists(os.path.join(input_folder, JSON_FNAME)):
        comparison = compare_input_parameters_with_reference(input_folder, ext=JSON_EXT)
        assert (
            MISSING_PARAMETERS_KEY not in comparison
        ), f"In path {input_folder}, the key {MISSING_PARAMETERS_KEY} is included."
