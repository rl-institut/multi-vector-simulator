import os
import shutil
import pandas as pd

import src.F1_plotting as F1
from tests.constants import TEST_REPO_PATH, DUMMY_CSV_PATH

SECTOR = "Electricity"
INTERVAL = 2

OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "test_outputs")

USER_INPUT = {"path_output_folder": OUTPUT_PATH}
PROJECT_DATA = {"project_name": "a_project",
                "scenario_name": "a_scenario"}

RESULTS_TIMESERIES = pd.read_csv(
            os.path.join(DUMMY_CSV_PATH, "plot_data_for_F1.csv"),
            sep=";",
            header=0,
            index_col=0,
        )

DICT_KPI = {
    "kpi": {
        "scalar_matrix": pd.DataFrame(
            {"label": ["asset_a", "asset_b"],
             "optimizedAddCap": [1, 2]}
        )
    },
}

class TestFileCreation:

    def setup_class(self):
        """ """
        shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
        os.mkdir(OUTPUT_PATH)

    def test_if_plot_of_all_energy_flows_for_all_sectors_are_stored_for_14_days(self):
        F1.flows(USER_INPUT, PROJECT_DATA, RESULTS_TIMESERIES, SECTOR, INTERVAL)
        assert (
                os.path.exists(
                    os.path.join(OUTPUT_PATH, SECTOR + "_flows_" + str(INTERVAL) + "_days.png")
                )
                is True
        )

    def test_if_bar_charts_of_costs_are_stored(self):
        assert 0 == 0

    def test_store_barchart_for_capacities(self):
        """ """
        F1.capacities(
            USER_INPUT,
            PROJECT_DATA,
            DICT_KPI["kpi"]["scalar_matrix"]["label"],
            DICT_KPI["kpi"]["scalar_matrix"]["optimizedAddCap"],
        )

        assert (
                os.path.exists(
                    os.path.join(OUTPUT_PATH, "optimal_additional_capacities.png")
                )
                is True
        )

    def test_if_networkx_graph_is_stored(self):
        assert 0 == 0

    def teardown_class(self):
        """ """
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)