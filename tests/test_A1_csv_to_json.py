import os
import pytest

import src.A1_csv_to_json as load_data_from_csv
import src.B0_data_input_json as data_input

from .constants import CSV_PATH, CSV_FNAME, DUMMY_CSV_PATH, REQUIRED_CSV_FILES


CSV_PARAMETERS = ["param1", "param2"]

CSV_EXAMPLE = {"col1": {"param1": "val11", "param2": {"value": 21, "unit": "factor"}}}


def test_create_input_json_creation_of_json_file():
    load_data_from_csv.create_input_json(
        input_directory=CSV_PATH, output_filename="test_example_create.json"
    )
    assert os.path.exists(os.path.join(CSV_PATH, "test_example_create.json"))


def test_create_input_json_required_fields_are_filled():
    pass
    #
    # js_file = load_data_from_csv.create_input_json(
    #     input_directory=CSV_PATH, output_filename="test_example_field.json"
    # )
    # js = data_input.load_json(js_file)
    # for k in js.keys():
    #     assert k in load_data_from_csv.REQUIRED_FILES


def test_create_json_from_csv_file_not_exist():
    pass


def test_create_json_from_csv_correct_output():
    pass


def test_create_json_from_csv_with_comma_separated_csv():
    d = load_data_from_csv.create_json_from_csv(
        DUMMY_CSV_PATH, "csv_comma", CSV_PARAMETERS, storage=False
    )
    assert d == {"csv_comma": CSV_EXAMPLE}


def test_create_json_from_csv_with_semicolon_separated_csv():
    d = load_data_from_csv.create_json_from_csv(
        DUMMY_CSV_PATH, "csv_semicolon", CSV_PARAMETERS, storage=False
    )

    assert d == {"csv_semicolon": CSV_EXAMPLE}


def test_create_json_from_csv_with_ampersand_separated_csv():
    d = load_data_from_csv.create_json_from_csv(
        DUMMY_CSV_PATH, "csv_ampersand", CSV_PARAMETERS, storage=False
    )

    assert d == {"csv_ampersand": CSV_EXAMPLE}


def test_create_json_from_csv_with_unknown_separator_for_csv():

    with pytest.raises(ValueError):
        load_data_from_csv.create_json_from_csv(
            DUMMY_CSV_PATH, "csv_unknown_separator", CSV_PARAMETERS, storage=False
        )


def teardown_module():
    os.remove(os.path.join(CSV_PATH, "test_example_create.json"))
