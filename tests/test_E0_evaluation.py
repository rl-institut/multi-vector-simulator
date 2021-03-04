import logging
import os
import pickle
import shutil

import mock
import pandas as pd
import numpy as np

import multi_vector_simulator.A0_initialization as A0
import multi_vector_simulator.B0_data_input_json as B0
import multi_vector_simulator.C0_data_processing as C0
import multi_vector_simulator.D0_modelling_and_optimization as D0
import multi_vector_simulator.E0_evaluation as E0

from multi_vector_simulator.utils.constants import OUTPUT_FOLDER

from multi_vector_simulator.utils.constants_json_strings import *

from _constants import (
    TEST_REPO_PATH,
    INPUT_FOLDER,
    PATH_INPUT_FILE,
    PATH_INPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
)

PARSER = A0.mvs_arg_parser()
TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER)
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, OUTPUT_FOLDER)

DICT_BEFORE = os.path.join(TEST_REPO_PATH, "dict_values_before_E0.pickle")

DICT_AFTER = os.path.join(TEST_REPO_PATH, "dict_values_after_E0.pickle")


@mock.patch(
    "argparse.ArgumentParser.parse_args",
    return_value=PARSER.parse_args(
        ["-f", "-log", "warning", "-i", TEST_INPUT_PATH, "-o", TEST_OUTPUT_PATH]
    ),
)
def setup_module(m_args):
    """Run the simulation up to module E0 and save dict_values before and after evaluation"""
    if os.path.exists(TEST_OUTPUT_PATH):
        shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
    user_input = A0.process_user_arguments()

    logging.debug("Accessing script: B0_data_input_json")
    dict_values = B0.load_json(
        user_input[PATH_INPUT_FILE],
        path_input_folder=user_input[PATH_INPUT_FOLDER],
        path_output_folder=user_input[PATH_OUTPUT_FOLDER],
        move_copy=False,
    )
    logging.debug("Accessing script: C0_data_processing")
    C0.all(dict_values)

    logging.debug("Accessing script: D0_modelling_and_optimization")
    results_meta, results_main = D0.run_oemof(dict_values)

    with open(DICT_BEFORE, "wb") as handle:
        pickle.dump(dict_values, handle, protocol=pickle.HIGHEST_PROTOCOL)

    logging.debug("Accessing script: E0_evaluation")
    E0.evaluate_dict(dict_values, results_main, results_meta)

    with open(DICT_AFTER, "wb") as handle:
        pickle.dump(dict_values, handle, protocol=pickle.HIGHEST_PROTOCOL)


def test_store_result_matrix():
    dict_kpi = {
        KPI_COST_MATRIX: pd.DataFrame(columns=["A", "B", "C"]),
        KPI_SCALAR_MATRIX: pd.DataFrame(columns=["D", "E", "F", "G"]),
    }
    dict_asset = {
        "A": 3.551111,
        "B": "str",
        "D": None,
        "E": {VALUE: 2},
        "F": False,
        "G": {VALUE: None},  # Returns empty cell
        "H": 1,
    }

    E0.store_result_matrix(dict_kpi, dict_asset)
    assert len(dict_kpi[KPI_COST_MATRIX]) == 1
    assert len(dict_kpi[KPI_SCALAR_MATRIX]) == 1
    assert dict_kpi[KPI_COST_MATRIX]["A"][0] == 3.55111
    assert dict_kpi[KPI_COST_MATRIX]["B"][0] == "str"
    assert dict_kpi[KPI_SCALAR_MATRIX]["D"][0] is None
    assert dict_kpi[KPI_SCALAR_MATRIX]["E"][0] == 2
    assert dict_kpi[KPI_SCALAR_MATRIX]["F"][0] is False


def test_evaluate_dict_append_new_fields():
    with open(DICT_BEFORE, "rb") as handle:
        dict_values_before = pickle.load(handle)

    with open(DICT_AFTER, "rb") as handle:
        dict_values_after = pickle.load(handle)

    for k in (KPI, OPTIMIZED_FLOWS):
        assert k not in dict_values_before
        assert k in dict_values_after


def test_evaluate_dict_important_fields_in_output_dict():

    with open(DICT_AFTER, "rb") as handle:
        dict_values_after = pickle.load(handle)

    for k in (KPI_SCALAR_MATRIX, KPI_COST_MATRIX):
        assert k in dict_values_after[KPI]


def test_evaluate_dict_fields_values_in_output_dict_are_dataframes():

    with open(DICT_AFTER, "rb") as handle:
        dict_values_after = pickle.load(handle)

    for k in (KPI_SCALAR_MATRIX, KPI_COST_MATRIX):
        assert isinstance(dict_values_after[KPI][k], pd.DataFrame)


def test_evaluate_check_dict_fields_in_output_dict_under_kpi_scalar_fields():

    with open(DICT_AFTER, "rb") as handle:
        dict_values_after = pickle.load(handle)

    for k in KPI_SCALARS:
        assert k in dict_values_after[KPI][KPI_SCALARS_DICT]

    # for k in dict_values_after[KPI][KPI_SCALARS_DICT]:
    #    assert k in KPI_SCALARS


def test_process_fixcost():
    economic_data = {
        PROJECT_DURATION: {VALUE: 20},
        ANNUITY_FACTOR: {VALUE: 1},
        CRF: {VALUE: 1},
        DISCOUNTFACTOR: {VALUE: 0},
        TAX: {VALUE: 0},
        CURR: CURR,
    }
    fix_cost_entry = "one entry"
    dict_test = {
        ECONOMIC_DATA: economic_data,
        SIMULATION_SETTINGS: {EVALUATED_PERIOD: {VALUE: 365, UNIT: "Days"}},
        FIX_COST: {
            fix_cost_entry: {
                LABEL: fix_cost_entry,
                SPECIFIC_COSTS_OM: {VALUE: 1, UNIT: CURR},
                SPECIFIC_COSTS: {VALUE: 1, UNIT: CURR},
                DEVELOPMENT_COSTS: {VALUE: 1, UNIT: CURR},
                LIFETIME: {VALUE: 20},
                AGE_INSTALLED: {VALUE: 0},
                LIFETIME_SPECIFIC_COST: {VALUE: 1, UNIT: CURR},
                LIFETIME_SPECIFIC_COST_OM: {VALUE: 1, UNIT: CURR},
                ANNUITY_SPECIFIC_INVESTMENT_AND_OM: {VALUE: 1, UNIT: CURR},
                SIMULATION_ANNUITY: {VALUE: 1, UNIT: CURR},
                SPECIFIC_REPLACEMENT_COSTS_INSTALLED: {VALUE: 1, UNIT: CURR},
                SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED: {VALUE: 1, UNIT: CURR},
            }
        },
    }
    E0.initalize_kpi(dict_test)
    E0.process_fixcost(dict_test)
    assert (
        fix_cost_entry in dict_test[KPI][KPI_COST_MATRIX][LABEL].values
    ), f"The fix cost entry `{fix_cost_entry}` is not added to the cost matrix ({KPI_COST_MATRIX})."
    for k in [
        COST_TOTAL,
        COST_OPERATIONAL_TOTAL,
        COST_INVESTMENT,
        COST_UPFRONT,
        COST_REPLACEMENT,
        COST_OM,
        ANNUITY_TOTAL,
        ANNUITY_OM,
    ]:
        assert isinstance(dict_test[KPI][KPI_COST_MATRIX][k][0], float) or isinstance(
            dict_test[KPI][KPI_COST_MATRIX][k][0], int
        ), f"A float or int should be added for fix cost entry `{fix_cost_entry}` and its KPI `{k}`."
    for k in [
        COST_DISPATCH,
        LCOE_ASSET,
    ]:
        assert np.isnan(
            dict_test[KPI][KPI_COST_MATRIX][k][0]
        ), f"No value should be added for fix cost entry `{fix_cost_entry}` and KPI `{k}`, but value {dict_test[KPI][KPI_COST_MATRIX][k][fix_cost_entry]} is attributed."

    assert (
        fix_cost_entry not in dict_test[KPI][KPI_SCALAR_MATRIX][LABEL].values
    ), f"No line should be added for the fix cost entry `{fix_cost_entry}` to the scalar matrix ({KPI_SCALAR_MATRIX})."


def teardown_module():
    # Remove the output folder
    if os.path.exists(TEST_OUTPUT_PATH):
        shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
    # Remove the pickle files
    for d in (DICT_BEFORE, DICT_AFTER):
        if os.path.exists(d):
            os.remove(d)


"""
from oemof import solph
energysystem = solph.EnergySystem()
energysystem.restore(dpath=None, filename=None)

# define an alias for shorter calls below (optional)
results = energysystem.results["main"]
storage = energysystem.groups["storage"]
"""
