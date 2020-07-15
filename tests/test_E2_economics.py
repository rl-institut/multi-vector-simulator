import logging
import os
import pickle
import shutil

import mock

import src.A0_initialization as initializing
import src.B0_data_input_json as data_input
import src.C0_data_processing as data_processing
import src.D0_modelling_and_optimization as modelling
import src.E0_evaluation as evaluation
import src.E2_economics as E2

from src.constants_json_strings import (
    UNIT,
    CURR,
    DEVELOPMENT_COSTS,
    SPECIFIC_COSTS,
    DISPATCH_PRICE,
    VALUE,
    LABEL,
    INSTALLED_CAP,
    LIFETIME_SPECIFIC_COST,
    CRF,
    LIFETIME_SPECIFIC_COST_OM,
    LIFETIME_PRICE_DISPATCH,
    ANNUAL_TOTAL_FLOW,
    OPTIMIZED_ADD_CAP,
    ANNUITY_OM,
    ANNUITY_TOTAL,
    COST_TOTAL,
    COST_OM_TOTAL,
    COST_DISPATCH,
    COST_OM_FIX,
    LCOE_ASSET,
    ENERGY_CONSUMPTION,
    ENERGY_CONVERSION,
    ENERGY_PRODUCTION,
    ENERGY_STORAGE,
)

from .constants import (
    TEST_REPO_PATH,
    INPUT_FOLDER,
    PATH_INPUT_FILE,
    PATH_INPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
)

dict_asset = {
    LABEL: "DSO_feedin_sink",
    DISPATCH_PRICE: {VALUE: -0.4, UNIT: "currency/kWh"},
    SPECIFIC_COSTS: {VALUE: 0, UNIT: "currency/kW"},
    INSTALLED_CAP: {VALUE: 0.0, UNIT: UNIT},
    DEVELOPMENT_COSTS: {VALUE: 0, UNIT: CURR},
    LIFETIME_SPECIFIC_COST: {VALUE: 0.0, UNIT: "currency/kW"},
    LIFETIME_SPECIFIC_COST_OM: {VALUE: 0.0, UNIT: "currency/ye"},
    LIFETIME_PRICE_DISPATCH: {VALUE: -5.505932460595773, UNIT: "?"},
    ANNUAL_TOTAL_FLOW: {VALUE: 0.0, UNIT: "kWh"},
    OPTIMIZED_ADD_CAP: {VALUE: 0, UNIT: "?"},
}

dict_economic = {
    CRF: {VALUE: 0.07264891149004721, UNIT: "?"},
}

PARSER = initializing.create_parser()
TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER)
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "MVS_outputs")

DICT_BEFORE = os.path.join(TEST_REPO_PATH, "dict_values_before_E0.pickle")

DICT_AFTER = os.path.join(TEST_REPO_PATH, "dict_values_after_E0.pickle")


def test_all_cost_info_parameters_added_to_dict_asset():
    """Tests whether the function get_costs is adding all the calculated costs to dict_asset."""
    E2.get_costs(dict_asset, dict_economic)
    for k in (
        COST_DISPATCH,
        COST_OM_FIX,
        COST_TOTAL,
        COST_OM_TOTAL,
        ANNUITY_TOTAL,
        ANNUITY_OM,
    ):
        assert k in dict_asset


def test_add_costs_and_total():
    """Tests if new costs are adding to current costs correctly and if dict_asset is being updated accordingly."""
    current_costs = 10000
    new_cost = 5000
    total_costs = E2.add_costs_and_total(
        dict_asset, "new_cost", new_cost, current_costs
    )
    assert total_costs == new_cost + current_costs
    assert "new_cost" in dict_asset


def test_all_list_in_dict_passes_as_all_keys_included():
    """Tests whether looking for list items in dict_asset is plausible."""
    list_true = ["annual_total_flow", OPTIMIZED_ADD_CAP]
    boolean = E2.all_list_in_dict(dict_asset, list_true)
    assert boolean is True


def test_all_list_in_dict_fails_due_to_not_included_keys():
    """Tests whether looking for list items in dict_asset is plausible."""
    list_false = ["flow", OPTIMIZED_ADD_CAP]
    boolean = E2.all_list_in_dict(dict_asset, list_false)
    assert boolean is False


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


def test_lcoe_parameter_added_to_dict_asset():
    with open(DICT_BEFORE, "rb") as handle:
        dict_values_before = pickle.load(handle)

    with open(DICT_AFTER, "rb") as handle:
        dict_values_after = pickle.load(handle)

    asset_group_list = [
        ENERGY_CONSUMPTION,
        ENERGY_CONVERSION,
        ENERGY_PRODUCTION,
        ENERGY_STORAGE,
    ]
    for asset_group in asset_group_list:
        for asset in dict_values_before[asset_group]:
            assert LCOE_ASSET not in dict_values_before[asset_group][asset]
        for asset in dict_values_after[asset_group]:
            assert LCOE_ASSET in dict_values_after[asset_group][asset]
