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
    AUTO_SINK,
    EXCESS,
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
)

# Determines which assets are defined by...
# a influx from a bus
ASSET_GROUPS_DEFINED_BY_INFLUX = [ENERGY_CONSUMPTION]
# b outflux into a bus
ASSET_GROUPS_DEFINED_BY_OUTFLUX = [ENERGY_CONVERSION, ENERGY_PRODUCTION]


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
            for key in bus_data[bus]["sequences"].keys()
            if key[0][1] == bus and key[1] == "flow"
        }
        for asset in to_bus:
            bus_data_timeseries[bus][asset] = bus_data[bus]["sequences"][to_bus[asset]]

        # obtain flows that flow out of the bus
        from_bus = {
            key[0][1]: key
            for key in bus_data[bus]["sequences"].keys()
            if key[0][0] == bus and key[1] == "flow"
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
                ]["sequences"][from_bus[asset]]
            except KeyError:
                # The asset was not previously added to the `OPTIMIZED_FLOWS`, ie. is not a storage asset
                bus_data_timeseries[bus][asset] = -bus_data[bus]["sequences"][
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
    power_charge = storage_bus["sequences"][
        ((dict_asset[INFLOW_DIRECTION], dict_asset[LABEL]), "flow")
    ]
    add_info_flows(settings, dict_asset[INPUT_POWER], power_charge)

    power_discharge = storage_bus["sequences"][
        ((dict_asset[LABEL], dict_asset[OUTFLOW_DIRECTION]), "flow")
    ]
    add_info_flows(settings, dict_asset[OUTPUT_POWER], power_discharge)

    capacity = storage_bus["sequences"][
        ((dict_asset[LABEL], TYPE_NONE), "storage_content")
    ]
    add_info_flows(settings, dict_asset[STORAGE_CAPACITY], capacity)

    if OPTIMIZE_CAP in dict_asset:
        if dict_asset[OPTIMIZE_CAP][VALUE] is True:
            power_charge = storage_bus["scalars"][
                ((dict_asset[INFLOW_DIRECTION], dict_asset[LABEL]), "invest")
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

            power_discharge = storage_bus["scalars"][
                ((dict_asset[LABEL], dict_asset[OUTFLOW_DIRECTION]), "invest")
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

            capacity = storage_bus["scalars"][
                ((dict_asset[LABEL], TYPE_NONE), "invest")
            ]
            dict_asset[STORAGE_CAPACITY].update(
                {
                    OPTIMIZED_ADD_CAP: {
                        VALUE: capacity,
                        UNIT: dict_asset[STORAGE_CAPACITY][UNIT],
                    }
                }
            )
            logging.debug(
                "Accessed optimized capacity of asset %s: %s",
                dict_asset[STORAGE_CAPACITY][LABEL],
                capacity,
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

    dict_asset.update(  # todo: this could be a separate function for testing.
        {
            "timeseries_soc": dict_asset[STORAGE_CAPACITY]["flow"]
            / (
                dict_asset[STORAGE_CAPACITY][INSTALLED_CAP][VALUE]
                + dict_asset[STORAGE_CAPACITY][OPTIMIZED_ADD_CAP][VALUE]
            )
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
            # Get flow information
            get_flow(
                settings=settings,
                bus=bus_data[bus_instance],
                dict_asset=dict_asset,
                flow_tuple=flow_tuple,
            )
            # Get capacity information
            get_optimal_cap(bus_data[bus_instance], dict_asset, flow_tuple)


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

    possible todos
    --------------
    * direction as optimal parameter or with default value None (direction is
        not needed if 'optimizeCap' is not in `dict_asset` or if it's value is False

    Returns
    -------
    Indirectly updated `dict_asset` with optimal capacity to be added
    ('optimizedAddCap').

    """
    if OPTIMIZE_CAP in dict_asset:
        if (
            dict_asset[OPTIMIZE_CAP][VALUE] is True
            and (flow_tuple, "invest") in bus["scalars"]
        ):
            optimal_capacity = bus["scalars"][(flow_tuple, "invest")]

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
            dict_asset.update({OPTIMIZED_ADD_CAP: {VALUE: 0, UNIT: dict_asset[UNIT]}})


def get_flow(settings, bus, dict_asset, flow_tuple):
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

    Returns
    -------
    Indirectly updates `dict_asset` with the flow of `bus`, the total flow, the annual
    total flow, the maximum of the flow ('peak_flow') and the average value of
    the flow ('average_flow').

    """
    flow = bus["sequences"][(flow_tuple, "flow")]
    add_info_flows(settings, dict_asset, flow)

    logging.debug(
        "Accessed simulated timeseries of asset %s (total sum: %s)",
        dict_asset[LABEL],
        round(dict_asset[TOTAL_FLOW][VALUE]),
    )


def add_info_flows(settings, dict_asset, flow):
    r"""
    Adds `flow` and total flow amongst other information to `dict_asset`.

    Parameters
    ----------
    settings : dict
        Contains simulation settings from `simulation_settings.csv` with
        additional information like the amount of time steps simulated in the
        optimization ('periods').
    dict_asset : dict
        Contains information about the asset `flow` belongs to.
    flow : pd.Series
        Time series of the flow.

    Returns
    -------
    Indirectly updates `dict_asset` with the `flow`, the total flow, the annual
    total flow, the maximum of the flow ('peak_flow') and the average value of
    the flow ('average_flow').

    """
    total_flow = sum(flow)
    dict_asset.update(
        {
            FLOW: flow,
            TOTAL_FLOW: {VALUE: total_flow, UNIT: "kWh"},
            ANNUAL_TOTAL_FLOW: {
                VALUE: total_flow * 365 / settings[EVALUATED_PERIOD][VALUE],
                UNIT: "kWh",
            },
            PEAK_FLOW: {VALUE: max(flow), UNIT: "kW"},
            AVERAGE_FLOW: {VALUE: total_flow / len(flow), UNIT: "kW"},
        }
    )


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
        if EXCESS in column_label:
            drop_list.append(column_label)
        # Identifies DSO_feedin sink in demands for removal
        elif DSO_FEEDIN + AUTO_SINK in column_label:
            drop_list.append(column_label)
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

    """

    # Read the subdicts energyProduction, energyConversion and energyStorage as separate dicts
    components1 = dict_values[ENERGY_PRODUCTION]
    components2 = dict_values[ENERGY_CONVERSION]
    components3 = dict_values[ENERGY_STORAGE]

    # Read the keys of the above dicts into separate lists
    comp1_keys = list(components1.keys())
    comp2_keys = list(components2.keys())
    comp3_keys = list(components3.keys())

    # Add the above dictionaries and lists of keys into new lists for iterating through, later
    comp_dict_list = [components1, components2]
    components_list = [comp1_keys, comp2_keys]

    # Dict to hold the data for creating a pandas dataframe
    components = {}

    # Defining the columns of the table and filling them up with the appropriate data
    for (component_key, comp_dict) in zip(components_list, comp_dict_list):
        for comps in component_key:
            components.update(
                {
                    comps: [
                        comp_dict[comps][OEMOF_ASSET_TYPE],
                        comp_dict[comps][ENERGY_VECTOR],
                        comp_dict[comps][UNIT],
                        comp_dict[comps][INSTALLED_CAP][VALUE],
                        comp_dict[comps][OPTIMIZE_CAP][VALUE],
                    ]
                }
            )

    for storage_component in comp3_keys:
        for sub_stor_comp in [INPUT_POWER, STORAGE_CAPACITY, OUTPUT_POWER]:
            comp_label = components3[storage_component][sub_stor_comp][LABEL]
            components.update(
                {
                    comp_label: [
                        components3[storage_component][OEMOF_ASSET_TYPE],
                        components3[storage_component][ENERGY_VECTOR],
                        components3[storage_component][sub_stor_comp][INSTALLED_CAP][
                            UNIT
                        ],
                        components3[storage_component][sub_stor_comp][INSTALLED_CAP][
                            VALUE
                        ],
                        components3[storage_component][sub_stor_comp][OPTIMIZE_CAP][
                            VALUE
                        ],
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

    # Add True or False for each component in the column for capacity optimization
    for i in range(len(df_comp)):
        if df_comp.at[i, "Capacity optimization"] is True:
            df_comp.iloc[i, df_comp.columns.get_loc("Capacity optimization")] = "Yes"
        else:
            df_comp.iloc[i, df_comp.columns.get_loc("Capacity optimization")] = "No"

    return df_comp


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
    df_pie_plot = df_pie_plot.append(
        df_pie_plot.sum(numeric_only=True), ignore_index=True
    )

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
