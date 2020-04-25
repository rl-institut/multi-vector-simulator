import pytest
import pandas as pd
import os
import json
import oemof.solph as solph

# internal imports
import src.D1_model_components as D1
from tests.constants import (
    D1_JSON
)


# fixtures that help creating variables and data needed for the tests
@pytest.fixture()
def get_json():
    """ Reads input json file. """
    with open(D1_JSON) as json_file:
        dict_values = json.load(json_file)
    yield dict_values


@pytest.fixture()
def get_model():
    time_index = pd.date_range(start=pd.to_datetime("2018-01-01 00:00:00"),
                               end=pd.to_datetime("2018-12-31 23:00:00"),
                               freq="H")
    """ Creates solph.EnergySystem model. """
    yield solph.EnergySystem(timeindex=time_index)


@pytest.fixture()
def get_busses():
    """ Creates busses (solph.Bus) dictionary. """
    yield {
        "Fuel bus": solph.Bus(label="Fuel bus"),
        "Electricity bus": solph.Bus(label="Electricity bus")
    }

class TestTransformerComponent:
    @pytest.fixture(autouse=True)
    def setup_class(self, get_json, get_model, get_busses):
        """ Sets up class attributes for the tests. """
        self.dict_values = get_json
        self.model = get_model
        self.transformers = {}
        self.busses = get_busses

    def test_transformer_optimize_cap_multiple_input_busses(self):
        pass

    def test_transformer_optimize_cap_multiple_output_busses(self):
        pass

    def test_transformer_optimize_cap_single_busses(self):
        dict_asset = self.dict_values["energyConversion"][
            "transformer_optimize_single_busses"]
        label = dict_asset["label"]

        D1.transformer(model=self.model, dict_asset=dict_asset,
                       transformers=self.transformers, busses=self.busses)

        # self.model should contain the transformer
        assert self.model.entities[-1].label == label
        assert isinstance(self.model.entities[-1], solph.network.Transformer)
        # only one output and one input bus
        assert len(self.transformers[dict_asset["label"]].outputs.data) == 1
        # check output bus

    def test_transformer_fix_cap_multiple_input_busses(self):
        pass

    def test_transformer_fix_cap_multiple_output_busses(self):
        pass

    def test_transformer_fix_cap_single_busses(self):
        pass

    ### tests for transformer with time dependent efficiency
    def test_transformer_efficiency_time_series_optimize_cap_multiple_input_busses(self):
        pass

    def test_transformer_efficiency_time_series_optimize_cap_multiple_output_busses(self):
        pass

    def test_transformer_efficiency_time_series_optimize_cap_single_busses(self):
        pass

    def test_transformer_efficiency_time_series_fix_cap_multiple_input_busses(self):
        pass

    def test_transformer_efficiency_time_series_fix_cap_multiple_output_busses(self):
        pass

    def test_transformer_efficiency_time_series_fix_cap_single_busses(self):
        pass


class TestSinkComponent:
    def test_sink_non_dispatchable_multiple_input_busses(self):
        pass
        # check if model was updated with sink (check inputs and outputs)
        # check if sinks now contains sink

    def test_sink_non_dispatchable_single_input_bus(self):
        pass

    def test_sink_dispatchable_multiple_input_busses(self):
        pass

    def test_sink_dispatchable_single_input_bus(self):
        pass


class TestSourceComponent:
    # todo: only single output busses...
    #  We should actually not allow multiple output busses, probably - because a pv would then feed in twice as much as solar_gen_specific for example, see issue #121
    ## non dispatchable
    def test_source_non_dispatchable_optimize_cap_multiple_output_busses(self):
        pass

    def test_source_non_dispatchable_optimize_cap_single_output_bus(self):
        pass

    def test_source_non_dispatchable_fix_cap_multiple_output_busses(self):
        pass

    def test_source_non_dispatchable_fix_cap_single_output_bus(self):
        pass

    ## dispatchable
    def test_source_dispatchable_optimize_cap_normalized_timeseries_multiple_output_busses(self):
        pass

    def test_source_dispatchable_optimize_cap_normalized_timeseries_single_output_bus(self):
        pass

    def test_source_dispatchable_optimize_cap_timeseries_not_normalized_multiple_output_busses(self):
        pass

    def test_source_dispatchable_optimize_cap_timeseries_not_normalized_single_output_bus(self):
        pass

    def test_source_dispatchable_optimize_cap_without_timeseries_multiple_output_busses(self):
        pass

    def test_source_dispatchable_optimize_cap_without_timeseries_single_output_bus(self):
        pass

    def test_source_dispatchable_fix_cap_normalized_timeseries_multiple_output_busses(self):
        pass

    def test_source_dispatchable_fix_cap_normalized_timeseries_single_output_bus(self):
        pass

    def test_source_dispatchable_fix_cap_timeseries_not_normalized_multiple_output_busses(self):
        pass

    def test_source_dispatchable_fix_cap_timeseries_not_normalized_single_output_bus(self):
        pass

    def test_source_dispatchable_fix_cap_without_timeseries_multiple_output_busses(self):
        pass

    def test_source_dispatchable_fix_cap_without_timeseries_single_output_bus(self):
        pass


class TestStorageComponent:

    # could think about what is definitely necessary for the storage and test whether these attributes were set
    def test_storage_optimize(self):
        pass

    def test_storage_fix(self):
        pass


### other functionalities
def test_bus():
    pass


def test_check_optimize_cap_raise_error():
    pass
