import os

from src.constants import REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS

import src.A1_csv_to_json as load_data_from_csv

elements = os.path.join(REPO_PATH, "tests", INPUT_FOLDER, CSV_ELEMENTS)
CSV_TEST = os.path.join(REPO_PATH, "tests", "test_data")
CSV_PARAMETERS = ["param1", "param2"]

CSV_EXAMPLE = {"col1": {"param1": "val11", "param2": {"value": 21, "unit": "factor"}}}


def test_create_input_json_creation_of_json_file():
    load_data_from_csv.create_input_json(
        input_directory=elements, output_filename="test_example_create.json"
    )
    assert os.path.exists(os.path.join(elements, "test_example_create.json"))


def test_create_json_from_csv_with_comma_separated_csv():
    d = load_data_from_csv.create_json_from_csv(
        CSV_TEST, "csv_comma", CSV_PARAMETERS, storage=False
    )
    assert d == {"csv_comma": CSV_EXAMPLE}


def test_create_json_from_csv_with_semicolon_separated_csv():
    d = load_data_from_csv.create_json_from_csv(
        CSV_TEST, "csv_semicolon", CSV_PARAMETERS, storage=False
    )

    assert d == {"csv_semicolon": CSV_EXAMPLE}


def test_create_json_from_csv_with_ampersand_separated_csv():
    d = load_data_from_csv.create_json_from_csv(
        CSV_TEST, "csv_ampersand", CSV_PARAMETERS, storage=False
    )

    assert d == {"csv_ampersand": CSV_EXAMPLE}


def teardown_module():
    os.remove(os.path.join(elements, "test_example_create.json"))
