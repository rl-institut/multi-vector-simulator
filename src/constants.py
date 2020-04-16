import os

# path to the root of this repository (assumes this file is in src folder)
REPO_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# name of the input folder
INPUT_FOLDER = "inputs"
# name of the json extension
JSON_EXT = "json"
# name of the csv extension
CSV_EXT = "csv"
# name of the folder containing mvs model described by .csv files
CSV_ELEMENTS = "csv_elements"
# name of the json file which should be present in the input folder if option -i json was chosen
JSON_FNAME = "mvs_config.json"
# name of the json file which is should be created in the input folder if option -i csv was chosen
CSV_FNAME = "mvs_csv_config.json"
# list of csv filename which must be present within the CSV_ELEMENTS folder
REQUIRED_CSV_FILES = (
    "fixcost",
    "simulation_settings",
    "project_data",
    "economic_data",
    "energyConversion",
    "energyProduction",
    "energyStorage",
    "energyProviders",
    "energyConsumption",
)
# name of the folder containing timeseries described by .csv files
TIME_SERIES = "time_series"
# name of the folder containing the output of the simulation
OUTPUT_FOLDER = "MVS_outputs"
# name of the folder containing the copied content of the input folder within the output folder
INPUTS_COPY = INPUT_FOLDER

# default paths to input, output and sequences folders
DEFAULT_INPUT_PATH = os.path.join(REPO_PATH, INPUT_FOLDER)
DEFAULT_OUTPUT_PATH = os.path.join(REPO_PATH, OUTPUT_FOLDER)

USER_INPUT_ARGUMENTS = (
    "path_input_file",
    "path_output_folder",
    "input_type" "path_input_sequences",
    "overwrite",
    "display_output",
)

DEFAULT_MAIN_KWARGS = dict(
    overwrite=False,
    input_type=JSON_EXT,
    path_input_folder=DEFAULT_INPUT_PATH,
    path_output_folder=DEFAULT_OUTPUT_PATH,
    display_output="info",
    lp_file_output=False,
)
