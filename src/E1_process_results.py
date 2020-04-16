r"""
Module E1 process results
-------------------------
Module E1 processes the oemof results.
- receive time series per bus for all assets
- write time series to dictionary
- get optimal capacity of optimized assets
- add the evaluation of time series

"""

import logging
import pandas as pd


def get_timeseries_per_bus(dict_values, bus_data):
    """
    Reads simulation results of all busses.
    :param dict_values:
    :param bus_data:
    :return:
    """
    bus_data_timeseries = {}
    for bus in bus_data.keys():
        bus_data_timeseries.update(
            {bus: pd.DataFrame(index=dict_values["simulation_settings"]["time_index"])}
        )
        to_bus = {
            key[0][0]: key
            for key in bus_data[bus]["sequences"].keys()
            if key[0][1] == bus and key[1] == "flow"
        }
        for asset in to_bus:
            bus_data_timeseries[bus][asset] = bus_data[bus]["sequences"][to_bus[asset]]

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


def write_bus_timeseries_to_dict_values(dict_asset):
    """

    :param dict_asset:
    :return:
    """
    logging.debug(
        "Accessing oemof simulation results for asset %s", dict_asset["label"]
    )
    return


def get_storage_results(settings, storage_bus, dict_asset):
    """

    :param settings:
    :param storage_bus:
    :param dict_asset:
    :return:
    """
    power_charge = storage_bus["sequences"][
        ((dict_asset["input_bus_name"], dict_asset["label"]), "flow")
    ]
    add_info_flows(settings, dict_asset["charging_power"], power_charge)

    power_discharge = storage_bus["sequences"][
        ((dict_asset["label"], dict_asset["output_bus_name"]), "flow")
    ]
    add_info_flows(settings, dict_asset["discharging_power"], power_discharge)

    capacity = storage_bus["sequences"][((dict_asset["label"], "None"), "capacity")]
    add_info_flows(settings, dict_asset["capacity"], capacity)

    if "optimizeCap" in dict_asset:
        if dict_asset["optimizeCap"]["value"] == True:
            power_charge = storage_bus["scalars"][
                ((dict_asset["input_bus_name"], dict_asset["label"]), "invest")
            ]
            dict_asset["charging_power"].update(
                {
                    "optimizedAddCap": {
                        "value": power_charge,
                        "unit": dict_asset["charging_power"]["unit"],
                    }
                }
            )
            logging.debug(
                "Accessed optimized capacity of asset %s: %s",
                dict_asset["charging_power"]["label"],
                power_charge,
            )

            power_discharge = storage_bus["scalars"][
                ((dict_asset["label"], dict_asset["output_bus_name"]), "invest")
            ]
            dict_asset["discharging_power"].update(
                {
                    "optimizedAddCap": {
                        "value": power_discharge,
                        "unit": dict_asset["discharging_power"]["unit"],
                    }
                }
            )
            logging.debug(
                "Accessed optimized capacity of asset %s: %s",
                dict_asset["discharging_power"]["label"],
                power_discharge,
            )

            capacity = storage_bus["scalars"][((dict_asset["label"], "None"), "invest")]
            dict_asset["capacity"].update(
                {
                    "optimizedAddCap": {
                        "value": capacity,
                        "unit": dict_asset["capacity"]["unit"],
                    }
                }
            )
            logging.debug(
                "Accessed optimized capacity of asset %s: %s",
                dict_asset["capacity"]["label"],
                capacity,
            )

        else:
            dict_asset["charging_power"].update(
                {
                    "optimizedAddCap": {
                        "value": 0,
                        "unit": dict_asset["capacity"]["unit"],
                    }
                }
            )
            dict_asset["discharging_power"].update(
                {
                    "optimizedAddCap": {
                        "value": 0,
                        "unit": dict_asset["capacity"]["unit"],
                    }
                }
            )
            dict_asset["capacity"].update(
                {
                    "optimizedAddCap": {
                        "value": 0,
                        "unit": dict_asset["capacity"]["unit"],
                    }
                }
            )

    dict_asset.update(
        {
            "timeseries_soc": dict_asset["capacity"]["flow"]
            / (
                dict_asset["capacity"]["installedCap"]["value"]
                + dict_asset["capacity"]["optimizedAddCap"]["value"]
            )
        }
    )
    return


def get_results(settings, bus_data, dict_asset):
    """

    :param settings:
    :param bus_data:
    :param dict_asset:
    :return:
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
    """

    :param bus:
    :param dict_asset:
    :param bus_name:
    :param direction:
    :return:
    """
    if "optimizeCap" in dict_asset:
        if dict_asset["optimizeCap"]["value"] == True:
            if direction == "input":
                optimal_capacity = bus["scalars"][
                    ((bus_name, dict_asset["label"]), "invest")
                ]
            elif direction == "output":
                optimal_capacity = bus["scalars"][
                    ((dict_asset["label"], bus_name), "invest")
                ]
            else:
                logging.error(
                    "Function get_optimal_cap has invalid value of parameter direction."
                )

            if "timeseries_peak" in dict_asset:
                if dict_asset["timeseries_peak"]["value"] > 0:
                    dict_asset.update(
                        {
                            "optimizedAddCap": {
                                "value": optimal_capacity
                                / dict_asset["timeseries_peak"]["value"],
                                "unit": dict_asset["unit"],
                            }
                        }
                    )
                else:
                    logging.warning(
                        "Time series peak of asset %s negative or zero! Check timeseries. No optimized capacity derived.",
                        dict_asset["label"],
                    )
                    pass
            else:
                dict_asset.update(
                    {
                        "optimizedAddCap": {
                            "value": optimal_capacity,
                            "unit": dict_asset["unit"],
                        }
                    }
                )
            logging.debug(
                "Accessed optimized capacity of asset %s: %s",
                dict_asset["label"],
                optimal_capacity,
            )
        else:
            dict_asset.update(
                {"optimizedAddCap": {"value": 0, "unit": dict_asset["unit"]}}
            )

    return


def get_flow(settings, bus, dict_asset, bus_name, direction):
    """

    :param settings:
    :param bus:
    :param dict_asset:
    :param bus_name:
    :param direction:
    :return:
    """
    if direction == "input":
        flow = bus["sequences"][((bus_name, dict_asset["label"]), "flow")]
    elif direction == "output":
        flow = bus["sequences"][((dict_asset["label"], bus_name), "flow")]

    else:
        logging.warning('Value %s not "input" or "output"!', direction)
    add_info_flows(settings, dict_asset, flow)

    logging.debug(
        "Accessed simulated timeseries of asset %s (total sum: %s)",
        dict_asset["label"],
        round(dict_asset["total_flow"]["value"]),
    )
    return


def add_info_flows(settings, dict_asset, flow):
    """

    :param settings:
    :param dict_asset:
    :param flow:
    :return:
    """
    total_flow = sum(flow)
    dict_asset.update(
        {
            "flow": flow,
            "total_flow": {"value": total_flow, "unit": "kWh"},
            "annual_total_flow": {
                "value": total_flow * 365 / settings["evaluated_period"]["value"],
                "unit": "kWh",
            },
            "peak_flow": {"value": max(flow), "unit": "kW"},
            "average_flow": {"value": total_flow / len(flow), "unit": "kW"},
        }
    )
    return
