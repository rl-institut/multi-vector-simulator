import src.D0_modelling_and_optimization as D0
import pytest

# this test should be ensured by the benchmark tests itself.
#def test_if_oemof_simulation_runs_through(self):


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

dict_values = {"simulation_settings": {"time_index": pandas_DatetimeIndex},
               ENERGY_BUSSES: "bus"}

def test_energysystem_initialized():
    model, dict_model = D0.model_building.initialize(dict_values)
    for k in ("busses","sinks", "sources", "transformers", "storages"):
        assert k in dict_model.keys()
    assert isinstance(model, oemof.solph.network.EnergySystem)


'''

def test_error_raise_if_oemof_asset_type_accepted_for_asset_group():
    model, dict_model = D0.model_building.initialize(dict_values)
    dict_test = {ENERGY_CONSUMPTION: {"Asset": {OEMOF_ASSET_TYPE: OEMOF_TRANSFORMER}}}
    dict_test.update(dict_values)
    with pytest.raises(ValueError):
        D0.model_building.adding_assets_to_energysystem_model(dict_values, dict_model, model)

def test_error_raise_if_oemof_asset_type_not_defined():
    model, dict_model = D0.model_building.initialize(dict_values)
    dict_test = {ENERGY_CONSUMPTION: {"Asset": {OEMOF_ASSET_TYPE: OEMOF_TRANSFORMER}}}
    dict_test.update(dict_values)
    with pytest.raises(ValueError):
        D0.model_building.adding_assets_to_energysystem_model(dict_values, dict_model, model)


def test_if_oemof_results_are_stored_to_file_if_setting_true(self):
   assert 1 == 0
   
def test_if_lp_file_is_stored_to_file_if_setting_true(self):
   assert 1 == 0
   
def test_if_networkx_graph_function_called(self):
   assert 1 == 0

def test_if_simulation_parameters_added_to_dict(self):
   assert 1 == 0
   
def test_if_result_data_for_E0_in_correct_format(self):
   assert 1 == 0

def test_if_constraint_settings_add_constraints(self):
   assert 1 == 0
   
def test_if_all_assets_added_to_dict_oemof_components(self):
   assert 1 == 0

def test_if_energy_conversion_assets_added(self):
   assert 1 == 0

def test_if_energy_production_assets_added(self):
   assert 1 == 0
   
def test_if_energy_provider_assets_added(self):
   assert 1 == 0    

def test_if_energy_system_model_generated_by_oemof(self):
   assert 1 == 0
   
def test_if_energy_storage_assets_added(self):
   assert 1 == 0
   
def test_if_energy_busses_added(self):
   assert 1 == 0
'''