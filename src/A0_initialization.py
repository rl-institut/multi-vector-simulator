"""
Module A0_initialization should define the most basic settings of the MVS simulation. This includes
- Executing the MVS from terminal
   - Using json input file
   - Using csv input files
   - Optional: Force folder overwrite
   - Optional: Display logging in terminal
- Set default values for MVS execution
- Check that all necessary (and called) files exist
- Create output directory
- Display welcome message with current version number
- Define logging depth
"""

import os
import sys
import shutil
import logging
import argparse

from src.constants import (
    DEFAULT_INPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SEQUENCES_PATH,
    JSON_FNAME,
    CSV_FNAME,
    JSON_EXT,
    CSV_EXT,
    CSV_ELEMENTS,
    INPUTS_COPY,
    USER_INPUT_ARGUMENTS,
)

from oemof.tools import logger

# works only when the commands are executed from the root of the repository
REPO_PATH = os.path.abspath(os.curdir)


def create_parser():
    parser = argparse.ArgumentParser(prog="mvs", description="Process MVS arguments")
    parser.add_argument(
        "-i",
        dest="path_input_folder",
        nargs="?",
        type=str,
        help="path to the json input file",
        default=DEFAULT_INPUT_PATH,
    )
    parser.add_argument(
        "-ext",
        dest="input_type",
        nargs="?",
        type=str,
        help="type (json or csv) of the input files",
        default="json",
        const="json",
        choices=["json", "csv"],
    )
    parser.add_argument(
        "-o",
        dest="path_output_folder",
        nargs="?",
        type=str,
        help="output folder for the simulation's results",
        default=DEFAULT_OUTPUT_PATH,
    )
    parser.add_argument(
        "-log",
        dest="display_output",
        help="level of log in the console",
        nargs="?",
        default="info",
        const="info",
        choices=["debug", "info", "error", "warning"],
    )
    parser.add_argument(
        "-f",
        dest="overwrite",
        help="overwrite the output folder",
        nargs="?",
        const=True,
        default=False,
        type=bool,
    )
    return parser


def check_input_folder(path_input_folder, input_type):
    """

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
        print(path_input_file)
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
    """
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
                    "Output folder exists and should not be overwritten. Please choose other folder."
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

    return path_output_folder_inputs


def process_user_arguments(
    path_input_folder=None,
    input_type=None,
    path_output_folder=None,
    path_input_sequences=None,
    overwrite=None,
    display_output=None,
    lp_file_output=False,
    welcome_text=None,
):
    """
    Process user command from terminal inputs. If inputs provided as arguments of the function,
    it will overwrite the command line arguments.

    :param path_input_folder:
        Descripes path to inputs folder (command line "-i")
    :param input_type:
        Descripes type of input to expect (command line "-ext")
    :param path_output_folder:
        Describes path to folder to be used for terminal output (command line "-o")
        Must not exist before
    :param path_input_sequences:
        Describes path to sequences/timeseries
    :param overwrite:
        (Optional) Can force tool to replace existing output folder (command line "-f")
    :param display_output:
        (Optional) Determines which messages are used for terminal output (command line "-log")
            "-debug": All logging messages
            "-info": All informative messages and warnings (default)
            "-warnings": All warnings
            "-errors": Only errors
    :param lp_file_output:
        Save linear equation system generated as lp file
    :param welcome_text:
        Text to be displayed
    :return:
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

    if path_input_sequences is None:
        path_input_sequences = args.get("path_input_sequences", DEFAULT_SEQUENCES_PATH)

    if overwrite is None:
        overwrite = args.get("overwrite")

    if display_output is None:
        display_output = args.get("display_output")

    print(path_input_folder)
    path_input_file = check_input_folder(path_input_folder, input_type)
    path_output_folder_inputs = check_output_folder(
        path_input_folder, path_output_folder, overwrite
    )

    user_input = {
        "label": "simulation_settings",
        "path_input_folder": path_input_folder,
        "path_input_sequences": path_input_sequences,
        "input_type": input_type,
        "path_input_file": path_input_file,
        "path_output_folder": path_output_folder,
        "path_output_folder_inputs": path_output_folder_inputs,
        "lp_file_output": lp_file_output,
        "overwrite": overwrite,
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


logger.define_logging(
    logpath=".",
    logfile="mvst_logfile.log",
    file_level=logging.DEBUG,
    screen_level=logging.ERROR,
)
