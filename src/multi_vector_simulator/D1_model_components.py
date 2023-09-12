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

from oemof import solph

from multi_vector_simulator.utils.constants_json_strings import (
    VALUE,
    UNIT,
    LABEL,
    DISPATCH_PRICE,
    AVAILABILITY_DISPATCH,
    OPTIMIZE_CAP,
    INSTALLED_CAP,
    INSTALLED_CAP_NORMALIZED,
    EFFICIENCY,
    ENERGY_VECTOR,
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
    MAXIMUM_ADD_CAP,
    MAXIMUM_ADD_CAP_NORMALIZED,
    DISPATCHABILITY,
    OEMOF_ASSET_TYPE,
    OEMOF_GEN_STORAGE,
    OEMOF_SINK,
    OEMOF_SOURCE,
    OEMOF_TRANSFORMER,
    OEMOF_BUSSES,
    OEMOF_ExtractionTurbineCHP,
    EMISSION_FACTOR,
    BETA,
    INVESTMENT_BUS,
)
from multi_vector_simulator.utils.helpers import get_item_if_list, get_length_if_list
from multi_vector_simulator.utils.exceptions import (
    MissingParameterError,
    WrongParameterFormatError,
)


def check_list_parameters_transformers_single_input_single_output(
    dict_asset, n_timesteps
):
    parameters_defined_as_list = []
    for parameter in [DISPATCH_PRICE, EFFICIENCY]:
        len_param = get_length_if_list(dict_asset[parameter][VALUE])
        if len_param != 0 and len_param != n_timesteps:
            parameters_defined_as_list.append(parameter)

    if parameters_defined_as_list:
        parameters_defined_as_list = ", ".join(parameters_defined_as_list)
        missing_dispatch_prices_or_efficiencies = (
            f"You defined multiple values for parameter(s) '{parameters_defined_as_list}'"
            f" although you you have one input and one output for"
            f" the conversion asset named '{dict_asset[LABEL]}', please provide only scalars"
            f" or define more input/output busses"
        )
        logging.error(missing_dispatch_prices_or_efficiencies)
        raise ValueError(missing_dispatch_prices_or_efficiencies)


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


def chp(model, dict_asset, **kwargs):
    r"""
    Defines a chp component specified in `dict_asset`.

    Depending on the 'value' of 'optimizeCap' in `dict_asset` the chp
    is defined with a fixed capacity or a capacity to be optimized.
    The chp has single input and multiple output busses.

    Parameters
    ----------
    model : oemof.solph.network.EnergySystem object
        See the oemof documentation for more information.
    dict_asset : dict
        Contains information about the chp like (not exhaustive):
        efficiency, installed capacity ('installedCap'), information on the
        busses the chp is connected to ('inflow_direction',
        'outflow_direction'), beta coefficient.

    Other Parameters
    ----------------
    busses : dict
    sinks : dict, optional
    sources : dict, optional
    transformers : dict
    storages : dict, optional
    extractionTurbineCHP: dict, optional

    Notes
    -----
    The transformer has either multiple input or multiple output busses.

    The following functions are used for defining the chp:
    * :py:func:`~.chp_fix`
    * :py:func:`~.chp_optimize` for investment optimization

    Tested with:
    - test_chp_fix_cap()
    - test_chp_optimize_cap()
    - test_chp_missing_beta()
    - test_chp_wrong_beta_formatting()
    - test_chp_wrong_efficiency_formatting()
    - test_chp_wrong_outflow_bus_energy_vector()

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with chp object.

    """
    if BETA in dict_asset:
        beta = dict_asset[BETA]
        if isinstance(beta, dict) is False:
            raise WrongParameterFormatError(
                f"For the conversion asset named '{dict_asset[LABEL]}' of type {OEMOF_ExtractionTurbineCHP}, "
                f"the {BETA} parameter should have the following format {{ '{VALUE}': ..., '{UNIT}': ... }}"
            )
        else:
            beta = beta[VALUE]
        if 0 <= beta <= 1:
            pass
        else:
            raise ValueError("beta should be a number between 0 and 1.")
    else:
        raise MissingParameterError("No beta for extraction turbine chp specified.")

    if isinstance(dict_asset[EFFICIENCY][VALUE], list) is False:
        missing_efficiencies = (
            f"For the conversion asset named '{dict_asset[LABEL]}' of type {OEMOF_ExtractionTurbineCHP} "
            f"you must provide exactly 2 values for the parameter '{EFFICIENCY}'."
        )
        logging.error(missing_efficiencies)
        raise WrongParameterFormatError(missing_efficiencies)

    busses_energy_vectors = [
        kwargs[OEMOF_BUSSES][b].energy_vector for b in dict_asset[OUTFLOW_DIRECTION]
    ]
    if (
        "Heat" not in busses_energy_vectors
        or "Electricity" not in busses_energy_vectors
    ):
        mapping_busses = [
            f"'{v}' (from '{k}')"
            for k, v in zip(dict_asset[OUTFLOW_DIRECTION], busses_energy_vectors)
        ]
        wrong_output_energy_vectors = (
            f"For the conversion asset named '{dict_asset[LABEL]}' of type {OEMOF_ExtractionTurbineCHP} "
            f"you must provide 1 output bus for energy vector 'Heat' and one for 'Electricity'. You provided "
            f"{' and '.join(mapping_busses)}"
        )
        logging.error(wrong_output_energy_vectors)
        raise WrongParameterFormatError(wrong_output_energy_vectors)

    check_optimize_cap(
        model, dict_asset, func_constant=chp_fix, func_optimize=chp_optimize, **kwargs
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

    TODOS
    ^^^^^
    * We should actually not allow multiple output busses, probably - because a pv would then
    feed in twice as much as solar_gen_specific for example, see issue #121

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

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the component object.

    TODOS
    ^^^^^
    Might be possible to drop non invest optimization in favour of invest optimization if max_capactiy
    attributes ie. are set to 0 for fix (but less beautiful, and in case of generator even blocks nonconvex opt.).

    Notes
    -----
    Tested with:
    - test_check_optimize_cap_raise_error()

    """
    if dict_asset[OPTIMIZE_CAP][VALUE] is False:
        func_constant(model, dict_asset, **kwargs)
        if dict_asset[OEMOF_ASSET_TYPE] != OEMOF_SOURCE:
            logging.debug(
                "Added: %s %s (fixed capacity)",
                dict_asset[OEMOF_ASSET_TYPE].capitalize(),
                dict_asset[LABEL],
            )

    elif dict_asset[OPTIMIZE_CAP][VALUE] is True:
        func_optimize(model, dict_asset, **kwargs)
        if dict_asset[OEMOF_ASSET_TYPE] != OEMOF_SOURCE:
            logging.debug(
                "Added: %s %s (capacity to be optimized)",
                dict_asset[OEMOF_ASSET_TYPE].capitalize(),
                dict_asset[LABEL],
            )
    else:
        raise ValueError(
            f"Input error! '{OPTIMIZE_CAP}' of asset {dict_asset[LABEL]}\n should be True/False but is {dict_asset[OPTIMIZE_CAP][VALUE]}."
        )


class CustomBus(solph.Bus):
    def __init__(self, *args, **kwargs):
        ev = kwargs.pop("energy_vector", None)  # change to ENERGY_VECTOR
        super(CustomBus, self).__init__(*args, **kwargs)
        self.energy_vector = ev


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
    energy_vector = kwargs.get("energy_vector", None)  # change to ENERGY_VECTOR
    bus = CustomBus(label=name, energy_vector=energy_vector)
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

    missing_dispatch_prices_or_efficiencies = None

    # check if the transformer has multiple input or multiple output busses
    if isinstance(dict_asset[INFLOW_DIRECTION], list) or isinstance(
        dict_asset[OUTFLOW_DIRECTION], list
    ):
        if isinstance(dict_asset[INFLOW_DIRECTION], list) and isinstance(
            dict_asset[OUTFLOW_DIRECTION], str
        ):
            # multiple inputs and single output
            inputs = {}

            num_inputs = len(dict_asset[INFLOW_DIRECTION])
            inputs_names = ", ".join([f"'{n}'" for n in dict_asset[INFLOW_DIRECTION]])
            if get_length_if_list(dict_asset[EFFICIENCY][VALUE]) != num_inputs:
                missing_dispatch_prices_or_efficiencies = (
                    f"You defined multiple values for parameter '{INFLOW_DIRECTION}' "
                    f"({inputs_names}) of the conversion asset named '{dict_asset[LABEL]}'. "
                    f"You must also provide exactly {num_inputs} values for the parameter '{EFFICIENCY}'."
                )
                logging.error(missing_dispatch_prices_or_efficiencies)
                raise ValueError(missing_dispatch_prices_or_efficiencies)

            if get_length_if_list(dict_asset[DISPATCH_PRICE][VALUE]) == 0:
                # only one dispatch price provided --> it will be ignored
                warning_msg = (
                    f"You defined multiple values for parameter '{INFLOW_DIRECTION}' "
                    f"({inputs_names}) of the conversion asset named '{dict_asset[LABEL]}'. "
                    f"You can also provide exactly {num_inputs} values for the parameter '{DISPATCH_PRICE}'."
                    f"You did only provide one value, so we will ignore it"
                )
                logging.warning(warning_msg)
                for i, bus in enumerate(dict_asset[INFLOW_DIRECTION]):
                    inputs[kwargs[OEMOF_BUSSES][bus]] = solph.Flow()
            else:
                for i, bus in enumerate(dict_asset[INFLOW_DIRECTION]):
                    inputs[kwargs[OEMOF_BUSSES][bus]] = solph.Flow(
                        variable_costs=get_item_if_list(
                            dict_asset[DISPATCH_PRICE][VALUE], i
                        )
                    )

            outputs = {
                kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
                    nominal_value=dict_asset[INSTALLED_CAP][VALUE]
                )
            }
            efficiencies = {}
            for i, efficiency in enumerate(dict_asset[EFFICIENCY][VALUE]):
                efficiencies[
                    kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION][i]]
                ] = efficiency

        elif isinstance(dict_asset[INFLOW_DIRECTION], str) and isinstance(
            dict_asset[OUTFLOW_DIRECTION], list
        ):
            # single input and multiple outputs
            num_outputs = len(dict_asset[OUTFLOW_DIRECTION])
            if get_length_if_list(dict_asset[EFFICIENCY][VALUE]) != num_outputs:
                outputs_names = ", ".join(
                    [f"'{n}'" for n in dict_asset[OUTFLOW_DIRECTION]]
                )
                missing_dispatch_prices_or_efficiencies = (
                    f"You defined multiple values for parameter '{OUTFLOW_DIRECTION}' "
                    f"({outputs_names}) of the conversion asset named '{dict_asset[LABEL]}'. "
                    f"You must also provide exactly {num_outputs} values for the parameters "
                    f"'{EFFICIENCY}' and you can do so for the parameter '{DISPATCH_PRICE}'."
                )
                logging.error(missing_dispatch_prices_or_efficiencies)
                raise ValueError(missing_dispatch_prices_or_efficiencies)

            inputs = {kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow()}
            outputs = {}
            for i, bus in enumerate(dict_asset[OUTFLOW_DIRECTION]):
                outputs[kwargs[OEMOF_BUSSES][bus]] = solph.Flow(
                    nominal_value=get_item_if_list(dict_asset[INSTALLED_CAP][VALUE], i),
                    variable_costs=get_item_if_list(
                        dict_asset[DISPATCH_PRICE][VALUE], i
                    ),
                )

            efficiencies = {}
            for i, efficiency in enumerate(dict_asset[EFFICIENCY][VALUE]):
                efficiencies[
                    kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION][i]]
                ] = efficiency

        else:
            # multiple inputs and multiple outputs
            inputs_names = ", ".join([f"'{n}'" for n in dict_asset[INFLOW_DIRECTION]])
            outputs_names = ", ".join([f"'{n}'" for n in dict_asset[OUTFLOW_DIRECTION]])
            missing_dispatch_prices_or_efficiencies = (
                f"You defined multiple values for parameter '{INFLOW_DIRECTION}'"
                f" ({inputs_names}) as well as for parameter '{OUTFLOW_DIRECTION}' ({outputs_names})"
                f" of the conversion asset named '{dict_asset[LABEL]}', this is not supported"
                f" at the moment."
            )
            logging.error(missing_dispatch_prices_or_efficiencies)
            raise ValueError(missing_dispatch_prices_or_efficiencies)
    else:
        # single input and single output

        check_list_parameters_transformers_single_input_single_output(
            dict_asset, model.timeindex.size
        )

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

    if missing_dispatch_prices_or_efficiencies is None:
        t = solph.components.Transformer(
            label=dict_asset[LABEL],
            inputs=inputs,
            outputs=outputs,
            conversion_factors=efficiencies,
        )

        model.add(t)
        kwargs[OEMOF_TRANSFORMER].update({dict_asset[LABEL]: t})


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
    missing_dispatch_prices_or_efficiencies = None

    investment_bus = dict_asset.get(INVESTMENT_BUS)
    investment = solph.Investment(
        ep_costs=dict_asset[SIMULATION_ANNUITY][VALUE],
        maximum=dict_asset[MAXIMUM_ADD_CAP][VALUE],
        existing=dict_asset[INSTALLED_CAP][VALUE],
    )

    # check if the transformer has multiple input or multiple output busses
    # the investment object is always in the output bus
    if isinstance(dict_asset[INFLOW_DIRECTION], list) or isinstance(
        dict_asset[OUTFLOW_DIRECTION], list
    ):
        if isinstance(dict_asset[INFLOW_DIRECTION], list) and isinstance(
            dict_asset[OUTFLOW_DIRECTION], str
        ):
            # multiple inputs and single output
            num_inputs = len(dict_asset[INFLOW_DIRECTION])
            if get_length_if_list(dict_asset[EFFICIENCY][VALUE]) != num_inputs:
                inputs_names = ", ".join(
                    [f"'{n}'" for n in dict_asset[INFLOW_DIRECTION]]
                )
                missing_dispatch_prices_or_efficiencies = (
                    f"You defined multiple values for parameter '{INFLOW_DIRECTION}' "
                    f"({inputs_names}) of the conversion asset named '{dict_asset[LABEL]}'. "
                    f"You must also provide exactly {num_inputs} values for the parameter "
                    f"'{EFFICIENCY}' and you can do so for the parameter '{DISPATCH_PRICE}'."
                )
                logging.error(missing_dispatch_prices_or_efficiencies)
                raise ValueError(missing_dispatch_prices_or_efficiencies)

            if investment_bus is None:
                investment_bus = dict_asset[OUTFLOW_DIRECTION]

            inputs = {}
            for i, bus in enumerate(dict_asset[INFLOW_DIRECTION]):
                inputs[kwargs[OEMOF_BUSSES][bus]] = solph.Flow(
                    variable_costs=get_item_if_list(
                        dict_asset[DISPATCH_PRICE][VALUE], i
                    ),
                    investment=investment if bus == investment_bus else None,
                )

            bus = dict_asset[OUTFLOW_DIRECTION]
            outputs = {
                kwargs[OEMOF_BUSSES][bus]: solph.Flow(
                    investment=investment if bus == investment_bus else None
                )
            }

            efficiencies = {}
            for i, efficiency in enumerate(dict_asset[EFFICIENCY][VALUE]):
                efficiencies[
                    kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION][i]]
                ] = efficiency

        elif isinstance(dict_asset[INFLOW_DIRECTION], str) and isinstance(
            dict_asset[OUTFLOW_DIRECTION], list
        ):
            # single input and multiple outputs
            num_outputs = len(dict_asset[OUTFLOW_DIRECTION])
            if get_length_if_list(dict_asset[EFFICIENCY][VALUE]) != num_outputs:
                outputs_names = ", ".join(
                    [f"'{n}'" for n in dict_asset[OUTFLOW_DIRECTION]]
                )
                missing_dispatch_prices_or_efficiencies = (
                    f"You defined multiple values for parameter '{OUTFLOW_DIRECTION}' "
                    f"({outputs_names}) of the conversion asset named '{dict_asset[LABEL]}'. "
                    f"You must also provide exactly {num_outputs} values for the parameter "
                    f"'{EFFICIENCY}' and you can do so for the parameter '{DISPATCH_PRICE}'."
                )
                logging.error(missing_dispatch_prices_or_efficiencies)
                raise ValueError(missing_dispatch_prices_or_efficiencies)

            if investment_bus is None:
                investment_bus = dict_asset[INFLOW_DIRECTION]
            bus = dict_asset[INFLOW_DIRECTION]
            inputs = {
                kwargs[OEMOF_BUSSES][bus]: solph.Flow(
                    investment=investment if bus == investment_bus else None
                )
            }
            outputs = {}
            efficiencies = {}

            for i, (bus, efficiency) in enumerate(
                zip(dict_asset[OUTFLOW_DIRECTION], dict_asset[EFFICIENCY][VALUE])
            ):

                outputs[kwargs[OEMOF_BUSSES][bus]] = solph.Flow(
                    investment=investment if bus == investment_bus else None
                )
                efficiencies[kwargs[OEMOF_BUSSES][bus]] = efficiency
        else:
            # multiple inputs and multiple outputs
            inputs_names = ", ".join([f"'{n}'" for n in dict_asset[INFLOW_DIRECTION]])
            outputs_names = ", ".join([f"'{n}'" for n in dict_asset[OUTFLOW_DIRECTION]])
            missing_dispatch_prices_or_efficiencies = (
                f"You defined multiple values for parameter '{INFLOW_DIRECTION}'"
                f" ({inputs_names}) as well as for parameter '{OUTFLOW_DIRECTION}' ({outputs_names})"
                f" of the conversion asset named '{dict_asset[LABEL]}', this is not supported"
                f" at the moment."
            )
            logging.error(missing_dispatch_prices_or_efficiencies)
            raise ValueError(missing_dispatch_prices_or_efficiencies)
    else:
        check_list_parameters_transformers_single_input_single_output(
            dict_asset, model.timeindex.size
        )

        # single input and single output

        if investment_bus is None:
            investment_bus = dict_asset[OUTFLOW_DIRECTION]

        bus = dict_asset[INFLOW_DIRECTION]
        inputs = {
            kwargs[OEMOF_BUSSES][bus]: solph.Flow(
                investment=investment if bus == investment_bus else None
            )
        }

        bus = dict_asset[OUTFLOW_DIRECTION]
        if AVAILABILITY_DISPATCH in dict_asset.keys():
            # This key is only present in DSO peak demand pricing transformers.
            outputs = {
                kwargs[OEMOF_BUSSES][bus]: solph.Flow(
                    investment=investment if bus == investment_bus else None,
                    variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
                    max=dict_asset[AVAILABILITY_DISPATCH].values,
                )
            }
        else:
            outputs = {
                kwargs[OEMOF_BUSSES][bus]: solph.Flow(
                    investment=investment if bus == investment_bus else None,
                    variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
                )
            }

        efficiencies = {
            kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: dict_asset[EFFICIENCY][
                VALUE
            ]
        }

    if missing_dispatch_prices_or_efficiencies is None:
        t = solph.components.Transformer(
            label=dict_asset[LABEL],
            inputs=inputs,
            outputs=outputs,
            conversion_factors=efficiencies,
        )

        model.add(t)
        kwargs[OEMOF_TRANSFORMER].update({dict_asset[LABEL]: t})


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
        nominal_storage_capacity=dict_asset[STORAGE_CAPACITY][INSTALLED_CAP][
            VALUE
        ],  # THERMAL --> yes
        inputs={
            kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow(
                nominal_value=dict_asset[INPUT_POWER][INSTALLED_CAP][
                    VALUE
                ],  # limited through installed capacity, NOT c-rate
                # might be too much
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
        - dict_asset[STORAGE_CAPACITY][EFFICIENCY][
            VALUE
        ],  # from timestep to timestep #THERMAL
        fixed_losses_absolute=dict_asset[STORAGE_CAPACITY][THERM_LOSSES_ABS][
            VALUE
        ],  # THERMAL
        fixed_losses_relative=dict_asset[STORAGE_CAPACITY][THERM_LOSSES_REL][
            VALUE
        ],  # THERMAL
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
            maximum=dict_asset[STORAGE_CAPACITY][MAXIMUM_ADD_CAP][VALUE],
            existing=dict_asset[STORAGE_CAPACITY][INSTALLED_CAP][VALUE],
        ),
        inputs={
            kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow(
                investment=solph.Investment(
                    ep_costs=dict_asset[INPUT_POWER][SIMULATION_ANNUITY][VALUE],
                    maximum=dict_asset[INPUT_POWER][MAXIMUM_ADD_CAP][VALUE],
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
                    maximum=dict_asset[OUTPUT_POWER][MAXIMUM_ADD_CAP][VALUE],
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
            fix=dict_asset[TIMESERIES],
            nominal_value=dict_asset[INSTALLED_CAP][VALUE],
            variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
            custom_attributes=dict(emission_factor=dict_asset[EMISSION_FACTOR][VALUE]),
        )
    }

    source_non_dispatchable = solph.components.Source(
        label=dict_asset[LABEL], outputs=outputs
    )

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
    if MAXIMUM_ADD_CAP_NORMALIZED in dict_asset:
        maximum = dict_asset[MAXIMUM_ADD_CAP_NORMALIZED][VALUE]
    else:
        maximum = dict_asset[MAXIMUM_ADD_CAP][VALUE]
    if INSTALLED_CAP_NORMALIZED in dict_asset:
        existing = dict_asset[INSTALLED_CAP_NORMALIZED][VALUE]
    else:
        existing = dict_asset[INSTALLED_CAP][VALUE]
    outputs = {
        kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION]]: solph.Flow(
            fix=dict_asset[TIMESERIES_NORMALIZED],
            investment=solph.Investment(
                ep_costs=dict_asset[SIMULATION_ANNUITY][VALUE]
                / dict_asset[TIMESERIES_PEAK][VALUE],
                maximum=maximum,
                existing=existing,
            ),
            # variable_costs are devided by time series peak as normalized time series are used as actual_value
            variable_costs=dict_asset[DISPATCH_PRICE][VALUE]
            / dict_asset[TIMESERIES_PEAK][VALUE],
            # add emission_factor for emission contraint
            custom_attributes=dict(emission_factor=dict_asset[EMISSION_FACTOR][VALUE]),
        )
    }

    source_non_dispatchable = solph.components.Source(
        label=dict_asset[LABEL], outputs=outputs
    )

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
                max=dict_asset[TIMESERIES_NORMALIZED],
                investment=solph.Investment(
                    ep_costs=dict_asset[SIMULATION_ANNUITY][VALUE]
                    / dict_asset[TIMESERIES_PEAK][VALUE],
                    maximum=dict_asset[MAXIMUM_ADD_CAP][VALUE],
                    existing=dict_asset[INSTALLED_CAP][VALUE],
                ),
                # variable_costs are devided by time series peak as normalized time series are used as actual_value
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE]
                / dict_asset[TIMESERIES_PEAK][VALUE],
                # add emission_factor for emission contraint
                custom_attributes=dict(
                    emission_factor=dict_asset[EMISSION_FACTOR][VALUE]
                ),
            )
        }
        source_dispatchable = solph.components.Source(
            label=dict_asset[LABEL], outputs=outputs,
        )
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
                investment=solph.Investment(
                    ep_costs=dict_asset[SIMULATION_ANNUITY][VALUE],
                    existing=dict_asset[INSTALLED_CAP][VALUE],
                    maximum=dict_asset[MAXIMUM_ADD_CAP][VALUE],
                ),
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
                # add emission_factor for emission contraint
                custom_attributes=dict(
                    emission_factor=dict_asset[EMISSION_FACTOR][VALUE],
                ),
            )
        }
        print(dict_asset[LABEL])
        source_dispatchable = solph.components.Source(
            label=dict_asset[LABEL], outputs=outputs
        )
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
                max=dict_asset[TIMESERIES_NORMALIZED],
                nominal_value=dict_asset[INSTALLED_CAP][VALUE],
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
                # add emission_factor for emission contraint
                custom_attributes=dict(
                    emission_factor=dict_asset[EMISSION_FACTOR][VALUE]
                ),
            )
        }
        source_dispatchable = solph.components.Source(
            label=dict_asset[LABEL], outputs=outputs,
        )
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
                nominal_value=dict_asset[INSTALLED_CAP][VALUE],
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
            )
        }
        source_dispatchable = solph.components.Source(
            label=dict_asset[LABEL], outputs=outputs,
        )
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
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE][index],
                investment=solph.Investment(),
            )
            index += 1
    else:
        inputs = {
            kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow(
                variable_costs=dict_asset[DISPATCH_PRICE][VALUE],
                investment=solph.Investment(),
            )
        }

    # create and add excess electricity sink to micro_grid_system - variable
    sink_dispatchable = solph.components.Sink(label=dict_asset[LABEL], inputs=inputs,)
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
    sink_demand = solph.components.Sink(label=dict_asset[LABEL], inputs=inputs,)
    model.add(sink_demand)
    kwargs[OEMOF_SINK].update({dict_asset[LABEL]: sink_demand})
    logging.debug(
        f"Added: Non-dispatchable sink {dict_asset[LABEL]} to bus {dict_asset[INFLOW_DIRECTION]}"
    )


def chp_fix(model, dict_asset, **kwargs):
    r"""
    Extraction turbine chp from Oemof solph. Extraction turbine must have one input and two outputs
    Notes
    -----
    Tested with:
    - test_to_be_written()

    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the extraction turbine component.

    """

    inputs = {
        kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow(
            nominal_value=dict_asset[INSTALLED_CAP][VALUE]
        )
    }

    busses_energy_vectors = [
        kwargs[OEMOF_BUSSES][b].energy_vector for b in dict_asset[OUTFLOW_DIRECTION]
    ]
    idx_el = busses_energy_vectors.index("Electricity")
    idx_th = busses_energy_vectors.index("Heat")
    el_bus = kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION][idx_el]]
    th_bus = kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION][idx_th]]

    outputs = {
        el_bus: solph.Flow(),
        th_bus: solph.Flow(),
    }  # if kW for heat and kW for elect then insert it under nominal_value

    beta = dict_asset[BETA][VALUE]

    efficiency_el_wo_heat_extraction = dict_asset[EFFICIENCY][VALUE][idx_th]
    efficiency_th_max_heat_extraction = dict_asset[EFFICIENCY][VALUE][idx_el]
    efficiency_el_max_heat_extraction = (
        efficiency_el_wo_heat_extraction - beta * efficiency_th_max_heat_extraction
    )
    efficiency_full_condensation = {el_bus: efficiency_el_wo_heat_extraction}

    efficiencies = {
        el_bus: efficiency_el_max_heat_extraction,
        th_bus: efficiency_th_max_heat_extraction,
    }

    ext_turb_chp = solph.components.ExtractionTurbineCHP(
        label=dict_asset[LABEL],
        inputs=inputs,
        outputs=outputs,
        conversion_factors=efficiencies,
        conversion_factor_full_condensation=efficiency_full_condensation,
    )

    model.add(ext_turb_chp)
    kwargs[OEMOF_ExtractionTurbineCHP].update({dict_asset[LABEL]: ext_turb_chp})


def chp_optimize(model, dict_asset, **kwargs):
    r"""
    Extraction turbine chp from Oemof solph. Extraction turbine must have one input and two outputs
    Notes
    -----
    Tested with:
    - test_to_be_written()
    
    Returns
    -------
    Indirectly updated `model` and dict of asset in `kwargs` with the extraction turbine component.

    """

    inputs = {kwargs[OEMOF_BUSSES][dict_asset[INFLOW_DIRECTION]]: solph.Flow()}

    busses_energy_vectors = [
        kwargs[OEMOF_BUSSES][b].energy_vector for b in dict_asset[OUTFLOW_DIRECTION]
    ]

    idx_el = busses_energy_vectors.index("Electricity")
    idx_th = busses_energy_vectors.index("Heat")
    el_bus = kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION][idx_el]]
    th_bus = kwargs[OEMOF_BUSSES][dict_asset[OUTFLOW_DIRECTION][idx_th]]

    outputs = {
        el_bus: solph.Flow(
            investment=solph.Investment(
                ep_costs=dict_asset[SIMULATION_ANNUITY][VALUE],
                maximum=dict_asset[MAXIMUM_ADD_CAP][VALUE],
                existing=dict_asset[INSTALLED_CAP][VALUE],
            )
        ),
        th_bus: solph.Flow(),
    }

    beta = dict_asset[BETA][VALUE]

    efficiency_el_wo_heat_extraction = dict_asset[EFFICIENCY][VALUE][idx_el]
    efficiency_th_max_heat_extraction = dict_asset[EFFICIENCY][VALUE][idx_th]
    efficiency_el_max_heat_extraction = (
        efficiency_el_wo_heat_extraction - beta * efficiency_th_max_heat_extraction
    )
    efficiency_full_condensation = {el_bus: efficiency_el_wo_heat_extraction}

    efficiencies = {
        el_bus: efficiency_el_max_heat_extraction,
        th_bus: efficiency_th_max_heat_extraction,
    }

    ext_turb_chp = solph.components.ExtractionTurbineCHP(
        label=dict_asset[LABEL],
        inputs=inputs,
        outputs=outputs,
        conversion_factors=efficiencies,
        conversion_factor_full_condensation=efficiency_full_condensation,
    )

    model.add(ext_turb_chp)
    kwargs[OEMOF_ExtractionTurbineCHP].update({dict_asset[LABEL]: ext_turb_chp})
