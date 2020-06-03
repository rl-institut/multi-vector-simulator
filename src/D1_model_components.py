"""
Module D1 includes all functions that are required to build an oemof model with adaptable components.

- add transformer objects (fix, to be optimized)
- add source objects (fix, to be optimized, dispatchable, non-dispatchable)
- add sink objects (fix, to be optimized, dispatchable, non-dispatchable)
- add storage objects (fix, to be optimized)
- add multiple input/output busses if required for each of the assets
- add oemof component parameters as scalar or timeseries values

"""

import logging

import oemof.solph as solph

from src.constants_json_strings import (
    VALUE,
    LABEL,
    OPEX_VAR,
    OPTIMIZE_CAP,
    INSTALLED_CAP,
    EFFICIENCY,
)


def transformer(model, dict_asset, **kwargs):
    r"""
    Defines a transformer component specified in `dict_asset`.

    Depending on the 'value' of 'optimizeCap' in `dict_asset` the transformer
    is defined with a fixed capacity or a capacity to be optimized.
    The transformer has multiple or single input or output busses depending on
    the types of keys 'input_bus_name' and 'output_bus_name' in `dict_asset`.
    todo info about constant efficiency and time series as efficiency

    Parameters
    ----------
    model : oemof.solph.network.EnergySystem object
        See the oemof documentation for more information.
    dict_asset : dict
        Contains information about the transformer like (not exhaustive):
        efficiency, installed capacity ('installedCap'), information on the
        busses the transformer is connected to ('input_bus_name',
        'output_bus_name').

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
    return


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
        busses the storage is connected to ('input_bus_name',
        'output_bus_name'),

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

    """
    check_optimize_cap(
        model,
        dict_asset,
        func_constant=storage_fix,
        func_optimize=storage_optimize,
        **kwargs,
    )
    return


def sink(model, dict_asset, **kwargs):
    r"""
    Defines a sink component specified in `dict_asset`.

    Depending on the 'value' of 'optimizeCap' in `dict_asset` the sink
    is defined with a fixed capacity or a capacity to be optimized. If a time
    series is provided for the sink (key 'timeseries' in `dict_asset`) it is
    defined as a non dispatchable sink, otherwise as dispatchable sink.
    The sink has multiple or a single input bus depending on the type of the
    key 'input_bus_name' in `dict_asset`.

    Parameters
    ----------
    model : oemof.solph.network.EnergySystem object
        See the oemof documentation for more information.
    dict_asset : dict
        Contains information about the storage like (not exhaustive):
        efficiency, installed capacity ('installedCap'), information on the
        busses the sink is connected to ('input_bus_name'),

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

    """
    if "timeseries" in dict_asset:
        sink_non_dispatchable(model, dict_asset, **kwargs)
    else:
        sink_dispatchable(model, dict_asset, **kwargs)
    return


def source(model, dict_asset, **kwargs):
    r"""
    Defines a source component specified in `dict_asset`.

    Depending on the 'value' of 'optimizeCap' in `dict_asset` the source
    is defined with a fixed capacity or a capacity to be optimized. If a time
    series is provided for the source (key 'timeseries' in `dict_asset`) it is
    defined as a non dispatchable source, otherwise as dispatchable source.
    The source has multiple or a single output bus depending on the type of the
    key 'input_bus_name' in `dict_asset`.

    Parameters
    ----------
    model : oemof.solph.network.EnergySystem object
        See the oemof documentation for more information.
    dict_asset : dict
        Contains information about the storage like (not exhaustive):
        efficiency, installed capacity ('installedCap'), information on the
        busses the sink is connected to ('input_bus_name'),

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

    Todos
    -----
    * We should actually not allow multiple output busses, probably - because a
        pv would then feed in twice as much as solar_gen_specific for example,
        see issue #121

    """
    if "dispatchable" in dict_asset and dict_asset["dispatchable"] == True:
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
    return


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
        busses the asset is connected to (f.e. 'input_bus_name',
        'output_bus_name').
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

    Todos
    -----
    Might be possible to drop non invest optimization in favour of invest optimization if max_capactiy
    attributes ie. are set to 0 for fix (but less beautiful, and in case of generator even blocks nonconvex opt.).

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the component object.

    """
    if dict_asset[OPTIMIZE_CAP][VALUE] == False:
        func_constant(model, dict_asset, **kwargs)
        logging.debug(
            "Defined asset %s as %s (fix capacity)",
            dict_asset[LABEL],
            dict_asset["type_oemof"],
        )

    elif dict_asset[OPTIMIZE_CAP][VALUE] == True:
        func_optimize(model, dict_asset, **kwargs)
        logging.debug(
            "Defined asset %s as %s (to be optimized)",
            dict_asset[LABEL],
            dict_asset["type_oemof"],
        )
    else:
        raise ValueError(
            f"Input error! 'optimize_cap' of asset {dict_asset['label']}\n should be True/False but is {dict_asset['optimizeCap']['value']}."
        )
    return


def bus(model, name, **kwargs):
    r"""
    Adds bus `name` to `model` and to 'busses' in `kwargs`.

    """
    logging.debug("Added: Bus %s", name)
    bus = solph.Bus(label=name)
    kwargs["busses"].update({name: bus})
    model.add(bus)
    return


def transformer_constant_efficiency_fix(model, dict_asset, **kwargs):
    r"""
    Defines a transformer with constant efficiency and fixed capacity.

    See :py:func:`~.transformer` for more information, including parameters.


    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the transformer object.

    """
    # check if the transformer has multiple input or multiple output busses
    if isinstance(dict_asset["input_bus_name"], list) or isinstance(
        dict_asset["output_bus_name"], list
    ):
        if isinstance(dict_asset["input_bus_name"], list):
            inputs = {}
            index = 0
            for bus in dict_asset["input_bus_name"]:
                variable_costs = dict_asset[OPEX_VAR][VALUE][index]
                inputs[kwargs["busses"][bus]] = solph.Flow(
                    nominal_value=dict_asset[INSTALLED_CAP][VALUE],
                    variable_costs=variable_costs,
                )
                index += 1
            outputs = {kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow()}
            efficiencies = {}
            for i in range(len(dict_asset[EFFICIENCY][VALUE])):
                efficiencies[kwargs["busses"][dict_asset["input_bus_name"][i]]] = (
                    1 / dict_asset[EFFICIENCY][VALUE][i]
                )

        else:
            inputs = {kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow()}
            outputs = {}
            index = 0
            for bus in dict_asset["output_bus_name"]:
                variable_costs = dict_asset[OPEX_VAR][VALUE][index]
                outputs[kwargs["busses"][bus]] = solph.Flow(
                    nominal_value=dict_asset[INSTALLED_CAP][VALUE],
                    variable_costs=variable_costs,
                )
                index += 1
            efficiencies = {}
            for i in range(len(dict_asset[EFFICIENCY][VALUE])):
                efficiencies[
                    kwargs["busses"][dict_asset["output_bus_name"][i]]
                ] = dict_asset[EFFICIENCY][VALUE][i]

    else:
        inputs = {kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow()}
        outputs = {
            kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                nominal_value=dict_asset[INSTALLED_CAP][VALUE],
                variable_costs=dict_asset[OPEX_VAR][VALUE],
            )
        }
        efficiencies = {
            kwargs["busses"][dict_asset["output_bus_name"]]: dict_asset[EFFICIENCY][
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
    kwargs["transformers"].update({dict_asset[LABEL]: transformer})
    return


def transformer_constant_efficiency_optimize(model, dict_asset, **kwargs):
    r"""
    Defines a transformer with constant efficiency and a capacity to be optimized.

    See :py:func:`~.transformer` for more information, including parameters.

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the transformer object.

    """
    # check if the transformer has multiple input or multiple output busses
    # the investment object is always in the output bus
    if isinstance(dict_asset["input_bus_name"], list) or isinstance(
        dict_asset["output_bus_name"], list
    ):
        if isinstance(dict_asset["input_bus_name"], list):
            inputs = {}
            index = 0
            for bus in dict_asset["input_bus_name"]:
                variable_costs = dict_asset[OPEX_VAR][VALUE][index]
                inputs[kwargs["busses"][bus]] = solph.Flow(
                    existing=dict_asset[INSTALLED_CAP][VALUE],
                    variable_costs=variable_costs,
                )
                index += 1
            outputs = {
                kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                    investment=solph.Investment(
                        ep_costs=dict_asset["simulation_annuity"][VALUE],
                        maximum=dict_asset["maximumCap"][VALUE],
                    ),
                    existing=dict_asset[INSTALLED_CAP][VALUE],
                    variable_costs=dict_asset[OPEX_VAR][VALUE],
                )
            }
            efficiencies = {}
            for i in range(len(dict_asset[EFFICIENCY][VALUE])):
                efficiencies[kwargs["busses"][dict_asset["input_bus_name"][i]]] = 1 / (
                    dict_asset[EFFICIENCY][VALUE][i]
                )

        else:
            inputs = {kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow()}
            outputs = {}
            index = 0
            for bus in dict_asset["output_bus_name"]:
                variable_costs = dict_asset[OPEX_VAR][VALUE][index]
                outputs[kwargs["busses"][bus]] = solph.Flow(
                    investment=solph.Investment(
                        ep_costs=dict_asset["simulation_annuity"][VALUE],
                        maximum=dict_asset["maximumCap"][VALUE],
                    ),
                    existing=dict_asset[INSTALLED_CAP][VALUE],
                    variable_costs=variable_costs,
                )
                index += 1
            efficiencies = {}
            for i in range(len(dict_asset[EFFICIENCY][VALUE])):
                efficiencies[
                    kwargs["busses"][dict_asset["output_bus_name"][i]]
                ] = dict_asset[EFFICIENCY][VALUE][i]

    else:
        inputs = {kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow()}
        outputs = {
            kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                investment=solph.Investment(
                    ep_costs=dict_asset["simulation_annuity"][VALUE],
                    maximum=dict_asset["maximumCap"][VALUE],
                ),
                existing=dict_asset[INSTALLED_CAP][VALUE],
                variable_costs=dict_asset[OPEX_VAR][VALUE],
            )
        }
        efficiencies = {
            kwargs["busses"][dict_asset["output_bus_name"]]: dict_asset[EFFICIENCY][
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
    kwargs["transformers"].update({dict_asset[LABEL]: transformer})
    return


def storage_fix(model, dict_asset, **kwargs):
    r"""
    Defines a storage with a fixed capacity.

    See :py:func:`~.storage` for more information, including parameters.

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the storage object.

    """
    storage = solph.components.GenericStorage(
        label=dict_asset[LABEL],
        nominal_storage_capacity=dict_asset["storage capacity"][INSTALLED_CAP][VALUE],
        inputs={
            kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow(
                nominal_value=dict_asset["input power"][INSTALLED_CAP][
                    VALUE
                ],  # limited through installed capacity, NOT c-rate
                variable_costs=dict_asset["input power"][OPEX_VAR][VALUE],
            )
        },  # maximum charge possible in one timestep
        outputs={
            kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                nominal_value=dict_asset["output power"][INSTALLED_CAP][
                    VALUE
                ],  # limited through installed capacity, NOT c-rate #todo actually, if we only have a lithium battery... crate should suffice? i mean, with crate fixed AND fixed power, this is defined two times
                variable_costs=dict_asset["output power"][OPEX_VAR][VALUE],
            )
        },  # maximum discharge possible in one timestep
        loss_rate=dict_asset["storage capacity"][EFFICIENCY][
            VALUE
        ],  # from timestep to timestep
        min_storage_level=dict_asset["storage capacity"]["soc_min"][VALUE],
        max_storage_level=dict_asset["storage capacity"]["soc_max"][VALUE],
        initial_storage_level=dict_asset["storage capacity"]["soc_initial"][
            VALUE
        ],  # in terms of SOC
        inflow_conversion_factor=dict_asset["input power"][EFFICIENCY][
            VALUE
        ],  # storing efficiency
        outflow_conversion_factor=dict_asset["output power"][EFFICIENCY][VALUE],
    )  # efficiency of discharge
    model.add(storage)
    kwargs["storages"].update({dict_asset[LABEL]: storage})
    return


def storage_optimize(model, dict_asset, **kwargs):
    r"""
    Defines a storage with a capacity to be optimized.

    See :py:func:`~.storage` for more information, including parameters.

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the storage object.

    """
    storage = solph.components.GenericStorage(
        label=dict_asset[LABEL],
        existing=dict_asset["storage capacity"][INSTALLED_CAP][
            VALUE
        ],  # todo I think this parameter is not used in the GenericStorage
        investment=solph.Investment(
            ep_costs=dict_asset["storage capacity"]["simulation_annuity"][VALUE],
            maximum=dict_asset["storage capacity"]["maximumCap"][VALUE],
        ),
        inputs={
            kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow(
                existing=dict_asset["input power"][INSTALLED_CAP][VALUE],
                investment=solph.Investment(
                    ep_costs=dict_asset["input power"]["simulation_annuity"][VALUE],
                    maximum=dict_asset["input power"]["maximumCap"][VALUE],
                ),
                variable_costs=dict_asset["input power"][OPEX_VAR][VALUE],
            )
        },  # maximum charge power
        outputs={
            kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                existing=dict_asset["output power"][INSTALLED_CAP][VALUE],
                investment=solph.Investment(
                    ep_costs=dict_asset["output power"]["simulation_annuity"][VALUE],
                    maximum=dict_asset["output power"]["maximumCap"][VALUE],
                ),
                variable_costs=dict_asset["output power"]["opex_var"][VALUE],
            )
        },  # maximum discharge power
        loss_rate=dict_asset["storage capacity"][EFFICIENCY][
            VALUE
        ],  # from timestep to timestep
        min_storage_level=dict_asset["storage capacity"]["soc_min"][VALUE],
        max_storage_level=dict_asset["storage capacity"]["soc_max"][VALUE],
        initial_storage_level=dict_asset["storage capacity"]["soc_initial"][
            VALUE
        ],  # in terms of SOC #implication: balanced = True, ie. start=end
        inflow_conversion_factor=dict_asset["input power"][EFFICIENCY][
            VALUE
        ],  # storing efficiency
        outflow_conversion_factor=dict_asset["output power"][EFFICIENCY][
            VALUE
        ],  # efficiency of discharge
        invest_relation_input_capacity=dict_asset["input power"]["c_rate"][VALUE],
        # storage can be charged with invest_relation_output_capacity*capacity in one timeperiod
        invest_relation_output_capacity=dict_asset["output power"]["c_rate"][VALUE]
        # storage can be emptied with invest_relation_output_capacity*capacity in one timeperiod
    )
    model.add(storage)
    kwargs["storages"].update({dict_asset[LABEL]: storage})
    return


def source_non_dispatchable_fix(model, dict_asset, **kwargs):
    r"""
    Defines a non dispatchable source with a fixed capacity.

    See :py:func:`~.source` for more information, including parameters.

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the source object.

    """
    # check if the source has multiple output flows
    if isinstance(dict_asset["output_bus_name"], list):
        outputs = {}
        index = 0
        for bus in dict_asset["output_bus_name"]:
            outputs[kwargs["busses"][bus]] = solph.Flow(
                label=dict_asset[LABEL],
                actual_value=dict_asset["timeseries"],
                fixed=True,
                nominal_value=dict_asset[INSTALLED_CAP][VALUE],
                variable_costs=dict_asset["opex_var"][0],
            )
            index += 1
    else:
        outputs = {
            kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                label=dict_asset[LABEL],
                actual_value=dict_asset["timeseries"],
                fixed=True,
                nominal_value=dict_asset[INSTALLED_CAP][VALUE],
                variable_costs=dict_asset["opex_var"][VALUE],
            )
        }

    source_non_dispatchable = solph.Source(label=dict_asset[LABEL], outputs=outputs)

    model.add(source_non_dispatchable)
    kwargs["sources"].update({dict_asset[LABEL]: source_non_dispatchable})
    return


def source_non_dispatchable_optimize(model, dict_asset, **kwargs):
    r"""
    Defines a non dispatchable source with a capacity to be optimized.

    See :py:func:`~.source` for more information, including parameters.

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the source object.

    """
    # check if the source has multiple output busses
    if isinstance(dict_asset["output_bus_name"], list):
        outputs = {}
        index = 0
        for bus in dict_asset["output_bus_name"]:
            outputs[kwargs["busses"][bus]] = solph.Flow(
                label=dict_asset[LABEL],
                actual_value=dict_asset["timeseries_normalized"],
                fixed=True,
                existing=dict_asset[INSTALLED_CAP][VALUE],
                investment=solph.Investment(
                    ep_costs=dict_asset["simulation_annuity"][VALUE]
                    / dict_asset["timeseries_peak"][VALUE],
                    maximum=dict_asset["maximumCap"][VALUE],
                ),
                variable_costs=dict_asset["opex_var"][VALUE][index]
                / dict_asset["timeseries_peak"][VALUE],
            )
            index += 1

    else:
        outputs = {
            kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                label=dict_asset[LABEL],
                actual_value=dict_asset["timeseries_normalized"],
                fixed=True,
                existing=dict_asset[INSTALLED_CAP][VALUE],
                investment=solph.Investment(
                    ep_costs=dict_asset["simulation_annuity"][VALUE]
                    / dict_asset["timeseries_peak"][VALUE],
                    maximum=dict_asset["maximumCap"][VALUE],
                ),
                variable_costs=dict_asset["opex_var"][VALUE]
                / dict_asset["timeseries_peak"][VALUE],
            )
        }
    source_non_dispatchable = solph.Source(label=dict_asset[LABEL], outputs=outputs)

    model.add(source_non_dispatchable)
    kwargs["sources"].update({dict_asset[LABEL]: source_non_dispatchable})
    return


def source_dispatchable_optimize(model, dict_asset, **kwargs):
    if "timeseries_normalized" in dict_asset:
        # check if the source has multiple output busses
        if isinstance(dict_asset["output_bus_name"], list):
            outputs = {}
            index = 0
            for bus in dict_asset["output_bus_name"]:
                # check if maximumCap parameter exists
                # and add it to solph.Flow()
                outputs[kwargs["busses"][bus]] = solph.Flow(
                    label=dict_asset[LABEL],
                    max=dict_asset["timeseries_normalized"],
                    investment=solph.Investment(
                        ep_costs=dict_asset["simulation_annuity"][VALUE]
                        / dict_asset["timeseries_peak"][VALUE],
                        maximum=dict_asset["maximumCap"][VALUE],
                    ),
                    variable_costs=dict_asset["opex_var"][VALUE][0]
                    / dict_asset["timeseries_peak"][VALUE],
                )
                index += 1
        else:
            outputs = {
                kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                    label=dict_asset[LABEL],
                    max=dict_asset["timeseries_normalized"],
                    investment=solph.Investment(
                        ep_costs=dict_asset["simulation_annuity"][VALUE]
                        / dict_asset["timeseries_peak"][VALUE],
                        maximum=dict_asset["maximumCap"][VALUE],
                    ),
                    variable_costs=dict_asset["opex_var"][VALUE]
                    / dict_asset["timeseries_peak"][VALUE],
                )
            }

        source_dispatchable = solph.Source(label=dict_asset[LABEL], outputs=outputs,)
    else:
        if "timeseries" in dict_asset:
            logging.error(
                "Change code in D1/source_dispatchable: timeseries_normalized not the only key determining the flow"
            )
        # check if the source has multiple output busses
        if isinstance(dict_asset["output_bus_name"], list):
            outputs = {}
            index = 0
            for bus in dict_asset["output_bus_name"]:
                outputs[kwargs["busses"][bus]] = solph.Flow(
                    label=dict_asset[LABEL],
                    investment=solph.Investment(
                        ep_costs=dict_asset["simulation_annuity"][VALUE]
                    ),
                    variable_costs=dict_asset["opex_var"][VALUE][index],
                )
                index += 1
        else:
            outputs = {
                kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                    label=dict_asset[LABEL],
                    investment=solph.Investment(
                        ep_costs=dict_asset["simulation_annuity"][VALUE]
                    ),
                    variable_costs=dict_asset["opex_var"][VALUE],
                )
            }

        source_dispatchable = solph.Source(label=dict_asset[LABEL], outputs=outputs,)
    model.add(source_dispatchable)
    kwargs["sources"].update({dict_asset[LABEL]: source_dispatchable})
    logging.info("Added: Dispatchable source %s", dict_asset[LABEL])
    return


def source_dispatchable_fix(model, dict_asset, **kwargs):
    r"""
    Defines a dispatchable source with a fixed capacity.

    See :py:func:`~.source` for more information, including parameters.

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the source object.

    """
    # todo 'timeseries_normalized' is correct term?
    if "timeseries_normalized" in dict_asset:
        # check if the source has multiple output busses
        if isinstance(dict_asset["output_bus_name"], list):
            outputs = {}
            index = 0
            for bus in dict_asset["output_bus_name"]:
                outputs[kwargs["busses"][bus]] = solph.Flow(
                    label=dict_asset[LABEL],
                    max=dict_asset["timeseries_normalized"],
                    existing=dict_asset[INSTALLED_CAP][VALUE],
                    variable_costs=dict_asset["opex_var"][VALUE][index],
                )
                index += 1
        else:
            outputs = {
                kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                    label=dict_asset[LABEL],
                    max=dict_asset["timeseries_normalized"],
                    existing=dict_asset[INSTALLED_CAP][VALUE],
                    variable_costs=dict_asset["opex_var"][VALUE],
                )
            }
        source_dispatchable = solph.Source(label=dict_asset[LABEL], outputs=outputs,)
    else:
        if "timeseries" in dict_asset:
            logging.error(
                "Change code in D1/source_dispatchable: timeseries_normalized not the only key determining the flow"
            )
        # check if the source has multiple output busses
        if isinstance(dict_asset["output_bus_name"], list):
            outputs = {}
            index = 0
            for bus in dict_asset["output_bus_name"]:
                outputs[kwargs["busses"][bus]] = solph.Flow(
                    label=dict_asset[LABEL],
                    existing=dict_asset[INSTALLED_CAP][VALUE],
                    variable_costs=dict_asset["opex_var"][VALUE][index],
                )
                index += 1
        else:
            outputs = {
                kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                    label=dict_asset[LABEL],
                    existing=dict_asset[INSTALLED_CAP][VALUE],
                    variable_costs=dict_asset["opex_var"][VALUE],
                )
            }
        source_dispatchable = solph.Source(label=dict_asset[LABEL], outputs=outputs,)
    model.add(source_dispatchable)
    kwargs["sources"].update({dict_asset[LABEL]: source_dispatchable})
    logging.info("Added: Dispatchable source %s", dict_asset[LABEL])
    return


def sink_dispatchable(model, dict_asset, **kwargs):
    r"""
    Defines a dispatchable sink.

    See :py:func:`~.sink` for more information, including parameters.

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the sink object.

    """
    # check if the sink has multiple input busses
    if isinstance(dict_asset["input_bus_name"], list):
        inputs = {}
        index = 0
        for bus in dict_asset["input_bus_name"]:
            inputs[kwargs["busses"][bus]] = solph.Flow(
                label=dict_asset[LABEL],
                variable_costs=dict_asset["opex_var"][VALUE][index],
            )
            index += 1
    else:
        inputs = {
            kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow(
                label=dict_asset[LABEL], variable_costs=dict_asset["opex_var"][VALUE],
            )
        }

    # create and add excess electricity sink to micro_grid_system - variable
    sink_dispatchable = solph.Sink(label=dict_asset[LABEL], inputs=inputs,)
    model.add(sink_dispatchable)
    kwargs["sinks"].update({dict_asset[LABEL]: sink_dispatchable})
    logging.info("Added: Dispatchable sink %s", dict_asset[LABEL])
    return


def sink_non_dispatchable(model, dict_asset, **kwargs):
    r"""
    Defines a non dispatchable sink.

    See :py:func:`~.sink` for more information, including parameters.

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the sink object.

    """
    # check if the sink has multiple input busses
    if isinstance(dict_asset["input_bus_name"], list):
        inputs = {}
        index = 0
        for bus in dict_asset["input_bus_name"]:
            inputs[kwargs["busses"][bus]] = solph.Flow(
                actual_value=dict_asset["timeseries"], nominal_value=1, fixed=True
            )
            index += 1
    else:
        inputs = {
            kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow(
                actual_value=dict_asset["timeseries"], nominal_value=1, fixed=True
            )
        }

    # create and add demand sink to micro_grid_system - fixed
    sink_demand = solph.Sink(label=dict_asset[LABEL], inputs=inputs,)
    model.add(sink_demand)
    kwargs["sinks"].update({dict_asset[LABEL]: sink_demand})
    logging.info("Added: Non-dispatchable sink %s", dict_asset[LABEL])
    return
