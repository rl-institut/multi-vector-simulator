import json
import os

from oemof import solph
from oemof import network
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

# internal imports
import multi_vector_simulator.D1_model_components as D1

from multi_vector_simulator.utils.constants import JSON_FNAME
from multi_vector_simulator.utils.exceptions import (
    MissingParameterError,
    WrongParameterFormatError,
)

from multi_vector_simulator.utils.constants_json_strings import (
    UNIT,
    VALUE,
    LABEL,
    ENERGY_CONVERSION,
    ENERGY_CONSUMPTION,
    ENERGY_STORAGE,
    ENERGY_PRODUCTION,
    DISPATCH_PRICE,
    EFFICIENCY,
    OPTIMIZE_CAP,
    INSTALLED_CAP,
    INPUT_POWER,
    OUTPUT_POWER,
    C_RATE,
    THERM_LOSSES_REL,
    THERM_LOSSES_ABS,
    STORAGE_CAPACITY,
    TIMESERIES,
    TIMESERIES_NORMALIZED,
    TIMESERIES_PEAK,
    INFLOW_DIRECTION,
    OUTFLOW_DIRECTION,
    SIMULATION_ANNUITY,
    MAXIMUM_CAP,
    MAXIMUM_ADD_CAP,
)
from _constants import TEST_REPO_PATH, TEST_INPUT_DIRECTORY

D1_JSON = os.path.join(
    TEST_REPO_PATH, TEST_INPUT_DIRECTORY, "inputs_for_D1", JSON_FNAME
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
        "Electricity bus": D1.CustomBus(
            label="Electricity bus", energy_vector="Electricity"
        ),
        "Electricity bus 2": D1.CustomBus(
            label="Electricity bus 2", energy_vector="Electricity"
        ),
        "Coal bus": solph.Bus(label="Coal bus"),
        "Storage bus": solph.Bus(label="Storage bus"),
        "Heat bus": D1.CustomBus(label="Heat bus", energy_vector="Heat"),
        "Gas bus": solph.Bus(label="Gas bus"),
    }


class TestTransformerComponent:
    @pytest.fixture(autouse=True)
    def setup_class(self, get_json, get_model, get_busses):
        """ Sets up class attributes for the tests. """
        self.dict_values = get_json
        self.model = get_model
        self.transformers = {}
        self.busses = get_busses

    def helper_test_transformer_in_model_and_dict(
        self, optimize, dict_asset, multiple_outputs=False
    ):
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
        assert (
            dict_asset[LABEL] in self.transformers
        ), f"Transformer '{dict_asset[LABEL]}' was not added to `asset_dict` but should have been added."
        assert isinstance(
            self.transformers[dict_asset[LABEL]], network.Transformer
        ), f"Transformer '{dict_asset[LABEL]}' was not added as type ' solph.network.Transformer' to `asset_dict`."

        # self.models should contain the transformer (indirectly tested)
        # check output bus (`nominal_value`, `investment` and `existing`) these
        # values are expected to be different depending on whether capacity is optimized or not
        if multiple_outputs == True:
            output_bus_list = [
                self.model._nodes[-1].outputs.data[self.busses[bus_name]]
                for bus_name in dict_asset[OUTFLOW_DIRECTION]
            ]
        else:
            output_bus_list = [
                self.model._nodes[-1].outputs.data[
                    self.busses[dict_asset[OUTFLOW_DIRECTION]]
                ]
            ]
        for output_bus in output_bus_list:
            if optimize is True:
                assert isinstance(
                    output_bus.investment, solph.Investment
                ), f"The output bus of transformer '{dict_asset[LABEL]}' misses an investment object."
                assert (
                    output_bus.investment.existing == dict_asset[INSTALLED_CAP][VALUE]
                ), f"`existing` of the `investment` attribute of the output bus of transformer '{dict_asset[LABEL]}' should be {dict_asset[INSTALLED_CAP][VALUE]}."
                assert (
                    output_bus.nominal_value is None
                ), f"The output bus of transformer '{dict_asset[LABEL]}' should have a `nominal_value` of value None."
            elif optimize is False:
                assert (
                    output_bus.investment is None
                ), f" The `investment` attribute of transformer '{dict_asset[LABEL]}' should be None."
                assert (
                    hasattr(output_bus.investment, "existing") is False
                ), f"`existing` of the `investment` attribute of the output bus of transformer '{dict_asset[LABEL]}' should not exist."
                assert (
                    output_bus.nominal_value == dict_asset[INSTALLED_CAP][VALUE]
                ), f"The `nominal_value` of the output bus of transformer '{dict_asset[LABEL]}' should be {dict_asset[INSTALLED_CAP][VALUE]}."
            else:
                raise ValueError(
                    f"`optimize` should be True/False but is '{optimize}' - check how helper_test_transformer_in_model_and_dict() is used."
                )

    def test_transformer_optimize_cap_single_busses(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "transformer_optimize_single_busses"
        ]

        D1.transformer(
            model=self.model,
            dict_asset=dict_asset,
            transformer=self.transformers,
            bus=self.busses,
        )

        # only one output and one input bus
        assert (
            len([str(i) for i in self.model._nodes[-1].outputs]) == 1
        ), f"Amount of output busses of transformer should be one but is {len([str(i) for i in self.model._nodes[-1].outputs])}."
        assert (
            len([str(i) for i in self.model._nodes[-1].inputs]) == 1
        ), f"Amount of input busses of transformer should be one but is {len([str(i) for i in self.model._nodes[-1].inputs])}."

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
            transformer=self.transformers,
            bus=self.busses,
        )

        # one output bus and two input busses
        assert (
            len([str(i) for i in self.model._nodes[-1].outputs]) == 1
        ), f"Amount of output busses of transformer should be one but is {len([str(i) for i in self.model._nodes[-1].outputs])}."
        assert (
            len([str(i) for i in self.model._nodes[-1].inputs]) == 2
        ), f"Amount of input busses of transformer should be two but is {len([str(i) for i in self.model._nodes[-1].inputs])}."
        assert (
            len(self.model._nodes[-1].conversion_factors) == 2,
            f"The amount of conversion factors should be two to match the amount of input busses but is {len(self.model._nodes[-1].conversion_factors)}",
        )
        # checks done with helper function (see func for more information)
        self.helper_test_transformer_in_model_and_dict(
            optimize=True, dict_asset=dict_asset
        )

    def test_transformer_optimize_cap_multiple_output_busses(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "transformer_optimize_multiple_output_busses"
        ]

        D1.transformer(
            model=self.model,
            dict_asset=dict_asset,
            transformer=self.transformers,
            bus=self.busses,
        )

        # two output busses and one input bus
        assert (
            len([str(i) for i in self.model._nodes[-1].outputs]) == 2
        ), f"Amount of output busses of transformer should be two but is {len([str(i) for i in self.model._nodes[-1].outputs])}."
        assert (
            len([str(i) for i in self.model._nodes[-1].inputs]) == 1
        ), f"Amount of input busses of transformer should be one but is {len([str(i) for i in self.model._nodes[-1].inputs])}."
        assert (
            len(self.model._nodes[-1].conversion_factors) == 2,
            f"The amount of conversion factors should be two to match the amount of output busses but is {len(self.model._nodes[-1].conversion_factors)}",
        )
        # # checks done with helper function (see func for more information)
        # self.helper_test_transformer_in_model_and_dict(
        #     optimize=True, dict_asset=dict_asset, multiple_outputs=True
        # )

    # def test_transformer_optimize_cap_multiple_output_busses_multiple_inst_cap(self):
    #     dict_asset = self.dict_values[ENERGY_CONVERSION][
    #         "transformer_optimize_multiple_output_busses"
    #     ]
    #
    #     inst_cap = [10, 15]
    #     dict_asset[INSTALLED_CAP][VALUE] = inst_cap
    #
    #     D1.transformer(
    #         model=self.model,
    #         dict_asset=dict_asset,
    #         transformer=self.transformers,
    #         bus=self.busses,
    #     )
    #
    #     output_bus_list = [
    #         self.model._nodes[-1].outputs.data[self.busses[bus_name]]
    #         for bus_name in dict_asset[OUTFLOW_DIRECTION]
    #     ]
    #     for cap, output_bus in zip(inst_cap, output_bus_list):
    #         assert output_bus.investment.existing == cap
    #
    # def test_transformer_optimize_cap_multiple_output_busses_multiple_max_add_cap(self):
    #     dict_asset = self.dict_values[ENERGY_CONVERSION][
    #         "transformer_optimize_multiple_output_busses"
    #     ]
    #
    #     inst_cap = [100, 500]
    #     dict_asset[MAXIMUM_ADD_CAP][VALUE] = inst_cap
    #
    #     D1.transformer(
    #         model=self.model,
    #         dict_asset=dict_asset,
    #         transformer=self.transformers,
    #         bus=self.busses,
    #     )
    #
    #     output_bus_list = [
    #         self.model._nodes[-1].outputs.data[self.busses[bus_name]]
    #         for bus_name in dict_asset[OUTFLOW_DIRECTION]
    #     ]
    #     for cap, output_bus in zip(inst_cap, output_bus_list):
    #         assert output_bus.investment.maximum == cap

    def test_transformer_optimize_cap_multiple_output_busses_multiple_single_efficiency_raises_error(
        self,
    ):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "transformer_optimize_multiple_output_busses"
        ]

        dict_asset[EFFICIENCY][VALUE] = 0.1
        with pytest.raises(ValueError):
            D1.transformer(
                model=self.model,
                dict_asset=dict_asset,
                transformer=self.transformers,
                bus=self.busses,
            )

    def test_transformer_fix_cap_single_busses(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "transformer_fix_single_busses"
        ]

        D1.transformer(
            model=self.model,
            dict_asset=dict_asset,
            transformer=self.transformers,
            bus=self.busses,
        )

        # only one output and one input bus
        assert (
            len([str(i) for i in self.model._nodes[-1].outputs]) == 1
        ), f"Amount of output busses of transformer should be one but is {len([str(i) for i in self.model._nodes[-1].outputs])}."
        assert (
            len([str(i) for i in self.model._nodes[-1].inputs]) == 1
        ), f"Amount of input busses of transformer should be one but is {len([str(i) for i in self.model._nodes[-1].inputs])}."

        # checks done with helper function (see func for more information)
        self.helper_test_transformer_in_model_and_dict(
            optimize=False, dict_asset=dict_asset
        )

    def test_transformer_fix_cap_single_busses_raises_error_if_parameter_provided_as_list(
        self,
    ):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "transformer_fix_single_busses"
        ]

        dict_asset[EFFICIENCY][VALUE] = [0.1, 0.2]

        with pytest.raises(ValueError):
            D1.transformer(
                model=self.model,
                dict_asset=dict_asset,
                transformer=self.transformers,
                bus=self.busses,
            )

    def test_transformer_optimize_cap_single_busses_raises_error_if_parameter_provided_as_list(
        self,
    ):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "transformer_optimize_single_busses"
        ]

        dict_asset[EFFICIENCY][VALUE] = [0.1, 0.2]

        with pytest.raises(ValueError):
            D1.transformer(
                model=self.model,
                dict_asset=dict_asset,
                transformer=self.transformers,
                bus=self.busses,
            )

    def test_transformer_fix_cap_multiple_input_busses(self,):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "transformer_fix_multiple_input_busses"
        ]

        D1.transformer(
            model=self.model,
            dict_asset=dict_asset,
            transformer=self.transformers,
            bus=self.busses,
        )

        # one output bus and two input busses
        assert (
            len([str(i) for i in self.model._nodes[-1].outputs]) == 1
        ), f"Amount of output busses of transformer should be one but is {len([str(i) for i in self.model._nodes[-1].outputs])}."
        assert (
            len([str(i) for i in self.model._nodes[-1].inputs]) == 2
        ), f"Amount of input busses of transformer should be two but is {len([str(i) for i in self.model._nodes[-1].inputs])}."
        assert (
            len(self.model._nodes[-1].conversion_factors) == 2,
            f"The amount of conversion factors should be two to match the amount of input busses but is {len(self.model._nodes[-1].conversion_factors)}",
        )

        # checks done with helper function (see func for more information)
        self.helper_test_transformer_in_model_and_dict(
            optimize=False, dict_asset=dict_asset
        )

    def test_transformer_fix_cap_multiple_output_busses(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "transformer_fix_multiple_output_busses"
        ]

        D1.transformer(
            model=self.model,
            dict_asset=dict_asset,
            transformer=self.transformers,
            bus=self.busses,
        )

        # two output busses and one input bus
        assert (
            len([str(i) for i in self.model._nodes[-1].outputs]) == 2
        ), f"Amount of output busses of transformer should be two but is {len([str(i) for i in self.model._nodes[-1].outputs])}."
        assert (
            len([str(i) for i in self.model._nodes[-1].inputs]) == 1
        ), f"Amount of input busses of transformer should be one but is {len([str(i) for i in self.model._nodes[-1].inputs])}."
        assert (
            len(self.model._nodes[-1].conversion_factors) == 2,
            f"The amount of conversion factors should be two to match the amount of output busses but is {len(self.model._nodes[-1].conversion_factors)}",
        )

        # checks done with helper function (see func for more information)
        self.helper_test_transformer_in_model_and_dict(
            optimize=False, dict_asset=dict_asset, multiple_outputs=True
        )

    def test_transformer_fix_cap_multiple_output_busses_multiple_inst_cap(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "transformer_fix_multiple_output_busses"
        ]

        inst_cap = [10, 15]
        dict_asset[INSTALLED_CAP][VALUE] = inst_cap

        D1.transformer(
            model=self.model,
            dict_asset=dict_asset,
            transformer=self.transformers,
            bus=self.busses,
        )

        output_bus_list = [
            self.model._nodes[-1].outputs.data[self.busses[bus_name]]
            for bus_name in dict_asset[OUTFLOW_DIRECTION]
        ]
        for cap, output_bus in zip(inst_cap, output_bus_list):
            assert output_bus.nominal_value == cap

    def test_transformer_fix_cap_multiple_output_busses_multiple_single_efficiency_raises_error(
        self,
    ):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "transformer_fix_multiple_output_busses"
        ]

        dict_asset[EFFICIENCY][VALUE] = 0.1
        with pytest.raises(ValueError):
            D1.transformer(
                model=self.model,
                dict_asset=dict_asset,
                transformer=self.transformers,
                bus=self.busses,
            )

    def test_chp_fix_cap(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION]["chp_fix"]

        D1.chp(
            model=self.model,
            dict_asset=dict_asset,
            extractionTurbineCHP=self.transformers,
            bus=self.busses,
        )

        # only two output and one input bus
        assert (
            len([str(i) for i in self.model._nodes[-1].outputs]) == 2
        ), f"Amount of output busses of chp should be 2 but is {len([str(i) for i in self.model._nodes[-1].outputs])}."
        assert (
            len([str(i) for i in self.model._nodes[-1].inputs]) == 1
        ), f"Amount of input busses of chp should be one but is {len([str(i) for i in self.model._nodes[-1].inputs])}."

    def test_chp_optimize_cap(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION]["chp_optimize"]

        D1.chp(
            model=self.model,
            dict_asset=dict_asset,
            extractionTurbineCHP=self.transformers,
            bus=self.busses,
        )

        # only two output and one input bus
        assert (
            len([str(i) for i in self.model._nodes[-1].outputs]) == 2
        ), f"Amount of output busses of chp should be 2 but is {len([str(i) for i in self.model._nodes[-1].outputs])}."
        assert (
            len([str(i) for i in self.model._nodes[-1].inputs]) == 1
        ), f"Amount of input busses of chp should be one but is {len([str(i) for i in self.model._nodes[-1].inputs])}."

    def test_chp_missing_beta(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION]["chp_missing_beta"]

        with pytest.raises(MissingParameterError):
            D1.chp(
                model=self.model,
                dict_asset=dict_asset,
                extractionTurbineCHP=self.transformers,
                bus=self.busses,
            )

    def test_chp_wrong_beta_formatting(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION]["chp_wrong_beta_formatting"]

        with pytest.raises(WrongParameterFormatError):
            D1.chp(
                model=self.model,
                dict_asset=dict_asset,
                extractionTurbineCHP=self.transformers,
                bus=self.busses,
            )

    def test_chp_wrong_efficiency_formatting(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "chp_wrong_efficiency_formatting"
        ]

        with pytest.raises(WrongParameterFormatError):
            D1.chp(
                model=self.model,
                dict_asset=dict_asset,
                extractionTurbineCHP=self.transformers,
                bus=self.busses,
            )

    def test_chp_wrong_outflow_bus_energy_vector(self):
        dict_asset = self.dict_values[ENERGY_CONVERSION][
            "chp_wrong_outflow_bus_energy_vector"
        ]

        with pytest.raises(WrongParameterFormatError):
            D1.chp(
                model=self.model,
                dict_asset=dict_asset,
                extractionTurbineCHP=self.transformers,
                bus=self.busses,
            )


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
        * input bus has appropriate values for `fix` and `variable_costs` (depending on 'dispatchable')
        * expected amount of input flows according to `amount_inputs`

        """
        # self.sinks should contain the sink (key = label, value = sink object)
        assert dict_asset[LABEL] in self.sinks
        assert isinstance(self.sinks[dict_asset[LABEL]], network.Sink)

        # check amount of inputs to sink
        assert len([str(i) for i in self.model._nodes[-1].inputs]) == amount_inputs

        # self.models should contain the sink (indirectly tested)
        # check input bus(es) (``fix` and `variable_costs`)
        # foreach input bus - these values are expected to be different
        # depending on `dispatchable`
        if amount_inputs == 1:
            inflow_direction_s = [dict_asset[INFLOW_DIRECTION]]
            if dispatchable is True:
                dispatch_price = [dict_asset[DISPATCH_PRICE][VALUE]]
        elif amount_inputs > 1:
            inflow_direction_s = dict_asset[INFLOW_DIRECTION]
            if dispatchable is True:
                dispatch_price = dict_asset[DISPATCH_PRICE][VALUE]
        else:
            raise ValueError("`amount_inputs` should be int but not zero.")
        for i, inflow_direction in enumerate(inflow_direction_s):
            input_bus = self.model._nodes[-1].inputs[self.busses[inflow_direction]]
            if dispatchable is False:
                assert_series_equal(input_bus.fix, dict_asset[TIMESERIES])
                assert (
                    input_bus.variable_costs.default == 0
                )  # this only is a real check if dispatch_price is not 0
            elif dispatchable is True:
                assert len(input_bus.fix) == 0
                assert input_bus.variable_costs.default == dispatch_price[i]
            else:
                raise ValueError(
                    f"`dispatchable` should be True/False but is '{dispatchable}'"
                )

    def test_sink_non_dispatchable_single_input_bus(self):
        dict_asset = self.dict_values[ENERGY_CONSUMPTION]["non_dispatchable_single"]
        dict_asset[TIMESERIES] = self.time_series

        D1.sink_non_dispatchable(
            model=self.model, dict_asset=dict_asset, sink=self.sinks, bus=self.busses,
        )

        self.helper_test_sink_in_model_and_dict(
            dispatchable=False, dict_asset=dict_asset, amount_inputs=1
        )

    def test_sink_non_dispatchable_multiple_input_busses(self):
        dict_asset = self.dict_values[ENERGY_CONSUMPTION]["non_dispatchable_multiple"]
        dict_asset[TIMESERIES] = self.time_series

        D1.sink_non_dispatchable(
            model=self.model, dict_asset=dict_asset, sink=self.sinks, bus=self.busses,
        )

        self.helper_test_sink_in_model_and_dict(
            dispatchable=False, dict_asset=dict_asset, amount_inputs=2
        )

    def test_sink_dispatchable_single_input_bus(self):
        dict_asset = self.dict_values[ENERGY_CONSUMPTION]["dispatchable_single"]

        D1.sink_dispatchable_optimize(
            model=self.model, dict_asset=dict_asset, sink=self.sinks, bus=self.busses,
        )

        self.helper_test_sink_in_model_and_dict(
            dispatchable=True, dict_asset=dict_asset, amount_inputs=1
        )

    def test_sink_dispatchable_multiple_input_busses(self):
        dict_asset = self.dict_values[ENERGY_CONSUMPTION]["dispatchable_multiple"]

        D1.sink_dispatchable_optimize(
            model=self.model, dict_asset=dict_asset, sink=self.sinks, bus=self.busses,
        )

        self.helper_test_sink_in_model_and_dict(
            dispatchable=True, dict_asset=dict_asset, amount_inputs=2
        )


class TestSourceComponent:
    @pytest.fixture(autouse=True)
    def setup_class(self, get_json, get_model, get_busses):
        """ Sets up class attributes for the tests. """
        self.dict_values = get_json
        self.model = get_model
        self.busses = get_busses
        self.sources = {}
        self.time_series = pd.Series(data=[10, 11, 12])

    def helper_test_source_in_model_and_dict(
        self, dict_asset, dispatchable, mode, timeseries=None
    ):
        """
        Helps testing whether `self.sources` and `self.model` was updated.

        Checks done:
        * self.sources contains the source (key = label, value = source object)
        * self.models contains the source (indirectly tested)
        * output bus has appropriate values for `actual_value`, investment and `variable_costs` (depending on `dispatchable`, `mode` and `timeseries`)
        * source only has one output flow

        """
        # self.sinks should contain the sink (key = label, value = sink object)
        assert dict_asset[LABEL] in self.sources
        assert isinstance(self.sources[dict_asset[LABEL]], network.Source)

        # check amount of outputs from source (only one)
        assert len([str(i) for i in self.model._nodes[-1].outputs]) == 1

        # self.models should contain the source (indirectly tested)
        # check output bus (`actual_value`, `investment` and `variable_costs`).
        # these values are expected to be different depending on `dispatchable`, `mode` and `timeseries`
        output_bus = self.model._nodes[-1].outputs[
            self.busses[dict_asset[OUTFLOW_DIRECTION]]
        ]
        if mode == "fix":
            assert (
                output_bus.variable_costs.default == dict_asset[DISPATCH_PRICE][VALUE]
            )
            assert output_bus.investment is None
            if dispatchable is False:
                assert output_bus.nominal_value == dict_asset[INSTALLED_CAP][VALUE]
                assert_series_equal(output_bus.fix, dict_asset[TIMESERIES])
                assert output_bus.max == []
            elif dispatchable is True:
                assert output_bus.nominal_value == dict_asset[INSTALLED_CAP][VALUE]
        elif mode == "optimize":
            assert output_bus.nominal_value is None
            if dispatchable is False:
                assert_series_equal(output_bus.fix, dict_asset[TIMESERIES_NORMALIZED])
                assert output_bus.max == []
            if timeseries == "normalized":
                assert (
                    output_bus.investment.ep_costs
                    == dict_asset[SIMULATION_ANNUITY][VALUE]
                    / dict_asset[TIMESERIES_PEAK][VALUE]
                )
                assert (
                    output_bus.variable_costs.default
                    == dict_asset[DISPATCH_PRICE][VALUE]
                    / dict_asset[TIMESERIES_PEAK][VALUE]
                )
                if dispatchable is True:
                    assert_series_equal(
                        output_bus.max, dict_asset[TIMESERIES_NORMALIZED]
                    )
            elif timeseries == "not_normalized":
                assert (
                    output_bus.investment.ep_costs
                    == dict_asset[SIMULATION_ANNUITY][VALUE]
                )
                assert (
                    output_bus.variable_costs.default
                    == dict_asset[DISPATCH_PRICE][VALUE]
                )
                assert output_bus.max == []
            else:
                raise ValueError(
                    f"`timeseries` should be 'normalized' or 'not_normalized' but is {timeseries}."
                )
        else:
            raise ValueError(f"`mode` should be 'fix' or 'optimize' but is {mode}.")

    ## non dispatchable
    def test_source_non_dispatchable_optimize(self):
        dict_asset = self.dict_values[ENERGY_PRODUCTION][
            "non_dispatchable_source_optimize"
        ]
        dict_asset[TIMESERIES_NORMALIZED] = self.time_series / max(self.time_series)
        dict_asset[TIMESERIES_PEAK] = {"unit": "kWp/H", "value": self.time_series.max()}

        D1.source(
            model=self.model,
            dict_asset=dict_asset,
            source=self.sources,
            bus=self.busses,
        )

        # checks done with helper function (see func for more information)
        self.helper_test_source_in_model_and_dict(
            dict_asset=dict_asset,
            dispatchable=False,
            mode="optimize",
            timeseries="normalized",
        )

    def test_source_non_dispatchable_fix(self):
        dict_asset = self.dict_values[ENERGY_PRODUCTION]["non_dispatchable_source_fix"]
        dict_asset[TIMESERIES] = self.time_series
        dict_asset[TIMESERIES_PEAK] = {"unit": "kWp/H", "value": self.time_series.max()}

        D1.source(
            model=self.model,
            dict_asset=dict_asset,
            source=self.sources,
            bus=self.busses,
        )

        # checks done with helper function (see func for more information)
        self.helper_test_source_in_model_and_dict(
            dict_asset=dict_asset, dispatchable=False, mode="fix"
        )

    ## dispatchable
    def test_source_dispatchable_optimize_normalized_timeseries(self):
        dict_asset = self.dict_values[ENERGY_PRODUCTION]["dispatchable_source_optimize"]
        dict_asset[TIMESERIES_NORMALIZED] = self.time_series / max(self.time_series)
        dict_asset[TIMESERIES_PEAK] = {"unit": "kWp/H", "value": self.time_series.max()}

        D1.source(
            model=self.model,
            dict_asset=dict_asset,
            source=self.sources,
            bus=self.busses,
        )

        # checks done with helper function (see func for more information)
        self.helper_test_source_in_model_and_dict(
            dict_asset=dict_asset,
            dispatchable=True,
            mode="optimize",
            timeseries="normalized",
        )

    def test_source_dispatchable_optimize_timeseries_not_normalized_timeseries(self,):
        dict_asset = self.dict_values[ENERGY_PRODUCTION]["dispatchable_source_optimize"]
        dict_asset[TIMESERIES] = self.time_series
        dict_asset[TIMESERIES_PEAK] = {"unit": "kWp/H", "value": self.time_series.max()}

        D1.source(
            model=self.model,
            dict_asset=dict_asset,
            source=self.sources,
            bus=self.busses,
        )
        # checks done with helper function (see func for more information)
        self.helper_test_source_in_model_and_dict(
            dict_asset=dict_asset,
            dispatchable=True,
            mode="optimize",
            timeseries="not_normalized",
        )

    def test_source_dispatchable_fix_normalized_timeseries(self):
        dict_asset = self.dict_values[ENERGY_PRODUCTION]["dispatchable_source_fix"]
        dict_asset[TIMESERIES_NORMALIZED] = self.time_series / max(self.time_series)
        dict_asset[TIMESERIES_PEAK] = {"unit": "kWp/H", "value": self.time_series.max()}

        D1.source(
            model=self.model,
            dict_asset=dict_asset,
            source=self.sources,
            bus=self.busses,
        )
        # checks done with helper function (see func for more information)
        self.helper_test_source_in_model_and_dict(
            dict_asset=dict_asset,
            dispatchable=True,
            mode="fix",
            timeseries="normalized",
        )

    def test_source_dispatchable_fix_timeseries_not_normalized_timeseries(self):
        dict_asset = self.dict_values[ENERGY_PRODUCTION]["dispatchable_source_fix"]
        dict_asset[TIMESERIES] = self.time_series
        dict_asset[TIMESERIES_PEAK] = {"unit": "kWp/H", "value": self.time_series.max()}

        D1.source(
            model=self.model,
            dict_asset=dict_asset,
            source=self.sources,
            bus=self.busses,
        )
        # checks done with helper function (see func for more information)
        self.helper_test_source_in_model_and_dict(
            dict_asset=dict_asset,
            dispatchable=True,
            mode="fix",
            timeseries="not_normalized",
        )


class TestStorageComponent:
    @pytest.fixture(autouse=True)
    def setup_class(self, get_json, get_model, get_busses):
        """ Sets up class attributes for the tests. """
        self.dict_values = get_json
        self.model = get_model
        self.busses = get_busses
        self.storages = {}

    def test_storage_fix(self):
        dict_asset = self.dict_values[ENERGY_STORAGE]["storage_fix"]
        D1.storage(
            model=self.model,
            dict_asset=dict_asset,
            bus=self.busses,
            storage=self.storages,
        )

        # self.storages should contain the storage (key = label, value = storage object)
        assert dict_asset[LABEL] in self.storages
        assert isinstance(
            self.storages[dict_asset[LABEL]], solph.components.GenericStorage
        )

        # check value of `existing`, `investment` and `nominal_value`(`nominal_storage_capacity`)
        input_bus = self.model._nodes[-1].inputs[self.busses["Storage bus"]]
        output_bus = self.model._nodes[-1].outputs[self.busses["Storage bus"]]

        assert hasattr(input_bus, "existing") is False
        assert input_bus.investment is None
        assert (
            input_bus.nominal_value
            == dict_asset[STORAGE_CAPACITY][INSTALLED_CAP][VALUE]
        )

        assert hasattr(output_bus, "existing") is False
        assert output_bus.investment is None
        assert output_bus.nominal_value == dict_asset[INPUT_POWER][INSTALLED_CAP][VALUE]

        assert (
            hasattr(self.model._nodes[-1], "existing") is False
        )  # todo probably not necessary parameter
        assert self.model._nodes[-1].investment is None
        assert (
            self.model._nodes[-1].nominal_storage_capacity
            == dict_asset[OUTPUT_POWER][INSTALLED_CAP][VALUE]
        )

        # # check that invest_relation_input_capacity and invest_relation_output_capacity is not added
        assert self.model._nodes[-1].invest_relation_input_capacity is None
        assert self.model._nodes[-1].invest_relation_output_capacity is None

        assert (
            self.model._nodes[-1].fixed_losses_relative.default
            == dict_asset[STORAGE_CAPACITY][THERM_LOSSES_REL][VALUE]
        )
        assert (
            self.model._nodes[-1].fixed_losses_absolute.default
            == dict_asset[STORAGE_CAPACITY][THERM_LOSSES_ABS][VALUE]
        )

    def test_storage_optimize(self):
        dict_asset = self.dict_values[ENERGY_STORAGE]["storage_optimize"]
        dict_asset[STORAGE_CAPACITY][MAXIMUM_CAP] = {VALUE: None, UNIT: "kWh"}
        dict_asset[INPUT_POWER][MAXIMUM_CAP] = {VALUE: None, UNIT: "kWh"}
        dict_asset[OUTPUT_POWER][MAXIMUM_CAP] = {VALUE: None, UNIT: "kWh"}
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_REL] = {VALUE: 0.001, UNIT: "no_unit"}
        D1.storage(
            model=self.model,
            dict_asset=dict_asset,
            bus=self.busses,
            storage=self.storages,
        )

        # self.storages should contain the storage (key = label, value = storage object)
        assert dict_asset[LABEL] in self.storages
        assert isinstance(
            self.storages[dict_asset[LABEL]], solph.components.GenericStorage
        )

        # check value of `existing`, `investment` and `nominal_value`(`nominal_storage_capacity`)
        input_bus = self.model._nodes[-1].inputs[self.busses["Storage bus"]]
        output_bus = self.model._nodes[-1].outputs[self.busses["Storage bus"]]

        assert (
            input_bus.investment.existing
            == dict_asset[INPUT_POWER][INSTALLED_CAP][VALUE]
        )
        assert (
            input_bus.investment.ep_costs
            == dict_asset[INPUT_POWER][SIMULATION_ANNUITY][VALUE]
        )
        assert input_bus.nominal_value is None

        assert (
            output_bus.investment.existing
            == dict_asset[OUTPUT_POWER][INSTALLED_CAP][VALUE]
        )
        assert (
            output_bus.investment.ep_costs
            == dict_asset[OUTPUT_POWER][SIMULATION_ANNUITY][VALUE]
        )
        assert output_bus.nominal_value is None

        # assert self.model._nodes[-1].existing ==  dict_asset[STORAGE_CAPACITY][INSTALLED_CAP][VALUE]  # todo probably not necessary parameter
        assert (
            self.model._nodes[-1].investment.ep_costs
            == dict_asset[STORAGE_CAPACITY][SIMULATION_ANNUITY][VALUE]
        )
        assert self.model._nodes[-1].nominal_storage_capacity is None

        # check that invest_relation_input_capacity and invest_relation_output_capacity is added
        assert (
            self.model._nodes[-1].invest_relation_input_capacity
            == dict_asset[INPUT_POWER][C_RATE][VALUE]
        )
        assert (
            self.model._nodes[-1].invest_relation_output_capacity
            == dict_asset[OUTPUT_POWER][C_RATE][VALUE]
        )

        assert (
            self.model._nodes[-1].fixed_losses_relative.default
            == dict_asset[STORAGE_CAPACITY][THERM_LOSSES_REL][VALUE]
        )
        assert (
            self.model._nodes[-1].fixed_losses_absolute.default
            == dict_asset[STORAGE_CAPACITY][THERM_LOSSES_ABS][VALUE]
        )

    def test_storage_optimize_investment_minimum_0_float(self):
        # Test if minimum value is zero if thermal losses are zero (float)
        dict_asset = self.dict_values[ENERGY_STORAGE]["storage_optimize"]
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_REL] = {VALUE: 0, UNIT: "no_unit"}
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_ABS] = {VALUE: 0, UNIT: "kWh"}

        D1.storage(
            model=self.model,
            dict_asset=dict_asset,
            bus=self.busses,
            storage=self.storages,
        )

        assert (
            self.model._nodes[-1].investment.minimum == 0
        ), f"investment.minimum should be zero with {THERM_LOSSES_REL} and {THERM_LOSSES_ABS} that are equal to zero"

    def test_storage_optimize_investment_minimum_0_time_series(self):
        # Test if minimum value is zero if thermal losses are zero (time series)
        dict_asset = self.dict_values[ENERGY_STORAGE]["storage_optimize"]
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_REL] = {
            VALUE: [0, 0, 0, 0],
            UNIT: "no_unit",
        }
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_ABS] = {
            VALUE: [0, 0, 0, 0],
            UNIT: "kWh",
        }

        D1.storage(
            model=self.model,
            dict_asset=dict_asset,
            bus=self.busses,
            storage=self.storages,
        )

        assert (
            self.model._nodes[-1].investment.minimum == 0
        ), f"investment.minimum should be zero with {THERM_LOSSES_REL} and {THERM_LOSSES_ABS} that are equal to zero"

    def test_storage_optimize_investment_minimum_1_rel_float(self):
        # Test if minimum value is one if relative thermal losses are not zero (float)
        dict_asset = self.dict_values[ENERGY_STORAGE]["storage_optimize"]
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_REL] = {VALUE: 0.001, UNIT: "no_unit"}
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_ABS] = {VALUE: 0, UNIT: "kWh"}

        D1.storage(
            model=self.model,
            dict_asset=dict_asset,
            bus=self.busses,
            storage=self.storages,
        )

        assert (
            self.model._nodes[-1].investment.minimum == 1
        ), f"investment.minimum should be one with non-zero {THERM_LOSSES_REL}"

    def test_storage_optimize_investment_minimum_1_abs_float(self):
        # Test if minimum value is one if absolute thermal losses are not zero (float)
        dict_asset = self.dict_values[ENERGY_STORAGE]["storage_optimize"]
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_REL] = {VALUE: 0, UNIT: "no_unit"}
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_ABS] = {VALUE: 0.001, UNIT: "kWh"}

        D1.storage(
            model=self.model,
            dict_asset=dict_asset,
            bus=self.busses,
            storage=self.storages,
        )

        assert (
            self.model._nodes[-1].investment.minimum == 1
        ), f"investment.minimum should be one with non-zero {THERM_LOSSES_ABS}"

    def test_storage_optimize_investment_minimum_1_rel_times_series(self):
        # Test if minimum value is one if relative thermal losses are not zero (time series)
        dict_asset = self.dict_values[ENERGY_STORAGE]["storage_optimize"]
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_REL] = {
            VALUE: [0.001, 0.001, 0.001, 0.001],
            UNIT: "no_unit",
        }
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_ABS] = {VALUE: 0, UNIT: "kWh"}

        D1.storage(
            model=self.model,
            dict_asset=dict_asset,
            bus=self.busses,
            storage=self.storages,
        )

        assert (
            self.model._nodes[-1].investment.minimum == 1
        ), f"investment.minimum should be one with non-zero {THERM_LOSSES_REL}"

    def test_storage_optimize_investment_minimum_1_abs_times_series(self):
        # Test if minimum value is one if absolute thermal losses are not zero (time series)
        dict_asset = self.dict_values[ENERGY_STORAGE]["storage_optimize"]
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_REL] = {VALUE: 0, UNIT: "no_unit"}
        dict_asset[STORAGE_CAPACITY][THERM_LOSSES_ABS] = {
            VALUE: [0.001, 0.001, 0.001, 0.001],
            UNIT: "kWh",
        }

        D1.storage(
            model=self.model,
            dict_asset=dict_asset,
            bus=self.busses,
            storage=self.storages,
        )

        assert (
            self.model._nodes[-1].investment.minimum == 1
        ), f"investment.minimum should be one with non-zero {THERM_LOSSES_ABS}"


### other functionalities


class TestBusFunction:
    @pytest.fixture(autouse=True)
    def setup_class(self, get_model, get_busses):
        self.model = get_model
        self.busses = get_busses

    def test_bus_add_to_empty_dict(self):
        label = "Test bus"
        busses = {}
        D1.bus(model=self.model, name=label, bus=busses)

        # self.model should contain the test bus
        assert self.model._nodes[-1].label == label
        assert isinstance(self.model._nodes[-1], network.Bus)

        # busses should contain the test bus (key = label, value = bus object)
        assert label in busses
        assert isinstance(busses[label], network.Bus)

    def test_bus_add_to_not_empty_dict(self):
        label = "Test bus 2"
        D1.bus(model=self.model, name=label, bus=self.busses)

        # self.model should contain the test bus
        assert self.model._nodes[-1].label == label
        assert isinstance(self.model._nodes[-1], network.Bus)

        # self.busses should contain the test bus (key = label, value = bus object)
        assert label in self.busses
        assert isinstance(self.busses[label], network.Bus)


def test_check_optimize_cap_raise_error(get_json, get_model, get_busses):
    dict_values = get_json
    model = get_model
    busses = get_busses
    test_asset = dict_values[ENERGY_CONVERSION]["test_asset_for_error_raising"]
    test_asset[OPTIMIZE_CAP][VALUE] = "wrong value"

    msg = f"Input error! '{OPTIMIZE_CAP}' of asset {test_asset[LABEL]}\n should be True/False but is {test_asset[OPTIMIZE_CAP][VALUE]}."
    with pytest.raises(ValueError, match=msg):
        D1.check_optimize_cap(
            model=model,
            dict_asset=test_asset,
            func_constant=D1.transformer_constant_efficiency_fix,
            func_optimize=D1.transformer_constant_efficiency_optimize,
            bus=busses,
            transformers={},
        )
