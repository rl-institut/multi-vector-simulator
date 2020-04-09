import os

# import constants from src
from src.constants import INPUT_FOLDER

from src.constants import JSON_FNAME

from src.constants import REPO_PATH

# name of the folder containing mvs model described by ".csv" files
CSV_ELEMENTS = "csv_elements"
# name of the folder containing the copied content of the input folder within the output folder
INPUTS_COPY = "inputs"

TEST_REPO_PATH = os.path.dirname((__file__))

JSON_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, JSON_FNAME)
