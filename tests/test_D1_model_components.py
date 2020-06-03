import json
import os

import oemof.solph as solph
import pandas as pd
import pytest
from pandas.util.testing import assert_series_equal

# internal imports
import src.D1_model_components as D1
from tests.constants import TEST_REPO_PATH, TEST_INPUT_DIRECTORY
from src.constants_json_strings import (
    UNIT,
    VALUE,
    LABEL,
    ENERGY_CONVERSION,
    ENERGY_CONSUMPTION,
    ENERGY_STORAGE,
    OPTIMIZE_CAP,
    INSTALLED_CAP,
)

D1_JSON = os.path.join(TEST_REPO_PATH, TEST_INPUT_DIRECTORY, "test_data_for_D1.json",)

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
        "Electricity bus 2": solph.Bus(label="Electricity bus 2"),
        "Coal bus": solph.Bus(label="Coal bus"),
        "Storage bus": solph.Bus(label="Storage bus"),
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

        Todos
        -----
        * adapt these checks according to changes in D1 after decision about
            which value is assigned to which bus (input or output or both)

        """
        # self.transformers should contain the transformer (key = label, value = transformer object)
        assert dict_asset[LABEL] in self.transformers
        assert isinstance(
            self.transformers[dict_asset[LABEL]], solph.network.Transformer
        )

        # self.models should contain the transformer (indirectly tested)
        # check output bus (`nominal_value`, `investment` and `existing`) these
        # values are expected to be different depending on whether capacity is optimized or not
        if optimize == True:
            output_bus = self.model.entities[-1].outputs.data[
                self.busses[dict_asset["output_bus_name"]]
            ]
            assert isinstance(
                output_bus.investment, solph.options.Investment
            )  # todo maybe ep costs
            assert output_bus.existing == dict_asset[INSTALLED_CAP][VALUE]
            assert output_bus.nominal_value == None
        elif optimize == False:
            output_bus = self.model.entities[-1].outputs.data[
                self.busses[dict_asset["output_bus_name"]]
            ]
            assert output_bus.investment == None
            assert hasattr(output_bus, "existing") == False
            assert output_bus.nominal_value == dict_asset[INSTALLED_CAP][VALUE]
        else:
            raise ValueError(f"`optimize` should be True/False but is '{optimize}'")

    def test_transformer_optimize_cap_single_busses(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
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
        self.helper_test_transformer_in_model_and_dict(
            optimize=True, dict_asset=dict_asset
        )

    def test_transformer_optimize_cap_multiple_input_busses(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "transformer_optimize_multiple_input_busses"
        ]

        D1.transformer(
            model=self.model,
            dict_asset=dict_asset,
            transformers=self.transformers,
            busses=self.busses,
        )

        # one output bus and two input busses
        assert len([str(i) for i in self.model.entities[-1].outputs]) == 1
        assert len([str(i) for i in self.model.entities[-1].inputs]) == 2

        # checks done with helper function (see func for more information)
        self.helper_test_transformer_in_model_and_dict(
            optimize=True, dict_asset=dict_asset
        )

    def test_transformer_optimize_cap_multiple_output_busses(self):
        pass

    def test_transformer_fix_cap_single_busses(self):  ## todo done
        dict_asset = self.dict_values[ENERGY_CONVERSION][
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
        self.helper_test_transformer_in_model_and_dict(
            optimize=False, dict_asset=dict_asset
        )

    def test_transformer_fix_cap_multiple_input_busses(self,):
        ## todo fix after decision on busses see todo in func above
        # dict_asset = self.dict_values[ENERGY_CONVERSION ][
        #     "transformer_fix_multiple_input_busses"
        # ]
        #
        # D1.transformer(
        #     model=self.model,
        #     dict_asset=dict_asset,
        #     transformers=self.transformers,
        #     busses=self.busses,
        # )
        #
        # # one output bus and two input busses
        # assert len([str(i) for i in self.model.entities[-1].outputs]) == 1
        # assert len([str(i) for i in self.model.entities[-1].inputs]) == 2
        #
        # # checks done with helper function (see func for more information)
        # self.helper_test_transformer_in_model_and_dict(optimize=False, dict_asset=dict_asset)
        pass

    def test_transformer_fix_cap_multiple_output_busses(self):
        pass

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
    @pytest.fixture(autouse=True)
    def setup_class(self, get_json, get_model, get_busses):
        """ Sets up class attributes for the tests. """
        self.dict_values = get_json
        self.model = get_model
        self.busses = get_busses
        self.sinks = {}
        self.time_series = pd.Series(data=[0.5, 0.4, 0.0])

    def helper_test_sink_in_model_and_dict(
        self, dispatchable, dict_asset, amount_inputs
    ):
        """
        Helps testing whether `self.sinks` and `self.model` was updated.

        Checks done:
        * self.sinks contains the sink (key = label, value = sink object)
        * self.models contains the sink (indirectly tested)
        * input bus has appropriate values for `fixed`, `actual_value` and `variable_costs` (depending on 'dispatchable')
        * expected amount of input flows according to `amount_inputs`

        """
        # self.sinks should contain the sink (key = label, value = sink object)
        assert dict_asset[LABEL] in self.sinks
        assert isinstance(self.sinks[dict_asset[LABEL]], solph.network.Sink)

        # check amount of sinks
        assert len([str(i) for i in self.model.entities[-1].inputs]) == amount_inputs

        # self.models should contain the sink (indirectly tested)
        # check input bus(es) (`fixed`, `actual_value` and `variable_costs`)
        # foreach input bus - these values are expected to be different
        # depending on `dispatchable`
        if amount_inputs == 1:
            input_bus_names = [dict_asset["input_bus_name"]]
            if dispatchable == True:
                opex_var = [dict_asset["opex_var"][VALUE]]
        elif amount_inputs > 1:
            input_bus_names = dict_asset["input_bus_name"]
            if dispatchable == True:
                opex_var = dict_asset["opex_var"][VALUE]
        else:
            raise ValueError("`amount_inputs` should be int but not zero.")
        for input_bus_name, i in zip(input_bus_names, range(len(input_bus_names))):
            input_bus = self.model.entities[-1].inputs[self.busses[input_bus_name]]
            if dispatchable == False:
                assert input_bus.fixed == True
                assert_series_equal(input_bus.actual_value, dict_asset["timeseries"])
                assert (
                    input_bus.variable_costs.default == 0
                )  # this only is a real check if opex_var is not 0
            elif dispatchable == True:
                assert input_bus.fixed == False
                assert len(input_bus.actual_value) == 0
                assert input_bus.variable_costs.default == opex_var[i]
            else:
                raise ValueError(
                    f"`dispatchable` should be True/False but is '{dispatchable}'"
                )

    def test_sink_non_dispatchable_single_input_bus(self):
        dict_asset = self.dict_values[ENERGY_CONSUMPTION]["non_dispatchable_single"]
        dict_asset["timeseries"] = self.time_series

        D1.sink_non_dispatchable(
            model=self.model,
            dict_asset=dict_asset,
            sinks=self.sinks,
            busses=self.busses,
        )

        self.helper_test_sink_in_model_and_dict(
            dispatchable=False, dict_asset=dict_asset, amount_inputs=1
        )

    def test_sink_non_dispatchable_multiple_input_busses(self):
        dict_asset = self.dict_values[ENERGY_CONSUMPTION]["non_dispatchable_multiple"]
        dict_asset["timeseries"] = self.time_series

        D1.sink_non_dispatchable(
            model=self.model,
            dict_asset=dict_asset,
            sinks=self.sinks,
            busses=self.busses,
        )

        self.helper_test_sink_in_model_and_dict(
            dispatchable=False, dict_asset=dict_asset, amount_inputs=2
        )

    def test_sink_dispatchable_single_input_bus(self):
        dict_asset = self.dict_values[ENERGY_CONSUMPTION]["dispatchable_single"]

        D1.sink_dispatchable(
            model=self.model,
            dict_asset=dict_asset,
            sinks=self.sinks,
            busses=self.busses,
        )

        self.helper_test_sink_in_model_and_dict(
            dispatchable=True, dict_asset=dict_asset, amount_inputs=1
        )

    def test_sink_dispatchable_multiple_input_busses(self):
        dict_asset = self.dict_values[ENERGY_CONSUMPTION]["dispatchable_multiple"]

        D1.sink_dispatchable(
            model=self.model,
            dict_asset=dict_asset,
            sinks=self.sinks,
            busses=self.busses,
        )

        self.helper_test_sink_in_model_and_dict(
            dispatchable=True, dict_asset=dict_asset, amount_inputs=2
        )


class TestSourceComponent:

    ## non dispatchable
    def test_source_non_dispatchable_optimize_cap(self):
        pass

    def test_source_non_dispatchable_fix_cap(self):
        pass

    ## dispatchable
    def test_source_dispatchable_optimize_cap_normalized_timeseries(self):
        pass

    def test_source_dispatchable_optimize_cap_timeseries_not_normalized_timeseries(
        self,
    ):
        pass

    def test_source_dispatchable_optimize_cap_without_timeseries(self):
        pass

    def test_source_dispatchable_fix_cap_normalized_timeseries(self):
        pass

    def test_source_dispatchable_fix_cap_timeseries_not_normalized_timeseries(self):
        pass

    def test_source_dispatchable_fix_cap_without_timeseries(self):
        pass


class TestStorageComponent:
    @pytest.fixture(autouse=True)
    def setup_class(self, get_json, get_model, get_busses):
        """ Sets up class attributes for the tests. """
        self.dict_values = get_json
        self.model = get_model
        self.busses = get_busses
        self.storages = {}

    def test_storage_optimize(self):
        dict_asset = self.dict_values[ENERGY_STORAGE]["storage_optimize"]
        dict_asset["storage capacity"]["maximumCap"] = {VALUE: None, UNIT: "kWh"}
        dict_asset["input power"]["maximumCap"] = {VALUE: None, UNIT: "kWh"}
        dict_asset["output power"]["maximumCap"] = {VALUE: None, UNIT: "kWh"}
        D1.storage(
            model=self.model,
            dict_asset=dict_asset,
            busses=self.busses,
            storages=self.storages,
        )

        # self.storages should contain the storage (key = label, value = storage object)
        assert dict_asset[LABEL] in self.storages
        assert isinstance(
            self.storages[dict_asset[LABEL]], solph.components.GenericStorage
        )

        # check value of `existing`, `investment` and `nominal_value`(`nominal_storage_capacity`)
        input_bus = self.model.entities[-1].inputs[self.busses["Storage bus"]]
        output_bus = self.model.entities[-1].outputs[self.busses["Storage bus"]]

        assert input_bus.existing == dict_asset["input power"][INSTALLED_CAP][VALUE]
        assert (
            input_bus.investment.ep_costs
            == dict_asset["input power"]["simulation_annuity"][VALUE]
        )
        assert input_bus.nominal_value == None

        assert output_bus.existing == dict_asset["output power"][INSTALLED_CAP][VALUE]
        assert (
            output_bus.investment.ep_costs
            == dict_asset["output power"]["simulation_annuity"][VALUE]
        )
        assert output_bus.nominal_value == None

        # assert self.model.entities[-1].existing ==  dict_asset["storage capacity"][INSTALLED_CAP][VALUE]  # todo probably not necessary parameter
        assert (
            self.model.entities[-1].investment.ep_costs
            == dict_asset["storage capacity"]["simulation_annuity"][VALUE]
        )
        assert self.model.entities[-1].nominal_storage_capacity == None

        # check that invest_relation_input_capacity and invest_relation_output_capacity is added
        assert (
            self.model.entities[-1].invest_relation_input_capacity
            == dict_asset["input power"]["c_rate"][VALUE]
        )
        assert (
            self.model.entities[-1].invest_relation_output_capacity
            == dict_asset["output power"]["c_rate"][VALUE]
        )

    def test_storage_fix(self):
        dict_asset = self.dict_values[ENERGY_STORAGE]["storage_fix"]
        D1.storage(
            model=self.model,
            dict_asset=dict_asset,
            busses=self.busses,
            storages=self.storages,
        )

        # self.storages should contain the storage (key = label, value = storage object)
        assert dict_asset[LABEL] in self.storages
        assert isinstance(
            self.storages[dict_asset[LABEL]], solph.components.GenericStorage
        )

        # check value of `existing`, `investment` and `nominal_value`(`nominal_storage_capacity`)
        input_bus = self.model.entities[-1].inputs[self.busses["Storage bus"]]
        output_bus = self.model.entities[-1].outputs[self.busses["Storage bus"]]

        assert hasattr(input_bus, "existing") == False
        assert input_bus.investment == None
        assert (
            input_bus.nominal_value
            == dict_asset["storage capacity"][INSTALLED_CAP][VALUE]
        )

        assert hasattr(output_bus, "existing") == False
        assert output_bus.investment == None
        assert (
            output_bus.nominal_value == dict_asset["input power"][INSTALLED_CAP][VALUE]
        )

        assert (
            hasattr(self.model.entities[-1], "existing") == False
        )  # todo probably not necessary parameter
        assert self.model.entities[-1].investment == None
        assert (
            self.model.entities[-1].nominal_storage_capacity
            == dict_asset["output power"][INSTALLED_CAP][VALUE]
        )

        # # check that invest_relation_input_capacity and invest_relation_output_capacity is not added
        assert self.model.entities[-1].invest_relation_input_capacity == None
        assert self.model.entities[-1].invest_relation_output_capacity == None


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
    test_asset = dict_values[ENERGY_CONVERSION]["test_asset_for_error_raising"]
    test_asset[OPTIMIZE_CAP][VALUE] = "wrong value"

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
