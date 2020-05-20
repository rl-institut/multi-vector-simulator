import logging
import os

from src.constants import REPO_PATH, OUTPUT_FOLDER
from src.B0_data_input_json import load_json
from src.F2_autoreport import create_app, open_in_browser

if __name__ == "__main__":
    fname = os.path.join(REPO_PATH, OUTPUT_FOLDER, "json_with_results.json")

    if os.path.exists(fname) is False:
        raise FileNotFoundError(
            "{} not found. You need to run a simulation to generate the data to report"
            "see `python mvs_tool.py -h` for help"
        )
    else:
        # load the results of a simulation
        dict_values = load_json(fname)
        test_app = create_app(dict_values)
        # run the dash server for 600s before shutting it down
        open_in_browser(test_app, timeout=600)
