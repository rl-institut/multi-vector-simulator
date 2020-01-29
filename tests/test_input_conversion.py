import os

from .constants import REPO_PATH

import src.A1_csv_to_json as load_data_from_csv
import src.B0_data_input_json as data_input
from src.A1_csv_to_json import ALLOWED_FILES

elements = os.path.join(REPO_PATH, "inputs", "elements")


def test_create_input_json_creation_of_json_file():
    load_data_from_csv.create_input_json(
        input_directory=elements, output_filename="test_example_create.json"
    )
    assert os.path.exists(os.path.join(elements, "test_example_create.json"))


def test_create_input_json_required_fields_are_filled():

    js_file = load_data_from_csv.create_input_json(
        input_directory=elements, output_filename="test_example_field.json"
    )
    js = data_input.load_json(js_file)
    for k in js.keys():
        assert k in ALLOWED_FILES


def test_create_json_from_csv_file_not_exist():
    pass


def test_create_json_from_csv_correct_output():
    pass


def teardown_module():
    os.remove(os.path.join(elements, "test_example_create.json"))
    os.remove(os.path.join(elements, "test_example_field.json"))
