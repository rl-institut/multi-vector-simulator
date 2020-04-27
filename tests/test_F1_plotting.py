import os
import shutil
import mock
import pandas as pd
import logging

import mvs_eland_tool.mvs_eland_tool as mvs_eland_tool
import src.A0_initialization as initializing

import src.F1_plotting as F1
from tests.constants import (
    TEST_REPO_PATH,
    DUMMY_CSV_PATH,
    INPUT_FOLDER,
    CSV_ELEMENTS,
    CSV_FNAME,
)

SECTOR = "Electricity"
INTERVAL = 2

OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "test_outputs")

PARSER = initializing.create_parser()
TEST_INPUT_PATH_NX_TRUE = os.path.join(TEST_REPO_PATH, "inputs_F1_plot_nx_true")
TEST_JSON_PATH_NX_TRUE = os.path.join(TEST_INPUT_PATH_NX_TRUE, CSV_ELEMENTS, CSV_FNAME)

TEST_INPUT_PATH_NX_FALSE = os.path.join(TEST_REPO_PATH, "inputs_F1_plot_nx_false")
TEST_JSON_PATH_NX_FALSE = os.path.join(
    TEST_INPUT_PATH_NX_FALSE, CSV_ELEMENTS, CSV_FNAME
)

TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "F1_outputs")

# Data for test_if_plot_of_all_energy_flows_for_all_sectors_are_stored_for_14_days
USER_INPUT = {"path_output_folder": OUTPUT_PATH}
PROJECT_DATA = {"project_name": "a_project", "scenario_name": "a_scenario"}

RESULTS_TIMESERIES = pd.read_csv(
    os.path.join(DUMMY_CSV_PATH, "plot_data_for_F1.csv"),
    sep=";",
    header=0,
    index_col=0,
)

# data for test_store_barchart_for_capacities
DICT_KPI = {
    "kpi": {
        "scalar_matrix": pd.DataFrame(
            {"label": ["asset_a", "asset_b"], "optimizedAddCap": [1, 2]}
        )
    },
}


class TestNetworkx:
    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            ["-i", TEST_INPUT_PATH_NX_TRUE, "-o", TEST_OUTPUT_PATH, "-ext", "csv", "-f"]
        ),
    )

    def test_if_networkx_graph_is_stored_save_plot_true(self, m_args):
        mvs_eland_tool.main()
        assert (
            os.path.exists(os.path.join(TEST_OUTPUT_PATH, "network_graph.png")) is True
        )

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            [
                "-i",
                TEST_INPUT_PATH_NX_FALSE,
                "-o",
                TEST_OUTPUT_PATH,
                "-ext",
                "csv",
                "-f",
            ]
        ),
    )

    def test_if_networkx_graph_is_stored_save_plot_false(self, m_args):
        mvs_eland_tool.main()
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
        F1.flows(USER_INPUT, PROJECT_DATA, RESULTS_TIMESERIES, SECTOR, INTERVAL)
        assert (
            os.path.exists(
                os.path.join(
                    OUTPUT_PATH, SECTOR + "_flows_" + str(INTERVAL) + "_days.png"
                )
            )
            is True
        )

    def test_if_pie_charts_of_costs_is_stored(self):
        costs = pd.DataFrame({"cost1": 0.2, "cost2": 0.8}, index=[0, 1])
        label = "a_label"
        title = "a_title"
        F1.plot_a_piechart(USER_INPUT, "filename", costs, label, title)
        assert os.path.exists(os.path.join(OUTPUT_PATH, "filename.png")) is True

    def test_determine_if_plotting_necessary_True(self):
        PARAMETER_VALUES = [2, 3, 0]
        process_pie_chart = F1.determine_if_plotting_necessary(PARAMETER_VALUES)
        assert process_pie_chart == True

    def test_determine_if_plotting_necessary_False(self):
        PARAMETER_VALUES = [0, 0, 0]
        process_pie_chart = F1.determine_if_plotting_necessary(PARAMETER_VALUES)
        assert process_pie_chart == False

    def test_recalculate_distribution_of_rest_costs_no_major(self):
        COSTS_PERC = pd.Series(
            {"asset3": 0.1, "asset4": 0.196, "asset5": 0.004, "DSO_consumption": 0.7}
        )
        (
            plot_minor_costs_pie,
            costs_perc_grouped_minor,
            rest,
        ) = F1.recalculate_distribution_of_rest_costs(COSTS_PERC)
        assert plot_minor_costs_pie == False

    def test_recalculate_distribution_of_rest_costs_with_major(self):
        COSTS_PERC = pd.Series(
            {"asset3": 0.05, "asset4": 0.046, "others": 0.004, "DSO_consumption": 0.9}
        )

        (
            plot_minor_costs_pie,
            costs_perc_grouped_minor,
            rest,
        ) = F1.recalculate_distribution_of_rest_costs(COSTS_PERC)
        assert plot_minor_costs_pie == True
        assert abs(costs_perc_grouped_minor["asset3"] - 0.5) < 0.001
        assert abs(costs_perc_grouped_minor["asset4"] - 0.46) < 0.001
        assert abs(costs_perc_grouped_minor["others"] - 0.04) < 0.001
        assert rest == 0.1

    def test_group_costs_for_pie_charts(self):
        COSTS = pd.Series(
            {
                "asset1": 0,
                "asset2": 0,
                "asset3": 100,
                "asset4": 196,
                "asset5": 4,
                "DSO_consumption": 700,
            }
        )

        costs_perc_grouped, total = F1.group_costs(COSTS, COSTS.index)

        exp = {"asset3": 0.1, "asset4": 0.196, "others": 0.004, "DSO_consumption": 0.7}

        assert total == 1000
        assert "asset1" not in costs_perc_grouped
        assert "asset2" not in costs_perc_grouped
        assert "asset3" in costs_perc_grouped
        assert "asset4" in costs_perc_grouped
        assert "asset5" not in costs_perc_grouped
        assert "DSO_consumption" in costs_perc_grouped
        assert "others" in costs_perc_grouped
        assert costs_perc_grouped == exp

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

    def teardown_class(self):
        """ """
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
