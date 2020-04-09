import os

# name of the folder containing mvs model described by ".csv" files
CSV_ELEMENTS = "csv_elements"
# name of the folder containing the copied content of the input folder within the output folder
INPUTS_COPY = "inputs"

REPO_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from src.constants import INPUT_FOLDER

from src.constants import JSON_FNAME

JSON_PATH = os.path.join(REPO_PATH, INPUT_FOLDER, JSON_FNAME)
