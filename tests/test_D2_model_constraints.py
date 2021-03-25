from oemof import solph
import os
import pytest
import mock
import pandas as pd
import logging
import shutil

import multi_vector_simulator.D2_model_constraints as D2
import multi_vector_simulator.A0_initialization as A0
import multi_vector_simulator.B0_data_input_json as B0
import multi_vector_simulator.C0_data_processing as C0
import multi_vector_simulator.D0_modelling_and_optimization as D0

from multi_vector_simulator.utils.constants import (
    DEFAULT_WEIGHTS_ENERGY_CARRIERS,
    CSV_EXT,
)

from multi_vector_simulator.utils.constants_json_strings import (
    OEMOF_SINK,
    OEMOF_SOURCE,
    OEMOF_BUSSES,
    ENERGY_PRODUCTION,
    ENERGY_PROVIDERS,
    ENERGY_VECTOR,
    VALUE,
    LABEL,
    OUTFLOW_DIRECTION,
    DSO_CONSUMPTION,
    RENEWABLE_SHARE_DSO,
    RENEWABLE_ASSET_BOOL,
    MAXIMUM_EMISSIONS,
    CONSTRAINTS,
    MINIMAL_RENEWABLE_FACTOR,
    MINIMAL_DEGREE_OF_AUTONOMY,
    ENERGY_CONSUMPTION,
    EXCESS_SINK,
    INFLOW_DIRECTION,
    DSO_FEEDIN,
    NET_ZERO_ENERGY,
    EVALUATED_PERIOD,
    SIMULATION_SETTINGS,
)

from multi_vector_simulator.utils.constants import OUTPUT_FOLDER

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


def test_prepare_constraint_minimal_renewable_share():
    pv_plant = "PV"
    diesel = "Diesel"
    electricity = "Electricity"
    fuel = "Fuel"
    dso_1 = "DSO_1"
    dso_2 = "DSO_2"
    dict_values = {
        ENERGY_PROVIDERS: {
            dso_1: {LABEL: dso_1, RENEWABLE_SHARE_DSO: {VALUE: 0.3}},
            dso_2: {LABEL: dso_2, RENEWABLE_SHARE_DSO: {VALUE: 0.7}},
        },
        ENERGY_PRODUCTION: {
            pv_plant: {
                RENEWABLE_ASSET_BOOL: {VALUE: True},
                LABEL: pv_plant,
                OUTFLOW_DIRECTION: electricity,
                ENERGY_VECTOR: electricity,
            },
            diesel: {
                RENEWABLE_ASSET_BOOL: {VALUE: False},
                LABEL: diesel,
                OUTFLOW_DIRECTION: fuel,
                ENERGY_VECTOR: electricity,
            },
            dso_1
            + DSO_CONSUMPTION: {
                LABEL: dso_1 + DSO_CONSUMPTION,
                OUTFLOW_DIRECTION: electricity,
                ENERGY_VECTOR: electricity,
            },
            dso_2
            + DSO_CONSUMPTION: {
                LABEL: dso_2 + DSO_CONSUMPTION,
                OUTFLOW_DIRECTION: electricity,
                ENERGY_VECTOR: electricity,
            },
        },
    }
    dict_model = {
        OEMOF_SOURCE: {
            pv_plant: pv_plant,
            diesel: diesel,
            dso_1 + DSO_CONSUMPTION: dso_1 + DSO_CONSUMPTION,
            dso_2 + DSO_CONSUMPTION: dso_2 + DSO_CONSUMPTION,
        },
        OEMOF_BUSSES: {electricity: electricity, fuel: fuel},
    }

    (
        renewable_assets,
        non_renewable_assets,
    ) = D2.prepare_constraint_minimal_renewable_share(
        dict_values=dict_values, dict_model=dict_model,
    )

    assert (
        pv_plant in renewable_assets
    ), f"The {pv_plant} is not added to the renewable assets."
    assert (
        pv_plant not in non_renewable_assets
    ), f"The {pv_plant} is not added to the renewable assets."
    assert (
        renewable_assets[pv_plant][D2.RENEWABLE_SHARE_ASSET_FLOW] == 1
    ), f"The renewable share of asset {pv_plant} is added incorrectly."

    assert (
        diesel in non_renewable_assets
    ), f"The {diesel} is added to the renewable assets."
    assert (
        diesel not in renewable_assets
    ), f"The {diesel} is not added to the non-renewable assets."
    assert (
        non_renewable_assets[diesel][D2.RENEWABLE_SHARE_ASSET_FLOW] == 0
    ), f"The renewable share of asset {diesel} is added incorrectly."

    assert (
        dso_1 + DSO_CONSUMPTION in renewable_assets
    ), f"The {dso_1 + DSO_CONSUMPTION} is not added as a renewable source."
    assert (
        renewable_assets[dso_1 + DSO_CONSUMPTION][D2.RENEWABLE_SHARE_ASSET_FLOW] == 0.3
    ), f"The renewable share of asset {dso_1 + DSO_CONSUMPTION} is added incorrectly."

    assert (
        dso_1 + DSO_CONSUMPTION in non_renewable_assets
    ), f"The {dso_1 + DSO_CONSUMPTION} is not added as a non-renewable source."
    assert (
        non_renewable_assets[dso_1 + DSO_CONSUMPTION][D2.RENEWABLE_SHARE_ASSET_FLOW]
        == 0.3
    ), f"The renewable share of asset {dso_1 + DSO_CONSUMPTION} is added incorrectly."

    assert (
        dso_2 + DSO_CONSUMPTION in renewable_assets
    ), f"The {dso_2 + DSO_CONSUMPTION} is not added as a renewable source."
    assert (
        renewable_assets[dso_2 + DSO_CONSUMPTION][D2.RENEWABLE_SHARE_ASSET_FLOW] == 0.7
    ), f"The renewable share of asset {dso_2 + DSO_CONSUMPTION} is added incorrectly."

    assert (
        dso_2 + DSO_CONSUMPTION in non_renewable_assets
    ), f"The {dso_2 + DSO_CONSUMPTION} is not added as a non-renewable source."
    assert (
        non_renewable_assets[dso_2 + DSO_CONSUMPTION][D2.RENEWABLE_SHARE_ASSET_FLOW]
        == 0.7
    ), f"The renewable share of asset {dso_2 + DSO_CONSUMPTION} is added incorrectly."


def test_prepare_demand_assets():
    asset = "asset"
    demand_profiles = "demand"
    electricity = "Electricity"
    dict_values = {
        ENERGY_CONSUMPTION: {
            asset + EXCESS_SINK: {},
            demand_profiles: {
                LABEL: demand_profiles,
                INFLOW_DIRECTION: electricity,
                ENERGY_VECTOR: electricity,
            },
        },
    }
    dict_model = {
        OEMOF_SINK: {demand_profiles: demand_profiles},
        OEMOF_BUSSES: {electricity: electricity},
    }

    demands = D2.prepare_demand_assets(dict_values, dict_model,)

    assert (
        demand_profiles in demands
    ), f"Demand asset {demand_profiles} should be in the demands taken into account for the constraints, but is not included in it ({demands.keys()})."
    exp = {
        D2.OEMOF_SOLPH_OBJECT_ASSET: dict_model[OEMOF_SINK][
            dict_values[ENERGY_CONSUMPTION][demand_profiles][LABEL]
        ],
        D2.OEMOF_SOLPH_OBJECT_BUS: dict_model[OEMOF_BUSSES][
            dict_values[ENERGY_CONSUMPTION][demand_profiles][INFLOW_DIRECTION]
        ],
        D2.WEIGHTING_FACTOR_ENERGY_CARRIER: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
            dict_values[ENERGY_CONSUMPTION][demand_profiles][ENERGY_VECTOR]
        ][VALUE],
    }

    for key in exp.keys():
        assert (
            key in demands[demand_profiles]
        ), f"The parameter {key} for demand {demand_profiles} not is not added for demand asset processing for the constraints."
        assert (
            demands[demand_profiles][key] == exp[key]
        ), f"The expected value (exp[key]) of {key} for {demand_profiles} is not met, but is of value {demands[demand_profiles][key]}."


def test_prepare_energy_provider_consumption_sources():
    electricity = "Electricity"
    dso = "DSO"
    dict_values = {
        ENERGY_PROVIDERS: {dso: {LABEL: dso},},
        ENERGY_PRODUCTION: {
            dso
            + DSO_CONSUMPTION: {
                LABEL: dso + DSO_CONSUMPTION,
                OUTFLOW_DIRECTION: electricity,
                ENERGY_VECTOR: electricity,
            }
        },
    }
    dict_model = {
        OEMOF_SOURCE: {dso + DSO_CONSUMPTION: dso + DSO_CONSUMPTION,},
        OEMOF_BUSSES: {electricity: electricity},
    }

    energy_provider_consumption_sources = D2.prepare_energy_provider_consumption_sources(
        dict_values, dict_model,
    )

    DSO_source_name = dict_values[ENERGY_PROVIDERS][dso][LABEL] + DSO_CONSUMPTION

    assert (
        DSO_source_name in energy_provider_consumption_sources
    ), f"DSO source asset {DSO_source_name} should be in the energy provider source list taken into account for the constraints, but is not included in it ({energy_provider_consumption_sources.keys()})."

    exp = {
        D2.OEMOF_SOLPH_OBJECT_ASSET: dict_model[OEMOF_SOURCE][
            dict_values[ENERGY_PRODUCTION][DSO_source_name][LABEL]
        ],
        D2.OEMOF_SOLPH_OBJECT_BUS: dict_model[OEMOF_BUSSES][
            dict_values[ENERGY_PRODUCTION][DSO_source_name][OUTFLOW_DIRECTION]
        ],
        D2.WEIGHTING_FACTOR_ENERGY_CARRIER: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
            dict_values[ENERGY_PRODUCTION][DSO_source_name][ENERGY_VECTOR]
        ][VALUE],
    }

    for key in exp.keys():
        assert (
            key in energy_provider_consumption_sources[DSO_source_name]
        ), f"The parameter {key} for DSO {DSO_source_name} not is not added for energy provider sources processing for constraints."
        assert (
            energy_provider_consumption_sources[DSO_source_name][key] == exp[key]
        ), f"The expected value (exp[key]) of {key} for {DSO_source_name} is not met, but is of value {energy_provider_consumption_sources[DSO_source_name][key]}."


def test_prepare_energy_provider_feedin_sinks():
    electricity = "Electricity"
    dso = "DSO"
    dict_values = {
        ENERGY_PROVIDERS: {dso: {LABEL: dso},},
        ENERGY_CONSUMPTION: {
            dso
            + DSO_FEEDIN: {
                LABEL: dso + DSO_FEEDIN,
                INFLOW_DIRECTION: electricity,
                ENERGY_VECTOR: electricity,
            }
        },
    }
    dict_model = {
        OEMOF_SINK: {dso + DSO_FEEDIN: dso + DSO_FEEDIN,},
        OEMOF_BUSSES: {electricity: electricity},
    }

    energy_provider_feedin_sinks = D2.prepare_energy_provider_feedin_sinks(
        dict_values, dict_model,
    )

    DSO_sink_name = dict_values[ENERGY_PROVIDERS][dso][LABEL] + DSO_FEEDIN

    assert (
        DSO_sink_name in energy_provider_feedin_sinks
    ), f"DSO sink asset {DSO_sink_name} should be in the energy provider sink list taken into account for the constraints, but is not included in it ({energy_provider_feedin_sinks.keys()})."

    exp = {
        D2.OEMOF_SOLPH_OBJECT_ASSET: dict_model[OEMOF_SINK][
            dict_values[ENERGY_CONSUMPTION][DSO_sink_name][LABEL]
        ],
        D2.OEMOF_SOLPH_OBJECT_BUS: dict_model[OEMOF_BUSSES][
            dict_values[ENERGY_CONSUMPTION][DSO_sink_name][INFLOW_DIRECTION]
        ],
        D2.WEIGHTING_FACTOR_ENERGY_CARRIER: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
            dict_values[ENERGY_CONSUMPTION][DSO_sink_name][ENERGY_VECTOR]
        ][VALUE],
    }

    for key in exp.keys():
        assert (
            key in energy_provider_feedin_sinks[DSO_sink_name]
        ), f"The parameter {key} for DSO {DSO_sink_name} not is not added for energy provider sinks processing for constraints."
        assert (
            energy_provider_feedin_sinks[DSO_sink_name][key] == exp[key]
        ), f"The expected value (exp[key]) of {key} for {DSO_sink_name} is not met, but is of value {energy_provider_feedin_sinks[DSO_sink_name][key]}."


class TestConstraints:
    def setup_class(self):
        """Run the simulation up to constraints adding in D2 and define class attributes."""

        # This function reads the json file provided in `tests/inputs` for the simulation.
        # Therefore, if changes are applied to the json file,
        # especially if new constraints are to be introduced,
        # it is necessary to recompile and update the json input file.

        @mock.patch(
            "argparse.ArgumentParser.parse_args",
            return_value=PARSER.parse_args(
                ["-f", "-log", "warning", "-i", TEST_INPUT_PATH, "-o", TEST_OUTPUT_PATH]
            ),
        )
        def run_parts(margs):
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

            dict_values[SIMULATION_SETTINGS][EVALUATED_PERIOD][VALUE] = 1

            logging.debug("Accessing script: C0_data_processing")
            C0.all(dict_values)

            logging.debug("Run parts of D0_modelling_and_optimization")
            model, dict_model = D0.model_building.initialize(dict_values)
            model = D0.model_building.adding_assets_to_energysystem_model(
                dict_values, dict_model, model
            )
            return dict_values, model, dict_model

        self.dict_values, self.model, self.dict_model = run_parts()
        self.exp_emission_limit = 1000
        self.exp_min_renewable_share = 0.60

        self.dict_values[CONSTRAINTS].update(
            {MAXIMUM_EMISSIONS: {VALUE: self.exp_emission_limit}}
        )
        self.dict_values[CONSTRAINTS].update(
            {MINIMAL_RENEWABLE_FACTOR: {VALUE: self.exp_min_renewable_share}}
        )
        return

    def test_constraint_maximum_emissions(self):
        """Checks if maximum emissions limit is properly added as a constraint"""
        # Create a solph model using the input values (especially the constraints setup as class variables above)
        model = D2.constraint_maximum_emissions(
            model=solph.Model(self.model), dict_values=self.dict_values,
        )
        assert (
            model.integral_limit_emission_factor.NoConstraint[0]
            == self.exp_emission_limit
        ), f"Either the maximum emission constraint has not been added or the wrong limit has been added; limit is {model.integral_limit_emission_factor.NoConstraint[0]}."

    def test_add_constraints_maximum_emissions(self):
        """Checks if maximum emissions constraint works as intended"""
        dict_values = self.dict_values.copy()
        # Modify the minimum renewable factor constraint to be 0, otherwise this constraint will also be added
        dict_values.update(
            {
                MINIMAL_RENEWABLE_FACTOR: {VALUE: 0},
                MINIMAL_DEGREE_OF_AUTONOMY: {VALUE: 0},
                NET_ZERO_ENERGY: {VALUE: False},
            }
        )
        model = D2.add_constraints(
            local_energy_system=solph.Model(self.model),
            dict_values=dict_values,
            dict_model=self.dict_model,
        )
        assert (
            model.integral_limit_emission_factor.NoConstraint[0]
            == self.exp_emission_limit
        ), f"Either the maximum emission constraint has not been added or the wrong limit has been added; limit is {model.integral_limit_emission_factor.NoConstraint[0]}."

    def test_add_constraints_maximum_emissions_None(self):
        """Verifies if the max emissions constraint was not added, in case the user does not provide a value"""
        dict_values = self.dict_values.copy()
        dict_values.update(
            {
                CONSTRAINTS: {
                    MAXIMUM_EMISSIONS: {VALUE: None},
                    MINIMAL_RENEWABLE_FACTOR: {VALUE: 0},
                    MINIMAL_DEGREE_OF_AUTONOMY: {VALUE: 0},
                    NET_ZERO_ENERGY: {VALUE: False},
                }
            }
        )
        model = D2.add_constraints(
            local_energy_system=solph.Model(self.model),
            dict_values=dict_values,
            dict_model=self.dict_model,
        )
        assert (
            hasattr(model, "integral_limit_emission_factor") == False
        ), f"When maximum_emission is None, no emission constraint should be added to the ESM."

    def test_add_constraints_minimal_renewable_share(self):
        """Checks if the constraint minimal renewable share value provided by the user is being applied or not"""
        model = D2.add_constraints(
            local_energy_system=solph.Model(self.model),
            dict_values=self.dict_values,
            dict_model=self.dict_model,
        )

        assert (
            hasattr(model, "constraint_minimal_renewable_share") == True
        ), f"The minimal renewable share has not been added, something has failed."

    def test_add_constraints_minimal_renewable_share_is_0(self):
        """Checks that the minimal renewable share constraint is not added if user provides a minimal share of 0"""
        dict_values = self.dict_values.copy()
        dict_values.update(
            {
                CONSTRAINTS: {
                    MAXIMUM_EMISSIONS: {VALUE: None},
                    MINIMAL_RENEWABLE_FACTOR: {VALUE: 0},
                    MINIMAL_DEGREE_OF_AUTONOMY: {VALUE: 0},
                    NET_ZERO_ENERGY: {VALUE: False},
                }
            }
        )

        model = D2.add_constraints(
            local_energy_system=solph.Model(self.model),
            dict_values=dict_values,
            dict_model=self.dict_model,
        )

        assert (
            hasattr(model, "constraint_minimal_renewable_share") == False
        ), f"When the minimal_renewable_share is 0, no constraint should be added"

    def test_add_constraints_net_zero_energy_requirement_is_true(self):
        """Checks that the nze constraint is added if user provides the value True"""
        dict_values = self.dict_values.copy()
        dict_values.update(
            {
                CONSTRAINTS: {
                    MAXIMUM_EMISSIONS: {VALUE: None},
                    MINIMAL_RENEWABLE_FACTOR: {VALUE: 0},
                    MINIMAL_DEGREE_OF_AUTONOMY: {VALUE: 0},
                    NET_ZERO_ENERGY: {VALUE: True},
                }
            }
        )

        model = D2.add_constraints(
            local_energy_system=solph.Model(self.model),
            dict_values=dict_values,
            dict_model=self.dict_model,
        )

        assert (
            hasattr(model, "constraint_net_zero_energy") == True
        ), f"When the net_zero_energy constraint is activated (True), the constraint should be added. Something went wrong."

    def test_add_constraints_net_zero_energy_requirement_is_false(self):
        """Checks that the nze constraint is not added if user provides the value False"""
        dict_values = self.dict_values.copy()
        dict_values.update(
            {
                CONSTRAINTS: {
                    MAXIMUM_EMISSIONS: {VALUE: None},
                    MINIMAL_RENEWABLE_FACTOR: {VALUE: 0},
                    MINIMAL_DEGREE_OF_AUTONOMY: {VALUE: 0},
                    NET_ZERO_ENERGY: {VALUE: False},
                }
            }
        )

        model = D2.add_constraints(
            local_energy_system=solph.Model(self.model),
            dict_values=dict_values,
            dict_model=self.dict_model,
        )

        assert (
            hasattr(model, "constraint_net_zero_energy") == False
        ), f"When the net_zero_energy constraint is deactivated (False), no constraint should be added"

    def teardown_class(self):
        # Remove the output folder
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
