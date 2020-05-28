import pytest

import src.C1_verification as C1
from .constants import JSON_PATH


def test_lookup_file_existing_file():
    file_name = JSON_PATH
    # no error is risen
    C1.lookup_file(file_path=file_name, name="test")


def test_lookup_file_non_existing_file_raises_error():
    file_name = "non_existing.json"
    msg = f"Missing file! The timeseries file '{file_name}'"
    with pytest.raises(FileNotFoundError, match=msg):
        C1.lookup_file(file_path=file_name, name="test")


# def test_check_input_values():
#     pass
#     # todo note: function is not used so far


# def test_all_valid_intervals():
#     pass
#     # todo note: function is not used so far
