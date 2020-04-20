import os

# import constants from src
from src.constants import (
    INPUT_FOLDER,
    JSON_FNAME,
    JSON_EXT,
    CSV_ELEMENTS,
    INPUTS_COPY,
    CSV_FNAME,
    CSV_EXT,
)

TEST_REPO_PATH = os.path.dirname(__file__)

CSV_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS)
JSON_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, JSON_FNAME)

# path of the file created automatically by
JSON_CSV_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS, CSV_FNAME)
