import os
import shutil
import argparse


from oemof import solph
import pandas as pd
import pytest
import mock

from multi_vector_simulator.cli import main
import multi_vector_simulator.D0_modelling_and_optimization as D0
from multi_vector_simulator.B0_data_input_json import (
    load_json,
    convert_from_json_to_special_types,
)

from multi_vector_simulator.utils.constants import LP_FILE

from multi_vector_simulator.utils.constants_json_strings import (
    ENERGY_BUSSES,
    ENERGY_CONSUMPTION,
    OEMOF_BUSSES,
    OEMOF_SOURCE,
    OEMOF_SINK,
    OEMOF_GEN_STORAGE,
    OEMOF_TRANSFORMER,
    OEMOF_ASSET_TYPE,
    LABEL,
    VALUE,
    SIMULATION_SETTINGS,
    TIME_INDEX,
    OUTPUT_LP_FILE,
    SIMULATION_RESULTS,
    OBJECTIVE_VALUE,
    SIMULTATION_TIME,
    MODELLING_TIME,
    ASSET_DICT,
    ENERGY_VECTOR,
)

from multi_vector_simulator.utils.exceptions import (
    MVSOemofError,
    WrongOemofAssetForGroupError,
    UnknownOemofAssetType,
)


from _constants import (
    TEST_REPO_PATH,
    PATH_OUTPUT_FOLDER,
    TEST_INPUT_DIRECTORY,
    ES_GRAPH,
    DATA_TYPE_JSON_KEY,
    TYPE_DATETIMEINDEX,
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    CSV_EXT,
    JSON_FNAME,
)

TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "test_outputs")


@pytest.fixture
def dict_values():
    answer = load_json(
        os.path.join(TEST_REPO_PATH, TEST_INPUT_DIRECTORY, "inputs_for_D0", JSON_FNAME),
        flag_missing_values=False,
    )
    answer[SIMULATION_SETTINGS].update({PATH_OUTPUT_FOLDER: TEST_OUTPUT_PATH})

    return answer


@pytest.fixture
def dict_values_minimal():
    pandas_DatetimeIndex = pd.date_range(
        start="2020-01-01 00:00", periods=3, freq="60min"
    )

    return convert_from_json_to_special_types(
        {
            SIMULATION_SETTINGS: {
                TIME_INDEX: {
                    DATA_TYPE_JSON_KEY: TYPE_DATETIMEINDEX,
                    VALUE: pandas_DatetimeIndex,
                }
            },
            ENERGY_BUSSES: {
                "bus": {
                    LABEL: "bus",
                    ENERGY_VECTOR: "Electricity",
                    ASSET_DICT: {"asset": "asset_label"},
                }
            },
        }
    )


def test_if_model_building_time_measured_and_stored():
    dict_values = {SIMULATION_RESULTS: {}}
    start = D0.timer.initalize()
    D0.timer.stop(dict_values, start)
    assert (
        MODELLING_TIME in dict_values[SIMULATION_RESULTS]
    ), f"The simulation time has not been added to to simulation results."
    assert isinstance(
        dict_values[SIMULATION_RESULTS][MODELLING_TIME], float
    ), f"The simulation time should be a floating number."


def test_energysystem_initialized(dict_values_minimal):
    model, dict_model = D0.model_building.initialize(dict_values_minimal)
    for k in (
        OEMOF_BUSSES,
        OEMOF_SINK,
        OEMOF_SOURCE,
        OEMOF_TRANSFORMER,
        OEMOF_GEN_STORAGE,
    ):
        assert k in dict_model.keys()
    assert isinstance(
        model, solph.EnergySystem
    ), f"The oemof model has not been successfully created."


def test_oemof_adding_assets_from_dict_values_passes(dict_values):
    model, dict_model = D0.model_building.initialize(dict_values)
    D0.model_building.adding_assets_to_energysystem_model(
        dict_values, dict_model, model
    )
    assert 1 == 1


def test_error_raise_WrongOemofAssetForGroupError_if_oemof_asset_type_not_accepted_for_asset_group(
    dict_values_minimal,
):
    model, dict_model = D0.model_building.initialize(dict_values_minimal)
    dict_test = {ENERGY_CONSUMPTION: {"asset": {OEMOF_ASSET_TYPE: OEMOF_TRANSFORMER}}}
    dict_test.update(dict_values_minimal)
    with pytest.raises(WrongOemofAssetForGroupError):
        D0.model_building.adding_assets_to_energysystem_model(
            dict_test, dict_model, model
        )


from multi_vector_simulator.utils.constants_json_strings import (
    ACCEPTED_ASSETS_FOR_ASSET_GROUPS,
)


def test_error_raise_UnknownOemofAssetType_if_oemof_asset_type_not_defined_in_D0(
    dict_values_minimal,
):
    model, dict_model = D0.model_building.initialize(dict_values_minimal)
    dict_test = {ENERGY_CONSUMPTION: {"asset": {OEMOF_ASSET_TYPE: "unknown_type"}}}
    dict_test.update(dict_values_minimal)
    ACCEPTED_ASSETS_FOR_ASSET_GROUPS[ENERGY_CONSUMPTION].append("unknown_type")
    with pytest.raises(UnknownOemofAssetType):
        D0.model_building.adding_assets_to_energysystem_model(
            dict_test, dict_model, model, **ACCEPTED_ASSETS_FOR_ASSET_GROUPS
        )


@pytest.mark.skipif(
    EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
    reason="Benchmark test deactivated, set env variable "
    "EXECUTE_TESTS_ON to 'master' to run this test",
)
@mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
def test_error_raise_MVSOemofError_if_solver_could_not_finish_simulation(margs):
    use_case = os.path.join("test_data", "known_oemof_errors", "insufficient_capacity")
    with pytest.raises(MVSOemofError):
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_REPO_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )


PATH_ES_GRAPH = os.path.join(TEST_OUTPUT_PATH, ES_GRAPH)


def setup_function():
    if os.path.exists(TEST_OUTPUT_PATH):
        shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True, onerror=None)
    if os.path.exists(TEST_OUTPUT_PATH) is False:
        os.mkdir(TEST_OUTPUT_PATH)


def test_networkx_graph_requested_store_nx_graph_true(dict_values):
    setup_function()
    assert (
        os.path.isfile(PATH_ES_GRAPH) is False
    ), f"The {PATH_ES_GRAPH} does already exist before the test is run it should be non-existant, so the test can not be executed."
    model, dict_model = D0.model_building.initialize(dict_values)
    D0.model_building.adding_assets_to_energysystem_model(
        dict_values, dict_model, model
    )
    D0.model_building.plot_networkx_graph(
        dict_values, model, save_energy_system_graph=True
    )
    assert (
        os.path.isfile(PATH_ES_GRAPH) is True
    ), f"Eventhough the energy system graph is requested, it is not stored to disk"


def test_networkx_graph_requested_store_nx_graph_false(dict_values):
    setup_function()
    assert (
        os.path.isfile(PATH_ES_GRAPH) is False
    ), f"The {PATH_ES_GRAPH} does already exist before the test is run it should be non-existant, so the test can not be executed."
    model, dict_model = D0.model_building.initialize(dict_values)
    D0.model_building.adding_assets_to_energysystem_model(
        dict_values, dict_model, model
    )
    D0.model_building.plot_networkx_graph(
        dict_values, model, save_energy_system_graph=False
    )
    assert (
        os.path.isfile(PATH_ES_GRAPH) is False
    ), f"Eventhough the energy system graph is not requested, it is stored to disk"


path_lp_file = os.path.join(TEST_OUTPUT_PATH, LP_FILE)


def test_if_lp_file_is_stored_to_file_if_output_lp_file_true(dict_values):
    setup_function()
    assert (
        os.path.isfile(path_lp_file) is False
    ), f"The {LP_FILE} does exist before the test is run eventhough it should be non-existant, so the test can not be executed."
    model, dict_model = D0.model_building.initialize(dict_values)
    model = D0.model_building.adding_assets_to_energysystem_model(
        dict_values, dict_model, model
    )
    local_energy_system = solph.Model(model)
    dict_values[SIMULATION_SETTINGS][OUTPUT_LP_FILE].update({VALUE: True})
    D0.model_building.store_lp_file(dict_values, local_energy_system)
    assert (
        os.path.isfile(path_lp_file) is True
    ), f"Eventhough the {LP_FILE} is requested, it is not stored to disk"


def test_if_lp_file_is_stored_to_file_if_output_lp_file_false(dict_values):
    setup_function()
    assert (
        os.path.isfile(path_lp_file) is False
    ), f"The {LP_FILE} does already exist before the test is run it should be non-existant, so the test can not be executed."
    model, dict_model = D0.model_building.initialize(dict_values)
    model = D0.model_building.adding_assets_to_energysystem_model(
        dict_values, dict_model, model
    )
    local_energy_system = solph.Model(model)
    dict_values[SIMULATION_SETTINGS][OUTPUT_LP_FILE].update({VALUE: False})
    D0.model_building.store_lp_file(dict_values, local_energy_system)
    assert (
        os.path.isfile(path_lp_file) is False
    ), f"Eventhough the {LP_FILE} is not requested, it is stored to disk"


def test_if_simulation_results_added_to_dict_values(dict_values):
    D0.run_oemof(dict_values)
    for k in (LABEL, OBJECTIVE_VALUE, SIMULTATION_TIME):
        assert k in dict_values[SIMULATION_RESULTS].keys()
