import os

# import constants from src
from src.constants import INPUT_FOLDER, JSON_FNAME, CSV_ELEMENTS, INPUTS_COPY

TEST_REPO_PATH = os.path.dirname(__file__)

CSV_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS)
JSON_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, JSON_FNAME)

# input directory for file you need for specific tests
SPECIFIC_TESTS_INPUT = "input_for_specific_tests"

# json file for specific D1 tests
D1_JSON = os.path.join(TEST_REPO_PATH, SPECIFIC_TESTS_INPUT,
                       "mvs_config_for_D1_tests.json")