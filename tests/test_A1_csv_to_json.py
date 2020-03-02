import os

from .constants import REPO_PATH

import src.A1_csv_to_json as load_data_from_csv

elements = os.path.join(REPO_PATH, "tests", "inputs", "csv_elements")

def test_create_input_json_creation_of_json_file():
    load_data_from_csv.create_input_json(
        input_directory=elements, output_filename="test_example_create.json"
    )
    assert os.path.exists(os.path.join(elements, "test_example_create.json"))


def teardown_module():
    os.remove(os.path.join(elements, "test_example_create.json"))
