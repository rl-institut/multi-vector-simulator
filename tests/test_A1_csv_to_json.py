import os
import pytest

import src.A1_csv_to_json as A1
import src.B0_data_input_json as data_input

from .constants import CSV_PATH, CSV_FNAME, DUMMY_CSV_PATH, REQUIRED_CSV_FILES


CSV_PARAMETERS = ["param1", "param2"]

CSV_EXAMPLE = {"col1": {"param1": "val11", "param2": {"value": 21, "unit": "factor"}}}


def test_create_input_json_creation_of_json_file():
    A1.create_input_json(input_directory=CSV_PATH)
    assert os.path.exists(os.path.join(CSV_PATH, CSV_FNAME))


def test_create_input_json_already_existing_json_file_raises_FileExistsError():
    with open(os.path.join(CSV_PATH, CSV_FNAME), "w") as of:
        of.write("something")
    with pytest.raises(FileExistsError):
        A1.create_input_json(input_directory=CSV_PATH)


def test_create_input_json_required_fields_are_filled():
    js_file = A1.create_input_json(input_directory=CSV_PATH, pass_back=True)
    js = data_input.load_json(js_file)
    for k in js.keys():
        assert k in REQUIRED_CSV_FILES


def test_create_json_from_csv_file_not_exist_raises_filenotfound_error():
    with pytest.raises(FileNotFoundError):
        A1.create_json_from_csv(
            input_directory=CSV_PATH, filename="not_existing", parameters=[]
        )


def test_create_json_from_csv_with_comma_separated_csv():
    d = A1.create_json_from_csv(
        DUMMY_CSV_PATH, "csv_comma", CSV_PARAMETERS, storage=False
    )
    assert d == {"csv_comma": CSV_EXAMPLE}


def test_create_json_from_csv_with_semicolon_separated_csv():
    d = A1.create_json_from_csv(
        DUMMY_CSV_PATH, "csv_semicolon", CSV_PARAMETERS, storage=False
    )

    assert d == {"csv_semicolon": CSV_EXAMPLE}


def test_create_json_from_csv_with_ampersand_separated_csv():
    d = A1.create_json_from_csv(
        DUMMY_CSV_PATH, "csv_ampersand", CSV_PARAMETERS, storage=False
    )

    assert d == {"csv_ampersand": CSV_EXAMPLE}


def test_create_json_from_csv_with_unknown_separator_for_csv():

    with pytest.raises(ValueError):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH, "csv_unknown_separator", CSV_PARAMETERS, storage=False
        )


def teardown_function():
    if os.path.exists(os.path.join(CSV_PATH, CSV_FNAME)):
        os.remove(os.path.join(CSV_PATH, CSV_FNAME))
