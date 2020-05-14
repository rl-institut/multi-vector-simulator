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
    REQUIRED_CSV_FILES,
    REQUIRED_CSV_PARAMETERS,
    KPI_SCALARS,
    PDF_REPORT,
)

TEST_REPO_PATH = os.path.dirname(__file__)

DUMMY_CSV_PATH = os.path.join(TEST_REPO_PATH, "test_data")

CSV_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS)
JSON_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, JSON_FNAME)

# path of the file created automatically by
JSON_CSV_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS, CSV_FNAME)
