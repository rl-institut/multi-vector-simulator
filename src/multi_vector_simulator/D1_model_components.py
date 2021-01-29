"""
Module D1 - Oemof components
============================

Module D1 includes all functions that are required to build an oemof model with adaptable components.

- add transformer objects (fix, to be optimized)
- add source objects (fix, to be optimized, dispatchable, non-dispatchable)
- add sink objects (fix, to be optimized, dispatchable, non-dispatchable)
- add storage objects (fix, to be optimized)
- add multiple input/output busses if required for each of the assets
- add oemof component parameters as scalar or time series values

"""

import logging

import oemof.solph as solph

from multi_vector_simulator.utils.constants_json_strings import (
    VALUE,
    LABEL,
    DISPATCH_PRICE,
    AVAILABILITY_DISPATCH,
    OPTIMIZE_CAP,
    INSTALLED_CAP,
    EFFICIENCY,
    INPUT_POWER,
    OUTPUT_POWER,
    C_RATE,
    SOC_INITIAL,
    SOC_MAX,
    SOC_MIN,
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
    DISPATCHABILITY,
    OEMOF_ASSET_TYPE,
    OEMOF_GEN_STORAGE,
    OEMOF_SINK,
    OEMOF_SOURCE,
    OEMOF_TRANSFORMER,
    OEMOF_BUSSES,
    EMISSION_FACTOR,
)


def transformer(model, dict_asset, **kwargs):
    r"""
    Defines a transformer component specified in `dict_asset`.

    Depending on the 'value' of 'optimizeCap' in `dict_asset` the transformer
    is defined with a fixed capacity or a capacity to be optimized.
    The transformer has multiple or single input or output busses depending on
    the types of keys 'inflow_direction' and 'outflow_direction' in `dict_asset`.

    Parameters
    ----------
    model : oemof.solph.network.EnergySystem object
        See the oemof documentation for more information.
    dict_asset : dict
        Contains information about the transformer like (not exhaustive):
        efficiency, installed capacity ('installedCap'), information on the
        busses the transformer is connected to ('inflow_direction',
        'outflow_direction').

    Other Parameters
    ----------------
    busses : dict
    sinks : dict, optional
    sources : dict, optional
    transformers : dict
    storages : dict, optional

    Notes
    -----
    The transformer has either multiple input or multiple output busses.

    The following functions are used for defining the transformer:
    * :py:func:`~.transformer_constant_efficiency_fix`
    * :py:func:`~.transformer_constant_efficiency_optimize`

    Tested with:
    - test_transformer_optimize_cap_single_busses()
    - test_transformer_optimize_cap_multiple_input_busses()
    - test_transformer_optimize_cap_multiple_output_busses()
    - test_transformer_fix_cap_single_busses()
    - test_transformer_fix_cap_multiple_input_busses()
    - test_transformer_fix_cap_multiple_output_busses()

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with transformer object.

    """
    check_optimize_cap(
        model,
        dict_asset,
        func_constant=transformer_constant_efficiency_fix,
        func_optimize=transformer_constant_efficiency_optimize,
        **kwargs,
    )


def storage(model, dict_asset, **kwargs):
    r"""
    Defines a storage component specified in `dict_asset`.

    Depending on the 'value' of 'optimizeCap' in `dict_asset` the storage
    is defined with a fixed capacity or a capacity to be optimized.

    Parameters
    ----------
    model : oemof.solph.network.EnergySystem object
        See the oemof documentation for more information.
    dict_asset : dict
        Contains information about the storage like (not exhaustive):
        efficiency, installed capacity ('installedCap'), information on the
        busses the storage is connected to ('inflow_direction',
        'outflow_direction'),

    Other Parameters
    ----------------
    busses : dict
    sinks : dict, optional
    sources : dict, optional
    transformers : dict, optional
    storages : dict

    Notes
    -----
    The following functions are used for defining the storage:
    * :py:func:`~.storage_fix`
    * :py:func:`~.storage_optimize`

    Tested with:
    - test_storage_optimize()
    - test_storage_fix()

    """
    check_optimize_cap(
        model,
        dict_asset,
        func_constant=storage_fix,
        func_optimize=storage_optimize,
        **kwargs,
    )


def sink(model, dict_asset, **kwargs):
    r"""
    Defines a sink component specified in `dict_asset`.

    Depending on the 'value' of 'optimizeCap' in `dict_asset` the sink
    is defined with a fixed capacity or a capacity to be optimized. If a time
    series is provided for the sink (key 'timeseries' in `dict_asset`) it is
    defined as a non dispatchable sink, otherwise as dispatchable sink.
    The sink has multiple or a single input bus depending on the type of the
    key 'inflow_direction' in `dict_asset`.

    Parameters
    ----------
    model : oemof.solph.network.EnergySystem object
        See the oemof documentation for more information.
    dict_asset : dict
        Contains information about the storage like (not exhaustive):
        efficiency, installed capacity ('installedCap'), information on the
        busses the sink is connected to ('inflow_direction'),

    Other Parameters
    ----------------
    busses : dict
    sinks : dict
    sources : dict, optional
    transformers : dict, optional
    storages : dict, optional

    Notes
    -----
    The following functions are used for defining the sink:
    * :py:func:`~.sink_non_dispatchable`
    * :py:func:`~.sink_dispatchable`

    Tested with:
    - test_sink_non_dispatchable_single_input_bus()
    - test_sink_non_dispatchable_multiple_input_busses()
    - test_sink_dispatchable_single_input_bus()
    - test_sink_dispatchable_multiple_input_busses()

    """
    if TIMESERIES in dict_asset:
        sink_non_dispatchable(model, dict_asset, **kwargs)
    else:
        sink_dispatchable_optimize(model, dict_asset, **kwargs)


def source(model, dict_asset, **kwargs):
    r"""
    Defines a source component specified in `dict_asset`.

    Depending on the 'value' of 'optimizeCap' in `dict_asset` the source
    is defined with a fixed capacity or a capacity to be optimized. If a time
    series is provided for the source (key 'timeseries' in `dict_asset`) it is
    defined as a non dispatchable source, otherwise as dispatchable source.
    The source has multiple or a single output bus depending on the type of the
    key 'inflow_direction' in `dict_asset`.

    Parameters
    ----------
    model : oemof.solph.network.EnergySystem object
        See the oemof documentation for more information.
    dict_asset : dict
        Contains information about the storage like (not exhaustive):
        efficiency, installed capacity ('installedCap'), information on the
        busses the sink is connected to ('inflow_direction'),

    Other Parameters
    ----------------
    busses : dict
    sinks : dict
    sources : dict, optional
    transformers : dict, optional
    storages : dict, optional

    Notes
    -----
    The following functions are used for defining the source:
    * :py:func:`~.source_dispatchable_fix`
    * :py:func:`~.source_dispatchable_optimize`
    * :py:func:`~.source_non_dispatchable_fix`
    * :py:func:`~.source_non_dispatchable_optimize`

    Tested with:
    - test_source_non_dispatchable_optimize()
    - test_source_non_dispatchable_fix()
    - test_source_dispatchable_optimize_normalized_timeseries()
    - test_source_dispatchable_optimize_timeseries_not_normalized_timeseries()
    - test_source_dispatchable_fix_normalized_timeseries()
    - test_source_dispatchable_fix_timeseries_not_normalized_timeseries()

    Todos
    -----
    * We should actually not allow multiple output busses, probably - because a
        pv would then feed in twice as much as solar_gen_specific for example,
        see issue #121

    """
    if DISPATCHABILITY in dict_asset and dict_asset[DISPATCHABILITY] is True:
        check_optimize_cap(
            model,
            dict_asset,
            func_constant=source_dispatchable_fix,
            func_optimize=source_dispatchable_optimize,
            **kwargs,
        )

    else:
        check_optimize_cap(
            model,
            dict_asset,
            func_constant=source_non_dispatchable_fix,
            func_optimize=source_non_dispatchable_optimize,
            **kwargs,
        )


def check_optimize_cap(model, dict_asset, func_constant, func_optimize, **kwargs):
    r"""
    Defines a component specified in `dict_asset` with fixed capacity or capacity to be optimized.

    Parameters
    ----------
    model : oemof.solph.network.EnergySystem object
        See the oemof documentation for more information.
    dict_asset : dict
        Contains information about the asset like (not exhaustive):
        efficiency, installed capacity ('installedCap'), information on the
        busses the asset is connected to (f.e. 'inflow_direction',
        'outflow_direction').
    func_constant : func
        Function to be applied if optimization not intended.
    func_optimize : func
        Function to be applied if optimization not intended.

    Other Parameters
    ----------------
    Required are `busses` and a dictionary belonging to the respective oemof
    type of the asset.

    busses : dict, optional
    sinks : dict, optional
    sources : dict, optional
    transformers : dict, optional
    storages : dict, optional

    Notes
    -----
    Tested with:
    - test_check_optimize_cap_raise_error()

    Todos
    -----
    Might be possible to drop non invest optimization in favour of invest optimization if max_capactiy
    attributes ie. are set to 0 for fix (but less beautiful, and in case of generator even blocks nonconvex opt.).

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the component object.

    """
    if dict_asset[OPTIMIZE_CAP][VALUE] is False:
        func_constant(model, dict_asset, **kwargs)
        if dict_asset[OEMOF_ASSET_TYPE] != "source":
            logging.debug(
                "Added: %s %s (fixed capacity)",
                dict_asset[OEMOF_ASSET_TYPE].capitalize(),
                dict_asset[LABEL],
            )

    elif dict_asset[OPTIMIZE_CAP][VALUE] is True:
        func_optimize(model, dict_asset, **kwargs)
        if dict_asset[OEMOF_ASSET_TYPE] != "source":
            logging.debug(
                "Added: %s %s (capacity to be optimized)",
                dict_asset[OEMOF_ASSET_TYPE].capitalize(),
                dict_asset[LABEL],
            )
    else:
        raise ValueError(
            f"Input error! '{OPTIMIZE_CAP}' of asset {dict_asset[LABEL]}\n should be True/False but is {dict_asset[OPTIMIZE_CAP][VALUE]}."
        )


def bus(model, name, **kwargs):
    r"""
    Adds bus `name` to `model` and to 'busses' in `kwargs`.

    Notes
    -----
    Tested with:
    - test_bus_add_to_empty_dict()
    - test_bus_add_to_not_empty_dict()

    """
    logging.debug(f"Added: Bus {name}")
    bus = solph.Bus(label=name)
    kwargs[OEMOF_BUSSES].update({name: bus})
    model.add(bus)


def transformer_constant_efficiency_fix(model, dict_asset, **kwargs):
    r"""
    Defines a transformer with constant efficiency and fixed capacity.

    See :py:func:`~.transformer` for more information, including parameters.

    Notes
    -----
    Tested with:
    - test_transformer_fix_cap_single_busses()
    - test_transformer_fix_cap_multiple_input_busses()
    - test_transformer_fix_cap_multiple_output_busses()

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the transformer object.

    """
    # check if the transformer has multiple input or multiple output busses
    if isinstance(dict_asset[INFLOW_DIRECTION], list) or isinstance(
        dict_asset[OUTFLOW_DIRECTION], list
    ):
        if isinstance(dict_asset[INFLOW_DIRECTION], list):
            inputs = {}
            for bus in dict_asset[INFLOW_DIRECTION]:
                inputs[kwargs[OEMOF_BUSSES][bus]] = solph.Flow()
            outputs = {
                kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
                    nominal_value=dict_asset[INSTALLED_CAP][VALUE],
                    variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
                )
            }
            efficiencies = {
                kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: dict_asset[
                    EFFICIENCY
                ][VALUE]
            }

        else:
            inputs = {kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow()}
            outputs = {}
            index = 0
            for bus in dict_asset[OUTFLOW_DIRECTION]:
                variable_costs = dict_asset[DISPATCH_PRICE][VALUE][index]
                outputs[kwargs[OEMOF_BUSSES][bus]] = solph.Flow(
                    nominal_value=dict_asset[INSTALLED_CAP][VALUE],
                    variable_costs=variable_costs,
                )
                index += 1
            efficiencies = {}
            for i in range(len(dict_asset[EFFICIENCY][VALUE])):
                efficiencies[
                    kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION][i]]
                ] = dict_asset[EFFICIENCY][VALUE][i]

    else:
        inputs = {kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow()}
        outputs = {
            kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
                nominal_value=dict_asset[INSTALLED_CAP][VALUE],
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
            )
        }
        efficiencies = {
            kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: dict_asset[EFFICIENCY][
                VALUE
            ]
        }

    transformer = solph.Transformer(
        label=dict_asset[LABEL],
        inputs=inputs,
        outputs=outputs,
        conversion_factors=efficiencies,
    )

    model.add(transformer)
    kwargs[OEMOF_TRANSFORMER].update({dict_asset[LABEL]: transformer})


def transformer_constant_efficiency_optimize(model, dict_asset, **kwargs):
    r"""
    Defines a transformer with constant efficiency and a capacity to be optimized.

    See :py:func:`~.transformer` for more information, including parameters.

    Notes
    -----
    Tested with:
    - test_transformer_optimize_cap_single_busses()
    - test_transformer_optimize_cap_multiple_input_busses()
    - test_transformer_optimize_cap_multiple_output_busses()

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the transformer object.

    """
    # check if the transformer has multiple input or multiple output busses
    # the investment object is always in the output bus
    if isinstance(dict_asset[INFLOW_DIRECTION], list) or isinstance(
        dict_asset[OUTFLOW_DIRECTION], list
    ):
        if isinstance(dict_asset[INFLOW_DIRECTION], list):
            inputs = {}
            for bus in dict_asset[INFLOW_DIRECTION]:
                inputs[kwargs[OEMOF_BUSSES][bus]] = solph.Flow()
            outputs = {
                kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
                    investment=solph.Investment(
                        ep_costs=dict_asset[SIMULATION_ANNUITY][VALUE],
                        maximum=dict_asset[MAXIMUM_CAP][VALUE],
                        existing=dict_asset[INSTALLED_CAP][VALUE],
                    ),
                    variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
                )
            }
            efficiencies = {
                kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: dict_asset[
                    EFFICIENCY
                ][VALUE]
            }

        else:
            inputs = {kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow()}
            outputs = {}
            index = 0
            for bus in dict_asset[OUTFLOW_DIRECTION]:
                variable_costs = dict_asset[DISPATCH_PRICE][VALUE][index]
                outputs[kwargs[OEMOF_BUSSES][bus]] = solph.Flow(
                    investment=solph.Investment(
                        ep_costs=dict_asset[SIMULATION_ANNUITY][VALUE],
                        maximum=dict_asset[MAXIMUM_CAP][VALUE],
                        existing=dict_asset[INSTALLED_CAP][VALUE],
                    ),
                    variable_costs=variable_costs,
                )
                index += 1
            efficiencies = {}
            for i in range(len(dict_asset[EFFICIENCY][VALUE])):
                efficiencies[
                    kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION][i]]
                ] = dict_asset[EFFICIENCY][VALUE][i]

    else:
        inputs = {kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow()}
        if AVAILABILITY_DISPATCH in dict_asset.keys():
            # This key is only present in DSO peak demand pricing transformers.
            outputs = {
                kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
                    investment=solph.Investment(
                        ep_costs=dict_asset[SIMULATION_ANNUITY][VALUE],
                        maximum=dict_asset[MAXIMUM_CAP][VALUE],
                        existing=dict_asset[INSTALLED_CAP][VALUE],
                    ),
                    variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
                    max=dict_asset[AVAILABILITY_DISPATCH].values,
                )
            }
        else:
            outputs = {
                kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
                    investment=solph.Investment(
                        ep_costs=dict_asset[SIMULATION_ANNUITY][VALUE],
                        maximum=dict_asset[MAXIMUM_CAP][VALUE],
                        existing=dict_asset[INSTALLED_CAP][VALUE],
                    ),
                    variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
                )
            }

        efficiencies = {
            kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: dict_asset[EFFICIENCY][
                VALUE
            ]
        }

    transformer = solph.Transformer(
        label=dict_asset[LABEL],
        inputs=inputs,
        outputs=outputs,
        conversion_factors=efficiencies,
    )

    model.add(transformer)
    kwargs[OEMOF_TRANSFORMER].update({dict_asset[LABEL]: transformer})


def storage_fix(model, dict_asset, **kwargs):
    r"""
    Defines a storage with a fixed capacity.

    See :py:func:`~.storage` for more information, including parameters.

    Notes
    -----
    Tested with:
    - test_storage_fix()

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the storage object.

    """
    storage = solph.components.GenericStorage(
        label=dict_asset[LABEL],
        nominal_storage_capacity=dict_asset[STORAGE_CAPACITY][INSTALLED_CAP][VALUE],
        inputs={
            kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow(
                nominal_value=dict_asset[INPUT_POWER][INSTALLED_CAP][
                    VALUE
                ],  # limited through installed capacity, NOT c-rate
                variable_costs=dict_asset[INPUT_POWER][DISPATCH_PRICE][VALUE],
            )
        },  # maximum charge possible in one timestep
        outputs={
            kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
                nominal_value=dict_asset[OUTPUT_POWER][INSTALLED_CAP][
                    VALUE
                ],  # limited through installed capacity, NOT c-rate #todo actually, if we only have a lithium battery... crate should suffice? i mean, with crate fixed AND fixed power, this is defined two times
                variable_costs=dict_asset[OUTPUT_POWER][DISPATCH_PRICE][VALUE],
            )
        },  # maximum discharge possible in one timestep
        loss_rate=1
        - dict_asset[STORAGE_CAPACITY][EFFICIENCY][VALUE],  # from timestep to timestep
        fixed_losses_absolute=dict_asset[STORAGE_CAPACITY][THERM_LOSSES_ABS][VALUE],
        fixed_losses_relative=dict_asset[STORAGE_CAPACITY][THERM_LOSSES_REL][VALUE],
        min_storage_level=dict_asset[STORAGE_CAPACITY][SOC_MIN][VALUE],
        max_storage_level=dict_asset[STORAGE_CAPACITY][SOC_MAX][VALUE],
        initial_storage_level=dict_asset[STORAGE_CAPACITY][SOC_INITIAL][
            VALUE
        ],  # in terms of SOC
        inflow_conversion_factor=dict_asset[INPUT_POWER][EFFICIENCY][
            VALUE
        ],  # storing efficiency
        outflow_conversion_factor=dict_asset[OUTPUT_POWER][EFFICIENCY][VALUE],
    )  # efficiency of discharge
    model.add(storage)
    kwargs[OEMOF_GEN_STORAGE].update({dict_asset[LABEL]: storage})


def storage_optimize(model, dict_asset, **kwargs):
    r"""
    Defines a storage with a capacity to be optimized.

    See :py:func:`~.storage` for more information, including parameters.

    Notes
    -----
    Tested with:
    - test_storage_optimize()
    - test_storage_optimize_investment_minimum_0_float()
    - test_storage_optimize_investment_minimum_0_time_series()
    - test_storage_optimize_investment_minimum_1_rel_float()
    - test_storage_optimize_investment_minimum_1_abs_float()
    - test_storage_optimize_investment_minimum_1_rel_times_series()
    - test_storage_optimize_investment_minimum_1_abs_times_series()

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the storage object.

    """
    # investment.minimum for an InvestmentStorage is 0 as default
    minimum = 0

    # Set investment.minimum to 1 if
    # non-zero fixed_thermal_losses_relative or fixed_thermal_losses_absolute exist as
    for losses in [THERM_LOSSES_REL, THERM_LOSSES_ABS]:
        # 1. float or
        try:
            float(dict_asset[STORAGE_CAPACITY][losses][VALUE])
            if dict_asset[STORAGE_CAPACITY][losses][VALUE] != 0:
                minimum = 1
        # 2. time series
        except TypeError:
            if sum(dict_asset[STORAGE_CAPACITY][losses][VALUE]) != 0:
                minimum = 1

    storage = solph.components.GenericStorage(
        label=dict_asset[LABEL],
        investment=solph.Investment(
            ep_costs=dict_asset[STORAGE_CAPACITY][SIMULATION_ANNUITY][VALUE],
            minimum=minimum,
            maximum=dict_asset[STORAGE_CAPACITY][MAXIMUM_CAP][VALUE],
            existing=dict_asset[STORAGE_CAPACITY][INSTALLED_CAP][VALUE],
        ),
        inputs={
            kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow(
                investment=solph.Investment(
                    ep_costs=dict_asset[INPUT_POWER][SIMULATION_ANNUITY][VALUE],
                    maximum=dict_asset[INPUT_POWER][MAXIMUM_CAP][VALUE],
                    existing=dict_asset[INPUT_POWER][INSTALLED_CAP][
                        VALUE
                    ],  # todo: `existing needed here?`
                ),
                variable_costs=dict_asset[INPUT_POWER][DISPATCH_PRICE][VALUE],
            )
        },  # maximum charge power
        outputs={
            kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
                investment=solph.Investment(
                    ep_costs=dict_asset[OUTPUT_POWER][SIMULATION_ANNUITY][VALUE],
                    maximum=dict_asset[OUTPUT_POWER][MAXIMUM_CAP][VALUE],
                    existing=dict_asset[OUTPUT_POWER][INSTALLED_CAP][
                        VALUE
                    ],  # todo: `existing needed here?`
                ),
                variable_costs=dict_asset[OUTPUT_POWER][DISPATCH_PRICE][VALUE],
            )
        },  # maximum discharge power
        loss_rate=1
        - dict_asset[STORAGE_CAPACITY][EFFICIENCY][VALUE],  # from timestep to timestep
        fixed_losses_absolute=dict_asset[STORAGE_CAPACITY][THERM_LOSSES_ABS][VALUE],
        fixed_losses_relative=dict_asset[STORAGE_CAPACITY][THERM_LOSSES_REL][VALUE],
        min_storage_level=dict_asset[STORAGE_CAPACITY][SOC_MIN][VALUE],
        max_storage_level=dict_asset[STORAGE_CAPACITY][SOC_MAX][VALUE],
        initial_storage_level=dict_asset[STORAGE_CAPACITY][SOC_INITIAL][
            VALUE
        ],  # in terms of SOC #implication: balanced = True, ie. start=end
        inflow_conversion_factor=dict_asset[INPUT_POWER][EFFICIENCY][
            VALUE
        ],  # storing efficiency
        outflow_conversion_factor=dict_asset[OUTPUT_POWER][EFFICIENCY][
            VALUE
        ],  # efficiency of discharge
        invest_relation_input_capacity=dict_asset[INPUT_POWER][C_RATE][VALUE],
        # storage can be charged with invest_relation_output_capacity*capacity in one timeperiod
        invest_relation_output_capacity=dict_asset[OUTPUT_POWER][C_RATE][VALUE]
        # storage can be emptied with invest_relation_output_capacity*capacity in one timeperiod
    )
    model.add(storage)
    kwargs[OEMOF_GEN_STORAGE].update({dict_asset[LABEL]: storage})


def source_non_dispatchable_fix(model, dict_asset, **kwargs):
    r"""
    Defines a non dispatchable source with a fixed capacity.

    See :py:func:`~.source` for more information, including parameters.

    Notes
    -----
    Tested with:
    - test_source_non_dispatchable_fix()

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the source object.

    """
    outputs = {
        kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
            label=dict_asset[LABEL],
            fix=dict_asset[TIMESERIES],
            nominal_value=dict_asset[INSTALLED_CAP][VALUE],
            variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
            emission_factor=dict_asset[EMISSION_FACTOR][VALUE],
        )
    }

    source_non_dispatchable = solph.Source(label=dict_asset[LABEL], outputs=outputs)

    model.add(source_non_dispatchable)
    kwargs[OEMOF_SOURCE].update({dict_asset[LABEL]: source_non_dispatchable})
    logging.debug(
        f"Added: Non-dispatchable source {dict_asset[LABEL]} (fixed capacity) to bus {dict_asset[OUTFLOW_DIRECTION]}.",
    )


def source_non_dispatchable_optimize(model, dict_asset, **kwargs):
    r"""
    Defines a non dispatchable source with a capacity to be optimized.

    See :py:func:`~.source` for more information, including parameters.

    Notes
    -----
    Tested with:
    - test_source_non_dispatchable_optimize()

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the source object.

    """
    outputs = {
        kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
            label=dict_asset[LABEL],
            fix=dict_asset[TIMESERIES_NORMALIZED],
            investment=solph.Investment(
                ep_costs=dict_asset[SIMULATION_ANNUITY][VALUE]
                / dict_asset[TIMESERIES_PEAK][VALUE],
                maximum=dict_asset[MAXIMUM_CAP][VALUE],
                existing=dict_asset[INSTALLED_CAP][VALUE],
            ),
            # variable_costs are devided by time series peak as normalized time series are used as actual_value
            variable_costs=dict_asset[DISPATCH_PRICE][VALUE]
            / dict_asset[TIMESERIES_PEAK][VALUE],
            # add emission_factor for emission contraint
            emission_factor=dict_asset[EMISSION_FACTOR][VALUE],
        )
    }
    source_non_dispatchable = solph.Source(label=dict_asset[LABEL], outputs=outputs)

    model.add(source_non_dispatchable)
    kwargs[OEMOF_SOURCE].update({dict_asset[LABEL]: source_non_dispatchable})
    logging.debug(
        f"Added: Non-dispatchable source {dict_asset[LABEL]} (capacity to be optimized) to bus {dict_asset[OUTFLOW_DIRECTION]}."
    )


def source_dispatchable_optimize(model, dict_asset, **kwargs):
    r"""
    Defines a dispatchable source with a fixed capacity.

    See :py:func:`~.source` for more information, including parameters.

    Notes
    -----
    Tested with:
    - test_source_dispatchable_optimize_normalized_timeseries()
    - test_source_dispatchable_optimize_timeseries_not_normalized_timeseries()

     Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the source object.

    """
    if TIMESERIES_NORMALIZED in dict_asset:
        outputs = {
            kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
                label=dict_asset[LABEL],
                max=dict_asset[TIMESERIES_NORMALIZED],
                investment=solph.Investment(
                    ep_costs=dict_asset[SIMULATION_ANNUITY][VALUE]
                    / dict_asset[TIMESERIES_PEAK][VALUE],
                    maximum=dict_asset[MAXIMUM_CAP][VALUE],
                    existing=dict_asset[INSTALLED_CAP][VALUE],
                ),
                # variable_costs are devided by time series peak as normalized time series are used as actual_value
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE]
                / dict_asset[TIMESERIES_PEAK][VALUE],
                # add emission_factor for emission contraint
                emission_factor=dict_asset[EMISSION_FACTOR][VALUE],
            )
        }
        source_dispatchable = solph.Source(label=dict_asset[LABEL], outputs=outputs,)
    else:
        if TIMESERIES in dict_asset:
            logging.info(
                f"Asset {dict_asset[LABEL]} is introduced as a dispatchable source with an availability schedule."
            )
            logging.debug(
                f"The availability schedule is solely introduced because the key {TIMESERIES_NORMALIZED} was not in the asset´s dictionary. \n"
                f"It should only be applied to DSO sources. "
                f"If the asset should not have this behaviour, please create an issue.",
            )
        outputs = {
            kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
                label=dict_asset[LABEL],
                investment=solph.Investment(
                    ep_costs=dict_asset[SIMULATION_ANNUITY][VALUE],
                    existing=dict_asset[INSTALLED_CAP][VALUE],
                    maximum=dict_asset[MAXIMUM_CAP][VALUE],
                ),
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
                # add emission_factor for emission contraint
                emission_factor=dict_asset[EMISSION_FACTOR][VALUE],
            )
        }
        source_dispatchable = solph.Source(label=dict_asset[LABEL], outputs=outputs,)
    model.add(source_dispatchable)
    kwargs[OEMOF_SOURCE].update({dict_asset[LABEL]: source_dispatchable})
    logging.debug(
        f"Added: Dispatchable source {dict_asset[LABEL]} (capacity to be optimized) to bus {dict_asset[OUTFLOW_DIRECTION]}."
    )


def source_dispatchable_fix(model, dict_asset, **kwargs):
    r"""
    Defines a dispatchable source with a fixed capacity.

    See :py:func:`~.source` for more information, including parameters.

    Notes
    -----
    Tested with:
    - test_source_dispatchable_fix_normalized_timeseries()
    - test_source_dispatchable_fix_timeseries_not_normalized_timeseries()

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the source object.

    """
    if TIMESERIES_NORMALIZED in dict_asset:
        outputs = {
            kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
                label=dict_asset[LABEL],
                max=dict_asset[TIMESERIES_NORMALIZED],
                existing=dict_asset[INSTALLED_CAP][VALUE],
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
                # add emission_factor for emission contraint
                emission_factor=dict_asset[EMISSION_FACTOR][VALUE],
            )
        }
        source_dispatchable = solph.Source(label=dict_asset[LABEL], outputs=outputs,)
    else:
        if TIMESERIES in dict_asset:
            logging.info(
                f"Asset {dict_asset[LABEL]} is introduced as a dispatchable source with an availability schedule."
            )
            logging.debug(
                f"The availability schedule is solely introduced because the key {TIMESERIES_NORMALIZED} was not in the asset´s dictionary. \n"
                f"It should only be applied to DSO sources. "
                f"If the asset should not have this behaviour, please create an issue.",
            )
        outputs = {
            kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
                label=dict_asset[LABEL],
                existing=dict_asset[INSTALLED_CAP][VALUE],
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
            )
        }
        source_dispatchable = solph.Source(label=dict_asset[LABEL], outputs=outputs,)
    model.add(source_dispatchable)
    kwargs[OEMOF_SOURCE].update({dict_asset[LABEL]: source_dispatchable})
    logging.debug(
        f"Added: Dispatchable source {dict_asset[LABEL]} (fixed capacity) to bus {dict_asset[OUTFLOW_DIRECTION]}."
    )


def sink_dispatchable_optimize(model, dict_asset, **kwargs):
    r"""
    Define a dispatchable sink.

    The dispatchable sink is capacity-optimized, without any costs connected to the capacity of the asset.
    Applications of this asset type are: Feed-in sink, excess sink.

    See :py:func:`~.sink` for more information, including parameters.

    Notes
    -----
    Tested with:
    - test_sink_dispatchable_single_input_bus()
    - test_sink_dispatchable_multiple_input_busses()

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the sink object.

    """
    # check if the sink has multiple input busses
    if isinstance(dict_asset[INFLOW_DIRECTION], list):
        inputs = {}
        index = 0
        for bus in dict_asset[INFLOW_DIRECTION]:
            inputs[kwargs[OEMOF_BUSSES][bus]] = solph.Flow(
                label=dict_asset[LABEL],
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE][index],
                investment=solph.Investment(),
            )
            index += 1
    else:
        inputs = {
            kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow(
                label=dict_asset[LABEL],
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
                investment=solph.Investment(),
            )
        }

    # create and add excess electricity sink to micro_grid_system - variable
    sink_dispatchable = solph.Sink(label=dict_asset[LABEL], inputs=inputs,)
    model.add(sink_dispatchable)
    kwargs[OEMOF_SINK].update({dict_asset[LABEL]: sink_dispatchable})
    logging.debug(
        f"Added: Dispatchable sink {dict_asset[LABEL]} (to be capacity optimized) to bus {dict_asset[INFLOW_DIRECTION]}.",
    )


def sink_non_dispatchable(model, dict_asset, **kwargs):
    r"""
    Defines a non dispatchable sink.

    See :py:func:`~.sink` for more information, including parameters.

    Notes
    -----
    Tested with:
    - test_sink_non_dispatchable_single_input_bus()
    - test_sink_non_dispatchable_multiple_input_busses()

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the sink object.

    """
    # check if the sink has multiple input busses
    if isinstance(dict_asset[INFLOW_DIRECTION], list):
        inputs = {}
        index = 0
        for bus in dict_asset[INFLOW_DIRECTION]:
            inputs[kwargs[OEMOF_BUSSES][bus]] = solph.Flow(
                fix=dict_asset[TIMESERIES], nominal_value=1
            )
            index += 1
    else:
        inputs = {
            kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow(
                fix=dict_asset[TIMESERIES], nominal_value=1
            )
        }

    # create and add demand sink to micro_grid_system - fixed
    sink_demand = solph.Sink(label=dict_asset[LABEL], inputs=inputs,)
    model.add(sink_demand)
    kwargs[OEMOF_SINK].update({dict_asset[LABEL]: sink_demand})
    logging.debug(
        f"Added: Non-dispatchable sink {dict_asset[LABEL]} to bus {dict_asset[INFLOW_DIRECTION]}"
    )
