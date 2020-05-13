import os
import sys
import shutil
import logging
import pandas as pd
import matplotlib.pyplot as plt
import logging

logging.getLogger("matplotlib.font_manager").disabled = True

from src.constants import INPUTS_COPY, TIME_SERIES
from src.constants import PATHS_TO_PLOTS, PLOTS_DEMANDS, PLOTS_RESOURCES

import src.C1_verification as verify
import src.C2_economic_functions as economics
import src.F0_output as output


def all(dict_values):
    """
    Function executing all pre-processing steps necessary
    :param dict_values
    All input data in dict format

    :return Pre-processed dictionary with all input parameters

    """
    simulation_settings(dict_values["simulation_settings"])
    economic_parameters(dict_values["economic_data"])
    identify_energy_vectors(dict_values)

    ## Verify inputs
    # todo check whether input values can be true
    # verify.check_input_values(dict_values)
    # todo Check, whether files (demand, generation) are existing

    # Adds costs to each asset and sub-asset
    process_all_assets(dict_values)

    output.store_as_json(
        dict_values,
        dict_values["simulation_settings"]["path_output_folder"],
        "json_input_processed",
    )
    return


def identify_energy_vectors(dict_values):
    """
    Identifies all energyVectors used in the energy system by checking every entry 'energyVector' of all assets.
    energyVectors later will be used to distribute costs and KPI amongst the sectors (not implemented)

    :param: dict
    All input data in dict format

    :return:
    Update dict['project_data'] by used sectors
    """
    dict_of_sectors = {}
    names_of_sectors = ""
    for level1 in dict_values.keys():
        for level2 in dict_values[level1].keys():
            if (
                isinstance(dict_values[level1][level2], dict)
                and "energyVector" in dict_values[level1][level2].keys()
            ):
                energy_vector_name = dict_values[level1][level2]["energyVector"]
                if energy_vector_name not in dict_of_sectors.keys():
                    dict_of_sectors.update(
                        {energy_vector_name: energy_vector_name.replace("_", " ")}
                    )
                    names_of_sectors = names_of_sectors + energy_vector_name + ", "

    dict_values["project_data"].update({"sectors": dict_of_sectors})
    logging.info(
        "The energy system modelled includes following energy vectors / sectors: %s",
        names_of_sectors[:-2],
    )
    return


def simulation_settings(simulation_settings):
    """
    Updates simulation settings by all time-related parameters.
    :param: dict
    Simulation parameters of the input data
    :return: dict
    Update simulation_settings by start date, end date, timeindex, and number of simulation periods
    """
    simulation_settings.update(
        {"start_date": pd.to_datetime(simulation_settings["start_date"])}
    )
    simulation_settings.update(
        {
            "end_date": simulation_settings["start_date"]
            + pd.DateOffset(
                days=simulation_settings["evaluated_period"]["value"], hours=-1
            )
        }
    )
    # create time index used for initializing oemof simulation
    simulation_settings.update(
        {
            "time_index": pd.date_range(
                start=simulation_settings["start_date"],
                end=simulation_settings["end_date"],
                freq=str(simulation_settings["timestep"]["value"]) + "min",
            )
        }
    )

    simulation_settings.update({"periods": len(simulation_settings["time_index"])})
    return simulation_settings


def economic_parameters(economic_parameters):
    """Calculate annuity factor

    :param economic_parameters:
    :return:
    """

    economic_parameters.update(
        {
            "annuity_factor": {
                "value": economics.annuity_factor(
                    economic_parameters["project_duration"]["value"],
                    economic_parameters["discount_factor"]["value"],
                ),
                "unit": "?",
            }
        }
    )
    # Calculate crf
    economic_parameters.update(
        {
            "crf": {
                "value": economics.crf(
                    economic_parameters["project_duration"]["value"],
                    economic_parameters["discount_factor"]["value"],
                ),
                "unit": "?",
            }
        }
    )
    return


def process_all_assets(dict_values):
    """defines dict_values['energyBusses'] for later reference

    :param dict_values:
    :return:
    """
    #
    define_busses(dict_values)

    # Define all excess sinks for sectors
    for sector in dict_values["project_data"]["sectors"]:
        define_sink(
            dict_values,
            dict_values["project_data"]["sectors"][sector] + " excess",
            {"value": 0, "unit": "currency/kWh"},
            dict_values["project_data"]["sectors"][sector],
        )
        logging.debug(
            "Created excess sink for sector %s",
            dict_values["project_data"]["sectors"][sector],
        )

    # process all energyAssets:
    # Attention! Order of asset_groups important. for energyProviders/energyConversion sinks and sources
    # might be defined that have to be processed in energyProduction/energyConsumption
    asset_group_list = [
        "energyProviders",
        "energyConversion",
        "energyStorage",
        "energyProduction",
        "energyConsumption",
    ]

    for asset_group in asset_group_list:
        logging.info("Pre-processing all assets in asset group %s.", asset_group)
        if asset_group != "energyProviders":
            # Populates dict_values['energyBusses'] with assets
            update_busses_in_out_direction(dict_values, dict_values[asset_group])
        if asset_group == "energyConversion":
            energyConversion(dict_values, asset_group)
        elif asset_group == "energyProduction":
            energyProduction(dict_values, asset_group)
        elif asset_group == "energyStorage":
            energyStorage(dict_values, asset_group)
        elif asset_group == "energyProviders":
            energyProviders(dict_values, asset_group)
        elif asset_group == "energyConsumption":
            energyConsumption(dict_values, asset_group)
        else:
            logging.error(
                "Coding error. Asset group list item %s not known.", asset_group
            )
        logging.debug(
            "Finished pre-processing all assets in asset group %s.", asset_group
        )

    logging.info("Processed cost data and added economic values.")
    return


def energyConversion(dict_values, group):
    """Add lifetime capex (incl. replacement costs), calculate annuity (incl. om), and simulation annuity to each asset

    :param dict_values:
    :param group:
    :return:
    """
    #
    for asset in dict_values[group]:
        define_missing_cost_data(dict_values, dict_values[group][asset])
        evaluate_lifetime_costs(
            dict_values["simulation_settings"],
            dict_values["economic_data"],
            dict_values[group][asset],
        )
        # check if maximumCap exists and add it to dict_values
        add_maximum_cap(dict_values=dict_values, group=group, asset=asset)

        # in case there is only one parameter provided (input bus and one output bus)
        if isinstance(dict_values[group][asset]["efficiency"]["value"], dict):
            receive_timeseries_from_csv(dict_values,dict_values,
                dict_values["simulation_settings"],
                dict_values[group][asset],
                "efficiency",
            )
        # in case there is more than one parameter provided (either (A) n input busses and 1 output bus or (B) 1 input bus and n output busses)
        # dictionaries with filenames and headers will be replaced by timeseries, scalars will be mantained
        elif isinstance(dict_values[group][asset]["efficiency"]["value"], list):
            treat_multiple_flows(dict_values[group][asset], dict_values, "efficiency")

            # same distinction of values provided with dictionaries (one input and one output) or list (multiple).
            # They can at turn be scalars, mantained, or timeseries
            logging.debug(
                "Asset %s has multiple input/output busses with a list of efficiencies. Reading list",
                dict_values[group][asset]["label"],
            )
    return


def energyProduction(dict_values, group):
    """

    :param dict_values:
    :param group:
    :return:
    """
    for asset in dict_values[group]:
        define_missing_cost_data(dict_values, dict_values[group][asset])
        evaluate_lifetime_costs(
            dict_values["simulation_settings"],
            dict_values["economic_data"],
            dict_values[group][asset],
        )

        if "file_name" in dict_values[group][asset]:
            receive_timeseries_from_csv(dict_values, dict_values["simulation_settings"], dict_values[group][asset], "input"
            )
        # check if maximumCap exists and add it to dict_values
        add_maximum_cap(dict_values, group, asset)

    return


def energyStorage(dict_values, group):
    """

    :param dict_values:
    :param group:
    :return:
    """
    for asset in dict_values[group]:
        for subasset in ["storage capacity", "input power", "output power"]:
            define_missing_cost_data(
                dict_values, dict_values[group][asset][subasset],
            )
            evaluate_lifetime_costs(
                dict_values["simulation_settings"],
                dict_values["economic_data"],
                dict_values[group][asset][subasset],
            )

            # check if parameters are provided as timeseries
            for parameter in ["efficiency", "soc_min", "soc_max"]:
                if parameter in dict_values[group][asset][subasset] and isinstance(
                    dict_values[group][asset][subasset][parameter]["value"], dict
                ):
                    receive_timeseries_from_csv(dict_values,
                        dict_values["simulation_settings"],
                        dict_values[group][asset][subasset],
                        parameter,
                    )
                elif parameter in dict_values[group][asset][subasset] and isinstance(
                    dict_values[group][asset][subasset][parameter]["value"], list
                ):
                    treat_multiple_flows(
                        dict_values[group][asset][subasset], dict_values, parameter
                    )
            # check if maximumCap exists and add it to dict_values
            add_maximum_cap(dict_values, group, asset, subasset)

        # define input and output bus names
        dict_values[group][asset].update(
            {
                "input_bus_name": bus_suffix(
                    dict_values[group][asset]["inflow_direction"]
                )
            }
        )
        dict_values[group][asset].update(
            {
                "output_bus_name": bus_suffix(
                    dict_values[group][asset]["outflow_direction"]
                )
            }
        )
    return


def energyProviders(dict_values, group):
    """

    :param dict_values:
    :param group:
    :return:
    """
    # add sources and sinks depending on items in energy providers as pre-processing
    for asset in dict_values[group]:
        define_dso_sinks_and_sources(dict_values, asset)

        # Add lifetime capex (incl. replacement costs), calculate annuity
        # (incl. om), and simulation annuity to each asset
        define_missing_cost_data(dict_values, dict_values[group][asset])
        evaluate_lifetime_costs(
            dict_values["simulation_settings"],
            dict_values["economic_data"],
            dict_values[group][asset],
        )
    return


def energyConsumption(dict_values, group):
    """

    :param dict_values:
    :param group:
    :return:
    """
    for asset in dict_values[group]:
        define_missing_cost_data(dict_values, dict_values[group][asset])
        evaluate_lifetime_costs(
            dict_values["simulation_settings"],
            dict_values["economic_data"],
            dict_values[group][asset],
        )
        if "input_bus_name" not in dict_values[group][asset]:
            dict_values[group][asset].update(
                {
                    "input_bus_name": bus_suffix(
                        dict_values[group][asset]["energyVector"]
                    )
                }
            )

        if "file_name" in dict_values[group][asset]:
            receive_timeseries_from_csv(dict_values,
                                        dict_values["simulation_settings"], dict_values[group][asset], "input", is_demand_profile = True
                                        )
    return


def define_missing_cost_data(dict_values, dict_asset):
    """

    :param dict_values:
    :param dict_asset:
    :return:
    """

    # read timeseries with filename provided for variable costs.
    # if multiple opex_var are given for multiple busses, it checks if any v
    # alue is a timeseries
    if "opex_var" in dict_asset:
        if isinstance(dict_asset["opex_var"]["value"], dict):
            receive_timeseries_from_csv(dict_values,
                dict_values["simulation_settings"], dict_asset, "opex_var"
            )
        elif isinstance(dict_asset["opex_var"]["value"], list):
            treat_multiple_flows(dict_asset, dict_values, "opex_var")

    economic_data = dict_values["economic_data"]

    basic_costs = {
        "optimizeCap": {"value": False, "unit": "bool"},
        "unit": "?",
        "installedCap": {"value": 0.0, "unit": "unit"},
        "capex_fix": {"value": 0, "unit": "currency"},
        "capex_var": {"value": 0, "unit": "currency/unit"},
        "opex_fix": {"value": 0, "unit": "currency/year"},
        "opex_var": {"value": 0, "unit": "currency/unit/year"},
        "lifetime": {
            "value": economic_data["project_duration"]["value"],
            "unit": "year",
        },
    }

    # checks that an asset has all cost parameters needed for evaluation.
    # Adds standard values.
    str = ""
    for cost in basic_costs:
        if cost not in dict_asset:
            dict_asset.update({cost: basic_costs[cost]})
            str = str + " " + cost

    if len(str) > 1:
        logging.debug("Added basic costs to asset %s: %s", dict_asset["label"], str)
    return


def define_busses(dict_values):
    """

    :param dict_values:
    :return:
    """
    # create new group of assets: busses
    dict_values.update({"energyBusses": {}})

    # defines energy busses of sectors
    for sector in dict_values["project_data"]["sectors"]:
        dict_values["energyBusses"].update(
            {bus_suffix(dict_values["project_data"]["sectors"][sector]): {}}
        )
    # defines busses accessed by conversion assets
    update_busses_in_out_direction(dict_values, dict_values["energyConversion"])
    return


def update_busses_in_out_direction(dict_values, asset_group, **kwargs):
    """

    :param dict_values:
    :param asset_group:
    :param kwargs:
    :return:
    """
    # checks for all assets of an group
    for asset in asset_group:
        # the bus that is connected to the inflow
        if "inflow_direction" in asset_group[asset]:
            bus = asset_group[asset]["inflow_direction"]
            if isinstance(bus, list):
                bus_list = []
                for subbus in bus:
                    bus_list.append(bus_suffix(subbus))
                    update_bus(dict_values, subbus, asset, asset_group[asset]["label"])
                asset_group[asset].update({"input_bus_name": bus_list})
            else:
                asset_group[asset].update({"input_bus_name": bus_suffix(bus)})
                update_bus(dict_values, bus, asset, asset_group[asset]["label"])
        # the bus that is connected to the outflow
        if "outflow_direction" in asset_group[asset]:
            bus = asset_group[asset]["outflow_direction"]
            if isinstance(bus, list):
                bus_list = []
                for subbus in bus:
                    bus_list.append(bus_suffix(subbus))
                    update_bus(dict_values, subbus, asset, asset_group[asset]["label"])
                asset_group[asset].update({"output_bus_name": bus_list})
            else:
                asset_group[asset].update({"output_bus_name": bus_suffix(bus)})
                update_bus(dict_values, bus, asset, asset_group[asset]["label"])

    return


def bus_suffix(bus):
    """

    :param bus:
    :return:
    """
    bus_label = bus + " bus"
    return bus_label


def update_bus(dict_values, bus, asset, asset_label):
    """

    :param dict_values:
    :param bus:
    :param asset:
    :param asset_label:
    :return:
    """
    bus_label = bus_suffix(bus)
    if bus_label not in dict_values["energyBusses"]:
        # add bus to asset group energyBusses
        dict_values["energyBusses"].update({bus_label: {}})

    # Asset should added to respective bus
    dict_values["energyBusses"][bus_label].update({asset: asset_label})
    logging.debug("Added asset %s to bus %s", asset_label, bus_label)
    return


def define_dso_sinks_and_sources(dict_values, dso):
    """

    :param dict_values:
    :param dso:
    :return:
    """
    # define to shorten code
    number_of_pricing_periods = dict_values["energyProviders"][dso][
        "peak_demand_pricing_period"
    ]["value"]
    # defines the evaluation period
    months_in_a_period = 12 / number_of_pricing_periods
    logging.info(
        "Peak demand pricing is taking place %s times per year, ie. every %s "
        "months.",
        number_of_pricing_periods,
        months_in_a_period,
    )

    dict_asset = dict_values["energyProviders"][dso]
    if isinstance(dict_asset["peak_demand_pricing"]["value"], dict):
        receive_timeseries_from_csv(dict_values,
            dict_values["simulation_settings"], dict_asset, "peak_demand_pricing"
        )

    peak_demand_pricing = dict_values["energyProviders"][dso]["peak_demand_pricing"][
        "value"
    ]
    if isinstance(peak_demand_pricing, float) or isinstance(peak_demand_pricing, int):
        logging.debug(
            "The peak demand pricing price of %s %s is set as capex_var of "
            "the sources of grid energy.",
            peak_demand_pricing,
            dict_values["economic_data"]["currency"],
        )
    else:
        logging.debug(
            "The peak demand pricing price of %s %s is set as capex_var of "
            "the sources of grid energy.",
            sum(peak_demand_pricing) / len(peak_demand_pricing),
            dict_values["economic_data"]["currency"],
        )

    peak_demand_pricing = {
        "value": dict_values["energyProviders"][dso]["peak_demand_pricing"]["value"],
        "unit": "currency/kWpeak",
    }

    if number_of_pricing_periods == 1:
        # if only one period: avoid suffix dso+'_consumption_period_1"
        timeseries = pd.Series(
            1, index=dict_values["simulation_settings"]["time_index"]
        )
        define_source(
            dict_values,
            dso + "_consumption",
            dict_values["energyProviders"][dso]["energy_price"],
            dict_values["energyProviders"][dso]["outflow_direction"],
            timeseries,
            opex_fix=peak_demand_pricing,
        )
    else:
        # define one source for each pricing period
        for pricing_period in range(1, number_of_pricing_periods + 1):
            timeseries = pd.Series(
                0, index=dict_values["simulation_settings"]["time_index"]
            )
            time_period = pd.date_range(
                start=dict_values["simulation_settings"]["start_date"]
                + pd.DateOffset(months=(pricing_period - 1) * months_in_a_period),
                end=dict_values["simulation_settings"]["start_date"]
                + pd.DateOffset(months=pricing_period * months_in_a_period, hours=-1),
                freq=str(dict_values["simulation_settings"]["timestep"]["value"])
                + "min",
            )

            timeseries = timeseries.add(pd.Series(1, index=time_period), fill_value=0)
            define_source(
                dict_values,
                dso + "_consumption_period_" + str(pricing_period),
                dict_values["energyProviders"][dso]["energy_price"],
                dict_values["energyProviders"][dso]["outflow_direction"],
                timeseries,
                opex_fix=peak_demand_pricing,
            )

    define_sink(
        dict_values,
        dso + "_feedin",
        dict_values["energyProviders"][dso]["feedin_tariff"],
        dict_values["energyProviders"][dso]["inflow_direction"],
        capex_var={"value": 0, "unit": "currency/kW"},
    )

    return


def define_source(dict_values, asset_name, price, output_bus, timeseries, **kwargs):
    """

    :param dict_values:
    :param asset_name:
    :param price:
    :param output_bus:
    :param timeseries:
    :param kwargs:
    :return:
    """
    # create name of bus. Check if multiple busses are given
    if isinstance(output_bus, list):
        output_bus_name = []
        for bus in output_bus:
            output_bus_name.append(bus_suffix(bus))
    else:
        output_bus_name = bus_suffix(output_bus)

    source = {
        "type_oemof": "source",
        "label": asset_name + " source",
        "output_direction": output_bus,
        "output_bus_name": output_bus_name,
        "dispatchable": True,
        "timeseries": timeseries,
        # "opex_var": {"value": price, "unit": "currency/unit"},
        "lifetime": {
            "value": dict_values["economic_data"]["project_duration"]["value"],
            "unit": "year",
        },
    }

    # check if multiple busses are provided
    # for each bus, read time series for opex_var if a file name has been
    # provided in energy price
    if isinstance(price["value"], list):
        source.update({"opex_var": {"value": [], "unit": price["unit"]}})
        values_info = []
        for element in price["value"]:
            if isinstance(element, dict):
                source["opex_var"]["value"].append(
                    get_timeseries_multiple_flows(
                        dict_values["simulation_settings"],
                        source,
                        element["file_name"],
                        element["header"],
                    )
                )
                values_info.append(element)
            else:
                source["opex_var"]["value"].append(element)
        if len(values_info) > 0:
            source["opex_var"]["values_info"] = values_info

    elif isinstance(price["value"], dict):
        source.update(
            {
                "opex_var": {
                    "value": {
                        "file_name": price["value"]["file_name"],
                        "header": price["value"]["header"],
                    },
                    "unit": price["unit"],
                }
            }
        )
        receive_timeseries_from_csv(dict_values,
            dict_values["simulation_settings"], source, "opex_var"
        )
    else:
        source.update({"opex_var": {"value": price["value"], "unit": price["unit"]}})

    logging.debug(
        "Asset %s: sum of timeseries = %s", asset_name, sum(timeseries.values)
    )

    if "opex_fix" in kwargs or "capex_var" in kwargs:
        if "opex_fix" in kwargs:
            source.update({"opex_fix": kwargs["opex_fix"]})
        else:
            source.update({"capex_var": kwargs["capex_var"]})

        source.update(
            {
                "optimizeCap": {"value": True, "unit": "bool"},
                "timeseries_peak": {"value": max(timeseries), "unit": "kW"},
                # todo if we have normalized timeseries hiere, the capex/opex (simulation) have changed, too
                "timeseries_normalized": timeseries / max(timeseries),
            }
        )
        if type(source["opex_var"]["value"]) == pd.Series:
            logging.warning(
                "Attention! %s is created, with a price defined as a timeseries (average: %s). "
                "If this is DSO supply, this could be improved. Please refer to Issue #23.",
                source["label"],
                source["opex_var"]["value"].mean(),
            )
        else:
            logging.warning(
                "Attention! %s is created, with a price of %s."
                "If this is DSO supply, this could be improved. Please refer to Issue #23. ",
                source["label"],
                source["opex_var"]["value"],
            )
    else:
        source.update({"optimizeCap": {"value": False, "unit": "bool"}})

    # add the parameter "maximumCap" to DSO source
    source.update({"maximumCap": {"value": None, "unit": "kWp"}})

    # update dictionary
    dict_values["energyProduction"].update({asset_name: source})

    # create new input bus if non-existent before. Check if multiple busses are provided
    if isinstance(output_bus, list):
        for bus in output_bus:
            # add to list of assets on busses
            update_bus(dict_values, bus, asset_name, source["label"])
    else:
        # add to list of assets on busses
        update_bus(dict_values, output_bus, asset_name, source["label"])

    return


def define_sink(dict_values, asset_name, price, input_bus, **kwargs):
    """

    :param dict_values:
    :param asset_name:
    :param price:
    :param input_bus:
    :param kwargs:
    :return:
    """
    # create name of bus. Check if multiple busses are given
    if isinstance(input_bus, list):
        input_bus_name = []
        for bus in input_bus:
            input_bus_name.append(bus_suffix(bus))
    else:
        input_bus_name = bus_suffix(input_bus)

    # create a dictionary for the sink
    sink = {
        "type_oemof": "sink",
        "label": asset_name + "_sink",
        "input_direction": input_bus,
        "input_bus_name": input_bus_name,
        # "opex_var": {"value": price, "unit": "currency/kWh"},
        "lifetime": {
            "value": dict_values["economic_data"]["project_duration"]["value"],
            "unit": "year",
        },
    }

    # check if multiple busses are provided
    # for each bus, read time series for opex_var if a file name has been provided in feedin tariff
    if isinstance(price["value"], list):
        sink.update({"opex_var": {"value": [], "unit": price["unit"]}})
        values_info = []
        for element in price["value"]:
            if isinstance(element, dict):
                timeseries = get_timeseries_multiple_flows(
                    dict_values["simulation_settings"],
                    sink,
                    element["file_name"],
                    element["header"],
                )
                if asset_name[-6:] == "feedin":
                    sink["opex_var"]["value"].append([-i for i in timeseries])
                else:
                    sink["opex_var"]["value"].append(timeseries)
            else:
                sink["opex_var"]["value"].append(element)
        if len(values_info) > 0:
            sink["opex_var"]["values_info"] = values_info

    elif isinstance(price["value"], dict):
        sink.update(
            {
                "opex_var": {
                    "value": {
                        "file_name": price["value"]["file_name"],
                        "header": price["value"]["header"],
                    },
                    "unit": price["unit"],
                }
            }
        )
        receive_timeseries_from_csv(dict_values,
            dict_values["simulation_settings"], sink, "opex_var"
        )
        if (
            asset_name[-6:] == "feedin"
        ):  # change into negative value if this is a feedin sink
            sink["opex_var"].update({"value": [-i for i in sink["opex_var"]["value"]]})
    else:
        if asset_name[-6:] == "feedin":
            value = -price["value"]
        else:
            value = price["value"]
        sink.update({"opex_var": {"value": value, "unit": price["unit"]}})

    if "capex_var" in kwargs:
        sink.update(
            {
                "capex_var": kwargs["capex_var"],
                "optimizeCap": {"value": True, "unit": "bool"},
            }
        )
    if "opex_fix" in kwargs:
        sink.update(
            {
                "opex_fix": kwargs["opex_fix"],
                "optimizeCap": {"value": True, "unit": "bool"},
            }
        )
    else:
        sink.update({"optimizeCap": {"value": False, "unit": "bool"}})

    # update dictionary
    dict_values["energyConsumption"].update({asset_name: sink})

    # If multiple input busses exist
    if isinstance(input_bus, list):
        for bus in input_bus:
            update_bus(dict_values, bus, asset_name, sink["label"])
    else:
        # add to list of assets on busses
        update_bus(dict_values, input_bus, asset_name, sink["label"])

    return


def evaluate_lifetime_costs(settings, economic_data, dict_asset):
    """

    :param settings:
    :param economic_data:
    :param dict_asset:
    :return:
    """
    if "capex_var" not in dict_asset:
        dict_asset.update({"capex_var": 0})
    if "opex_fix" not in dict_asset:
        dict_asset.update({"opex_fix": 0})

    opex_fix = dict_asset["opex_fix"]["value"]
    capex_var = dict_asset["capex_var"]["value"]
    # take average value of opex_var if it is a timeseries
    if isinstance(dict_asset["opex_var"]["value"], float) or isinstance(
        dict_asset["opex_var"]["value"], int
    ):
        opex_var = dict_asset["opex_var"]["value"]

    # if multiple busses are provided, it takes the first opex_var (corresponding to the first bus)
    # to calculate the lifetime_opex_var
    elif isinstance(dict_asset["opex_var"]["value"], list):
        first_value = dict_asset["opex_var"]["value"][0]
        if isinstance(first_value, float) or isinstance(first_value, int):
            opex_var = first_value
        else:
            opex_var = sum(first_value) / len(first_value)
    else:
        opex_var = sum(dict_asset["opex_var"]["value"]) / len(
            dict_asset["opex_var"]["value"]
        )

    dict_asset.update(
        {
            "lifetime_capex_var": {
                "value": economics.capex_from_investment(
                    capex_var,
                    dict_asset["lifetime"]["value"],
                    economic_data["project_duration"]["value"],
                    economic_data["discount_factor"]["value"],
                    economic_data["tax"]["value"],
                ),
                "unit": dict_asset["capex_var"]["unit"],
            }
        }
    )

    # Annuities of components including opex AND capex #
    dict_asset.update(
        {
            "annuity_capex_opex_var": {
                "value": economics.annuity(
                    dict_asset["lifetime_capex_var"]["value"],
                    economic_data["crf"]["value"],
                )
                + opex_fix,  # changes from opex_var
                "unit": dict_asset["lifetime_capex_var"]["unit"] + "/a",
            }
        }
    )

    dict_asset.update(
        {
            "lifetime_opex_fix": {
                "value": dict_asset["opex_fix"]["value"]
                * economic_data["annuity_factor"]["value"],
                "unit": dict_asset["opex_fix"]["unit"][:-2],
            }
        }
    )

    dict_asset.update(
        {
            "lifetime_opex_var": {
                "value": opex_var * economic_data["annuity_factor"]["value"],
                "unit": "?",
            }
        }
    )

    # Scaling annuity to timeframe
    # Updating all annuities above to annuities "for the timeframe", so that optimization is based on more adequate
    # costs. Includes project_cost_annuity, distribution_grid_cost_annuity, maingrid_extension_cost_annuity for
    # consistency eventhough these are not used in optimization.
    dict_asset.update(
        {
            "simulation_annuity": {
                "value": dict_asset["annuity_capex_opex_var"]["value"]
                / 365
                * settings["evaluated_period"]["value"],
                "unit": "currency/unit/simulation period",
            }
        }
    )

    return


# read timeseries. 2 cases are considered: Input type is related to demand or generation profiles,
# so additional values like peak, total or average must be calculated. Any other type does not need this additional info.
def receive_timeseries_from_csv(dict_values, settings, dict_asset, type, is_demand_profile=False):
    """

    :param settings:
    :param dict_asset:
    :param type:
    :return:
    """
    if type == "input" and "input" in dict_asset:
        file_name = dict_asset[type]["file_name"]
        header = dict_asset[type]["header"]
        unit = dict_asset[type]["unit"]
    elif "file_name" in dict_asset:
        # todo this input/file_name thing is a workaround and has to be improved in the future
        # if only filename is given here, then only one column can be in the csv
        file_name = dict_asset["file_name"]
        unit = dict_asset["unit"] + "/h"
    else:
        file_name = dict_asset[type]["value"]["file_name"]
        header = dict_asset[type]["value"]["header"]
        unit = dict_asset[type]["unit"]

    file_path = os.path.join(settings["path_input_folder"], TIME_SERIES, file_name)
    verify.lookup_file(file_path, dict_asset["label"])

    data_set = pd.read_csv(file_path, sep=",")

    if "file_name" in dict_asset:
        header = data_set.columns[0]

    if len(data_set.index) == settings["periods"]:
        if type == "input":
            dict_asset.update(
                {
                    "timeseries": pd.Series(
                        data_set[header].values, index=settings["time_index"]
                    )
                }
            )
        else:
            dict_asset[type]["value_info"] = dict_asset[type]["value"]
            dict_asset[type]["value"] = pd.Series(
                data_set[header].values, index=settings["time_index"]
            )

        logging.debug("Added timeseries of %s (%s).", dict_asset["label"], file_path)
    elif len(data_set.index) >= settings["periods"]:
        if type == "input":
            dict_asset.update(
                {
                    "timeseries": pd.Series(
                        data_set[header][0 : len(settings["time_index"])].values,
                        index=settings["time_index"],
                    )
                }
            )
        else:
            dict_asset[type]["value_info"] = dict_asset[type]["value"]
            dict_asset[type]["value"] = pd.Series(
                data_set[header][0 : len(settings["time_index"])].values,
                index=settings["time_index"],
            )

        logging.info(
            "Provided timeseries of %s (%s) longer than evaluated period. "
            "Excess data dropped.",
            dict_asset["label"],
            file_path,
        )

    elif len(data_set.index) <= settings["periods"]:
        logging.critical(
            "Input error! "
            "Provided timeseries of %s (%s) shorter then evaluated period. "
            "Operation terminated",
            dict_asset["label"],
            file_path,
        )
        sys.exit()

    if type == "input":
        dict_asset.update(
            {
                "timeseries_peak": {
                    "value": max(dict_asset["timeseries"]),
                    "unit": unit,
                },
                "timeseries_total": {
                    "value": sum(dict_asset["timeseries"]),
                    "unit": unit,
                },
                "timeseries_average": {
                    "value": sum(dict_asset["timeseries"])
                    / len(dict_asset["timeseries"]),
                    "unit": unit,
                },
            }
        )

        if dict_asset["optimizeCap"]["value"] == True:
            logging.debug("Normalizing timeseries of %s.", dict_asset["label"])
            dict_asset.update(
                {
                    "timeseries_normalized": dict_asset["timeseries"]
                    / dict_asset["timeseries_peak"]["value"]
                }
            )
            # just to be sure!
            if any(dict_asset["timeseries_normalized"].values) > 1:
                logging.warning(
                    "Error, %s timeseries not normalized, greater than 1.",
                    dict_asset["label"],
                )
            if any(dict_asset["timeseries_normalized"].values) < 0:
                logging.warning("Error, %s timeseries negative.", dict_asset["label"])

    # plot all timeseries that are red into simulation input
    try:
        plot_input_timeseries(dict_values, settings, dict_asset["timeseries"], dict_asset["label"], header, is_demand_profile
        )
    except:
        plot_input_timeseries(dict_values, settings, dict_asset[type]["value"], dict_asset["label"], header, is_demand_profile
        )

    # copy input files
    shutil.copy(
        file_path, os.path.join(settings["path_output_folder"], INPUTS_COPY, file_name)
    )
    logging.debug("Copied timeseries %s to output folder / inputs.", file_path)
    return

def plot_input_timeseries(dict_values,user_input, timeseries, asset_name, column_head, is_demand_profile):
    logging.info("Creating plots for asset %s's parameter %s", asset_name, column_head)
    fig, axes = plt.subplots(nrows=1, figsize=(16 / 2.54, 10 / 2.54 / 2))
    axes_mg = axes

    timeseries.plot(
        title=asset_name, ax=axes_mg, drawstyle="steps-mid",
    )
    axes_mg.set(xlabel="Time", ylabel=column_head)
    path = os.path.join(user_input["path_output_folder"],  "input_timeseries_"+ asset_name+ "_"+ column_head+ ".png")
    if is_demand_profile is True:
        dict_values[PATHS_TO_PLOTS][PLOTS_DEMANDS] += [str(path)]
    else:
        dict_values[PATHS_TO_PLOTS][PLOTS_RESOURCES] += [str(path)]
    plt.savefig(
        path,
        bbox_inches="tight",
    )

    plt.close()
    plt.clf()
    plt.cla()


def treat_multiple_flows(dict_asset, dict_values, parameter):
    """
    This function consider the case a technical parameter on the json file has a list of values because multiple
    inputs or outputs busses are considered.
    Parameters
    ----------
    dict_values:
    dictionary of current values of the asset
    parameter:
    usually efficiency. Different efficiencies will be given if an asset has multiple inputs or outputs busses,
    so a list must be considered.

    Returns
    -------

    """
    updated_values = []
    values_info = (
        []
    )  # filenames and headers will be stored to allow keeping track of the timeseries generation
    for element in dict_asset[parameter]["value"]:
        if isinstance(element, dict):
            updated_values.append(
                get_timeseries_multiple_flows(
                    dict_values["simulation_settings"],
                    dict_asset,
                    element["file_name"],
                    element["header"],
                )
            )
            values_info.append(element)
        else:
            updated_values.append(element)
    dict_asset[parameter]["value"] = updated_values
    if len(values_info) > 0:
        dict_asset[parameter].update({"values_info": values_info})

    return


# reads timeseries specifically when the need comes from a multiple or output busses situation
# returns the timeseries. Does not update any dictionary
def get_timeseries_multiple_flows(settings, dict_asset, file_name, header):
    """

    Parameters
    ----------
    dict_asset:
    dictionary of the asset
    file_name:
    name of the file to read the time series
    header:
    name of the column where the timeseries is provided

    Returns
    -------

    """
    file_path = os.path.join(settings["path_input_folder"], TIME_SERIES, file_name)
    verify.lookup_file(file_path, dict_asset["label"])

    data_set = pd.read_csv(file_path, sep=",")
    if len(data_set.index) == settings["periods"]:
        return pd.Series(data_set[header].values, index=settings["time_index"])
    elif len(data_set.index) >= settings["periods"]:
        return pd.Series(
            data_set[header][0 : len(settings["time_index"])].values,
            index=settings["time_index"],
        )
    elif len(data_set.index) <= settings["periods"]:
        logging.critical(
            "Input error! "
            "Provided timeseries of %s (%s) shorter then evaluated period. "
            "Operation terminated",
            dict_asset["label"],
            file_path,
        )
        sys.exit()


def add_maximum_cap(dict_values, group, asset, subasset=None):
    """
    Checks if maximumCap is in the csv file and if not, adds it to the dict

    Parameters
    ----------
    dict_values: dict
        dictionary of all assets
    asset: str
        asset name
    subasset: str
        subasset name

    Returns
    -------

    """
    if subasset is None:
        dict = dict_values[group][asset]
    else:
        dict = dict_values[group][asset][subasset]
    if "maximumCap" in dict:
        # check if maximumCap is greater that installedCap
        if dict["maximumCap"]["value"] is not None:
            if dict["maximumCap"]["value"] < dict["installedCap"]["value"]:

                logging.warning(
                    f"The stated maximumCap in {group} {asset} is smaller than the "
                    "installedCap. Please enter a greater maximumCap."
                    "For this simulation, the maximumCap will be "
                    "disregarded and not be used in the simulation"
                )
                dict["maximumCap"]["value"] = None
            # check if maximumCao is 0
            elif dict["maximumCap"]["value"] == 0:
                logging.warning(
                    f"The stated maximumCap of zero in {group} {asset} is invalid."
                    "For this simulation, the maximumCap will be "
                    "disregarded and not be used in the simulation."
                )
                dict["maximumCap"]["value"] = None
    else:
        dict.update({"maximumCap": {"value": None, "unit": dict["unit"]}})
