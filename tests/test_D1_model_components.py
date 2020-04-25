import pytest
import pandas as pd
import os
import json
import oemof.solph as solph

# internal imports
import src.D1_model_components as D1
from tests.constants import D1_JSON

# fixtures that help creating variables and data needed for the tests
@pytest.fixture()
def get_json():
    """ Reads input json file. """
    with open(D1_JSON) as json_file:
        dict_values = json.load(json_file)
    yield dict_values


@pytest.fixture()
def get_model():
    """ Creates solph.EnergySystem model. """
    time_index = pd.date_range(
        start=pd.to_datetime("2018-01-01 00:00:00"),
        end=pd.to_datetime("2018-12-31 23:00:00"),
        freq="H",
    )
    yield solph.EnergySystem(timeindex=time_index)


@pytest.fixture()
def get_busses():
    """ Creates busses (solph.Bus) dictionary. """
    yield {
        "Fuel bus": solph.Bus(label="Fuel bus"),
        "Electricity bus": solph.Bus(label="Electricity bus"),
    }


class TestTransformerComponent:
    @pytest.fixture(autouse=True)
    def setup_class(self, get_json, get_model, get_busses):
        """ Sets up class attributes for the tests. """
        self.dict_values = get_json
        self.model = get_model
        self.transformers = {}
        self.busses = get_busses

    def helper_test_transformer_in_model_and_dict(self, optimize, dict_asset):
        """
        Helps testing whether `self.transformers` and `self.model` was updated.

        Checks done:
        * self.transformers contains the transformer (key = label, value = transformer object)
        * self.models contains the transformer (indirectly tested)
        * output bus has appropriate values for `nominal_value`, `investment` and `existing` (depending on 'optimize')

        """
        # self.transformers should contain the transformer (key = label, value = transformer object)
        assert dict_asset["label"] in self.transformers
        assert isinstance(self.transformers[dict_asset["label"]], solph.network.Transformer)

        # self.models should contain the transformer (indirectly tested)
        # check output bus (`nominal_value`, `investment` and `existing`) these values are expected to be different depending on whether capacity is optimized or not
        if optimize == True:
            output_bus = self.model.entities[-1].outputs.data[self.busses[dict_asset["output_bus_name"]]]
            assert isinstance(output_bus.investment, solph.options.Investment)
            assert output_bus.existing == dict_asset["installedCap"]["value"]
            assert output_bus.nominal_value == None
        elif optimize == False:
            output_bus = self.model.entities[-1].outputs.data[self.busses[dict_asset["output_bus_name"]]]
            assert output_bus.investment == None
            assert hasattr(output_bus, "existing") == False
            assert output_bus.nominal_value == dict_asset["installedCap"]["value"]
        else:
            raise ValueError(f"`optimize` should be True/False but is '{optimize}'")


    def test_transformer_optimize_cap_multiple_input_busses(self):
        pass

    def test_transformer_optimize_cap_multiple_output_busses(self):
        pass

    def test_transformer_optimize_cap_single_busses(self):
        dict_asset = self.dict_values["energyConversion"][
            "transformer_optimize_single_busses"
        ]

        D1.transformer(
            model=self.model,
            dict_asset=dict_asset,
            transformers=self.transformers,
            busses=self.busses,
        )

        # only one output and one input bus
        assert len([str(i) for i in self.model.entities[-1].outputs]) == 1
        assert len([str(i) for i in self.model.entities[-1].inputs]) == 1

        # checks done with helper function (see func for more information)
        self.helper_test_transformer_in_model_and_dict(optimize=True, dict_asset=dict_asset)

    def test_transformer_fix_cap_multiple_input_busses(self):
        pass

    def test_transformer_fix_cap_multiple_output_busses(self):
        pass

    def test_transformer_fix_cap_single_busses(self):
        dict_asset = self.dict_values["energyConversion"][
            "transformer_fix_single_busses"
        ]

        D1.transformer(
            model=self.model,
            dict_asset=dict_asset,
            transformers=self.transformers,
            busses=self.busses,
        )

        # only one output and one input bus
        assert len([str(i) for i in self.model.entities[-1].outputs]) == 1
        assert len([str(i) for i in self.model.entities[-1].inputs]) == 1

        # checks done with helper function (see func for more information)
        self.helper_test_transformer_in_model_and_dict(optimize=False, dict_asset=dict_asset)

    ### tests for transformer with time dependent efficiency
    def test_transformer_efficiency_time_series_optimize_cap_multiple_input_busses(
        self,
    ):
        pass

    def test_transformer_efficiency_time_series_optimize_cap_multiple_output_busses(
        self,
    ):
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
    def test_source_dispatchable_optimize_cap_normalized_timeseries_multiple_output_busses(
        self,
    ):
        pass

    def test_source_dispatchable_optimize_cap_normalized_timeseries_single_output_bus(
        self,
    ):
        pass

    def test_source_dispatchable_optimize_cap_timeseries_not_normalized_multiple_output_busses(
        self,
    ):
        pass

    def test_source_dispatchable_optimize_cap_timeseries_not_normalized_single_output_bus(
        self,
    ):
        pass

    def test_source_dispatchable_optimize_cap_without_timeseries_multiple_output_busses(
        self,
    ):
        pass

    def test_source_dispatchable_optimize_cap_without_timeseries_single_output_bus(
        self,
    ):
        pass

    def test_source_dispatchable_fix_cap_normalized_timeseries_multiple_output_busses(
        self,
    ):
        pass

    def test_source_dispatchable_fix_cap_normalized_timeseries_single_output_bus(self):
        pass

    def test_source_dispatchable_fix_cap_timeseries_not_normalized_multiple_output_busses(
        self,
    ):
        pass

    def test_source_dispatchable_fix_cap_timeseries_not_normalized_single_output_bus(
        self,
    ):
        pass

    def test_source_dispatchable_fix_cap_without_timeseries_multiple_output_busses(
        self,
    ):
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


class TestBusFunction:
    @pytest.fixture(autouse=True)
    def setup_class(self, get_model, get_busses):
        self.model = get_model
        self.busses = get_busses

    def test_bus_add_to_empty_dict(self):
        label = "Test bus"
        busses = {}
        D1.bus(model=self.model, name=label, busses=busses)

        # self.model should contain the test bus
        assert self.model.entities[-1].label == label
        assert isinstance(self.model.entities[-1], solph.network.Bus)

        # busses should contain the test bus (key = label, value = bus object)
        assert label in busses
        assert isinstance(busses[label], solph.network.Bus)

    def test_bus_add_to_not_empty_dict(self):
        label = "Test bus 2"
        D1.bus(model=self.model, name=label, busses=self.busses)

        # self.model should contain the test bus
        assert self.model.entities[-1].label == label
        assert isinstance(self.model.entities[-1], solph.network.Bus)

        # self.busses should contain the test bus (key = label, value = bus object)
        assert label in self.busses
        assert isinstance(self.busses[label], solph.network.Bus)


def test_check_optimize_cap_raise_error(get_json, get_model, get_busses):
    dict_values = get_json
    model = get_model
    busses = get_busses
    test_asset = dict_values["energyConversion"]["test_asset_for_error_raising"]
    test_asset["optimizeCap"]["value"] = "wrong value"

    msg = f"Input error! 'optimize_cap' of asset {test_asset['label']}"
    with pytest.raises(ValueError, match=msg):
        D1.check_optimize_cap(
            model=model,
            dict_asset=test_asset,
            func_constant=D1.transformer_constant_efficiency_fix,
            func_optimize=D1.transformer_constant_efficiency_optimize,
            busses=busses,
            transformers={},
        )
