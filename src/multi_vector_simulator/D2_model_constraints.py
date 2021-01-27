"""
Module D2 - Model constraints
=============================

This module gathers all constraints that can be added to the MVS optimisation. 
we will probably require another input CSV file or further parameters in simulation_settings.

Future constraints are discussed in issue #133 (https://github.com/rl-institut/mvs_eland/issues/133)

constraints should be tested in-code (examples) and by comparing the lp file generated.
"""
import logging
import pyomo.environ as po
from oemof.solph import constraints

from multi_vector_simulator.utils.constants import DEFAULT_WEIGHTS_ENERGY_CARRIERS

from multi_vector_simulator.utils.constants_json_strings import (
    OEMOF_SOURCE,
    OEMOF_SINK,
    OEMOF_BUSSES,
    ENERGY_PRODUCTION,
    ENERGY_PROVIDERS,
    ENERGY_CONSUMPTION,
    ENERGY_VECTOR,
    VALUE,
    LABEL,
    INFLOW_DIRECTION,
    OUTFLOW_DIRECTION,
    DSO_CONSUMPTION,
    RENEWABLE_SHARE_DSO,
    RENEWABLE_ASSET_BOOL,
    AUTO_SINK,
    EXCESS,
    EXCESS_SINK_POSTFIX,
    CONSTRAINTS,
    MINIMAL_RENEWABLE_FACTOR,
    MAXIMUM_EMISSIONS,
    MINIMAL_DEGREE_OF_AUTONOMY,
)


def add_constraints(local_energy_system, dict_values, dict_model):
    r"""
    Adds all constraints activated in constraints.csv to the energy system model.

    Possible constraints:
    - Minimal renewable factor constraint
    Parameters
    ----------
    local_energy_system:  :oemof-solph: <oemof.solph.model>
        Energy system model generated from oemof-solph for the energy system scenario, including all energy system assets.

    dict_values: dict
        All simulation parameters

    dict_model: dict of :oemof-solph: <oemof.solph.assets>
        Dictionary including the oemof-solph component assets, which need to be connected with constraints

    Returns
    -------
    local_energy_system: :oemof-solph: <oemof.solph.model>
        Updated object local_energy_system with the additional constraints and bounds.

    Notes
    -----
    The constraints can be validated by evaluating the LP file.
    Additionally, there are validation tests in `E4_verification_of_constraints`.

    Tested with:
    - D2.test_add_constraints_maximum_emissions()
    - D2.test_add_constraints_maximum_emissions_None()
    - D2.test_add_constraints_minimal_renewable_share()
    - D2.test_test_add_constraints_minimal_renewable_share_is_0()
    """
    count_added_constraints = 0

    if dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_FACTOR][VALUE] > 0:
        # Add minimal renewable factor constraint
        local_energy_system = constraint_minimal_renewable_share(
            local_energy_system, dict_values, dict_model
        )
        count_added_constraints += 1

    if dict_values[CONSTRAINTS][MAXIMUM_EMISSIONS][VALUE] is not None:
        # Add maximum emissions constraint
        local_energy_system = constraint_maximum_emissions(
            local_energy_system, dict_values
        )
        count_added_constraints += 1

    if dict_values[CONSTRAINTS][MINIMAL_DEGREE_OF_AUTONOMY][VALUE] > 0:
        # Add minimal renewable factor constraint
        local_energy_system = constraint_minimal_degree_of_autonomy(
            local_energy_system, dict_values, dict_model
        )
        count_added_constraints += 1

    if count_added_constraints == 0:
        logging.info("No modelling constraint to be introduced.")
    else:
        logging.debug(f"Number of added constraints: {count_added_constraints}")

    return local_energy_system


def constraint_maximum_emissions(model, dict_values):
    r"""
    Resulting in an energy system adhering to a maximum amount of emissions.

    Parameters
    ----------
    model: :oemof-solph: <oemof.solph.model>
        Model to which constraint is added.

    dict_values: dict
        All simulation parameters

    Notes
    -----
    Tested with:
    - D2.test_constraint_maximum_emissions()

    """
    maximum_emissions = dict_values[CONSTRAINTS][MAXIMUM_EMISSIONS][VALUE]
    # Updates the model with the constraint for maximum amount of emissions
    constraints.emission_limit(model, limit=maximum_emissions)
    logging.info("Added maximum emission constraint.")
    return model


def constraint_minimal_renewable_share(model, dict_values, dict_model):
    r"""
    Resulting in an energy system adhering to a minimal renewable factor.

    Please be aware that the renewable factor that has to adhere to the minimal renewable factor is not the one of one specific sector,
    but of the overall energy system. This means that eg. 1 kg H2 is produced renewably, it goes into account with a heavier
    weighting factor then one renewably produced electricity unit.

    Parameters
    ----------
    model: :oemof-solph: <oemof.solph.model>
        Model to which constraint is added.

    dict_values: dict
        All simulation parameters

    dict_model: dict of :oemof-solph: <oemof.solph.assets>
        Dictionary including the oemof-solph component assets, which need to be connected with constraints

    Notes
    -----
    The renewable factor of the whole energy system has to adhere for following constraint:

    .. math::
        minimal renewable factor <= \frac{\sum renewable generation \cdot weighting factor}{\sum renewable generation \cdot weighting factor + \sum non-renewable generation \cdot weighting factor}

    Tested with:
    - Test_Constraints.test_benchmark_minimal_renewable_share_constraint()
    """

    # Keys for dicts renewable_assets and non_renewable_assets
    oemof_solph_object_asset = "object"
    weighting_factor_energy_carrier = "weighting_factor_energy_carrier"
    renewable_share_asset_flow = "renewable_share_asset_flow"
    oemof_solph_object_bus = "oemof_solph_object_bus"

    renewable_assets, non_renewable_assets = prepare_constraint_minimal_renewable_share(
        dict_values,
        dict_model,
        oemof_solph_object_asset,
        weighting_factor_energy_carrier,
        renewable_share_asset_flow,
        oemof_solph_object_bus,
    )

    def renewable_share_rule(model):
        renewable_generation = 0
        total_generation = 0

        # Get the flows from all renewable assets
        for asset in renewable_assets:
            generation = (
                sum(
                    model.flow[
                        renewable_assets[asset][oemof_solph_object_asset],
                        renewable_assets[asset][oemof_solph_object_bus],
                        :,
                    ]
                )
                * renewable_assets[asset][weighting_factor_energy_carrier]
                * renewable_assets[asset][renewable_share_asset_flow]
            )
            total_generation += generation
            renewable_generation += generation

        # Get the flows from all non renewable assets
        for asset in non_renewable_assets:
            generation = (
                sum(
                    model.flow[
                        non_renewable_assets[asset][oemof_solph_object_asset],
                        non_renewable_assets[asset][oemof_solph_object_bus],
                        :,
                    ]
                )
                * non_renewable_assets[asset][weighting_factor_energy_carrier]
                * (1 - non_renewable_assets[asset][renewable_share_asset_flow])
            )
            total_generation += generation

        expr = (
            renewable_generation
            - (dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_FACTOR][VALUE])
            * total_generation
        )
        return expr >= 0

    model.constraint_minimal_renewable_share = po.Constraint(rule=renewable_share_rule)

    logging.info("Added minimal renewable factor constraint.")
    return model


def prepare_constraint_minimal_renewable_share(
    dict_values,
    dict_model,
    oemof_solph_object_asset,
    weighting_factor_energy_carrier,
    renewable_share_asset_flow,
    oemof_solph_object_bus,
):
    r"""
    Prepare creating the minimal renewable factor constraint by processing dict_values

    Parameters
    ----------
    dict_values: dict
        All simulation parameters

    dict_model: dict of :oemof-solph: <oemof.solph.assets>
        Dictionary including the oemof-solph component assets, which need to be connected with constraints

    oemof_solph_object_asset: str
        Name under which the oemof-solph object of an asset shall be stored

    weighting_factor_energy_carrier: str
        Name under which the energy_carrier weighting factor shall be stored

    renewable_share_asset_flow: str
        Name under which the renewable weighting factor (renewable share of an asset`s flow) shall be stored

    oemof_solph_object_bus: str
        Name under which the oemof-solph object of the output bus of an asset shall be stored

    Returns
    -------
    renewable_assets: dict
        Dictionary of all assets with renewable generation in the energy system.
        Defined by: oemof_solph_object_asset, weighting_factor_energy_carrier, renewable_share_asset_flow, oemof_solph_object_bus

    non_renewable_assets: dict
        Dictionary of all assets with renewable generation in the energy system.
        Defined by: oemof_solph_object_asset, weighting_factor_energy_carrier, renewable_share_asset_flow, oemof_solph_object_bus

    """
    # dicts for processing
    renewable_assets = {}
    non_renewable_assets = {}

    # Determine which energy sources are of renewable origin and which are fossil-fuelled.
    # DSO sources are added separately (as they do not have parameter "RENEWABLE_ASSET_BOOL".
    assets_without_renewable_asset_bool = []
    for asset in dict_values[ENERGY_PRODUCTION]:
        if RENEWABLE_ASSET_BOOL in dict_values[ENERGY_PRODUCTION][asset]:
            if (
                dict_values[ENERGY_PRODUCTION][asset][RENEWABLE_ASSET_BOOL][VALUE]
                is True
            ):
                renewable_assets.update(
                    {
                        asset: {
                            oemof_solph_object_asset: dict_model[OEMOF_SOURCE][
                                dict_values[ENERGY_PRODUCTION][asset][LABEL]
                            ],
                            oemof_solph_object_bus: dict_model[OEMOF_BUSSES][
                                dict_values[ENERGY_PRODUCTION][asset][OUTFLOW_DIRECTION]
                            ],
                            weighting_factor_energy_carrier: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                                dict_values[ENERGY_PRODUCTION][asset][ENERGY_VECTOR]
                            ][
                                VALUE
                            ],
                            renewable_share_asset_flow: 1,
                        }
                    }
                )
            elif (
                dict_values[ENERGY_PRODUCTION][asset][RENEWABLE_ASSET_BOOL][VALUE]
                is False
            ):
                non_renewable_assets.update(
                    {
                        asset: {
                            oemof_solph_object_asset: dict_model[OEMOF_SOURCE][
                                dict_values[ENERGY_PRODUCTION][asset][LABEL]
                            ],
                            oemof_solph_object_bus: dict_model[OEMOF_BUSSES][
                                dict_values[ENERGY_PRODUCTION][asset][OUTFLOW_DIRECTION]
                            ],
                            weighting_factor_energy_carrier: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                                dict_values[ENERGY_PRODUCTION][asset][ENERGY_VECTOR]
                            ][
                                VALUE
                            ],
                            renewable_share_asset_flow: 0,
                        }
                    }
                )
            else:
                logging.warning(
                    f"Value of parameter {RENEWABLE_ASSET_BOOL} of asset {asset} is {dict_values[ENERGY_PRODUCTION][asset][RENEWABLE_ASSET_BOOL][VALUE]}, but should be True/False."
                )
        else:
            assets_without_renewable_asset_bool.append(asset)

    # This message is printed so that errors can be identified easier.
    assets_without_renewable_asset_bool_string = ", ".join(
        map(str, assets_without_renewable_asset_bool)
    )
    logging.debug(
        f"Following assets do not have key RENEWABLE_ASSET_BOOL: {assets_without_renewable_asset_bool_string}. "
        f"They should be all DSO consumption sources."
    )

    dso_sources = []
    for dso in dict_values[ENERGY_PROVIDERS]:
        # Get source connected to the specific DSO in question
        DSO_source_name = dso + DSO_CONSUMPTION
        # Add DSO to both renewable and nonrenewable assets (as only a share of their supply may be renewable)
        dso_sources.append(DSO_source_name)

        renewable_assets.update(
            {
                DSO_source_name: {
                    oemof_solph_object_asset: dict_model[OEMOF_SOURCE][
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][LABEL]
                    ],
                    oemof_solph_object_bus: dict_model[OEMOF_BUSSES][
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][
                            OUTFLOW_DIRECTION
                        ]
                    ],
                    weighting_factor_energy_carrier: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][ENERGY_VECTOR]
                    ][VALUE],
                    renewable_share_asset_flow: dict_values[ENERGY_PROVIDERS][dso][
                        RENEWABLE_SHARE_DSO
                    ][VALUE],
                }
            }
        )
        non_renewable_assets.update(
            {
                DSO_source_name: {
                    oemof_solph_object_asset: dict_model[OEMOF_SOURCE][
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][LABEL]
                    ],
                    oemof_solph_object_bus: dict_model[OEMOF_BUSSES][
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][
                            OUTFLOW_DIRECTION
                        ]
                    ],
                    weighting_factor_energy_carrier: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][ENERGY_VECTOR]
                    ][VALUE],
                    renewable_share_asset_flow: dict_values[ENERGY_PROVIDERS][dso][
                        RENEWABLE_SHARE_DSO
                    ][VALUE],
                }
            }
        )

    for k in assets_without_renewable_asset_bool:
        if k not in dso_sources:
            logging.warning(
                "There is an asset {k} that does not have any information whether it is of renewable origin or not. "
                "It is neither a DSO source nor a renewable or fuel source."
            )

    renewable_asset_string = ", ".join(map(str, renewable_assets.keys()))
    non_renewable_asset_string = ", ".join(map(str, non_renewable_assets.keys()))

    logging.debug(f"Data considered for the minimal renewable factor constraint:")
    logging.debug(f"Assets connected to renewable generation: {renewable_asset_string}")
    logging.debug(
        f"Assets connected to non-renewable generation: {non_renewable_asset_string}"
    )
    return renewable_assets, non_renewable_assets


def constraint_minimal_degree_of_autonomy(model, dict_values, dict_model):
    r"""
    Resulting in an energy system adhering to a minimal degree of autonomy.

    Please be aware that the minimal degree of autonomy is not applied to each sector individually,
    but to the overall energy system (via energy carrier weighting).

    Parameters
    ----------
    model: :oemof-solph: <oemof.solph.model>
        Model to which constraint is added.

    dict_values: dict
        All simulation parameters

    dict_model: dict of :oemof-solph: <oemof.solph.assets>
        Dictionary including the oemof-solph component assets, which need to be connected with constraints

    Notes
    -----
    The renewable factor of the whole energy system has to adhere for following constraint:

    .. math::
        minimal degree of autonomy \cdot (\sum local demand  \cdot weighting factor) <= \sum local demand \cdot weighting factor - \sum consumtion from energy providers \cdot weighting factor

    Tested with:
    - Test_Constraints.test_benchmark_minimal_degree_of_autonomy()
    """

    # Keys for dicts renewable_assets and non_renewable_assets
    oemof_solph_object_asset = "object"
    weighting_factor_energy_carrier = "weighting_factor_energy_carrier"
    oemof_solph_object_bus = "oemof_solph_object_bus"

    (
        demands,
        energy_provider_consumption_sources,
    ) = prepare_constraint_minimal_degree_of_autonomy(
        dict_values,
        dict_model,
        oemof_solph_object_asset,
        weighting_factor_energy_carrier,
        oemof_solph_object_bus,
    )

    def degree_of_autonomy_rule(model):
        total_demand = 0
        total_consumption_from_energy_provider = 0

        # Get the flows from demands and add weighing
        for asset in demands:
            demand_one_asset = (
                sum(
                    model.flow[
                        demands[asset][oemof_solph_object_bus],
                        demands[asset][oemof_solph_object_asset],
                        :,
                    ]
                )
                * demands[asset][weighting_factor_energy_carrier]
            )
            total_demand += demand_one_asset

        # Get the flows from providers and add weighing
        for asset in energy_provider_consumption_sources:
            consumption_of_one_provider = (
                sum(
                    model.flow[
                        energy_provider_consumption_sources[asset][
                            oemof_solph_object_asset
                        ],
                        energy_provider_consumption_sources[asset][
                            oemof_solph_object_bus
                        ],
                        :,
                    ]
                )
                * energy_provider_consumption_sources[asset][
                    weighting_factor_energy_carrier
                ]
            )
            total_consumption_from_energy_provider += consumption_of_one_provider

        expr = (
            1 - dict_values[CONSTRAINTS][MINIMAL_DEGREE_OF_AUTONOMY][VALUE]
        ) * total_demand - total_consumption_from_energy_provider
        return expr >= 0

    model.constraint_minimal_degree_of_autonomy = po.Constraint(
        rule=degree_of_autonomy_rule
    )

    logging.info("Added minimal degree of autonomy constraint.")
    return model


def prepare_constraint_minimal_degree_of_autonomy(
    dict_values,
    dict_model,
    oemof_solph_object_asset,
    weighting_factor_energy_carrier,
    oemof_solph_object_bus,
):
    r"""
    Prepare creating the minimal degree of autonomy constraint by processing `dict_values`

    Parameters
    ----------
    dict_values: dict
        All simulation parameters

    dict_model: dict of :oemof-solph: <oemof.solph.assets>
        Dictionary including the oemof-solph component assets, which need to be connected with constraints

    oemof_solph_object_asset: str
        Name under which the oemof-solph object of an asset shall be stored

    weighting_factor_energy_carrier: str
        Name under which the energy_carrier weighting factor shall be stored

    oemof_solph_object_bus: str
        Name under which the oemof-solph object of the output bus of an asset shall be stored

    Returns
    -------
    demands: dict
        Dictionary of all assets with all demands in the energy system.
        Defined by: oemof_solph_object_asset, weighting_factor_energy_carrier, oemof_solph_object_bus

    energy_provider_consumption_sources: dict
        Dictionary of all assets that are sources for the energy consumption from energy providers in the energy system.
        Defined by: oemof_solph_object_asset, weighting_factor_energy_carrier, oemof_solph_object_bus

    """
    # dicts for processing
    demands = {}
    demand_list = []
    energy_provider_consumption_sources = {}
    dso_consumption_source_list = []

    # Determine energy demands
    for asset in dict_values[ENERGY_CONSUMPTION]:
        if (
            AUTO_SINK not in asset
            and EXCESS not in asset
            and EXCESS_SINK_POSTFIX not in asset
        ):
            demands.update(
                {
                    asset: {
                        oemof_solph_object_asset: dict_model[OEMOF_SINK][
                            dict_values[ENERGY_CONSUMPTION][asset][LABEL]
                        ],
                        oemof_solph_object_bus: dict_model[OEMOF_BUSSES][
                            dict_values[ENERGY_CONSUMPTION][asset][INFLOW_DIRECTION]
                        ],
                        weighting_factor_energy_carrier: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                            dict_values[ENERGY_CONSUMPTION][asset][ENERGY_VECTOR]
                        ][
                            VALUE
                        ],
                    }
                }
            )
            demand_list.append(asset)

    for dso in dict_values[ENERGY_PROVIDERS]:
        # Get source connected to the specific DSO in question
        DSO_source_name = dso + DSO_CONSUMPTION
        # Add DSO to assets
        dso_consumption_source_list.append(DSO_source_name)

        energy_provider_consumption_sources.update(
            {
                DSO_source_name: {
                    oemof_solph_object_asset: dict_model[OEMOF_SOURCE][
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][LABEL]
                    ],
                    oemof_solph_object_bus: dict_model[OEMOF_BUSSES][
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][
                            OUTFLOW_DIRECTION
                        ]
                    ],
                    weighting_factor_energy_carrier: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][ENERGY_VECTOR]
                    ][VALUE],
                }
            }
        )

    # Preprocessing for log messages
    demand_string = ", ".join(map(str, demand_list))

    dso_consumption_source_string = ", ".join(map(str, dso_consumption_source_list))
    logging.debug(f"Data considered for the minimal renewable factor constraint:")
    logging.debug(f"Demands: {demand_string}")
    logging.debug(
        f"Energy provider consumption sources: {dso_consumption_source_string}"
    )
    return demands, energy_provider_consumption_sources
