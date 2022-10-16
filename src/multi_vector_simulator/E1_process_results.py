"""
Module E1 process results
=========================

Module E1 processes the oemof results.
- receive time series per bus for all assets
- write time series to dictionary
- get optimal capacity of optimized assets
- add the evaluation of time series

"""
import logging
import copy
import pandas as pd

from multi_vector_simulator.utils.constants import TYPE_NONE, TOTAL_FLOW
from multi_vector_simulator.utils.constants_json_strings import (
    ECONOMIC_DATA,
    FLOW,
    INSTALLED_CAP,
    INPUT_POWER,
    OUTPUT_POWER,
    STORAGE_CAPACITY,
    TIME_INDEX,
    INFLOW_DIRECTION,
    OUTFLOW_DIRECTION,
    KPI_SCALARS_DICT,
    OPTIMIZED_FLOWS,
    UNIT,
    CURR,
    UNIT_YEAR,
    ENERGY_CONSUMPTION,
    LABEL,
    VALUE,
    OPTIMIZE_CAP,
    SIMULATION_SETTINGS,
    EVALUATED_PERIOD,
    TIMESERIES_PEAK,
    TIMESERIES_TOTAL,
    TIMESERIES_AVERAGE,
    DSO_FEEDIN,
    EXCESS_SINK,
    ENERGY_CONVERSION,
    ENERGY_PRODUCTION,
    ENERGY_STORAGE,
    OEMOF_ASSET_TYPE,
    ENERGY_VECTOR,
    KPI,
    KPI_COST_MATRIX,
    KPI_SCALAR_MATRIX,
    TOTAL_FLOW,
    PEAK_FLOW,
    AVERAGE_FLOW,
    OPTIMIZED_ADD_CAP,
    ANNUAL_TOTAL_FLOW,
    COST_OPERATIONAL_TOTAL,
    COST_INVESTMENT,
    COST_DISPATCH,
    COST_OM,
    COST_TOTAL,
    COST_UPFRONT,
    ANNUITY_TOTAL,
    ANNUITY_OM,
    LCOE_ASSET,
    EMISSION_FACTOR,
    TOTAL_EMISSIONS,
    TIMESERIES_SOC,
    KPI_UNCOUPLED_DICT,
    FIX_COST,
    LIFETIME_PRICE_DISPATCH,
    AVERAGE_SOC,
)

# Oemof.solph variables
OEMOF_FLOW = "flow"
OEMOF_SEQUENCES = "sequences"
OEMOF_INVEST = "invest"
OEMOF_SCALARS = "scalars"
OEMOF_STORAGE_CONTENT = "storage_content"

# Determines which assets are defined by...
# a influx from a bus
ASSET_GROUPS_DEFINED_BY_INFLUX = [ENERGY_CONSUMPTION]
# b outflux into a bus
ASSET_GROUPS_DEFINED_BY_OUTFLUX = [ENERGY_CONVERSION, ENERGY_PRODUCTION]

# Threshold for precision limit:
THRESHOLD = 10 ** (-6)


def cut_below_micro(value, label):
    r"""
    Function trims results of oemof optimization to positive values and rounds to 0, if within a certain precision threshold (of -10^-6)

    Oemof termination is dependent on the simulation settings of oemof solph. Thus, it can terminate the optimization if the results are with certain bounds, which can sometimes lead to negative decision variables (capacities, flows). Negative values do not make sense in this context. If the values are between -10^-6 and 0, we assume that they can be rounded to 0, as they result from the precision settings of the solver. In that case the value is overwritten for the futher post-processing. This should also avoid SOC timeseries with doubtful values outside of [0,1]. If any value is a higher negative value then the threshold, its value is not changed but a warning raised.
    Similarily, if a positive devision variable is detected that has a value lower then the theshold, it is assumed that this only happends because of the solver settings, and the values below the theshold are rounded to 0.

    Parameters
    ----------
    value: float or pd.Series
        Decision variable determined by oemof

    label: str
        String to be mentioned in the debug messages

    Returns
    -------

    value: float of pd.Series
        Decision variable with rounded values in case that slight negative values or positive values were observed.

    Notes
    -----

    Tested with:
    - E1.test_cut_below_micro_scalar_value_below_0_larger_threshold
    - E1.test_cut_below_micro_scalar_value_below_0_smaller_threshold
    - E1.test_cut_below_micro_scalar_value_0
    - E1.test_cut_below_micro_scalar_value_larger_0
    - E1.test_cut_below_micro_scalar_value_larger_0_smaller_threshold
    - E1.test_cut_below_micro_pd_Series_below_0_larger_threshold
    - E1.test_cut_below_micro_pd_Series_below_0_smaller_threshold
    - E1.test_cut_below_micro_pd_Series_0
    - E1.test_cut_below_micro_pd_Series_larger_0
    - E1.test_cut_below_micro_pd_Series_larger_0_smaller_threshold
    """
    text_block_start = f"The value of {label} is below 0"
    text_block_set_0 = f"Negative value (s) are smaller than {-THRESHOLD}. This is likely a result of the termination/precision settings of the cbc solver. As the difference is marginal, the value will be set to 0. "
    text_block_oemof = "This is so far below 0, that the value is not changed. All oemof decision variables should be positive so this needs to be investigated. "

    logging.debug(
        f"Check if the dispatch of asset {label} as per the oemof results is within the defined margin of precision ({THRESHOLD})"
    )

    # flows
    if isinstance(value, pd.Series):
        # Identifies any negative values. Decision variables should not have a negative value
        if (value < 0).any():
            log_msg = text_block_start
            # Counts the incidents, in which the value is below 0.
            if isinstance(value, pd.Series):
                instances = sum(value < 0)
                log_msg += f" in {instances} instances. "
            # Checks that all values are at least within the threshold for negative values.
            if (value > -THRESHOLD).all():
                log_msg += text_block_set_0
                logging.debug(log_msg)
                value = value.clip(lower=0)
            # If any value has a large negative value (lower then threshold), no values are changed.
            else:
                test = value.clip(upper=-THRESHOLD).abs()
                log_msg += f"At least one value exceeds the scale of {-THRESHOLD}. The highest negative value is -{max(test)}. "
                log_msg += text_block_oemof
                logging.warning(log_msg)

        # Determine if there are any positive values that are between 0 and the threshold:
        # Clip to interval
        positive_threshold = value.clip(lower=0, upper=THRESHOLD)
        # Determine instances in which bounds are met: 1=either 0 or larger threshold, 0=smaller threshold
        positive_threshold = (positive_threshold == 0) + (
            positive_threshold == THRESHOLD
        )
        # Instances in which values are in determined interval:
        instances = len(value) - sum(positive_threshold)
        if instances > 0:
            logging.debug(
                f"There are {instances} instances in which there are positive values smaller then the threshold."
            )
            # Multiply with positive_threshold (1=either 0 or larger threshold, 0=smaller threshold)
            value = value * positive_threshold

    # capacities
    else:
        # Value is lower 0, which should not be possible for decision variables
        if value < 0:
            log_msg = text_block_start
            # Value between [threshold, 0] = [-10**(-6)], ie. is so small that it can be neglected.
            if value > -THRESHOLD:
                log_msg += text_block_set_0
                logging.debug(log_msg)
                value = 0
            # Value is below 0 but already large enough that it should not be neglected.
            else:
                log_msg += f"The value exceeds the scale of {-THRESHOLD}, with {value}."
                log_msg += text_block_oemof
                logging.warning(log_msg)
        # Value is above 0 but below threshold, should be rounded
        elif value < THRESHOLD:
            logging.debug(
                f"The positive value {value} is below the {THRESHOLD}, and rounded to 0."
            )
            value = 0

    return value


def get_timeseries_per_bus(dict_values, bus_data):
    r"""
    Reads simulation results of all busses and stores time series.

    Parameters
    ----------
    dict_values : dict
        Contains all input data of the simulation.
    bus_data : dict Contains information about all busses in a nested dict.

        1st level keys: bus names;
        2nd level keys:

            'scalars': (pd.Series) (does not exist in all dicts)
            'sequences': (pd.DataFrame) - contains flows between components and busses

    Notes
    -----
    Tested with:
    - test_get_timeseries_per_bus_two_timeseries_for_directly_connected_storage()

    #Todo: This is a duplicate of the `E1.get_flow()` assertions, and thus `E1.cut_below_micro` is applied twice for each flow. This should rather be merged into the other functions.

    Returns
    -------
    Indirectly updated `dict_values` with 'optimizedFlows' - one data frame for each bus.

    """
    logging.debug(
        "Time series for plots and 'timeseries.xlsx' are added to `dict_values[OPTIMIZED_FLOWS]` in `E1.get_timeseries_per_bus`; check there in case of problems."
    )
    bus_data_timeseries = {}
    for bus in bus_data.keys():
        bus_data_timeseries.update(
            {bus: pd.DataFrame(index=dict_values[SIMULATION_SETTINGS][TIME_INDEX])}
        )

        # obtain flows that flow into the bus
        to_bus = {
            key[0][0]: key
            for key in bus_data[bus][OEMOF_SEQUENCES].keys()
            if key[0][1] == bus and key[1] == OEMOF_FLOW
        }
        for asset in to_bus:
            flow = bus_data[bus][OEMOF_SEQUENCES][to_bus[asset]]
            flow = cut_below_micro(flow, bus + "/" + asset)
            bus_data_timeseries[bus][asset] = flow
        # obtain flows that flow out of the bus
        from_bus = {
            key[0][1]: key
            for key in bus_data[bus][OEMOF_SEQUENCES].keys()
            if key[0][0] == bus and key[1] == OEMOF_FLOW
        }
        for asset in from_bus:
            try:
                # if `asset` already exists add input/output power to column name
                # (occurs for storages that are directly added to a bus)
                bus_data_timeseries[bus][asset]
                # asset is already in bus_data_timeseries[bus]. Therefore a renaming is necessary:
                bus_data_timeseries[bus].rename(
                    columns={asset: " ".join([asset, OUTPUT_POWER])}, inplace=True
                )
                # Now the "from_bus" ie. the charging/input power of the storage asset is added to the data set:
                bus_data_timeseries[bus][" ".join([asset, INPUT_POWER])] = -bus_data[
                    bus
                ][OEMOF_SEQUENCES][from_bus[asset]]
            except KeyError:
                # The asset was not previously added to the `OPTIMIZED_FLOWS`, ie. is not a storage asset
                bus_data_timeseries[bus][asset] = -bus_data[bus][OEMOF_SEQUENCES][
                    from_bus[asset]
                ]

    dict_values.update({OPTIMIZED_FLOWS: bus_data_timeseries})


def get_storage_results(settings, storage_bus, dict_asset):
    r"""
    Reads storage results of simulation and stores them in `dict_asset`.

    Parameters
    ----------
    settings : dict
        Contains simulation settings from `simulation_settings.csv` with
        additional information like the amount of time steps simulated in the
        optimization ('periods').
    storage_bus : dict
        Contains information about the storage bus. Information about the scalars
        like investment or initial capacity in key 'scalars' (pd.Series) and the
        flows between the component and the busses in key 'sequences' (pd.DataFrame).
    dict_asset : dict
        Contains information about the storage like capacity, charging power, etc.

    Returns
    -------
    Indirectly updates `dict_asset` with simulation results concerning the
    storage.

    """
    power_charge = storage_bus[OEMOF_SEQUENCES][
        ((dict_asset[INFLOW_DIRECTION], dict_asset[LABEL]), OEMOF_FLOW)
    ]
    power_charge = cut_below_micro(power_charge, dict_asset[LABEL] + " charge flow")
    add_info_flows(
        evaluated_period=settings[EVALUATED_PERIOD][VALUE],
        dict_asset=dict_asset[INPUT_POWER],
        flow=power_charge,
    )

    power_discharge = storage_bus[OEMOF_SEQUENCES][
        ((dict_asset[LABEL], dict_asset[OUTFLOW_DIRECTION]), OEMOF_FLOW)
    ]
    power_discharge = cut_below_micro(
        power_discharge, dict_asset[LABEL] + " discharge flow"
    )

    add_info_flows(
        evaluated_period=settings[EVALUATED_PERIOD][VALUE],
        dict_asset=dict_asset[OUTPUT_POWER],
        flow=power_discharge,
    )

    storage_capacity = storage_bus[OEMOF_SEQUENCES][
        ((dict_asset[LABEL], TYPE_NONE), OEMOF_STORAGE_CONTENT)
    ]
    storage_capacity = cut_below_micro(
        storage_capacity, dict_asset[LABEL] + " " + STORAGE_CAPACITY
    )

    add_info_flows(
        evaluated_period=settings[EVALUATED_PERIOD][VALUE],
        dict_asset=dict_asset[STORAGE_CAPACITY],
        flow=storage_capacity,
        type=STORAGE_CAPACITY,
    )

    if OPTIMIZE_CAP in dict_asset:
        if dict_asset[OPTIMIZE_CAP][VALUE] is True:
            power_charge = storage_bus[OEMOF_SCALARS][
                ((dict_asset[INFLOW_DIRECTION], dict_asset[LABEL]), OEMOF_INVEST)
            ]
            dict_asset[INPUT_POWER].update(
                {
                    OPTIMIZED_ADD_CAP: {
                        VALUE: power_charge,
                        UNIT: dict_asset[INPUT_POWER][UNIT],
                    }
                }
            )
            logging.debug(
                "Accessed optimized capacity of asset %s: %s",
                dict_asset[INPUT_POWER][LABEL],
                power_charge,
            )

            power_discharge = storage_bus[OEMOF_SCALARS][
                ((dict_asset[LABEL], dict_asset[OUTFLOW_DIRECTION]), OEMOF_INVEST)
            ]
            dict_asset[OUTPUT_POWER].update(
                {
                    OPTIMIZED_ADD_CAP: {
                        VALUE: power_discharge,
                        UNIT: dict_asset[OUTPUT_POWER][UNIT],
                    }
                }
            )
            logging.debug(
                "Accessed optimized capacity of asset %s: %s",
                dict_asset[OUTPUT_POWER][LABEL],
                power_discharge,
            )

            storage_capacity = storage_bus[OEMOF_SCALARS][
                ((dict_asset[LABEL], TYPE_NONE), OEMOF_INVEST)
            ]
            dict_asset[STORAGE_CAPACITY].update(
                {
                    OPTIMIZED_ADD_CAP: {
                        VALUE: storage_capacity,
                        UNIT: dict_asset[STORAGE_CAPACITY][UNIT],
                    }
                }
            )
            logging.debug(
                "Accessed optimized capacity of asset %s: %s",
                dict_asset[STORAGE_CAPACITY][LABEL],
                storage_capacity,
            )

        else:
            dict_asset[INPUT_POWER].update(
                {
                    OPTIMIZED_ADD_CAP: {
                        VALUE: 0,
                        UNIT: dict_asset[STORAGE_CAPACITY][UNIT],
                    }
                }
            )
            dict_asset[OUTPUT_POWER].update(
                {
                    OPTIMIZED_ADD_CAP: {
                        VALUE: 0,
                        UNIT: dict_asset[STORAGE_CAPACITY][UNIT],
                    }
                }
            )
            dict_asset[STORAGE_CAPACITY].update(
                {
                    OPTIMIZED_ADD_CAP: {
                        VALUE: 0,
                        UNIT: dict_asset[STORAGE_CAPACITY][UNIT],
                    }
                }
            )

    get_state_of_charge_info(dict_asset)


def get_state_of_charge_info(dict_asset):
    r"""
    Adds state of charge timeseries and average value of the timeseries to the storage dict.

    Parameters
    ----------
    dict_asset: dict
        Dict of the asset, specifically including the STORAGE_CAPACITY

    Returns
    -------
    Updated dict_asset

    Notes
    -----

    Tested with:
    - E1.test_get_state_of_charge_info()
    """
    timeseries_soc = dict_asset[STORAGE_CAPACITY][FLOW] / (
        dict_asset[STORAGE_CAPACITY][INSTALLED_CAP][VALUE]
        + dict_asset[STORAGE_CAPACITY][OPTIMIZED_ADD_CAP][VALUE]
    )
    dict_asset.update(
        {
            TIMESERIES_SOC: timeseries_soc,
            AVERAGE_SOC: {VALUE: timeseries_soc.mean(), UNIT: "factor"},
        }
    )


def get_results(settings, bus_data, dict_asset, asset_group):
    r"""
    Reads results of the asset defined in `dict_asset` and stores them in `dict_asset`.

    Parameters
    ----------
    settings : dict
        Contains simulation settings from `simulation_settings.csv` with
        additional information like the amount of time steps simulated in the
        optimization ('periods').

    bus_data : dict
        Contains information about all busses in a nested dict.
        1st level keys: bus names;
        2nd level keys:

            'scalars': (pd.Series) (does not exist in all dicts)
            'sequences': (pd.DataFrame) - contains flows between components and busses

    dict_asset : dict
        Contains information about the asset.

    asset_group: str
       Asset group to which the evaluated asset belongs

    Returns
    -------
    Indirectly updates `dict_asset` with results.

    """
    # Get which parameter/bus needs to be evaluated
    parameter_to_be_evaluated = get_parameter_to_be_evaluated_from_oemof_results(
        asset_group, dict_asset[LABEL]
    )

    # Check if the parameter/bus is defined for dict_asset
    if parameter_to_be_evaluated not in dict_asset:
        logging.warning(
            f"The asset {dict_asset[LCOE_ASSET]} of group {asset_group} should contain parameter {parameter_to_be_evaluated}, but it does not."
        )

    # Determine bus that needs to be evaluated
    bus_name = dict_asset[parameter_to_be_evaluated]

    # Determine flows of the asset, also if flows are connected to multiple busses
    if not isinstance(bus_name, list):
        flow_tuple = get_tuple_for_oemof_results(
            dict_asset[LABEL], asset_group, bus_name
        )

        # Get flow information
        get_flow(
            settings=settings,
            bus=bus_data[bus_name],
            dict_asset=dict_asset,
            flow_tuple=flow_tuple,
        )
        # Get capacity information
        get_optimal_cap(bus_data[bus_name], dict_asset, flow_tuple)

    else:
        # Asset is connected to multiple busses, evaluate all
        for bus_instance in bus_name:
            flow_tuple = get_tuple_for_oemof_results(
                dict_asset[LABEL], asset_group, bus_instance
            )
            get_flow(
                settings=settings,
                bus=bus_data[bus_instance],
                dict_asset=dict_asset,
                flow_tuple=flow_tuple,
                multi_bus=bus_instance,
            )
            # Get capacity information
            get_optimal_cap(bus_data[bus_instance], dict_asset, flow_tuple)

        # For assets with multiple output busses
        if parameter_to_be_evaluated == OUTFLOW_DIRECTION:
            cumulative_flow = 0
            for bus_instance in bus_name:
                cumulative_flow += dict_asset[FLOW][bus_instance]
            dict_asset[PEAK_FLOW][VALUE] = max(cumulative_flow)
            dict_asset[PEAK_FLOW][VALUE] = cumulative_flow.mean()
        elif parameter_to_be_evaluated == INFLOW_DIRECTION:
            logging.error(
                "The result processing of asset with multiple inputs might not be done correctly"
            )


def get_parameter_to_be_evaluated_from_oemof_results(asset_group, asset_label):
    r"""
    Determine the parameter that needs to be evaluated to determine an asset`s optimized flow and capacity.

    Parameters
    ----------
    asset_group: str
        Asset group to which the evaluated asset belongs

    asset_label: str
        Label of the asset, needed for log message

    Returns
    -------
    parameter_to_be_evaluated: str
        Parameter that will be processed to get the dispatch and capacity of an asset

    Notes
    -----
    Tested by:
    - test_get_parameter_to_be_evaluated_from_oemof_results()
    """
    if asset_group in ASSET_GROUPS_DEFINED_BY_INFLUX:
        parameter_to_be_evaluated = INFLOW_DIRECTION

    elif asset_group in ASSET_GROUPS_DEFINED_BY_OUTFLUX:
        parameter_to_be_evaluated = OUTFLOW_DIRECTION

    else:
        logging.warning(
            f"The asset {asset_label} is of group {asset_group}, which is not defined in E1.get_results()."
        )

    return parameter_to_be_evaluated


def get_tuple_for_oemof_results(asset_label, asset_group, bus):
    r"""
    Determines the tuple with which to access the oemof-solph results

    The order of the parameters in the tuple depends on the direction of the flow.
    If the asset is defined...
    a) ...by its influx from a bus, the bus has to be named first in the touple
    b) ...by its outflux into a bus, the asset has to be named first in the touple

    Parameters
    ----------
    asset_label: str
        Name of the asset

    asset_group: str
        Asset group the asset belongs to

    bus: str
        Bus that is to be accessed for the asset´s information

    Returns
    -------
    flow_tuple: tuple of str
        Keys to be accessed in the oemof-solph results

    Notes
    -----
    Tested with
    - test_get_tuple_for_oemof_results()
    """
    # Determine which flux is evaluated for the flow
    if asset_group in ASSET_GROUPS_DEFINED_BY_INFLUX:
        flow_tuple = (bus, asset_label)
    elif asset_group in ASSET_GROUPS_DEFINED_BY_OUTFLUX:
        flow_tuple = (asset_label, bus)
    else:
        logging.warning(
            f"The asset {asset_label} is of group {asset_group}, but it is not defined in E1.get_results() which flux is to be evaluated."
        )

    return flow_tuple


def get_optimal_cap(bus, dict_asset, flow_tuple):
    r"""
    Retrieves optimized capacity of asset specified in `dict_asset`.

    Parameters
    ----------
    bus : dict
        Contains information about the busses linked to the asset specified in
        `dict_asset`. Information about the scalars like investment or initial
        capacity in key 'scalars' (pd.Series) and the flows between the
        component and the busses in key 'sequences' (pd.DataFrame).

    dict_asset : dict
        Contains information about the asset.

    flow_tuple : tuple
        Key of the oemof-solph outputs dict mapping the value to be evaluated

    Returns
    -------
    Indirectly updated `dict_asset` with optimal capacity to be added
    ('optimizedAddCap').

    TODOS
    ^^^^^
    * direction as optimal parameter or with default value None (direction is
        not needed if 'optimizeCap' is not in `dict_asset` or if it's value is False

    """
    if OPTIMIZE_CAP in dict_asset:
        if (
            dict_asset[OPTIMIZE_CAP][VALUE] is True
            and (flow_tuple, OEMOF_INVEST) in bus[OEMOF_SCALARS]
        ):
            optimal_capacity = bus[OEMOF_SCALARS][(flow_tuple, OEMOF_INVEST)]
            optimal_capacity = cut_below_micro(optimal_capacity, dict_asset[LABEL])
            if TIMESERIES_PEAK in dict_asset:
                if dict_asset[TIMESERIES_PEAK][VALUE] > 0:
                    dict_asset.update(
                        {
                            OPTIMIZED_ADD_CAP: {
                                VALUE: optimal_capacity
                                / dict_asset[TIMESERIES_PEAK][VALUE],
                                UNIT: dict_asset[UNIT],
                            }
                        }
                    )
                else:
                    logging.warning(
                        "Time series peak of asset %s negative or zero! Check timeseries. "
                        "No optimized capacity derived.",
                        dict_asset[LABEL],
                    )
                    pass
            else:
                dict_asset.update(
                    {
                        OPTIMIZED_ADD_CAP: {
                            VALUE: optimal_capacity,
                            UNIT: dict_asset[UNIT],
                        }
                    }
                )
            logging.debug(
                "Accessed optimized capacity of asset %s: %s",
                dict_asset[LABEL],
                optimal_capacity,
            )
        else:
            # only set a default optimized add cap value if the key does not exist already
            # this prevent erasing the value in case of multiple in/output busses
            if OPTIMIZED_ADD_CAP not in dict_asset:
                dict_asset.update(
                    {OPTIMIZED_ADD_CAP: {VALUE: 0, UNIT: dict_asset[UNIT]}}
                )


def get_flow(settings, bus, dict_asset, flow_tuple, multi_bus=None):
    r"""
    Adds flow of `bus` and total flow amongst other information to `dict_asset`.

    Depending on `direction` the input or the output flow is used.

    Parameters
    ----------
    settings : dict
        Contains simulation settings from `simulation_settings.csv` with
        additional information like the amount of time steps simulated in the
        optimization ('periods').

    bus : dict
        Contains information about a specific bus. Information about the scalars, if they exist,
            like investment or initial capacity in key 'scalars' (pd.Series) and the
            flows between the component and the bus(ses) in key 'sequences' (pd.DataFrame).

    dict_asset : dict
        Contains information about the asset.

    flow_tuple : tuple
        Entry of the oemof-solph outputs to be evaluated

    multi_bus: str or None
        The name of the current bus (for asset connected to more than one bus)

    Returns
    -------
    Indirectly updates `dict_asset` with the flow of `bus`, the total flow, the annual
    total flow, the maximum of the flow ('peak_flow') and the average value of
    the flow ('average_flow').

    """
    flow = bus[OEMOF_SEQUENCES][(flow_tuple, OEMOF_FLOW)]
    flow = cut_below_micro(flow, dict_asset[LABEL] + FLOW)
    add_info_flows(
        evaluated_period=settings[EVALUATED_PERIOD][VALUE],
        dict_asset=dict_asset,
        flow=flow,
        bus_name=multi_bus,
    )
    if multi_bus is None:
        total_flow = dict_asset[TOTAL_FLOW][VALUE]
        bus_info = ""
    else:
        total_flow = dict_asset[TOTAL_FLOW][multi_bus]
        bus_info = f" for bus '{multi_bus}'"

    logging.debug(
        "Accessed simulated timeseries of asset %s (total sum: %s)%s",
        dict_asset[LABEL],
        round(total_flow),
        bus_info,
    )


def add_info_flows(evaluated_period, dict_asset, flow, type=None, bus_name=None):
    r"""
    Adds `flow` and total flow amongst other information to `dict_asset`.

    Parameters
    ----------
    evaluated_period : int
        The number of days simulated with the energy system model.
    dict_asset : dict
        Contains information about the asset `flow` belongs to.
    flow : pd.Series
        Time series of the flow.
    type: str, default: None
        type of the flow, only exception is "STORAGE_CAPACITY".
    bus_name: str or None
        The name of the current bus (for asset connected to more than one bus)

    Returns
    -------
    Indirectly updates `dict_asset` with the `flow`, the total flow, the annual
    total flow, the maximum of the flow ('peak_flow') and the average value of
    the flow ('average_flow'). As Storage capacity is not a flow, an aggregation of the timeseries does not make sense
    and the parameters TOTAL_FLOW, ANNUAL_TOTAL_FLOW, PEAK_FLOW, AVERAGE_FLOW are added set to None.

    Notes
    -----

    Tested with:
    - E1.test_add_info_flows_365_days()
    - E1.test_add_info_flows_1_day()
    - E1.test_add_info_flows_storage_capacity()
    """
    total_flow = sum(flow)
    # import ipdb;ipdb.set_trace()
    if bus_name is None:
        dict_asset.update({FLOW: flow})
    else:
        if FLOW not in dict_asset:
            dict_asset.update({FLOW: {bus_name: flow}})
        else:
            dict_asset[FLOW][bus_name] = flow

    if type == STORAGE_CAPACITY:
        # The oemof-solph "flow" connected to the storage capacity describes the energy stored in the storage asset, not the actual flow. As such, the below parameters are non-sensical, especially TOTAL_FLOW and ANNUAL_TOTAL_FLOW. PEAK_FLOW and AVERAGE_FLOW are, as a consequence, also not captured. Instead, the AVERAGE_SOC is calculated in a later processing step.
        for parameter in [TOTAL_FLOW, ANNUAL_TOTAL_FLOW, PEAK_FLOW, AVERAGE_FLOW]:
            dict_asset.update({parameter: {VALUE: None, UNIT: "NaN"}})

    else:
        if bus_name is None:
            dict_asset.update(
                {
                    TOTAL_FLOW: {VALUE: total_flow, UNIT: "kWh"},
                    ANNUAL_TOTAL_FLOW: {
                        VALUE: total_flow * 365 / evaluated_period,
                        UNIT: "kWh",
                    },
                    PEAK_FLOW: {VALUE: max(flow), UNIT: "kW"},
                    AVERAGE_FLOW: {VALUE: flow.mean(), UNIT: "kW"},
                }
            )

        else:
            if TOTAL_FLOW not in dict_asset:
                dict_asset.update(
                    {TOTAL_FLOW: {bus_name: total_flow, VALUE: total_flow, UNIT: "kWh"}}
                )
            else:
                dict_asset[TOTAL_FLOW][bus_name] = total_flow
                dict_asset[TOTAL_FLOW][VALUE] += total_flow * 365 / evaluated_period

            if ANNUAL_TOTAL_FLOW not in dict_asset:
                dict_asset.update(
                    {
                        ANNUAL_TOTAL_FLOW: {
                            bus_name: total_flow * 365 / evaluated_period,
                            VALUE: total_flow * 365 / evaluated_period,
                            UNIT: "kWh",
                        }
                    }
                )
            else:
                dict_asset[ANNUAL_TOTAL_FLOW][bus_name] = (
                    total_flow * 365 / evaluated_period
                )
                dict_asset[ANNUAL_TOTAL_FLOW][VALUE] += (
                    total_flow * 365 / evaluated_period
                )

            if PEAK_FLOW not in dict_asset:
                dict_asset.update({PEAK_FLOW: {bus_name: max(flow), UNIT: "kW"}})
            else:
                dict_asset[PEAK_FLOW][bus_name] = max(flow)

            if AVERAGE_FLOW not in dict_asset:
                dict_asset.update({AVERAGE_FLOW: {bus_name: flow.mean(), UNIT: "kW"}})
            else:
                dict_asset[AVERAGE_FLOW][bus_name] = flow.mean()


def convert_demand_to_dataframe(dict_values, sector_demands=None):
    """Dataframe used for the demands table of the report

    Parameters
    ----------
    dict_values: dict
        output values of MVS

    sector_demands: str
        Name of the sector of the energy system whose demands must be returned as a df by this function
        Default: None

    Returns
    -------
    :class:`pandas.DataFrame<frame>`

    """

    # Make a dict which is a sub-dict of the JSON results file with only the consumption components of the energy system
    demands = copy.deepcopy(dict_values[ENERGY_CONSUMPTION])

    # The following block removes all the non-current sectoral demands from the demands dict
    if sector_demands is not None:
        non_sec_demands = []
        # Loop through the demands checking if there are keys which do not belong to the current sector
        for demand_key in demands.keys():
            if demands[demand_key][ENERGY_VECTOR] != (sector_demands.title()):
                non_sec_demands.append(demand_key)
        # Drop the non-sectoral demands from the demands dict
        for demand_to_drop in non_sec_demands:
            del demands[demand_to_drop]

    # Removing all the keys that do not represent actual demands
    drop_list = []

    # Loop though the demands identifying irrelevant demands
    for column_label in demands:
        # Identifies excess sink in demands for removal
        if EXCESS_SINK in column_label:
            drop_list.append(column_label)
        # Identifies DSO_feedin sink in demands for removal
        elif DSO_FEEDIN in column_label:
            drop_list.append(column_label)

    # Remove some elements from drop_list (ie. sinks that are not demands) from data
    for item in drop_list:
        del demands[item]

    # Create empty dict to hold the current-sector demands' data
    demand_data = {}

    # Populate the above dict with data for each of the demand in the current sector
    for dem in list(demands.keys()):
        demand_data.update(
            {
                dem: [
                    demands[dem][UNIT],
                    demands[dem][ENERGY_VECTOR],
                    demands[dem][TIMESERIES_PEAK][VALUE],
                    demands[dem][TIMESERIES_AVERAGE][VALUE],
                    demands[dem][TIMESERIES_TOTAL][VALUE],
                ]
            }
        )
    # Creating a dataframe with all of the demands from the above dict
    df_dem = pd.DataFrame.from_dict(
        demand_data,
        orient="index",
        columns=[
            UNIT,
            "Type of Demand",
            "Peak Demand",
            "Mean Demand",
            "Total Annual Demand",
        ],
    )

    # Operations on the index of the dataframe created above
    df_dem.index.name = "Demands"
    df_dem = df_dem.reset_index()
    df_dem = df_dem.round(2)

    return df_dem


def convert_components_to_dataframe(dict_values):
    """Dataframe used for the component table of the report

    Parameters
    ----------
    dict_values: dict
        output values of MVS

    Returns
    -------
    :class:`pandas.DataFrame<frame>`

    Notes
    -----

    Tested with:
        - test_E1_process_results.test_convert_components_to_dataframe()
    """

    # Read the subdicts energyProduction, energyConversion and energyStorage as separate dicts
    dict_energy_production = dict_values[ENERGY_PRODUCTION]
    dict_energy_conversion = dict_values[ENERGY_CONVERSION]
    dict_energy_storage = dict_values[ENERGY_STORAGE]

    # Read the keys of the above dicts into separate lists
    keys_production = list(dict_energy_production.keys())
    keys_conversion = list(dict_energy_conversion.keys())
    keys_storage = list(dict_energy_storage.keys())

    # Dict to hold the data for creating a pandas dataframe
    components = {}

    # Energy production and conversion have the same tree structure, can be processed together:

    # Add the above dictionaries and lists of keys into new lists for iterating through, later
    comp_dict_list = [dict_energy_production, dict_energy_conversion]
    components_list = [keys_production, keys_conversion]

    # Defining the columns of the table and filling them up with the appropriate data
    for (component_key, comp_dict) in zip(components_list, comp_dict_list):
        for comps in component_key:
            # Define whether optimization takes place
            optimize = translate_optimizeCap_from_boolean_to_yes_no(
                comp_dict[comps][OPTIMIZE_CAP][VALUE]
            )
            components.update(
                {
                    comps: [
                        comp_dict[comps][OEMOF_ASSET_TYPE],
                        comp_dict[comps][ENERGY_VECTOR],
                        comp_dict[comps][UNIT],
                        comp_dict[comps][INSTALLED_CAP][VALUE],
                        optimize,
                    ]
                }
            )

    # Energy storage assets have different structure, added individually
    for storage_component in keys_storage:
        for sub_stor_comp in [INPUT_POWER, STORAGE_CAPACITY, OUTPUT_POWER]:
            comp_label = dict_energy_storage[storage_component][sub_stor_comp][LABEL]
            # Define whether optimization takes place
            # Currently, storage optimization setting applies to all sub-categories.
            # Can be re-used when storage asset sub-components can be optimized individually:
            # dict_energy_storage[storage_component][sub_stor_comp][OPTIMIZE_CAP][VALUE]
            optimize = translate_optimizeCap_from_boolean_to_yes_no(
                dict_energy_storage[storage_component][OPTIMIZE_CAP][VALUE]
            )
            components.update(
                {
                    comp_label: [
                        dict_energy_storage[storage_component][OEMOF_ASSET_TYPE],
                        dict_energy_storage[storage_component][ENERGY_VECTOR],
                        dict_energy_storage[storage_component][sub_stor_comp][
                            INSTALLED_CAP
                        ][UNIT],
                        dict_energy_storage[storage_component][sub_stor_comp][
                            INSTALLED_CAP
                        ][VALUE],
                        optimize,
                    ]
                }
            )

    # Create a pandas dataframe from the dictionary created above
    df_comp = pd.DataFrame.from_dict(
        components,
        orient="index",
        columns=[
            "Type of Component",
            "Energy Vector",
            UNIT,
            "Installed Capacity",
            "Capacity optimization",
        ],
    )
    df_comp.index.name = "Component"
    df_comp = df_comp.reset_index()
    return df_comp


def translate_optimizeCap_from_boolean_to_yes_no(optimize_cap):
    r"""
    Translates the boolean OPTIMIZE_CAP to a yes-no value for readability of auto report

    Parameters
    ----------
    optimize_cap: bool
        Setting whether asset is optimized or not

    Returns
    -------
    optimize: str
        If OPTIMIZE_CAP==True: "Yes", else "No".

    Notes
    -----
    Tested with:
    - test_E1_process_results.test_translate_optimizeCap_from_boolean_to_yes_no()
    """
    if optimize_cap is True:
        optimize = "Yes"
    else:
        optimize = "No"
    return optimize


def convert_scalar_matrix_to_dataframe(dict_values):
    """Dataframe used for the scalar matrix table of the report

    Parameters
    ----------
    dict_values: dict
        output values of MVS

    Returns
    -------
    :class:`pandas.DataFrame<frame>`

    """

    # Read in the scalar matrix as pandas dataframe
    df_scalar_matrix = dict_values[KPI][KPI_SCALAR_MATRIX]

    # Changing the index to a sequence of 0,1,2...
    df_scalar_matrix = df_scalar_matrix.reset_index()

    # Dropping irrelevant columns from the dataframe
    df_scalar_matrix = df_scalar_matrix.drop(
        ["index", TOTAL_FLOW, PEAK_FLOW, AVERAGE_FLOW], axis=1
    )

    # Renaming the columns
    df_scalar_matrix = df_scalar_matrix.rename(
        columns={
            LABEL: "Component/Parameter",
            OPTIMIZED_ADD_CAP: "CAP",
            ANNUAL_TOTAL_FLOW: "Aggregated Flow",
        }
    )
    # Rounding the numeric values to two significant digits
    df_scalar_matrix = df_scalar_matrix.round(2)

    return df_scalar_matrix


def convert_cost_matrix_to_dataframe(dict_values):
    """Dataframe used for the cost matrix table of the report

    Parameters
    ----------
    dict_values: dict
        output values of MVS

    Returns
    -------
    :class:`pandas.DataFrame<frame>`

    """

    # Read in the cost matrix as a pandas dataframe
    df_cost_matrix = dict_values[KPI][KPI_COST_MATRIX]

    # Changing the index to a sequence of 0,1,2...
    df_cost_matrix = df_cost_matrix.reset_index()

    # Drop some irrelevant columns from the dataframe
    df_cost_matrix = df_cost_matrix.drop(
        ["index", COST_OPERATIONAL_TOTAL, COST_INVESTMENT, COST_DISPATCH, COST_OM],
        axis=1,
    )

    # Rename some of the column names
    df_cost_matrix = df_cost_matrix.rename(
        columns={
            LABEL: "Component",
            COST_TOTAL: "Total costs",
            COST_UPFRONT: "Upfront Investment Costs",
        }
    )

    # Round the numeric values to two significant digits
    df_cost_matrix = df_cost_matrix.round(2)
    return df_cost_matrix


def convert_costs_to_dataframe(dict_values):
    """Dataframe used for the costs piecharts of the report

    Parameters
    ----------
    dict_values: dict
        output values of MVS

    Returns
    -------
    :class:`pandas.DataFrame<frame>`

    """
    # Get the cost matrix from the results JSON file into a pandas DF
    df_pie_plot = dict_values[KPI][KPI_COST_MATRIX]

    # List of the needed parameters
    costs_needed = [LABEL, ANNUITY_TOTAL, COST_INVESTMENT, COST_OPERATIONAL_TOTAL]

    # Drop all the irrelevant columns
    df_pie_plot = df_pie_plot[costs_needed]

    # Add a row with total of each column, except label
    df_pie_plot = pd.concat([df_pie_plot, df_pie_plot.sum().to_frame().T])

    # Add a label for the row holding the sum of each column
    df_pie_plot.iloc[-1, 0] = "Total"

    return df_pie_plot


def convert_scalars_to_dataframe(dict_values):
    """
    Processes the scalar system-wide KPI so that they can be included in the report

    Parameters
    ----------
    dict_values: dict
        output values of MVS

    Returns
    -------
    kpi_scalars_dataframe: :class:`pandas.DataFrame<frame>`
        Dataframe to be displayed as a table in the report

    Notes
    -----
    Currently, as the KPI_SCALARS_DICT does not hold any units, the table printed in the report is unit-les.
    """

    units_cost_kpi = get_units_of_cost_matrix_entries(
        dict_values[ECONOMIC_DATA], dict_values[KPI][KPI_SCALARS_DICT]
    )

    kpi_scalars_dataframe = pd.DataFrame(
        dict_values[KPI][KPI_SCALARS_DICT], index=[VALUE]
    )
    kpi_names = kpi_scalars_dataframe.columns
    kpi_scalars_dataframe = kpi_scalars_dataframe.transpose()
    kpi_scalars_dataframe[KPI] = kpi_names
    kpi_scalars_dataframe[UNIT] = units_cost_kpi
    kpi_scalars_dataframe = kpi_scalars_dataframe[[KPI, UNIT, VALUE]]

    return kpi_scalars_dataframe


def convert_kpi_sector_to_dataframe(dict_values):
    """
    Processes the sector KPIs so that they can be included in the report

    Parameters
    ----------
    dict_values: dict
        output values of MVS

    Returns
    -------
    kpi_sectors_dataframe: :class:`pandas.DataFrame<frame>`
        Dataframe to be displayed as a table in the report

    Notes
    -----
    Currently, as the KPI_UNCOUPLED_DICT does not hold any units, the table printed in the report is unit-les.
    """

    if isinstance(dict_values[KPI][KPI_UNCOUPLED_DICT], dict):
        kpi_sectors_dataframe = pd.DataFrame.from_dict(
            dict_values[KPI][KPI_UNCOUPLED_DICT], orient="index"
        )
    else:
        kpi_sectors_dataframe = dict_values[KPI][KPI_UNCOUPLED_DICT]
    # Formats the kpi_sectors dataframe for nicer display
    cols = list(kpi_sectors_dataframe.columns)
    kpi_sectors_dataframe["KPI"] = kpi_sectors_dataframe.index  #
    kpi_sectors_dataframe = kpi_sectors_dataframe[["KPI"] + cols]

    return kpi_sectors_dataframe


def get_units_of_cost_matrix_entries(dict_economic, kpi_list):
    """
    Determines the units of the costs KPI to be stored to :class: DataFrame.

    Parameters
    ----------
    dict_economic:
        Economic project data

    kpi_list:
        List of cost matrix entries

    Returns
    -------
    unit_list: list
        List of units for the :class: DataFrame to be created
    """

    unit_list = []
    kpi_cost_unit_dict = {
        LABEL: None,
        UNIT: None,
        COST_TOTAL: dict_economic[CURR],
        COST_OPERATIONAL_TOTAL: dict_economic[CURR],
        COST_INVESTMENT: dict_economic[CURR],
        COST_UPFRONT: dict_economic[CURR],
        COST_DISPATCH: dict_economic[CURR],
        COST_OM: dict_economic[CURR],
        ANNUITY_TOTAL: dict_economic[CURR] + "/" + UNIT_YEAR,
        ANNUITY_OM: dict_economic[CURR] + "/" + UNIT_YEAR,
        LCOE_ASSET: dict_economic[CURR] + "/" + "energy carrier unit",
    }
    for key in kpi_list:
        if key not in kpi_cost_unit_dict:
            unit_list.append("NA")
        else:
            unit_list.append(kpi_cost_unit_dict[key])
    return unit_list
