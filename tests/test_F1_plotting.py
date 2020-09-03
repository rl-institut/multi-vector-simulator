import os
import shutil

import mock
import pandas as pd
import pytest

import mvs_eland.A0_initialization as initializing
import mvs_eland.F1_plotting as F1
from mvs_eland.cli import main
from mvs_eland.utils.constants import (
    PLOTS_BUSSES,
    PATHS_TO_PLOTS,
    PLOTS_DEMANDS,
    PLOTS_RESOURCES,
    PLOTS_ES,
    PLOTS_PERFORMANCE,
    PLOTS_COSTS,
    CSV_EXT,
)
from mvs_eland.utils.constants_json_strings import (
    LABEL,
    OPTIMIZED_ADD_CAP,
    PROJECT_NAME,
    SCENARIO_NAME,
    KPI,
    KPI_SCALAR_MATRIX,
)

from _constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    TEST_REPO_PATH,
    PATH_OUTPUT_FOLDER,
    TEST_INPUT_DIRECTORY,
    DUMMY_CSV_PATH,
    ES_GRAPH,
)

dict_values = {
    PATHS_TO_PLOTS: {
        PLOTS_BUSSES: [],
        PLOTS_DEMANDS: [],
        PLOTS_RESOURCES: [],
        PLOTS_ES: [],
        PLOTS_PERFORMANCE: [],
        PLOTS_COSTS: [],
    }
}

SECTOR = "Electricity"
INTERVAL = 2

OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "test_outputs")

PARSER = initializing.create_parser()

TEST_INPUT_PATH = os.path.join(
    TEST_REPO_PATH, TEST_INPUT_DIRECTORY, "inputs_F1_plot_es_graph"
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
                TEST_INPUT_PATH,
                "-o",
                TEST_OUTPUT_PATH,
                "-ext",
                CSV_EXT,
                "-png",
            ]
        ),
    )
    def test_if_energy_system_network_graph_is_stored_if_png_option(self, m_args):
        main(overwrite=True, display_output="warning")
        assert os.path.exists(os.path.join(TEST_OUTPUT_PATH, ES_GRAPH)) is True

    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER) or True,
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
                TEST_INPUT_PATH,
                "-o",
                TEST_OUTPUT_PATH,
                "-ext",
                CSV_EXT,
                "-pdf",
            ]
        ),
    )
    def test_if_energy_system_network_graph_is_stored_if_pdf_option(self, m_args):
        main(overwrite=True, display_output="warning")
        assert os.path.exists(os.path.join(TEST_OUTPUT_PATH, ES_GRAPH)) is True

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
                TEST_INPUT_PATH,
                "-o",
                TEST_OUTPUT_PATH,
                "-ext",
                CSV_EXT,
            ]
        ),
    )
    def test_if_energy_system_network_graph_is_stored_if_no_pdf_nor_png_option(
        self, m_args
    ):
        main(overwrite=True, display_output="warning")
        assert os.path.exists(os.path.join(TEST_OUTPUT_PATH, ES_GRAPH)) is False

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

    @pytest.mark.skipif(
        F1.PLOTLY_INSTALLED is False,
        reason="Test deactivated because plotly package is not installed",
    )
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


def test_get_color_is_cyclic():
    colors = [1, 2, 3]
    assert F1.get_color(3, colors) == colors[0]


def test_fixed_width_text_smaller_than_limit_returns_text():
    txt = "12345"
    assert txt == F1.fixed_width_text(txt, char_num=10)


def test_fixed_width_text_smaller_than_limit_returns_text():
    txt = "12345"
    assert F1.fixed_width_text(txt, char_num=2) == "12\n34\n5"
