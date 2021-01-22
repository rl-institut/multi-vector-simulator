r"""
Module A0 - Initialization
==========================

Module A0_initialization defines functions to parse user inputs to the MVS simulation.
    - Display welcome message with current version number
    - Parse command line arguments and set default values for MVS parameters if not provided
    - Check that all necessary files and folder exist
    - Create output directory
    - Define screen logging depth

Usage from root of repository:

.. code-block:: bash

    python mvs_tool.py [-h] [-i [PATH_INPUT_FOLDER]] [-ext [{json,csv}]] [-o [PATH_OUTPUT_FOLDER]]
    [-log [{debug,info,error,warning}]] [-f [OVERWRITE]] [-pdf [PDF_REPORT]] [-png [SAVE_PNG]]

Usage when multi-vector-simulator is installed as a package:

.. code-block:: bash

    mvs_tool [-h] [-i [PATH_INPUT_FOLDER]] [-ext [{json,csv}]] [-o [PATH_OUTPUT_FOLDER]]
    [-log [{debug,info,error,warning}]] [-f [OVERWRITE]] [-pdf [PDF_REPORT]] [-png [SAVE_PNG]]

Process MVS arguments

optional arguments:
    -h, --help
        show this help message and exit

    -i [PATH_INPUT_FOLDER]
        path to the input folder

    -ext [{json,csv}]
        type (json or csv) of the input files (default: 'json')

    -o [PATH_OUTPUT_FOLDER]
        path to the output folder for the simulation's results

    -log [{debug,info,error,warning}]
        level of logging in the console

    -f [OVERWRITE]
        overwrite the output folder if True (default: False)

    -pdf [PDF_REPORT]
        generate a pdf report of the simulation if True (default: False)

    -png [SAVE_PNG]
        generate png figures of the simulation in the output_folder if True (default: False)

"""

import argparse
import logging
import os
import shutil

from oemof.tools import logger


from multi_vector_simulator.utils.constants import (
    REPO_PATH,
    PACKAGE_DATA_PATH,
    DEFAULT_INPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    JSON_FNAME,
    CSV_FNAME,
    JSON_EXT,
    CSV_EXT,
    CSV_ELEMENTS,
    INPUT_FOLDER,
    INPUTS_COPY,
    DEFAULT_MAIN_KWARGS,
    PDF_REPORT,
    SIMULATION_SETTINGS,
    PATH_INPUT_FILE,
    PATH_INPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
    INPUT_TYPE,
    OVERWRITE,
    DISPLAY_OUTPUT,
    SAVE_PNG,
    LOGFILE,
    REPORT_FOLDER,
    OUTPUT_FOLDER,
    PDF_REPORT,
    JSON_WITH_RESULTS,
    JSON_FILE_EXTENSION,
    ARG_PDF,
    ARG_REPORT_PATH,
    ARG_PATH_SIM_OUTPUT,
    ARG_DEBUG_REPORT,
)
from multi_vector_simulator.utils.constants_json_strings import LABEL


def mvs_arg_parser():
    """Create a command line argument parser for MVS

    Usage from root of repository:

    .. code-block:: bash

        python mvs_tool.py [-h] [-i [PATH_INPUT_FOLDER]] [-ext [{json,csv}]] [-o [PATH_OUTPUT_FOLDER]]
        [-log [{debug,info,error,warning}]] [-f [OVERWRITE]] [-pdf [PDF_REPORT]] [-png [SAVE_PNG]]

    Usage when multi-vector-simulator is installed as a package:

    .. code-block:: bash

        mvs_tool [-h] [-i [PATH_INPUT_FOLDER]] [-ext [{json,csv}]] [-o [PATH_OUTPUT_FOLDER]]
        [-log [{debug,info,error,warning}]] [-f [OVERWRITE]] [-pdf [PDF_REPORT]] [-png [SAVE_PNG]]

    Process MVS arguments

    optional arguments:
        -h, --help
            show this help message and exit

        -i [PATH_INPUT_FOLDER]
            path to the input folder

        -ext [{json,csv}]
            type (json or csv) of the input files (default: 'json')

        -o [PATH_OUTPUT_FOLDER]
            path to the output folder for the simulation's results

        -log [{debug,info,error,warning}]
            level of logging in the console

        -f [OVERWRITE]
            overwrite the output folder if True (default: False)

        -pdf [PDF_REPORT]
            generate a pdf report of the simulation if True (default: False)

        -png [SAVE_PNG]
            generate png figures of the simulation in the output_folder if True (default: False)


    :return: parser
    """
    parser = argparse.ArgumentParser(
        prog="python mvs_tool.py", description="Process MVS arguments"
    )
    parser.add_argument(
        "-i",
        dest=PATH_INPUT_FOLDER,
        nargs="?",
        type=str,
        help="path to the input folder",
        default=DEFAULT_INPUT_PATH,
    )
    parser.add_argument(
        "-ext",
        dest=INPUT_TYPE,
        nargs="?",
        type=str,
        help="type (json or csv) of the input files (default: 'json'",
        default=JSON_EXT,
        const=JSON_EXT,
        choices=[JSON_EXT, CSV_EXT],
    )
    parser.add_argument(
        "-o",
        dest=PATH_OUTPUT_FOLDER,
        nargs="?",
        type=str,
        help="path to the output folder for the simulation's results",
        default=DEFAULT_OUTPUT_PATH,
    )
    parser.add_argument(
        "-log",
        dest=DISPLAY_OUTPUT,
        help="level of logging in the console",
        nargs="?",
        default="info",
        const="info",
        choices=["debug", "info", "error", "warning"],
    )
    parser.add_argument(
        "-f",
        dest=OVERWRITE,
        help="overwrite the output folder if True (default: False)",
        nargs="?",
        const=True,
        default=False,
        type=bool,
    )
    parser.add_argument(
        "-pdf",
        dest="pdf_report",
        help="generate a pdf report of the simulation if True (default: False)",
        nargs="?",
        const=True,
        default=False,
        type=bool,
    )
    parser.add_argument(
        "-png",
        dest=SAVE_PNG,
        help="generate png figures of the simulation in the output_folder if True (default: False)",
        nargs="?",
        const=True,
        default=False,
        type=bool,
    )
    return parser


def report_arg_parser():
    """Create a command line argument parser for MVS

    Usage when multi-vector-simulator is installed as a package:

    .. code-block:: bash

        mvs_report [-h] [-i [PATH_SIM_OUTPUT]] [-o [REPORT_PATH]] [-pdf]

    Process mvs report command line arguments

    optional arguments:
      -h, --help
        show this help message and exit

      -pdf [PRINT_REPORT]
        print the report as pdf (default: False)

      -i [OUTPUT_FOLDER]
        path to the simulation result json file 'json_with_results.json'
      -o [REPORT_PATH]
        path to save the pdf report


    :return: parser
    """
    parser = argparse.ArgumentParser(
        prog="mvs_report", description="Display the report of a MVS simulation",
    )
    parser.add_argument(
        "-pdf",
        dest=ARG_PDF,
        help="print the report as pdf (default: False)",
        nargs="?",
        const=True,
        default=False,
        type=bool,
    )
    parser.add_argument(
        "-i",
        dest=ARG_PATH_SIM_OUTPUT,
        nargs="?",
        type=str,
        help=f"path to the simulation result json file {JSON_WITH_RESULTS}.json'",
        default=os.path.join(
            REPO_PATH, OUTPUT_FOLDER, JSON_WITH_RESULTS + JSON_FILE_EXTENSION
        ),
    )
    parser.add_argument(
        "-o",
        dest=ARG_REPORT_PATH,
        nargs="?",
        type=str,
        help="path to save the pdf report",
        default="",
    )
    parser.add_argument(
        "-d",
        dest=ARG_DEBUG_REPORT,
        nargs="?",
        type=bool,
        help="run the dash app in debug mode with hot-reload",
        const=True,
        default=False,
    )
    return parser


def check_input_folder(path_input_folder, input_type):
    """Enforces the rules for the input folder and files

        There should be a single json file for config (described under JSON_FNAME) in case
        input_type is equal to JSON_EXT.
        There should be a folder with csv files (name of folder given by CSV_ELEMENTS) in case
        input_type is equal to CSV_EXT.


    :param path_input_folder: path to input folder
    :param input_type: of of JSON_EXT or CSV_EXT
    :return: the json filename which will be used as input of the simulation
    """

    logging.debug("Checking for inputs files")

    if input_type == JSON_EXT:
        path_input_file = os.path.join(path_input_folder, JSON_FNAME)
        if os.path.exists(path_input_file) is False:

            raise (
                FileNotFoundError(
                    "Missing input json file!\n"
                    "The input json file '{}' in path '{}' can not be found.\n"
                    "Operation terminated.".format(JSON_FNAME, path_input_folder)
                )
            )
        json_files = [f for f in os.listdir(path_input_folder) if f.endswith(JSON_EXT)]
        if len(json_files) > 1:
            raise (
                FileExistsError(
                    "Two many json files ({}) in input folder '{}'!\n"
                    "Only the input json file '{}' should be present.\n"
                    "Operation terminated.".format(
                        ", ".join(json_files), path_input_folder, JSON_FNAME
                    )
                )
            )
    elif input_type == CSV_EXT:
        path_input_file = os.path.join(path_input_folder, CSV_ELEMENTS, CSV_FNAME)
        if os.path.exists(os.path.join(path_input_folder, CSV_ELEMENTS)) is False:
            raise (
                FileNotFoundError(
                    "Missing folder for csv inputs! "
                    "The input csv folder '{}' can not be found in the input path '{}'.\n"
                    "Operation terminated.".format(CSV_ELEMENTS, path_input_folder)
                )
            )

    return path_input_file


def check_output_folder(path_input_folder, path_output_folder, overwrite):
    """Enforces the rules for the output folder

            An error is raised if the path_output_folder already exists, unless overwrite is set
            to True. The path_output_folder is created if not existing and the content of
            path_input_folder is copied in a folder named INPUTS_COPY.

    :param path_input_folder: path to input folder
    :param path_output_folder: path to output folder
    :param overwrite: boolean indicating what to do if the output folder exists already
    :return: the path to the folder stored in the output folder as copy of the input folder
    """

    path_output_folder_inputs = os.path.join(path_output_folder, INPUTS_COPY)

    logging.debug("Checking for output folder")
    if os.path.exists(path_output_folder) is True:
        if overwrite is False:
            raise (
                FileExistsError(
                    "Output folder {} already exists. "
                    "If you want to overwrite the folder, please choose the force option -f when executing the MVS. "
                    "Otherwise, provide a name to a new output folder with option -o.".format(
                        path_output_folder
                    )
                )
            )
        else:
            # Pre-existing folder is be deleted
            logging.info("Removing existing output folder " + path_output_folder)
            shutil.rmtree(path_output_folder, ignore_errors=True)

    try:
        # trying to create path_output_folder
        os.makedirs(path_output_folder, exist_ok=True)
        logging.info("Creating output folder " + path_output_folder)
    except OSError as error:
        # In case that path_output_folder already exists
        logging.info(
            "It was not possible to create the output folder " + path_output_folder
        )

    logging.info(f"Creating folder {INPUT_FOLDER} in output folder.")
    shutil.copytree(path_input_folder, path_output_folder_inputs)


def process_user_arguments(
    path_input_folder=None,
    input_type=None,
    path_output_folder=None,
    overwrite=None,
    pdf_report=None,
    display_output=None,
    save_png=None,
    lp_file_output=False,
    welcome_text=None,
):
    """
    Process user command from terminal inputs. If inputs provided as arguments of the function,
    they will overwrite the command line arguments.

    :param path_input_folder:
        Describes path to inputs folder (command line "-i")
    :param input_type:
        Describes type of input to expect (command line "-ext")
    :param path_output_folder:
        Describes path to folder to be used for terminal output (command line "-o")
        Must not exist before
    :param overwrite:
        (Optional) Can force tool to replace existing output folder (command line "-f")
    :param pdf_report:
        (Optional) Can generate an automatic pdf report of the simulation's results (Command line "-pdf")
    :param save_png:
        (Optional) Can generate png figures with the simulation's results (Command line "-png")
    :param display_output:
        (Optional) Determines which messages are used for terminal output (command line "-log")
        Allowed values are
        "debug": All logging messages,
        "info": All informative messages and warnings (default),
        "warning": All warnings,
        "error": Only errors,
    :param lp_file_output:
        Save linear equation system generated as lp file
    :param welcome_text:
        Text to be displayed
    :return: a dict with these arguments as keys (except welcome_text which is replaced by label)
    """

    logging.debug("Get user inputs from console")

    # Parse the arguments from the command line
    parser = mvs_arg_parser()
    args = vars(parser.parse_args())

    # Give priority from user input kwargs over command line arguments
    # However the command line arguments have priority over default kwargs
    if path_input_folder is None:
        path_input_folder = args.get(
            PATH_INPUT_FOLDER, DEFAULT_MAIN_KWARGS[PATH_INPUT_FOLDER]
        )

    if input_type is None:
        input_type = args.get(INPUT_TYPE, DEFAULT_MAIN_KWARGS[INPUT_TYPE])

    if path_output_folder is None:
        path_output_folder = args.get(
            PATH_OUTPUT_FOLDER, DEFAULT_MAIN_KWARGS[PATH_OUTPUT_FOLDER]
        )

    if overwrite is None:
        overwrite = args.get(OVERWRITE, DEFAULT_MAIN_KWARGS[OVERWRITE])

    if pdf_report is None:
        pdf_report = args.get("pdf_report", DEFAULT_MAIN_KWARGS["pdf_report"])

    if display_output is None:
        display_output = args.get(DISPLAY_OUTPUT, DEFAULT_MAIN_KWARGS[DISPLAY_OUTPUT])

    if save_png is None:
        save_png = args.get(SAVE_PNG, DEFAULT_MAIN_KWARGS[SAVE_PNG])

    # if the default input file does not exist, use package default input file
    if (
        path_input_folder == DEFAULT_INPUT_PATH
        and os.path.exists(os.path.join(path_input_folder, JSON_FNAME)) is False
    ):
        path_input_folder = os.path.join(PACKAGE_DATA_PATH, INPUT_FOLDER)
        logging.info(
            "No default input file found in your path, using example simulation input"
        )

    path_input_file = check_input_folder(path_input_folder, input_type)
    check_output_folder(path_input_folder, path_output_folder, overwrite)

    user_input = {
        LABEL: SIMULATION_SETTINGS,
        PATH_INPUT_FOLDER: path_input_folder,
        INPUT_TYPE: input_type,
        PATH_INPUT_FILE: path_input_file,
        PATH_OUTPUT_FOLDER: path_output_folder,
        OVERWRITE: overwrite,
        DISPLAY_OUTPUT: display_output,
        "lp_file_output": lp_file_output,
    }

    if pdf_report is True:
        user_input.update(
            {
                "path_pdf_report": os.path.join(
                    path_output_folder, REPORT_FOLDER, PDF_REPORT
                )
            }
        )

    if save_png is True:
        user_input.update({"path_png_figs": path_output_folder})

    if display_output == "debug":
        screen_level = logging.DEBUG
    elif display_output == "info":
        screen_level = logging.INFO
    elif display_output == "warning":
        screen_level = logging.WARNING
    elif display_output == "error":
        screen_level = logging.ERROR
    else:
        screen_level = logging.INFO

    # Define logging settings and path for saving log
    logger.define_logging(
        logpath=path_output_folder,
        logfile=LOGFILE,
        file_level=logging.DEBUG,
        screen_level=screen_level,
    )

    # Disable log messages of external libraries saving into the log file, unless they are ERROR or CRITICAL level
    for ext_lib_logger in (
        "asyncio",
        "asyncio.coroutines",
        "websockets.server",
        "websockets.protocol",
        "websockets.client",
        "urllib3.connectionpool",
        "PIL.PngImagePlugin",
    ):
        logger.getLogger(ext_lib_logger).setLevel(logging.ERROR)

    if welcome_text is not None:
        # display welcome text
        logging.info(welcome_text)

    return user_input
