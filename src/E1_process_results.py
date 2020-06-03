r"""
Module E1 process results
-------------------------
Module E1 processes the oemof results.
- receive time series per bus for all assets
- write time series to dictionary
- get optimal capacity of optimized assets
- add the evaluation of time series

"""
from src.constants_json_strings import (
    UNIT,
    SIMULATION_SETTINGS,
    VALUE,
    LABEL,
    OPTIMIZE_CAP,
    INSTALLED_CAP,
)

import logging

import pandas as pd


def get_timeseries_per_bus(dict_values, bus_data):
    r"""
    Reads simulation results of all busses and stores time series.

    Parameters
    ----------
    dict_values : dict
        Contains all input data of the simulation.
    bus_data : dict
        Contains information about all busses in a nested dict.
        1st level keys: bus names;
        2nd level keys:
            'scalars': (pd.Series) (does not exist in all dicts)
            'sequences': (pd.DataFrame) - contains flows between components and busses

    Returns
    -------
    Indirectly updated `dict_values` with 'optimizedFlows' - one data frame for each bus.

    """
    bus_data_timeseries = {}
    for bus in bus_data.keys():
        bus_data_timeseries.update(
            {bus: pd.DataFrame(index=dict_values[SIMULATION_SETTINGS]["time_index"])}
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
            bus_data_timeseries[bus][asset] = -bus_data[bus]["sequences"][
                from_bus[asset]
            ]

    dict_values.update({"optimizedFlows": bus_data_timeseries})
    return


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
        ((dict_asset["input_bus_name"], dict_asset[LABEL]), "flow")
    ]
    add_info_flows(settings, dict_asset["input power"], power_charge)

    power_discharge = storage_bus["sequences"][
        ((dict_asset[LABEL], dict_asset["output_bus_name"]), "flow")
    ]
    add_info_flows(settings, dict_asset["output power"], power_discharge)

    capacity = storage_bus["sequences"][((dict_asset[LABEL], "None"), "capacity")]
    add_info_flows(settings, dict_asset["storage capacity"], capacity)

    if OPTIMIZE_CAP in dict_asset:
        if dict_asset[OPTIMIZE_CAP][VALUE] == True:
            power_charge = storage_bus["scalars"][
                ((dict_asset["input_bus_name"], dict_asset[LABEL]), "invest")
            ]
            dict_asset["input power"].update(
                {
                    "optimizedAddCap": {
                        VALUE: power_charge,
                        UNIT: dict_asset["input power"][UNIT],
                    }
                }
            )
            logging.debug(
                "Accessed optimized capacity of asset %s: %s",
                dict_asset["input power"][LABEL],
                power_charge,
            )

            power_discharge = storage_bus["scalars"][
                ((dict_asset[LABEL], dict_asset["output_bus_name"]), "invest")
            ]
            dict_asset["output power"].update(
                {
                    "optimizedAddCap": {
                        VALUE: power_discharge,
                        UNIT: dict_asset["output power"][UNIT],
                    }
                }
            )
            logging.debug(
                "Accessed optimized capacity of asset %s: %s",
                dict_asset["output power"][LABEL],
                power_discharge,
            )

            capacity = storage_bus["scalars"][((dict_asset[LABEL], "None"), "invest")]
            dict_asset["storage capacity"].update(
                {
                    "optimizedAddCap": {
                        VALUE: capacity,
                        UNIT: dict_asset["storage capacity"][UNIT],
                    }
                }
            )
            logging.debug(
                "Accessed optimized capacity of asset %s: %s",
                dict_asset["storage capacity"][LABEL],
                capacity,
            )

        else:
            dict_asset["input power"].update(
                {
                    "optimizedAddCap": {
                        VALUE: 0,
                        UNIT: dict_asset["storage capacity"][UNIT],
                    }
                }
            )
            dict_asset["output power"].update(
                {
                    "optimizedAddCap": {
                        VALUE: 0,
                        UNIT: dict_asset["storage capacity"][UNIT],
                    }
                }
            )
            dict_asset["storage capacity"].update(
                {
                    "optimizedAddCap": {
                        VALUE: 0,
                        UNIT: dict_asset["storage capacity"][UNIT],
                    }
                }
            )

    dict_asset.update(  # todo: this could be a separate function for testing.
        {
            "timeseries_soc": dict_asset["storage capacity"]["flow"]
            / (
                dict_asset["storage capacity"][INSTALLED_CAP][VALUE]
                + dict_asset["storage capacity"]["optimizedAddCap"][VALUE]
            )
        }
    )
    return


def get_results(settings, bus_data, dict_asset):
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

    Returns
    -------
    Indirectly updates `dict_asset` with results.

    """
    # Check if the component has multiple input or output busses
    if "input_bus_name" in dict_asset:
        input_name = dict_asset["input_bus_name"]
        if not isinstance(input_name, list):
            get_flow(
                settings,
                bus_data[input_name],
                dict_asset,
                input_name,
                direction="input",
            )
        else:
            for bus in input_name:
                get_flow(settings, bus_data[bus], dict_asset, bus, direction="input")

    if "output_bus_name" in dict_asset:
        output_name = dict_asset["output_bus_name"]
        if not isinstance(output_name, list):
            get_flow(
                settings,
                bus_data[output_name],
                dict_asset,
                output_name,
                direction="output",
            )
        else:
            for bus in output_name:
                get_flow(settings, bus_data[bus], dict_asset, bus, direction="output")

    # definie capacities. Check if the component has multiple input or output busses
    if "output_bus_name" in dict_asset and "input_bus_name" in dict_asset:
        if not isinstance(output_name, list):
            get_optimal_cap(bus_data[output_name], dict_asset, output_name, "output")
        else:
            for bus in output_name:
                get_optimal_cap(bus_data[bus], dict_asset, bus, "output")

    elif "input_bus_name" in dict_asset:
        if not isinstance(input_name, list):
            get_optimal_cap(bus_data[input_name], dict_asset, input_name, "input")
        else:
            for bus in input_name:
                get_optimal_cap(bus_data[bus], dict_asset, bus, "input")

    elif "output_bus_name" in dict_asset:
        if not isinstance(output_name, list):
            get_optimal_cap(bus_data[output_name], dict_asset, output_name, "output")
        else:
            for bus in output_name:
                get_optimal_cap(bus_data[bus], dict_asset, bus, "output")
    return


def get_optimal_cap(bus, dict_asset, bus_name, direction):
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
    bus_name : str
        Name of `bus`.
    direction : str
        Direction of flow. Options: 'input', 'output'.

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
        if dict_asset[OPTIMIZE_CAP][VALUE] == True:
            if direction == "input":
                optimal_capacity = bus["scalars"][
                    ((bus_name, dict_asset[LABEL]), "invest")
                ]
            elif direction == "output":
                optimal_capacity = bus["scalars"][
                    ((dict_asset[LABEL], bus_name), "invest")
                ]
            else:
                raise ValueError(
                    f"`direction` should be 'input' or 'output' but is {direction}."
                )

            if "timeseries_peak" in dict_asset:
                if dict_asset["timeseries_peak"][VALUE] > 0:
                    dict_asset.update(
                        {
                            "optimizedAddCap": {
                                VALUE: optimal_capacity
                                / dict_asset["timeseries_peak"][VALUE],
                                UNIT: dict_asset[UNIT],
                            }
                        }
                    )
                else:
                    logging.warning(
                        "Time series peak of asset %s negative or zero! Check timeseries. No optimized capacity derived.",
                        dict_asset[LABEL],
                    )
                    pass
            else:
                dict_asset.update(
                    {
                        "optimizedAddCap": {
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
            dict_asset.update({"optimizedAddCap": {VALUE: 0, UNIT: dict_asset[UNIT]}})

    return


def get_flow(settings, bus, dict_asset, bus_name, direction):
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
    bus_name : str
        Name of `bus`.
    direction : str
        Direction of flow. Options: 'input', 'output'.

    Returns
    -------
    Indirectly updates `dict_asset` with the flow of `bus`, the total flow, the annual
    total flow, the maximum of the flow ('peak_flow') and the average value of
    the flow ('average_flow').

    """
    if direction == "input":
        flow = bus["sequences"][((bus_name, dict_asset[LABEL]), "flow")]
    elif direction == "output":
        flow = bus["sequences"][((dict_asset[LABEL], bus_name), "flow")]

    else:
        raise ValueError(
            f"`direction` should be 'input' or 'output' but is {direction}."
        )
    add_info_flows(settings, dict_asset, flow)

    logging.debug(
        "Accessed simulated timeseries of asset %s (total sum: %s)",
        dict_asset[LABEL],
        round(dict_asset["total_flow"][VALUE]),
    )
    return


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
            "flow": flow,
            "total_flow": {VALUE: total_flow, UNIT: "kWh"},
            "annual_total_flow": {
                VALUE: total_flow * 365 / settings["evaluated_period"][VALUE],
                UNIT: "kWh",
            },
            "peak_flow": {VALUE: max(flow), UNIT: "kW"},
            "average_flow": {VALUE: total_flow / len(flow), UNIT: "kW"},
        }
    )
    return
