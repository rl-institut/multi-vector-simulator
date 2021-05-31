"""
Module D2 - Model constraints
=============================

This module gathers all constraints that can be added to the MVS optimisation. 
we will probably require another input CSV file or further parameters in simulation_settings.

Future constraints are discussed in issue #133 (https://github.com/rl-institut/multi-vector-simulator/issues/133)

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
    EXCESS_SINK,
    CONSTRAINTS,
    MINIMAL_RENEWABLE_FACTOR,
    MAXIMUM_EMISSIONS,
    MINIMAL_DEGREE_OF_AUTONOMY,
    DSO_FEEDIN,
    NET_ZERO_ENERGY,
)

# Keys for dicts renewable_assets and non_renewable_assets
OEMOF_SOLPH_OBJECT_ASSET = "object"
WEIGHTING_FACTOR_ENERGY_CARRIER = "weighting_factor_energy_carrier"
RENEWABLE_SHARE_ASSET_FLOW = "renewable_share_asset_flow"
OEMOF_SOLPH_OBJECT_BUS = "oemof_solph_object_bus"


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
    - D2.test_add_constraints_minimal_renewable_share_is_0()
    - D2.test_add_constraints_net_zero_energy_requirement_is_true()
    - D2.test_add_constraints_net_zero_energy_requirement_is_false()
    """

    constraint_functions = {
        MINIMAL_RENEWABLE_FACTOR: constraint_minimal_renewable_share,
        MAXIMUM_EMISSIONS: constraint_maximum_emissions,
        MINIMAL_DEGREE_OF_AUTONOMY: constraint_minimal_degree_of_autonomy,
        NET_ZERO_ENERGY: constraint_net_zero_energy,
    }

    count_added_constraints = 0

    for constraint in dict_values[CONSTRAINTS]:
        # if the constraint is not within its proper range of admissible values, None is returned
        les = constraint_functions[constraint](
            local_energy_system, dict_values, dict_model
        )
        # if the contraint is not applied (because not defined by the user, or with a value which
        # is not in the acceptable range the constrain function will return None
        if les is not None:
            local_energy_system = les
            count_added_constraints += 1

    if count_added_constraints == 0:
        logging.info("No modelling constraint to be introduced.")
    else:
        logging.debug(f"Number of added constraints: {count_added_constraints}")

    return local_energy_system


def constraint_maximum_emissions(model, dict_values, dict_model=None):
    r"""
    Resulting in an energy system adhering to a maximum amount of emissions.

    Parameters
    ----------
    model: :oemof-solph: <oemof.solph.model>
        Model to which constraint is added.

    dict_values: dict
        All simulation parameters

    dict_model: None
        To match other constraint function's format

    Notes
    -----
    Tested with:
    - D2.test_constraint_maximum_emissions()

    """
    maximum_emissions = dict_values[CONSTRAINTS][MAXIMUM_EMISSIONS][VALUE]
    if maximum_emissions is not None:
        # Updates the model with the constraint for maximum amount of emissions
        constraints.emission_limit(model, limit=maximum_emissions)
        logging.info("Added maximum emission constraint.")
        answer = model
    else:
        answer = None

    return answer


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

    if dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_FACTOR][VALUE] > 0:

        (
            renewable_assets,
            non_renewable_assets,
        ) = prepare_constraint_minimal_renewable_share(dict_values, dict_model,)

        def renewable_share_rule(model):
            renewable_generation = 0
            total_generation = 0

            # Get the flows from all renewable assets
            for asset in renewable_assets:
                generation = (
                    sum(
                        model.flow[
                            renewable_assets[asset][OEMOF_SOLPH_OBJECT_ASSET],
                            renewable_assets[asset][OEMOF_SOLPH_OBJECT_BUS],
                            :,
                        ]
                    )
                    * renewable_assets[asset][WEIGHTING_FACTOR_ENERGY_CARRIER]
                    * renewable_assets[asset][RENEWABLE_SHARE_ASSET_FLOW]
                )
                total_generation += generation
                renewable_generation += generation

            # Get the flows from all non renewable assets
            for asset in non_renewable_assets:
                generation = (
                    sum(
                        model.flow[
                            non_renewable_assets[asset][OEMOF_SOLPH_OBJECT_ASSET],
                            non_renewable_assets[asset][OEMOF_SOLPH_OBJECT_BUS],
                            :,
                        ]
                    )
                    * non_renewable_assets[asset][WEIGHTING_FACTOR_ENERGY_CARRIER]
                    * (1 - non_renewable_assets[asset][RENEWABLE_SHARE_ASSET_FLOW])
                )
                total_generation += generation

            expr = (
                renewable_generation
                - (dict_values[CONSTRAINTS][MINIMAL_RENEWABLE_FACTOR][VALUE])
                * total_generation
            )
            return expr >= 0

        model.constraint_minimal_renewable_share = po.Constraint(
            rule=renewable_share_rule
        )

        logging.info("Added minimal renewable factor constraint.")
        answer = model
    else:
        answer = None

    return answer


def prepare_constraint_minimal_renewable_share(
    dict_values, dict_model,
):
    r"""
    Prepare creating the minimal renewable factor constraint by processing dict_values

    Parameters
    ----------
    dict_values: dict
        All simulation parameters

    dict_model: dict of :oemof-solph: <oemof.solph.assets>
        Dictionary including the oemof-solph component assets, which need to be connected with constraints

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
                            OEMOF_SOLPH_OBJECT_ASSET: dict_model[OEMOF_SOURCE][
                                dict_values[ENERGY_PRODUCTION][asset][LABEL]
                            ],
                            OEMOF_SOLPH_OBJECT_BUS: dict_model[OEMOF_BUSSES][
                                dict_values[ENERGY_PRODUCTION][asset][OUTFLOW_DIRECTION]
                            ],
                            WEIGHTING_FACTOR_ENERGY_CARRIER: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                                dict_values[ENERGY_PRODUCTION][asset][ENERGY_VECTOR]
                            ][
                                VALUE
                            ],
                            RENEWABLE_SHARE_ASSET_FLOW: 1,
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
                            OEMOF_SOLPH_OBJECT_ASSET: dict_model[OEMOF_SOURCE][
                                dict_values[ENERGY_PRODUCTION][asset][LABEL]
                            ],
                            OEMOF_SOLPH_OBJECT_BUS: dict_model[OEMOF_BUSSES][
                                dict_values[ENERGY_PRODUCTION][asset][OUTFLOW_DIRECTION]
                            ],
                            WEIGHTING_FACTOR_ENERGY_CARRIER: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                                dict_values[ENERGY_PRODUCTION][asset][ENERGY_VECTOR]
                            ][
                                VALUE
                            ],
                            RENEWABLE_SHARE_ASSET_FLOW: 0,
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
                    OEMOF_SOLPH_OBJECT_ASSET: dict_model[OEMOF_SOURCE][
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][LABEL]
                    ],
                    OEMOF_SOLPH_OBJECT_BUS: dict_model[OEMOF_BUSSES][
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][
                            OUTFLOW_DIRECTION
                        ]
                    ],
                    WEIGHTING_FACTOR_ENERGY_CARRIER: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][ENERGY_VECTOR]
                    ][VALUE],
                    RENEWABLE_SHARE_ASSET_FLOW: dict_values[ENERGY_PROVIDERS][dso][
                        RENEWABLE_SHARE_DSO
                    ][VALUE],
                }
            }
        )
        non_renewable_assets.update(
            {
                DSO_source_name: {
                    OEMOF_SOLPH_OBJECT_ASSET: dict_model[OEMOF_SOURCE][
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][LABEL]
                    ],
                    OEMOF_SOLPH_OBJECT_BUS: dict_model[OEMOF_BUSSES][
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][
                            OUTFLOW_DIRECTION
                        ]
                    ],
                    WEIGHTING_FACTOR_ENERGY_CARRIER: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][ENERGY_VECTOR]
                    ][VALUE],
                    RENEWABLE_SHARE_ASSET_FLOW: dict_values[ENERGY_PROVIDERS][dso][
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

    logging.debug(f"Data considered for the minimal degree of autonomy constraint:")

    if dict_values[CONSTRAINTS][MINIMAL_DEGREE_OF_AUTONOMY][VALUE] > 0:

        demands = prepare_demand_assets(dict_values, dict_model,)

        energy_provider_consumption_sources = prepare_energy_provider_consumption_sources(
            dict_values, dict_model,
        )

        def degree_of_autonomy_rule(model):
            total_demand = 0
            total_consumption_from_energy_provider = 0

            # Get the flows from demands and add weighing
            for asset in demands:
                demand_one_asset = (
                    sum(
                        model.flow[
                            demands[asset][OEMOF_SOLPH_OBJECT_BUS],
                            demands[asset][OEMOF_SOLPH_OBJECT_ASSET],
                            :,
                        ]
                    )
                    * demands[asset][WEIGHTING_FACTOR_ENERGY_CARRIER]
                )
                total_demand += demand_one_asset

            # Get the flows from providers and add weighing
            for asset in energy_provider_consumption_sources:
                consumption_of_one_provider = (
                    sum(
                        model.flow[
                            energy_provider_consumption_sources[asset][
                                OEMOF_SOLPH_OBJECT_ASSET
                            ],
                            energy_provider_consumption_sources[asset][
                                OEMOF_SOLPH_OBJECT_BUS
                            ],
                            :,
                        ]
                    )
                    * energy_provider_consumption_sources[asset][
                        WEIGHTING_FACTOR_ENERGY_CARRIER
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
        answer = model
    else:
        answer = None

    return answer


def prepare_demand_assets(
    dict_values, dict_model,
):
    r"""
    Perpare demand assets by processing `dict_values`

    Used for the following constraints:
    - minimal degree of autonomy

    Parameters
    ----------
    dict_values: dict
        All simulation parameters

    dict_model: dict of :oemof-solph: <oemof.solph.assets>
        Dictionary including the oemof-solph component assets, which need to be connected with constraints

    Notes
    -----
    Tested with:
    - test_prepare_demand_assets()

    Returns
    -------
    demands: dict
        Dictionary of all assets with all demands in the energy system.
        Defined by: oemof_solph_object_asset, weighting_factor_energy_carrier, oemof_solph_object_bus

    """
    # dicts for processing
    demands = {}
    demand_list = []

    # Determine energy demands
    for asset in dict_values[ENERGY_CONSUMPTION]:
        # Do not add flows into excess sink of feedin sink to the demands to be supplied
        if EXCESS_SINK not in asset and DSO_FEEDIN not in asset:
            demands.update(
                {
                    asset: {
                        OEMOF_SOLPH_OBJECT_ASSET: dict_model[OEMOF_SINK][
                            dict_values[ENERGY_CONSUMPTION][asset][LABEL]
                        ],
                        OEMOF_SOLPH_OBJECT_BUS: dict_model[OEMOF_BUSSES][
                            dict_values[ENERGY_CONSUMPTION][asset][INFLOW_DIRECTION]
                        ],
                        WEIGHTING_FACTOR_ENERGY_CARRIER: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                            dict_values[ENERGY_CONSUMPTION][asset][ENERGY_VECTOR]
                        ][
                            VALUE
                        ],
                    }
                }
            )
            demand_list.append(asset)

    # Preprocessing for log messages
    demand_string = ", ".join(map(str, demand_list))

    logging.debug(f"Demands: {demand_string}")
    return demands


def prepare_energy_provider_consumption_sources(
    dict_values, dict_model,
):
    r"""
    Prepare energy provider consumption sources by processing `dict_values`.

    Used for the following constraints:
    - minimal degree of autonomy
    - net zero energy (NZE)

    Parameters
    ----------
    dict_values: dict
        All simulation parameters

    dict_model: dict of :oemof-solph: <oemof.solph.assets>
        Dictionary including the oemof-solph component assets, which need to be connected with constraints

    Notes
    -----
    Tested with:
    - test_prepare_energy_provider_consumption_sources()

    Returns
    -------
    energy_provider_consumption_sources: dict
        Dictionary of all assets that are sources for the energy consumption from energy providers in the energy system.
        Defined by: oemof_solph_object_asset, weighting_factor_energy_carrier, oemof_solph_object_bus

    """
    # dicts for processing
    energy_provider_consumption_sources = {}
    dso_consumption_source_list = []

    for dso in dict_values[ENERGY_PROVIDERS]:
        # Get source connected to the specific DSO in question
        DSO_source_name = dso + DSO_CONSUMPTION
        # Add DSO to assets
        dso_consumption_source_list.append(DSO_source_name)

        energy_provider_consumption_sources.update(
            {
                DSO_source_name: {
                    OEMOF_SOLPH_OBJECT_ASSET: dict_model[OEMOF_SOURCE][
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][LABEL]
                    ],
                    OEMOF_SOLPH_OBJECT_BUS: dict_model[OEMOF_BUSSES][
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][
                            OUTFLOW_DIRECTION
                        ]
                    ],
                    WEIGHTING_FACTOR_ENERGY_CARRIER: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                        dict_values[ENERGY_PRODUCTION][DSO_source_name][ENERGY_VECTOR]
                    ][VALUE],
                }
            }
        )

    # Preprocessing for log messages
    dso_consumption_source_string = ", ".join(map(str, dso_consumption_source_list))

    logging.debug(
        f"Energy provider consumption sources: {dso_consumption_source_string}"
    )
    return energy_provider_consumption_sources


def prepare_energy_provider_feedin_sinks(
    dict_values, dict_model,
):
    r"""
    Prepare energy provider feedin sinks by processing `dict_values`.

    Used for the following constraints:
    - net zero energy (NZE)

    Parameters
    ----------
    dict_values: dict
        All simulation parameters

    dict_model: dict of :oemof-solph: <oemof.solph.assets>
        Dictionary including the oemof-solph component assets, which need to be connected with constraints

    Notes
    -----
    Tested with:
        - test_prepare_energy_provider_feedin_sinks()

    Returns
    -------
    energy_provider_feedin_sinks: dict
        Dictionary of all assets that are sinks for the energy feed-in to energy providers in the energy system.
        Defined by: oemof_solph_object_asset, weighting_factor_energy_carrier, oemof_solph_object_bus

    """
    # dicts for processing
    energy_provider_feedin_sinks = {}
    dso_feedin_sink_list = []

    for dso in dict_values[ENERGY_PROVIDERS]:
        # Get sink connected to the specific DSO in question
        DSO_sink_name = dso + DSO_FEEDIN
        # Add DSO to assets
        dso_feedin_sink_list.append(DSO_sink_name)

        energy_provider_feedin_sinks.update(
            {
                DSO_sink_name: {
                    OEMOF_SOLPH_OBJECT_ASSET: dict_model[OEMOF_SINK][
                        dict_values[ENERGY_CONSUMPTION][DSO_sink_name][LABEL]
                    ],
                    OEMOF_SOLPH_OBJECT_BUS: dict_model[OEMOF_BUSSES][
                        dict_values[ENERGY_CONSUMPTION][DSO_sink_name][INFLOW_DIRECTION]
                    ],
                    WEIGHTING_FACTOR_ENERGY_CARRIER: DEFAULT_WEIGHTS_ENERGY_CARRIERS[
                        dict_values[ENERGY_CONSUMPTION][DSO_sink_name][ENERGY_VECTOR]
                    ][VALUE],
                }
            }
        )

    # Preprocessing for log messages
    dso_feedin_sink_string = ", ".join(map(str, dso_feedin_sink_list))

    logging.debug(f"Energy provider feedin sinks: {dso_feedin_sink_string}")
    return energy_provider_feedin_sinks


def constraint_net_zero_energy(model, dict_values, dict_model):
    r"""
    Resulting in an energy system that is a net zero energy (NZE) or plus energy system.

    Please be aware that the NZE constraint is not applied to each sector individually,
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
    The constraint reads as follows:

    .. math::
        \sum_{i} {E_{feedin, DSO} (i) \cdot w_i - E_{consumption, DSO} (i) \cdot w_i} >= 0

    Tested with:
    - Test_Constraints.test_net_zero_energy_constraint()
    """

    logging.debug(f"Data considered for the net zero energy (NZE) constraint:")

    if dict_values[CONSTRAINTS][NET_ZERO_ENERGY][VALUE] == True:

        energy_provider_feedin_sinks = prepare_energy_provider_feedin_sinks(
            dict_values, dict_model,
        )

        energy_provider_consumption_sources = prepare_energy_provider_consumption_sources(
            dict_values, dict_model,
        )

        def net_zero_energy(model):
            total_feedin_to_energy_provider = 0
            total_consumption_from_energy_provider = 0

            # Get the flows from provider sources and add weighing
            for asset in energy_provider_consumption_sources:
                consumption_of_one_provider = (
                    sum(
                        model.flow[
                            energy_provider_consumption_sources[asset][
                                OEMOF_SOLPH_OBJECT_ASSET
                            ],
                            energy_provider_consumption_sources[asset][
                                OEMOF_SOLPH_OBJECT_BUS
                            ],
                            :,
                        ]
                    )
                    * energy_provider_consumption_sources[asset][
                        WEIGHTING_FACTOR_ENERGY_CARRIER
                    ]
                )
                total_consumption_from_energy_provider += consumption_of_one_provider

            # Get the flows from provider sources and add weighing
            for asset in energy_provider_feedin_sinks:
                feedin_of_one_provider = (
                    sum(
                        model.flow[
                            energy_provider_feedin_sinks[asset][OEMOF_SOLPH_OBJECT_BUS],
                            energy_provider_feedin_sinks[asset][
                                OEMOF_SOLPH_OBJECT_ASSET
                            ],
                            :,
                        ]
                    )
                    * energy_provider_feedin_sinks[asset][
                        WEIGHTING_FACTOR_ENERGY_CARRIER
                    ]
                )
                total_feedin_to_energy_provider += feedin_of_one_provider

            expr = (
                total_feedin_to_energy_provider - total_consumption_from_energy_provider
            )
            return expr >= 0

        model.constraint_net_zero_energy = po.Constraint(rule=net_zero_energy)

        logging.info("Added net zero energy (NZE) constraint.")
        answer = model
    else:
        answer = None

    return answer
