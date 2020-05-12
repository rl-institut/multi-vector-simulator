import pickle
import os
import shutil
import logging
import mock
import pandas as pd

import src.A0_initialization as initializing
import src.B0_data_input_json as data_input
import src.C0_data_processing as data_processing
import src.D0_modelling_and_optimization as modelling
import src.E0_evaluation as evaluation
import src.E2_economics as E2

from tests.constants import TEST_REPO_PATH, INPUT_FOLDER
import tests.inputs.csv_elements as inp

PARSER = initializing.create_parser()
TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER)
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "MVS_outputs")

DICT_ASSET_BEFORE = os.path.join(TEST_REPO_PATH, "dict_values_before_E2.pickle")

DICT_ASSET_AFTER = os.path.join(TEST_REPO_PATH, "dict_values_after_E2.pickle")

@mock.patch(
    "argparse.ArgumentParser.parse_args",
    return_value=PARSER.parse_args(["-i", TEST_INPUT_PATH, "-o", TEST_OUTPUT_PATH]),
)
def setup_module(m_args):
    """Run the simulation up to module E2 and save dict_asset before and after economics"""
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
    dict_asset = dict_values["energyProviders"][dso]
    data_processing.define_missing_cost_data(dict_values, dict_asset)
    data_processing.define_dso_sinks_and_sources(dict_values, dso)
    data_processing.evaluate_lifetime_costs(inp.settings, inp.economic_data, dict_asset)


    logging.debug("Accessing script: D0_modelling_and_optimization")
    results_meta, results_main = modelling.run_oemof(dict_values)

    logging.debug("Accessing script: E0_evaluation")
    evaluation.evaluate_dict(dict_values, results_main, results_meta)
    evaluation.store_result_matrix(dict_kpi, dict_asset)

    with open(DICT_ASSET_BEFORE, "wb") as handle:
        pickle.dump(dict_asset, handle, protocol=pickle.HIGHEST_PROTOCOL)

    #print(dict_asset)

    logging.debug("Accessing script: E2_economics")
    E2.get_costs(dict_asset, inp.economic_data)

    with open(DICT_ASSET_AFTER, "wb") as handle:
        pickle.dump(dict_asset, handle, protocol=pickle.HIGHEST_PROTOCOL)


def test_get_costs():
    with open(DICT_ASSET_BEFORE, "rb") as handle:
        dict_asset_before = pickle.load(handle)

    with open(DICT_ASSET_AFTER, "rb") as handle:
        dict_asset_after = pickle.load(handle)



def teardown_module():
    # Remove the output folder
    if os.path.exists(TEST_OUTPUT_PATH):
        shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
    # Remove the pickle files
    for d in (DICT_ASSET_BEFORE, DICT_ASSET_AFTER):
        if os.path.exists(d):
            os.remove(d)



"""
def test_add_costs_and_total(self):
    """"""
    Total_Costs = E2.add_costs_and_total(Dict_2, "cost", cost, total_costs)
    self.assertEqual(Total_Costs, cost + total_costs)

def test_all_list_in_dict(self):
    """"""
    self.assertEqual(E2.all_list_in_dict(Dict_3, list_test_true), True)
    self.assertEqual(E2.all_list_in_dict(Dict_3, list_test_false), False)

###

