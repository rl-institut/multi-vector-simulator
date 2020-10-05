import os
import argparse

from multi_vector_simulator.utils.constants import (
    REPO_PATH,
    REPORT_PATH,
    OUTPUT_FOLDER,
    PDF_REPORT,
    JSON_WITH_RESULTS,
)
from multi_vector_simulator.B0_data_input_json import load_json
from multi_vector_simulator.F2_autoreport import create_app, open_in_browser, print_pdf

ARG_PDF = "print_report"
ARG_REPORT_PATH = "report_path"
SIM_OUTPUT_PATH = "output_folder"


def report_arg_parser():
    """Create a command line argument parser for MVS

    usage: python mvs_report.py [-h] [-pdf [PRINT_REPORT]] [-i [OUTPUT_FOLDER]]
                                [-o [REPORT_PATH]]

    Display the report of a MVS simulation

    optional arguments:
      -h, --help           show this help message and exit
      -pdf [PRINT_REPORT]  print the report as pdf (default: False)
      -i [OUTPUT_FOLDER]   path to the simulation result json file
                           'json_with_results.json'
      -o [REPORT_PATH]     path to save the pdf report


    :return: parser
    """
    parser = argparse.ArgumentParser(
        prog="python mvs_report.py",
        description="Display the report of a MVS simulation",
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
        dest=SIM_OUTPUT_PATH,
        nargs="?",
        type=str,
        help="path to the simulation result json file 'json_with_results.json'",
        default=os.path.join(REPO_PATH, OUTPUT_FOLDER, JSON_WITH_RESULTS),
    )
    parser.add_argument(
        "-o",
        dest=ARG_REPORT_PATH,
        nargs="?",
        type=str,
        help="path to save the pdf report",
        default=os.path.join(REPORT_PATH, PDF_REPORT),
    )
    return parser


if __name__ == "__main__":

    # Parse the arguments from the command line
    parser = report_arg_parser()
    args = vars(parser.parse_args())
    print(args)
    bool_print_report = args.get(ARG_PDF)
    report_path = args.get(ARG_REPORT_PATH)
    fname = args.get(SIM_OUTPUT_PATH)

    if os.path.exists(fname) is False:
        raise FileNotFoundError(
            "{} not found. You need to run a simulation to generate the data to report"
            "see `python mvs_tool.py -h` for help"
        )
    else:
        # load the results of a simulation
        dict_values = load_json(fname)
        test_app = create_app(dict_values)
        banner = "*" * 40
        print(banner + "\nPress ctrl+c to stop the report server\n" + banner)
        if bool_print_report is True:
            print_pdf(test_app, path_pdf_report=report_path)
        else:
            # run the dash server for 600s before shutting it down
            open_in_browser(test_app, timeout=600)
            print(
                banner
                + "\nThe report server has timed out.\nTo start it again run `python "
                "mvs_report.py`.\nTo let it run for a longer time, change timeout setting in "
                "the mvs_report.py file\n" + banner
            )
