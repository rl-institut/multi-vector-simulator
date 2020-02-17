#!/usr/bin/env python
import os
import sys
import shutil
import logging
import argparse

from oemof.tools import logger

# works only when the commands are executed from the root of the repository
REPO_PATH = os.path.abspath(os.curdir)
DEFAULT_INPUT_FILE = os.path.join(REPO_PATH, "inputs", "working_example.json")
DEFAULT_OUTPUT_FOLDER = os.path.join(REPO_PATH, "MVS_outputs")


def create_parser():
    parser = argparse.ArgumentParser(prog="mvs", description="Process MVS arguments")
    parser.add_argument(
        "-i",
        dest="path_input_file",
        nargs="?",
        type=str,
        help="path to the json input file",
        default=None,
    )
    parser.add_argument(
        "-o",
        dest="path_output_folder",
        nargs="?",
        type=str,
        help="output folder for the simulation's results",
        default=None,
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


def check_input_directory(path_input_file):
    """
    :param path_input_file:
    :return:
    """

    if REPO_PATH not in os.path.abspath(path_input_file):
        path_input_file = os.path.join(REPO_PATH, path_input_file)

    path_input_folder = os.path.dirname(path_input_file)

    logging.debug("Checking for inputs files")

    if path_input_file.endswith("json"):
        if os.path.isfile(path_input_file) is False:
            raise (
                FileNotFoundError(
                    "Missing input json file! "
                    "\n The input json file can not be found. Operation terminated."
                )
            )
    else:
        if os.path.exists(path_input_file) is False:
            raise (
                NotADirectoryError(
                    "Missing folder for inputs! "
                    "\n The input folder can not be found. Operation terminated."
                )
            )

    return path_input_folder


def check_output_directory(path_output_folder, overwrite):
    """
    :param path_output_folder:
    :param overwrite:
    :return:
    """

    if REPO_PATH not in os.path.abspath(path_output_folder):
        path_output_folder = os.path.join(REPO_PATH, path_output_folder)

    logging.debug("Checking for output folder")
    if os.path.exists(path_output_folder) is True:
        if overwrite is False:
            user_reply = input(
                "Attention: Output overwrite? "
                "\n Output folder already exists. Should it be overwritten? (y/[N])"
            )
            if user_reply in ["y", "Y", "yes", "Yes"]:
                overwrite = True
            else:
                logging.critical(
                    "Output folder exists and should not be overwritten. Please choose other folder."
                )

                raise (
                    FileExistsError(
                        "Output folder exists and should not be overwritten. Please choose other folder."
                    )
                )

        if overwrite is True:
            logging.info("Removing existing folder " + path_output_folder)
            path_removed = os.path.abspath(path_output_folder)
            shutil.rmtree(path_removed, ignore_errors=True)
            logging.info("Creating output folder " + path_output_folder)
            os.mkdir(path_output_folder)

    else:
        logging.info("Creating output folder " + path_output_folder)
        os.mkdir(path_output_folder)


def get_user_input(
    path_input_file=None,
    path_output_folder=None,
    overwrite=False,  # todo this means that results will be overwritten.
    display_output="info",
    lp_file_output=False,
    **kwargs
):
    """
    Read user command from terminal inputs. Command:

    python A_mvs_eland.py path_to_input_file path_to_output_folder overwrite display_output lp_file_output

    :param path_input_file:
        Descripes path to inputs excel file
        This file includes paths to timeseries file
    :param path_output_folder:
        Describes path to folder to be used for terminal output
        Must not exist before
    :param overwrite:
        (Optional) Can force tool to replace existing output folder
        "-f"
    :param display_output:
        (Optional) Determines which messages are used for terminal output
            "-debug": All logging messages
            "-info": All informative messages and warnings (default)
            "-warnings": All warnings
            "-errors": Only errors

    :param lp_file_output:
        Save linear equation system generated as lp file

    :return:
    """

    if path_input_file is None:
        path_input_file = DEFAULT_INPUT_FILE

    if path_output_folder is None:
        path_output_folder = DEFAULT_OUTPUT_FOLDER
    else:
        pass

    if "test" in kwargs and kwargs["test"] is True:
        overwrite = True

    path_input_folder = check_input_directory(path_input_file)
    check_output_directory(path_output_folder, overwrite)

    user_input = {
        "label": "simulation_settings",
        "path_input_folder": path_input_folder,
        "path_input_file": path_input_file,
        "path_output_folder": path_output_folder,
        "path_output_folder_inputs": os.path.join(path_output_folder, "inputs"),
        "lp_file_output": lp_file_output,
        "display_output": display_output,
        "overwrite": overwrite,
    }

    logging.info('Creating folder "inputs" in output folder.')

    os.mkdir(user_input["path_output_folder_inputs"])
    if os.path.isdir(user_input["path_input_file"]):
        shutil.copytree(user_input["path_input_file"],
                    user_input["path_output_folder_inputs"])
    else:
        shutil.copy(user_input["path_input_file"],
                    user_input["path_output_folder_inputs"])
    return user_input


def welcome(welcome_text, **kwargs):
    """
    Welcome message and initialization of logging on screen and on file level.

    :param welcome_text: Welcome text defined in main function
    :return: user input settings regarding screen output, input folder/file and output folder
    """
    logging.debug("Get user inputs from console")
    user_input = get_user_input(**kwargs)

    # Set screen level (terminal output) according to user inputs
    console_log = user_input.pop("display_output")

    if console_log == "debug":
        screen_level = logging.DEBUG
    elif console_log == "info":
        screen_level = logging.INFO
    elif console_log == "warning":
        screen_level = logging.WARNING
    elif console_log == "error":
        screen_level = logging.ERROR
    else:
        screen_level = logging.INFO

    # Define logging settings and path for saving log
    logger.define_logging(
        logpath=user_input["path_output_folder"],
        logfile="mvst_logfile.log",
        file_level=logging.DEBUG,
        screen_level=screen_level,
    )

    # display welcome text
    logging.info(welcome_text)
    return user_input
