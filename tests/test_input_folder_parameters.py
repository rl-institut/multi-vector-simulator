import os
import pytest

from src.utils import find_input_folders, compare_input_parameters_with_reference
from src.constants import REPO_PATH
from .constants import TEST_REPO_PATH, JSON_EXT, CSV_EXT, MISSING_PARAMETERS_KEY

TEST_INPUT_FOLDERS = find_input_folders(REPO_PATH)

@pytest.mark.parametrize("input_folder", TEST_INPUT_FOLDERS)
def test_input_folder_csv_files_have_required_parameters(input_folder):
    comparison = compare_input_parameters_with_reference(input_folder, ext=CSV_EXT)
    assert MISSING_PARAMETERS_KEY not in comparison

@pytest.mark.parametrize("input_folder", TEST_INPUT_FOLDERS)
def test_input_folder_json_file_have_required_parameters(input_folder):
    comparison = compare_input_parameters_with_reference(input_folder, ext=JSON_EXT)
    assert MISSING_PARAMETERS_KEY not in comparison