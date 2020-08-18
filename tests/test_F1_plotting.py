import os
import shutil
import copy

import mock
import pandas as pd
import pytest

import src.A0_initialization as initializing
import src.F1_plotting as F1
from mvs_eland_tool import main
from src.constants import (
    PLOTS_BUSSES,
    PATHS_TO_PLOTS,
    PLOTS_DEMANDS,
    PLOTS_RESOURCES,
    PLOTS_NX,
    PLOTS_PERFORMANCE,
    PLOTS_COSTS,
    CSV_EXT,
)
from src.constants_json_strings import (
    LABEL,
    OPTIMIZED_ADD_CAP,
    PROJECT_NAME,
    SCENARIO_NAME,
    KPI,
    KPI_SCALAR_MATRIX,
    SIMULATION_SETTINGS,
)

from .constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    TEST_REPO_PATH,
    PATH_OUTPUT_FOLDER,
    TEST_INPUT_DIRECTORY,
    DUMMY_CSV_PATH,
    CSV_ELEMENTS,
    CSV_FNAME,
    DICT_PLOTS,
)

dict_values = {
    PATHS_TO_PLOTS: {
        PLOTS_BUSSES: [],
        PLOTS_DEMANDS: [],
        PLOTS_RESOURCES: [],
        PLOTS_NX: [],
        PLOTS_PERFORMANCE: [],
        PLOTS_COSTS: [],
    }
}

SECTOR = "Electricity"
INTERVAL = 2

OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "test_outputs")

PARSER = initializing.create_parser()
TEST_INPUT_PATH_NX_TRUE = os.path.join(
    TEST_REPO_PATH, TEST_INPUT_DIRECTORY, "inputs_F1_plot_nx_true"
)
TEST_JSON_PATH_NX_TRUE = os.path.join(TEST_INPUT_PATH_NX_TRUE, CSV_ELEMENTS, CSV_FNAME)

TEST_INPUT_PATH_NX_FALSE = os.path.join(
    TEST_REPO_PATH, TEST_INPUT_DIRECTORY, "inputs_F1_plot_nx_false"
)
TEST_JSON_PATH_NX_FALSE = os.path.join(
    TEST_INPUT_PATH_NX_FALSE, CSV_ELEMENTS, CSV_FNAME
)

TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "F1_outputs")

# Data for test_if_plot_of_all_energy_flows_for_all_sectors_are_stored_for_14_days
USER_INPUT = {PATH_OUTPUT_FOLDER: OUTPUT_PATH}
PROJECT_DATA = {PROJECT_NAME: "a_project", SCENARIO_NAME: "a_scenario"}

RESULTS_TIMESERIES = pd.read_csv(
    os.path.join(DUMMY_CSV_PATH, "plot_data_for_F1.csv"),
    sep=";",
    header=0,
    index_col=0,
)

# data for test_store_barchart_for_capacities
DICT_KPI = {
    KPI: {
        KPI_SCALAR_MATRIX: pd.DataFrame(
            {LABEL: ["asset_a", "asset_b"], OPTIMIZED_ADD_CAP: [1, 2]}
        )
    },
}


class TestNetworkx:
    def setup_class(self):
        """ """
        shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)

    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            [
                "-f",
                "-log",
                "warning",
                "-i",
                TEST_INPUT_PATH_NX_TRUE,
                "-o",
                TEST_OUTPUT_PATH,
                "-ext",
                CSV_EXT,
            ]
        ),
    )
    def test_if_networkx_graph_is_stored_save_plot_true(self, m_args):
        main(overwrite=True, display_output="warning")
        assert (
            os.path.exists(os.path.join(TEST_OUTPUT_PATH, "network_graph.png")) is True
        )

    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            [
                "-f",
                "-log",
                "warning",
                "-i",
                TEST_INPUT_PATH_NX_FALSE,
                "-o",
                TEST_OUTPUT_PATH,
                "-ext",
                CSV_EXT,
            ]
        ),
    )
    def test_if_networkx_graph_is_stored_save_plot_false(self, m_args):
        main(overwrite=True, display_output="warning")
        assert (
            os.path.exists(os.path.join(TEST_OUTPUT_PATH, "network_graph.png")) is False
        )

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)


class TestFileCreation:
    def setup_class(self):
        """ """
        shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
        os.mkdir(OUTPUT_PATH)

    def test_if_plot_of_all_energy_flows_for_all_sectors_are_stored_for_14_days(self):
        pass
        # F1.flows(
        #     dict_values, USER_INPUT, PROJECT_DATA, RESULTS_TIMESERIES, SECTOR, INTERVAL
        # )
        # assert (
        #     os.path.exists(
        #         os.path.join(
        #             OUTPUT_PATH, SECTOR + "_flows_" + str(INTERVAL) + "_days.png"
        #         )
        #     )
        #     is True
        # )

    def test_if_pie_charts_of_costs_is_stored(self):
        F1.create_plotly_piechart_fig(
            title_of_plot="a_title",
            names=["costs1", "costs2"],
            values=[0.2, 0.8],
            file_name="filename.png",
            file_path=OUTPUT_PATH,
        )
        assert os.path.exists(os.path.join(OUTPUT_PATH, "filename.png")) is True

    def teardown_class(self):
        """ """
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
