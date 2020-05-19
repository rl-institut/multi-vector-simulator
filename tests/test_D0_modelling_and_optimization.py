import src.D0_modelling_and_optimization as D0
import pytest

# this test should be ensured by the benchmark tests itself.
#def test_if_oemof_simulation_runs_through(self):
import os
import json
from src.B0_data_input_json import load_json

json_path = os.path.join("tests", "test_data", "test_data_for_D0.json")

dict_values = load_json(json_path)

def test_if_model_building_time_measured_and_stored():
    dict_values = {"simulation_results": {}}
    start = D0.timer.initalize()
    D0.timer.stop(dict_values, start)
    assert "modelling_time" in dict_values["simulation_results"]
    assert isinstance(dict_values["simulation_results"]["modelling_time"], float)

import pandas as pd
import oemof.solph
from src.constants_json_strings import ENERGY_BUSSES,ENERGY_CONSUMPTION, OEMOF_TRANSFORMER, OEMOF_ASSET_TYPE

START_TIME = "2020-01-01 00:00"
PERIODS = 3
pandas_DatetimeIndex = pd.date_range(start=START_TIME, periods=PERIODS, freq="60min")

dict_values_minimal = {"simulation_settings": {"time_index": pandas_DatetimeIndex},
                       ENERGY_BUSSES: "bus"}

def test_energysystem_initialized():
    model, dict_model = D0.model_building.initialize(dict_values_minimal)
    for k in ("busses", "sinks", "sources", "transformers", "storages"):
        assert k in dict_model.keys()
    assert isinstance(model, oemof.solph.network.EnergySystem)


def test_oemof_adding_assets_from_dict_values_passes():
    model, dict_model = D0.model_building.initialize(dict_values)
    D0.model_building.adding_assets_to_energysystem_model(dict_values, dict_model, model)
    assert 1 == 1

def test_error_raise_WrongOemofAssetForGroupError_if_oemof_asset_type_not_accepted_for_asset_group():
    model, dict_model = D0.model_building.initialize(dict_values_minimal)
    dict_test = {ENERGY_CONSUMPTION: {"asset": {OEMOF_ASSET_TYPE: OEMOF_TRANSFORMER}}}
    dict_test.update(dict_values_minimal)
    with pytest.raises(D0.WrongOemofAssetForGroupError):
        D0.model_building.adding_assets_to_energysystem_model(dict_test, dict_model, model)

from src.constants_json_strings import ACCEPTED_ASSETS_FOR_ASSET_GROUPS
def test_error_raise_UnknownOemofAssetType_if_oemof_asset_type_not_defined_in_D0():
    model, dict_model = D0.model_building.initialize(dict_values_minimal)
    dict_test = {ENERGY_CONSUMPTION: {"asset": {OEMOF_ASSET_TYPE: "unknown_type"}}}
    dict_test.update(dict_values_minimal)
    ACCEPTED_ASSETS_FOR_ASSET_GROUPS[ENERGY_CONSUMPTION].append("unknown_type")
    with pytest.raises(D0.UnknownOemofAssetType):
        D0.model_building.adding_assets_to_energysystem_model(dict_test, dict_model, model, **ACCEPTED_ASSETS_FOR_ASSET_GROUPS)

from tests.constants import TEST_REPO_PATH
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "test_outputs")

def test_networkx_graph_requested_store_nx_graph_true():
    model, dict_model = D0.model_building.initialize(dict_values)
    D0.model_building.adding_assets_to_energysystem_model(dict_values, dict_model, model)
    dict_values["simulation_settings"]["store_nx_graph"].update({"value": True})
    D0.model_building.plot_networkx_graph(dict_values, model)
    assert (
            os.path.exists(os.path.join(TEST_OUTPUT_PATH, "network_graph.png")) is True
        )

def test_networkx_graph_requested_display_and_store_nx_graph_true():
    model, dict_model = D0.model_building.initialize(dict_values)
    D0.model_building.adding_assets_to_energysystem_model(dict_values, dict_model, model)
    dict_values["simulation_settings"]["store_nx_graph"].update({"value": False})
    D0.model_building.plot_networkx_graph(dict_values, model)
    assert (
            os.path.exists(os.path.join(TEST_OUTPUT_PATH, "network_graph.png")) is False
        )


import oemof.solph as solph
path_lp_file = os.path.join(dict_values["simulation_settings"]["path_output_folder"], "lp_file.lp")
def test_if_lp_file_is_stored_to_file_if_output_lp_file_true():
    model, dict_model = D0.model_building.initialize(dict_values)
    print(dict_values["simulation_settings"]["time_index"])
    model = D0.model_building.adding_assets_to_energysystem_model(dict_values, dict_model, model)
    local_energy_system = solph.Model(model)
    dict_values["simulation_settings"]["output_lp_file"].update({"value": True})
    D0.model_building.store_lp_file(dict_values, local_energy_system)
    assert (
            os.path.exists(path_lp_file) is True
    )

def test_if_lp_file_is_stored_to_file_if_output_lp_file_false():
    model, dict_model = D0.model_building.initialize(dict_values)
    model = D0.model_building.adding_assets_to_energysystem_model(dict_values, dict_model, model)
    local_energy_system = solph.Model(model)
    dict_values["simulation_settings"]["output_lp_file"].update({"value": False})
    D0.model_building.store_lp_file(dict_values, local_energy_system)
    assert (
            os.path.exists(path_lp_file) is False
    )

path_oemof_file = os.path.join(TEST_OUTPUT_PATH, "oemof_simulation_results.oemof")

def test_if_oemof_results_are_stored_to_file_if_store_oemof_results_true(self):
    dict_values["simulation_settings"]["output_lp_file"].update({"value": False})
    D0.run_oemof(dict_values)
    assert (
            os.path.exists(path_oemof_file) is True
    )

def test_if_oemof_results_are_stored_to_file_if_store_oemof_results_false(self):
    dict_values["simulation_settings"]["output_lp_file"].update({"value": False})
    D0.run_oemof(dict_values)
    assert (
            os.path.exists(path_oemof_file) is False
    )

def test_if_simulation_results_added_to_dict_values():
    D0.run_oemof(dict_values)
    for k in ("label", "objective_value", "simulation_time"):
        assert k in dict_values["simulation_results"] is True
