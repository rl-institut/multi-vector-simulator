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

from multi_vector_simulator.utils.constants_json_strings import (
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
    oemof_solph_object_asset = "object"
    weighting_factor_energy_carrier = "weighting_factor_energy_carrier"
    renewable_share_asset_flow = "renewable_share_asset_flow"
    oemof_solph_object_bus = "oemof_solph_object_bus"

    (
        renewable_assets,
        non_renewable_assets,
    ) = D2.prepare_constraint_minimal_renewable_share(
        dict_values=dict_values,
        dict_model=dict_model,
        oemof_solph_object_asset=oemof_solph_object_asset,
        weighting_factor_energy_carrier=weighting_factor_energy_carrier,
        renewable_share_asset_flow=renewable_share_asset_flow,
        oemof_solph_object_bus=oemof_solph_object_bus,
    )

    assert (
        pv_plant in renewable_assets
    ), f"The {pv_plant} is not added to the renewable assets."
    assert (
        pv_plant not in non_renewable_assets
    ), f"The {pv_plant} is not added to the renewable assets."
    assert (
        renewable_assets[pv_plant][renewable_share_asset_flow] == 1
    ), f"The renewable share of asset {pv_plant} is added incorrectly."

    assert (
        diesel in non_renewable_assets
    ), f"The {diesel} is added to the renewable assets."
    assert (
        diesel not in renewable_assets
    ), f"The {diesel} is not added to the non-renewable assets."
    assert (
        non_renewable_assets[diesel][renewable_share_asset_flow] == 0
    ), f"The renewable share of asset {diesel} is added incorrectly."

    assert (
        dso_1 + DSO_CONSUMPTION in renewable_assets
    ), f"The {dso_1 + DSO_CONSUMPTION} is not added as a renewable source."
    assert (
        renewable_assets[dso_1 + DSO_CONSUMPTION][renewable_share_asset_flow] == 0.3
    ), f"The renewable share of asset {dso_1 + DSO_CONSUMPTION} is added incorrectly."

    assert (
        dso_1 + DSO_CONSUMPTION in non_renewable_assets
    ), f"The {dso_1 + DSO_CONSUMPTION} is not added as a non-renewable source."
    assert (
        non_renewable_assets[dso_1 + DSO_CONSUMPTION][renewable_share_asset_flow] == 0.3
    ), f"The renewable share of asset {dso_1 + DSO_CONSUMPTION} is added incorrectly."

    assert (
        dso_2 + DSO_CONSUMPTION in renewable_assets
    ), f"The {dso_2 + DSO_CONSUMPTION} is not added as a renewable source."
    assert (
        renewable_assets[dso_2 + DSO_CONSUMPTION][renewable_share_asset_flow] == 0.7
    ), f"The renewable share of asset {dso_2 + DSO_CONSUMPTION} is added incorrectly."

    assert (
        dso_2 + DSO_CONSUMPTION in non_renewable_assets
    ), f"The {dso_2 + DSO_CONSUMPTION} is not added as a non-renewable source."
    assert (
        non_renewable_assets[dso_2 + DSO_CONSUMPTION][renewable_share_asset_flow] == 0.7
    ), f"The renewable share of asset {dso_2 + DSO_CONSUMPTION} is added incorrectly."


class TestConstraints:
    def setup_class(self):
        """Run the simulation up to constraints adding in D2 and define class attributes."""

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
        self.min_renewable_share = 0.60
        self.dict_values[CONSTRAINTS].update(
            {MAXIMUM_EMISSIONS: {VALUE: self.exp_emission_limit}}
        )
        self.dict_values[CONSTRAINTS].update(
            {MINIMAL_RENEWABLE_FACTOR: {VALUE: self.min_renewable_share}}
        )
        return

    def test_constraint_maximum_emissions(self):
        model = D2.constraint_maximum_emissions(
            model=solph.Model(self.model), dict_values=self.dict_values
        )
        assert (
            model.integral_limit_emission_factor.NoConstraint[0]
            == self.exp_emission_limit
        ), f"Either the maximum emission constraint has not been added or the wrong limit has been added; limit is {model.integral_limit_emission_factor.NoConstraint[0]}."

    def test_add_constraints_maximum_emissions(self):
        model = D2.add_constraints(
            local_energy_system=solph.Model(self.model),
            dict_values=self.dict_values,
            dict_model=self.dict_model,
        )
        assert (
            model.integral_limit_emission_factor.NoConstraint[0]
            == self.exp_emission_limit
        ), f"Either the maximum emission constraint has not been added or the wrong limit has been added; limit is {model.integral_limit_emission_factor.NoConstraint[0]}."

    def test_add_constraints_maximum_emissions_None(self):
        dict_values = self.dict_values.copy()
        dict_values.update(
            {
                CONSTRAINTS: {
                    MAXIMUM_EMISSIONS: {VALUE: None},
                    MINIMAL_RENEWABLE_FACTOR: {
                        VALUE: self.dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_FACTOR][
                            VALUE
                        ]
                    },
                }
            }
        )
        model = D2.add_constraints(
            local_energy_system=solph.Model(self.model),
            dict_values=dict_values,
            dict_model=self.dict_model,
        )
        assert (
            hasattr(model, "integral_limit_emission_factor")
            == False
        ), f"When maximum_emission is None, no emission constraint should be added to the ESM."

    """
    def test_add_constraints_minimal_renewable_share(self):
    # todo to be added
    pass
    """

    def test_add_constraints_minimal_renewable_share_None(self):
        dict_values = self.dict_values.copy()
        dict_values.update(
            {
                CONSTRAINTS: {
                    MAXIMUM_EMISSIONS: {
                        VALUE: self.dict_values[CONSTRAINTS][MAXIMUM_EMISSIONS][VALUE]
                    },
                    MINIMAL_RENEWABLE_FACTOR: {VALUE: None},
                }
            }
        )
        model = D2.add_constraints(
            local_energy_system=solph.Model(self.model),
            dict_values=dict_values,
            dict_model=self.dict_model,
        )
        assert (
            model.constraint_minimal_renewable_share == self.min_renewable_share
        ), f"When the minimal_renewable_share is None, no constraint should be added"

    def teardown_class(self):
        # Remove the output folder
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
