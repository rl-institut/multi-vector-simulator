import os
import pytest

from .constants import REPO_PATH
import src.C1_verification as C1


def test_lookup_file_existing_file():
    file_name = os.path.join(os.path.dirname(__file__), "inputs",
                             "mvs_config.json")
    # no error is risen
    C1.lookup_file(file_path=file_name, name="test")


def test_lookup_file_non_existing_file_raises_error():
    file_name = os.path.join(os.path.dirname(__file__), "non_existing.json")
    msg = f"Missing file! The timeseries file '{file_name}'"
    with pytest.raises(FileNotFoundError, match=msg):
        C1.lookup_file(file_path=file_name, name="test")


# def test_check_input_values():
#     pass
#     # todo note: function is not used so far


# def test_all_valid_intervals():
#     pass
#     # todo note: function is not used so far
