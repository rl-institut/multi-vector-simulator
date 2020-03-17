"""
Module A0_initialization defines functions to parse user inputs to the MVS simulation.
    - Display welcome message with current version number
    - Parse command line arguments and set default values for MVS parameters if not provided
    - Check that all necessary files and folder exists
    - Create output directory
    - Define screen logging depth

Usage from root of repository:
python mvs_tool.py [-h] [-i [PATH_INPUT_FOLDER]] [-ext [{json,csv}]]
                          [-o [PATH_OUTPUT_FOLDER]]
                          [-log [{debug,info,error,warning}]] [-f [OVERWRITE]]

Process MVS arguments

optional arguments:
  -h, --help            show this help message and exit
  -i [PATH_INPUT_FOLDER]
                        path to the input folder
  -ext [{json,csv}]     type (json or csv) of the input files (default: 'json'
  -o [PATH_OUTPUT_FOLDER]
                        path to the output folder for the simulation's results
  -log [{debug,info,error,warning}]
                        level of logging in the console
  -f [OVERWRITE]        overwrite the output folder if True (default: False)

"""

import os
import shutil
import logging
import argparse

from src.constants import (
    REPO_PATH,
    DEFAULT_INPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    JSON_FNAME,
    CSV_FNAME,
    JSON_EXT,
    CSV_EXT,
    CSV_ELEMENTS,
    INPUTS_COPY,
)

from oemof.tools import logger


def create_parser():
    """Create a command line argument parser for MVS

    :return: parser
    """
    parser = argparse.ArgumentParser(
        prog="python mvs_tool.py", description="Process MVS arguments"
    )
    parser.add_argument(
        "-i",
        dest="path_input_folder",
        nargs="?",
        type=str,
        help="path to the input folder",
        default=DEFAULT_INPUT_PATH,
    )
    parser.add_argument(
        "-ext",
        dest="input_type",
        nargs="?",
        type=str,
        help="type (json or csv) of the input files (default: 'json'",
        default=JSON_EXT,
        const=JSON_EXT,
        choices=[JSON_EXT, CSV_EXT],
    )
    parser.add_argument(
        "-o",
        dest="path_output_folder",
        nargs="?",
        type=str,
        help="path to the output folder for the simulation's results",
        default=DEFAULT_OUTPUT_PATH,
    )
    parser.add_argument(
        "-log",
        dest="display_output",
        help="level of logging in the console",
        nargs="?",
        default="info",
        const="info",
        choices=["debug", "info", "error", "warning"],
    )
    parser.add_argument(
        "-f",
        dest="overwrite",
        help="overwrite the output folder if True (default: False)",
        nargs="?",
        const=True,
        default=False,
        type=bool,
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

    # make the path absolute
    if REPO_PATH not in os.path.abspath(path_input_folder):
        path_input_folder = os.path.join(REPO_PATH, path_input_folder)

    logging.debug("Checking for inputs files")

    if input_type == JSON_EXT:
        path_input_file = os.path.join(path_input_folder, JSON_FNAME)
        if os.path.exists(path_input_file) is False:
            raise (
                FileNotFoundError(
                    "Missing input json file!\n"
                    "The input json file '{}' can not be found.\n"
                    "Operation terminated.".format(JSON_FNAME)
                )
            )
        json_files = [f for f in os.listdir(path_input_folder) if f.endswith(JSON_EXT)]
        if len(json_files) > 1:
            raise (
                FileExistsError(
                    "Two many json files in input folder ({})!\n"
                    "Only the input json file '{}' should be present.\n"
                    "Operation terminated.".format(", ".join(json_files), JSON_FNAME)
                )
            )
    elif input_type == CSV_EXT:
        path_input_file = os.path.join(path_input_folder, CSV_ELEMENTS, CSV_FNAME)
        if os.path.exists(os.path.join(path_input_folder, CSV_ELEMENTS)) is False:
            raise (
                FileNotFoundError(
                    "Missing folder for csv inputs! "
                    "The input csv folder '{}' can not be found.\n"
                    "Operation terminated.".format(CSV_ELEMENTS)
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

    # make the path absolute
    if REPO_PATH not in os.path.abspath(path_input_folder):
        path_input_folder = os.path.join(REPO_PATH, path_input_folder)
    if REPO_PATH not in os.path.abspath(path_output_folder):
        path_output_folder = os.path.join(REPO_PATH, path_output_folder)

    path_output_folder_inputs = os.path.join(path_output_folder, INPUTS_COPY)

    logging.debug("Checking for output folder")
    if os.path.exists(path_output_folder) is True:
        if overwrite is False:
            raise (
                FileExistsError(
                    "Output folder {} already exists and should not be overwritten. "
                    "Please choose other folder.".format(path_output_folder)
                )
            )
        else:
            logging.info("Removing existing output folder " + path_output_folder)
            # might not work on windows
            shutil.rmtree(path_output_folder, ignore_errors=True)

            logging.info("Creating output folder " + path_output_folder)
            os.mkdir(path_output_folder)

            logging.info('Creating folder "inputs" in output folder.')
            shutil.copytree(path_input_folder, path_output_folder_inputs)
    else:
        logging.info("Creating output folder " + path_output_folder)
        os.mkdir(path_output_folder)

        logging.info('Creating folder "inputs" in output folder.')
        shutil.copytree(path_input_folder, path_output_folder_inputs)


def process_user_arguments(
    path_input_folder=None,
    input_type=None,
    path_output_folder=None,
    overwrite=None,
    display_output=None,
    lp_file_output=False,
    welcome_text=None,
):
    """
    Process user command from terminal inputs. If inputs provided as arguments of the function,
    they will overwrite the command line arguments.

    :param path_input_folder:
        Descripes path to inputs folder (command line "-i")
    :param input_type:
        Descripes type of input to expect (command line "-ext")
    :param path_output_folder:
        Describes path to folder to be used for terminal output (command line "-o")
        Must not exist before
    :param overwrite:
        (Optional) Can force tool to replace existing output folder (command line "-f")
    :param display_output:
        (Optional) Determines which messages are used for terminal output (command line "-log")
            "debug": All logging messages
            "info": All informative messages and warnings (default)
            "warnings": All warnings
            "errors": Only errors
    :param lp_file_output:
        Save linear equation system generated as lp file
    :param welcome_text:
        Text to be displayed
    :return: a dict with these arguments as keys (except welcome_text which is replaced by label)
    """

    logging.debug("Get user inputs from console")

    # Parse the arguments from the command line
    parser = create_parser()
    args = vars(parser.parse_args())

    # Give priority from kwargs over command line arguments
    if path_input_folder is None:
        path_input_folder = args.get("path_input_folder")

    if input_type is None:
        input_type = args.get("input_type")

    if path_output_folder is None:
        path_output_folder = args.get("path_output_folder")

    if overwrite is None:
        overwrite = args.get("overwrite")

    if display_output is None:
        display_output = args.get("display_output")

    path_input_file = check_input_folder(path_input_folder, input_type)
    check_output_folder(path_input_folder, path_output_folder, overwrite)

    user_input = {
        "label": "simulation_settings",
        "path_input_folder": path_input_folder,
        "input_type": input_type,
        "path_input_file": path_input_file,
        "path_output_folder": path_output_folder,
        "overwrite": overwrite,
        "display_output": display_output,
        "lp_file_output": lp_file_output,
    }

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
        logfile="mvst_logfile.log",
        file_level=logging.DEBUG,
        screen_level=screen_level,
    )

    if welcome_text is not None:
        # display welcome text
        logging.info(welcome_text)

    return user_input
