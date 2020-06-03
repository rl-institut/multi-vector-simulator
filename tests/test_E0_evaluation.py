import logging
import os
import pickle
import shutil

import mock
import pandas as pd

import src.A0_initialization as initializing
import src.B0_data_input_json as data_input
import src.C0_data_processing as data_processing
import src.D0_modelling_and_optimization as modelling
import src.E0_evaluation as evaluation
from src.constants_json_strings import KPI, KPI_SCALARS
from .constants import (
    TEST_REPO_PATH,
    INPUT_FOLDER,
    PATH_INPUT_FILE,
    PATH_INPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
)

PARSER = initializing.create_parser()
TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER)
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "MVS_outputs")

DICT_BEFORE = os.path.join(TEST_REPO_PATH, "dict_values_before_E0.pickle")

DICT_AFTER = os.path.join(TEST_REPO_PATH, "dict_values_after_E0.pickle")


@mock.patch(
    "argparse.ArgumentParser.parse_args",
    return_value=PARSER.parse_args(["-i", TEST_INPUT_PATH, "-o", TEST_OUTPUT_PATH]),
)
def setup_module(m_args):
    """Run the simulation up to module E0 and save dict_values before and after evaluation"""
    if os.path.exists(TEST_OUTPUT_PATH):
        shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
    user_input = initializing.process_user_arguments()

    logging.debug("Accessing script: B0_data_input_json")
    dict_values = data_input.load_json(
        user_input[PATH_INPUT_FILE],
        path_input_folder=user_input[PATH_INPUT_FOLDER],
        path_output_folder=user_input[PATH_OUTPUT_FOLDER],
        move_copy=False,
    )
    logging.debug("Accessing script: C0_data_processing")
    data_processing.all(dict_values)

    logging.debug("Accessing script: D0_modelling_and_optimization")
    results_meta, results_main = modelling.run_oemof(dict_values)

    with open(DICT_BEFORE, "wb") as handle:
        pickle.dump(dict_values, handle, protocol=pickle.HIGHEST_PROTOCOL)

    logging.debug("Accessing script: E0_evaluation")
    evaluation.evaluate_dict(dict_values, results_main, results_meta)

    with open(DICT_AFTER, "wb") as handle:
        pickle.dump(dict_values, handle, protocol=pickle.HIGHEST_PROTOCOL)


def test_evaluate_dict_append_new_fields():
    with open(DICT_BEFORE, "rb") as handle:
        dict_values_before = pickle.load(handle)

    with open(DICT_AFTER, "rb") as handle:
        dict_values_after = pickle.load(handle)

    for k in (KPI, "optimizedFlows"):
        assert k not in dict_values_before
        assert k in dict_values_after


def test_evaluate_dict_important_fields_in_output_dict():

    with open(DICT_AFTER, "rb") as handle:
        dict_values_after = pickle.load(handle)

    for k in ("scalar_matrix", "cost_matrix"):
        assert k in dict_values_after[KPI]


def test_evaluate_dict_fields_values_in_output_dict_are_dataframes():

    with open(DICT_AFTER, "rb") as handle:
        dict_values_after = pickle.load(handle)

    for k in ("scalar_matrix", "cost_matrix"):
        assert isinstance(dict_values_after[KPI][k], pd.DataFrame)


def test_evaluate_check_dict_fields_in_output_dict_under_kpi_scalar_fields():

    with open(DICT_AFTER, "rb") as handle:
        dict_values_after = pickle.load(handle)

    for k in KPI_SCALARS:
        assert k in dict_values_after[KPI]["scalars"]

    # for k in dict_values_after[KPI]["scalars"]:
    #    assert k in KPI_SCALARS


def teardown_module():
    # Remove the output folder
    if os.path.exists(TEST_OUTPUT_PATH):
        shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
    # Remove the pickle files
    for d in (DICT_BEFORE, DICT_AFTER):
        if os.path.exists(d):
            os.remove(d)
