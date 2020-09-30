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
    CSV_ELEMENTS,
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
    if MISSING_PARAMETERS_KEY in comparison:
        for k in comparison[MISSING_PARAMETERS_KEY].keys():
            for el in comparison[MISSING_PARAMETERS_KEY][k]:
                try:
                    assert el in EXTRA_CSV_PARAMETERS
                except AssertionError:
                    raise AssertionError(
                        f"Parameter '{el}' is missing in you csv input files although it is required. It "
                        f"should be added in the '{k}.csv' file of the folder '{input_folder}"
                        f"/{CSV_ELEMENTS}' or listed in the dict 'EXTRA_CSV_PARAMETERS' in "
                        f"src/mvs_eland/utils/constants.py. The csv required parameters are listed in "
                        f"the dict 'REQUIRED_CSV_PARAMETERS' in the aforementionned constant.py "
                        f"file.\n\nSee previous exception in the pytest log for more details on "
                        f"this error."
                    )

    if TEMPLATE_INPUT_FOLDER in input_folder:
        if EXTRA_PARAMETERS_KEY in comparison:
            for k in comparison[EXTRA_PARAMETERS_KEY].keys():
                for el in comparison[EXTRA_PARAMETERS_KEY][k]:
                    try:
                        assert el in EXTRA_CSV_PARAMETERS
                    except AssertionError:
                        raise AssertionError(
                            f"\n\nParameter '{el}' is an extra parameter in the file '{input_folder}/"
                            f"{CSV_ELEMENTS}/{k}'. The '{TEMPLATE_INPUT_FOLDER}' folder should only "
                            f"contain the required parameters and no extra parameters.\n\nSee "
                            f"previous exception in the pytest log for more details on this error."
                        )


@pytest.mark.parametrize("input_folder", TEST_JSON_INPUT_FOLDERS)
def test_input_folder_json_file_have_required_parameters(input_folder):
    """
    Browse all folders which contains a {CSV_ELEMENTS} folder and a {JSON_FNAME} json file
    (defined as json input folders) and verify that this json file have all required
    parameters
    """
    if os.path.exists(os.path.join(input_folder, JSON_FNAME)):
        comparison = compare_input_parameters_with_reference(input_folder, ext=JSON_EXT)
        assert MISSING_PARAMETERS_KEY not in comparison, (
            f"In path {input_folder}/{JSON_FNAME}, the following parameters are missing:"
            + str(comparison[MISSING_PARAMETERS_KEY])
        )
