import os
import argparse

from multi_vector_simulator.utils.constants import (
    REPO_PATH,
    REPORT_FOLDER,
    OUTPUT_FOLDER,
    PDF_REPORT,
    JSON_WITH_RESULTS,
)
from multi_vector_simulator.B0_data_input_json import load_json
from multi_vector_simulator.F2_autoreport import create_app, open_in_browser, print_pdf

ARG_PDF = "print_report"
ARG_REPORT_PATH = "report_path"
PATH_SIM_OUTPUT = "output_folder"




if __name__ == "__main__":

    # Parse the arguments from the command line
    parser = report_arg_parser()
    args = vars(parser.parse_args())
    print(args)
    bool_print_report = args.get(ARG_PDF)
    report_path = args.get(ARG_REPORT_PATH)
    fname = args.get(PATH_SIM_OUTPUT)

    # if the user only provided the path to the folder, we complete with default json file
    if os.path.isdir(fname) is True:
        fname = os.path.join(fname, JSON_WITH_RESULTS)

    if os.path.exists(fname) is False:
        raise FileNotFoundError(
            "{} not found. You need to run a simulation to generate the data to report"
            "see `python mvs_tool.py -h` for help".format(fname)
        )
    else:
        # path to the mvs simulation output files
        path_sim_output = os.path.dirname(fname)

        # if report path is not specified it will be included in the mvs simulation outputs folder
        if report_path == "":
            report_path = os.path.join(path_sim_output, REPORT_FOLDER)

        # load the results of a simulation
        dict_values = load_json(fname)
        test_app = create_app(dict_values, path_sim_output=path_sim_output)
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
