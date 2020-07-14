import os

# import constants from src
from src.constants import (
    INPUT_FOLDER,
    TEMPLATE_INPUT_FOLDER,
    OUTPUT_FOLDER,
    TEMPLATE_INPUT_PATH,
    DEFAULT_INPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    PATH_INPUT_FILE,
    PATH_INPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
    PATH_OUTPUT_FOLDER_INPUTS,
    INPUT_TYPE,
    OVERWRITE,
    DISPLAY_OUTPUT,
    JSON_FNAME,
    JSON_EXT,
    CSV_ELEMENTS,
    INPUTS_COPY,
    CSV_FNAME,
    CSV_EXT,
    REQUIRED_CSV_FILES,
    REQUIRED_CSV_PARAMETERS,
    MISSING_PARAMETERS_KEY,
    EXTRA_PARAMETERS_KEY,
    KPI_SCALARS,
    PDF_REPORT,
    DICT_PLOTS,
    TYPE_DATETIMEINDEX,
    TYPE_DATAFRAME,
    TYPE_SERIES,
    TYPE_TIMESTAMP,
    TYPE_BOOL,
    TYPE_STR,
    TYPE_NONE,
    PATHS_TO_PLOTS,
)

TESTS_ON_MASTER = "master"
TESTS_ON_DEV = "dev"

EXECUTE_TESTS_ON = os.environ.get("EXECUTE_TESTS_ON", "skip")

TEST_REPO_PATH = os.path.dirname(__file__)

DUMMY_CSV_PATH = os.path.join(TEST_REPO_PATH, "test_data")

CSV_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS)
JSON_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, JSON_FNAME)

# path of the file created automatically by
JSON_CSV_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS, CSV_FNAME)

# folder to store input directory for tests
TEST_INPUT_DIRECTORY = "test_data"

def PARSER_ARGS(input_folder = None, output_folder = None, ext = None, force = True, log = None):
    """
    This function defines the parser arguments needed for a multitude of pytests (unit and benchmark)

    Parameters
    ----------
    input_folder
        Input folder for MVS

    output_folder
        Output folder for MVS

    ext
        File extension to be used ("csv" or "json")

    Returns
    -------
    List of arguments to execute MVS.
    """
    parser_args = []

    if input_folder != None:
        parser_args.append("-i")
        parser_args.append(input_folder)

    if output_folder != None:
        parser_args.append("-o")
        parser_args.append(output_folder)

    if log is None:
        parser_args.append("-log")
        parser_args.append("warning")
    else:
        parser_args.append("-log")
        parser_args.append(log)

    if force is True:
        parser_args.append("-f")

    if ext != None:
        parser_args.append("-ext")
        parser_args.append(ext)

    return parser_args