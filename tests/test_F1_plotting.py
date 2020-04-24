import os
import shutil
import mock
import pandas as pd
import logging

import src.A0_initialization as initializing
import src.B0_data_input_json as data_input
import src.C0_data_processing as data_processing
import src.D0_modelling_and_optimization as modelling

import src.F1_plotting as F1
from tests.constants import TEST_REPO_PATH, DUMMY_CSV_PATH, INPUT_FOLDER

SECTOR = "Electricity"
INTERVAL = 2

OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "test_outputs")

PARSER = initializing.create_parser()
TEST_INPUT_PATH_NX_TRUE = os.path.join(TEST_REPO_PATH, "inputs_F1_plot_nx_true")
TEST_INPUT_PATH_NX_FALSE  = os.path.join(TEST_REPO_PATH, "inputs_F1_plot_nx_true")
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "F1_outputs")

# Data for test_if_plot_of_all_energy_flows_for_all_sectors_are_stored_for_14_days
USER_INPUT = {"path_output_folder": OUTPUT_PATH}
PROJECT_DATA = {"project_name": "a_project",
                "scenario_name": "a_scenario"}

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
            {"label": ["asset_a", "asset_b"],
             "optimizedAddCap": [1, 2]}
        )
    },
}


class TestNetworkx:
    def test_if_networkx_graph_is_stored_save_plot_true(self):
        @mock.patch(
            "argparse.ArgumentParser.parse_args",
            return_value=PARSER.parse_args(["-i", TEST_INPUT_PATH_NX_TRUE, "-o", TEST_OUTPUT_PATH, "-ext", "csv"]),
        )
        def setup_module(m_args):
            """Run the simulation up to module E0 and save dict_values before and after evaluation"""
            if os.path.exists(TEST_OUTPUT_PATH):
                shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
            user_input = initializing.process_user_arguments()

            logging.debug("Accessing script: B0_data_input_json")
            dict_values = data_input.load_json(
                user_input["path_input_file"],
                path_input_folder=user_input["path_input_folder"],
                path_output_folder=user_input["path_output_folder"],
                move_copy=False,
            )
            logging.debug("Accessing script: C0_data_processing")
            data_processing.all(dict_values)

            logging.debug("Accessing script: D0_modelling_and_optimization")
            results_meta, results_main = modelling.run_oemof(dict_values)

        assert (
                os.path.exists(
                    os.path.join(OUTPUT_PATH, "network_graph.png")
                )
                is True
        )

    def test_if_networkx_graph_is_stored_save_plot_false(self):
        @mock.patch(
            "argparse.ArgumentParser.parse_args",
            return_value=PARSER.parse_args(["-i", TEST_INPUT_PATH_NX_FALSE, "-o", TEST_OUTPUT_PATH, "-ext", "csv"]),
        )
        def setup_module(m_args):
            """Run the simulation up to module E0 and save dict_values before and after evaluation"""
            if os.path.exists(TEST_OUTPUT_PATH):
                shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
            user_input = initializing.process_user_arguments()

            logging.debug("Accessing script: B0_data_input_json")
            dict_values = data_input.load_json(
                user_input["path_input_file"],
                path_input_folder=user_input["path_input_folder"],
                path_output_folder=user_input["path_output_folder"],
                move_copy=False,
            )
            logging.debug("Accessing script: C0_data_processing")
            data_processing.all(dict_values)

            logging.debug("Accessing script: D0_modelling_and_optimization")
            results_meta, results_main = modelling.run_oemof(dict_values)

        assert (
                os.path.exists(
                    os.path.join(OUTPUT_PATH, "network_graph.png")
                )
                is False
        )

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

    def teardown_class(self):
        """ """
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
