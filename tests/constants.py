import os

# import constants from src
from src.constants import INPUT_FOLDER, JSON_FNAME, CSV_ELEMENTS, INPUTS_COPY

TEST_REPO_PATH = os.path.dirname(__file__)

CSV_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS)
JSON_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, JSON_FNAME)
