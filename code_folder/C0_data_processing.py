try:
    from .C1_verification import verify
    from .C2_economic_functions import economics
    from .F0_output import helpers as output
except ModuleNotFoundError:
    from code_folder.C1_verification import verify
    from code_folder.C2_economic_functions import economics
    from code_folder.F0_output import helpers as output

import logging
import sys, shutil
import pandas as pd

from copy import deepcopy


class data_processing:
    def all(dict_values):
        data_processing.simulation_settings(dict_values["simulation_settings"])

        ## Verify inputs
        # todo check whether input values can be true
        # verify.check_input_values(dict_values)
        # todo Check, whether files (demand, generation) are existing

        # Adds costs to each asset and sub-asset
        data_processing.process_all_assets(dict_values)

        output.store_as_json(dict_values, "json_input_processed")
        return

    def simulation_settings(simulation_settings):
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

    def process_all_assets(dict_values):
        # read timeseries with filename provided for technical parameters (efficiency and minimum and maximum storage level)

        for asset in dict_values["energyConversion"]:
            dict_asset = dict_values["energyConversion"][asset]
            # in case there is only one parameter provided (input bus and one output bus)
            if isinstance(dict_asset["efficiency"]["value"], dict):
                helpers.receive_timeseries_from_csv(
                    dict_values["simulation_settings"], dict_asset, "efficiency"
                )
            # in case there is more than one parameter provided (either (A) n input busses and 1 output bus or (B) 1 input bus and n output busses)
            # dictionaries with filenames and headers will be replaced by timeseries, scalars will be mantained
            elif isinstance(dict_asset["efficiency"]["value"], list):
                updated_values = []
                values_info = (
                    []
                )  # filenames and headers will be stored to allow keeping track of the timeseries generation
                for element in dict_asset["efficiency"]["value"]:
                    if isinstance(element, dict):
                        updated_values.append(
                            helpers.get_timeseries_multiple_flows(
                                dict_values["simulation_settings"],
                                dict_asset,
                                element["file_name"],
                                element["header"],
                            )
                        )
                        values_info.append(element)
                    else:
                        updated_values.append(element)
                dict_asset["efficiency"]["value"] = updated_values
                if len(values_info) > 0:
                    dict_asset["efficiency"].update({"values_info": values_info})

        # same distinction of parameters provided with dictionaries (one input and one output) or list (multiple).
        # The can in turn be scalars, mantained, or timeseries
        for sector in dict_values["energyStorage"]:
            for asset in dict_values["energyStorage"][sector]:
                for component in ["capacity", "charging_power", "discharging_power"]:
                    dict_asset = dict_values["energyStorage"][sector][asset][component]
                    for parameter in ["efficiency", "soc_min", "soc_max"]:
                        if parameter in dict_asset and isinstance(
                            dict_asset[parameter]["value"], dict
                        ):
                            helpers.receive_timeseries_from_csv(
                                dict_values["simulation_settings"],
                                dict_asset,
                                parameter,
                            )
                        elif parameter in dict_asset and isinstance(
                            dict_asset[parameter]["value"], list
                        ):
                            updated_values = []
                            values_info = (
                                []
                            )  # filenames and headers will be stored to allow keeping track of the timeseries generation
                            for element in dict_asset[parameter]["value"]:
                                if isinstance(element, dict):
                                    updated_values.append(
                                        helpers.get_timeseries_multiple_flows(
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
                                dict_asset[parameter].update(
                                    {"values_info": values_info}
                                )

        # Calculate annuitiy factor
        dict_values["economic_data"].update(
            {
                "annuity_factor": {
                    "value": economics.annuity_factor(
                        dict_values["economic_data"]["project_duration"]["value"],
                        dict_values["economic_data"]["discount_factor"]["value"],
                    ),
                    "unit": "?",
                }
            }
        )
        # Calculate crf
        dict_values["economic_data"].update(
            {
                "crf": {
                    "value": economics.crf(
                        dict_values["economic_data"]["project_duration"]["value"],
                        dict_values["economic_data"]["discount_factor"]["value"],
                    ),
                    "unit": "?",
                }
            }
        )

        # defines dict_values['energyBusses'] for later reference
        helpers.define_busses(dict_values)

        # Define all excess sinks for sectors
        for sector in dict_values["project_data"]["sectors"]:
            helpers.define_sink(
                dict_values,
                dict_values["project_data"]["sectors"][sector] + " excess",
                {"value": 0, "unit": "currency/kWh"},
                dict_values["project_data"]["sectors"][sector],
            )
            logging.debug(
                "Created excess sink for sector %s",
                dict_values["project_data"]["sectors"][sector],
            )

        # add sources and sinks depending on items in energy providers as pre-processing
        for sector in dict_values["energyProviders"]:
            for dso in dict_values["energyProviders"][sector]:
                helpers.define_dso_sinks_and_sources(dict_values, sector, dso)

        # Add lifetime capex (incl. replacement costs), calculate annuity (incl. om), and simulation annuity to each asset
        for asset in dict_values["energyConversion"]:
            helpers.define_missing_cost_data(
                dict_values, dict_values["energyConversion"][asset]
            )
            helpers.evaluate_lifetime_costs(
                dict_values["simulation_settings"],
                dict_values["economic_data"],
                dict_values["energyConversion"][asset],
            )

        for sector in dict_values["energyStorage"]:
            helpers.update_busses_in_out_direction(
                dict_values, dict_values["energyStorage"][sector]
            )
            for asset in dict_values["energyStorage"][sector]:
                for subasset in ["capacity", "charging_power", "discharging_power"]:
                    helpers.define_missing_cost_data(
                        dict_values,
                        dict_values["energyStorage"][sector][asset][subasset],
                    )
                    helpers.evaluate_lifetime_costs(
                        dict_values["simulation_settings"],
                        dict_values["economic_data"],
                        dict_values["energyStorage"][sector][asset][subasset],
                    )
                dict_values["energyStorage"][sector][asset].update(
                    {
                        "input_bus_name": helpers.bus_suffix(
                            dict_values["energyStorage"][sector][asset][
                                "inflow_direction"
                            ]
                        )
                    }
                )
                dict_values["energyStorage"][sector][asset].update(
                    {
                        "output_bus_name": helpers.bus_suffix(
                            dict_values["energyStorage"][sector][asset][
                                "outflow_direction"
                            ]
                        )
                    }
                )

        # Add lifetime capex (incl. replacement costs), calculate annuity (incl. om), and simulation annuity to each asset
        list_asset_groups = [
            "fixCost",
            "energyConsumption",
            "energyProduction",
            "energyProviders",
        ]
        for group in list_asset_groups:
            for sector in dict_values[group]:
                if group not in ["fixCost", "energyProviders"]:
                    # populated dict_values['energyBusses'] with assets
                    helpers.update_busses_in_out_direction(
                        dict_values, dict_values[group][sector]
                    )

                for asset in dict_values[group][sector]:
                    helpers.define_missing_cost_data(
                        dict_values, dict_values[group][sector][asset]
                    )
                    helpers.evaluate_lifetime_costs(
                        dict_values["simulation_settings"],
                        dict_values["economic_data"],
                        dict_values[group][sector][asset],
                    )
                    if (
                        group == "energyConsumption"
                        and "input_bus_name" not in dict_values[group][sector][asset]
                    ):
                        dict_values[group][sector][asset].update(
                            {"input_bus_name": helpers.bus_suffix(sector)}
                        )

                    if (
                        group == "energyProduction"
                        and "output_bus_name" not in dict_values[group][sector][asset]
                    ):
                        dict_values[group][sector][asset].update(
                            {"output_bus_name": helpers.bus_suffix(sector)}
                        )

                    if (
                        group in ["energyConsumption", "energyProduction"]
                        and "input" in dict_values[group][sector][asset]
                    ):
                        helpers.receive_timeseries_from_csv(
                            dict_values["simulation_settings"],
                            dict_values[group][sector][asset],
                            "input",
                        )

        logging.info("Processed cost data and added economic values.")
        return


class helpers:
    def define_missing_cost_data(dict_values, dict_asset):

        # read timeseries with filename provided for variable costs.
        # if multiple opex_var or capex_var are given for multiple busses, it checks if any value is a timeseries
        for parameter in ["capex_var", "opex_var"]:
            if parameter in dict_asset:
                if isinstance(dict_asset[parameter]["value"], dict):
                    helpers.receive_timeseries_from_csv(
                        dict_values["simulation_settings"], dict_asset, parameter
                    )
                elif isinstance(dict_asset[parameter]["value"], list):
                    updated_values = []
                    values_info = []
                    for element in dict_asset[parameter]["value"]:
                        if isinstance(element, dict):
                            updated_values.append(
                                helpers.get_timeseries_multiple_flows(
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

        economic_data = dict_values["economic_data"]

        basic_costs = {
            "installedCap": {"value": 0, "unit": "currency"},
            "optimizeCap": False,
            "unit": "?",
            "installedCap": {"value": 0.0, "unit": "kW"},
            "capex_fix": {"value": 0, "unit": "currency"},
            "capex_var": {"value": 0, "unit": "currency/unit"},
            "opex_fix": {"value": 0, "unit": "currency/year"},
            "opex_var": {"value": 0, "unit": "currency/unit/year"},
            "lifetime": {
                "value": economic_data["project_duration"]["value"],
                "unit": "year",
            },
        }

        # checks that an asset has all cost parameters needed for evaluation. Adds standard values.
        str = ""
        for cost in basic_costs:
            if cost not in dict_asset:
                dict_asset.update({cost: basic_costs[cost]})
                str = str + " " + cost

        if len(str) > 1:
            logging.debug("Added basic costs to asset %s: %s", dict_asset["label"], str)
        return

    def define_busses(dict_values):
        # create new group of assets: busses
        dict_values.update({"energyBusses": {}})

        # defines energy busses of sectors
        for sector in dict_values["project_data"]["sectors"]:
            dict_values["energyBusses"].update(
                {helpers.bus_suffix(dict_values["project_data"]["sectors"][sector]): {}}
            )

        # defines busses accessed by conversion assets
        helpers.update_busses_in_out_direction(
            dict_values, dict_values["energyConversion"]
        )
        return

    def update_busses_in_out_direction(dict_values, asset_group, **kwargs):
        # checks for all assets of an group
        for asset in asset_group:
            # the bus that is connected to the inflow
            if "inflow_direction" in asset_group[asset]:
                bus = asset_group[asset]["inflow_direction"]
                if isinstance(bus, list):
                    bus_list = []
                    for subbus in bus:
                        bus_list.append(helpers.bus_suffix(subbus))
                        helpers.update_bus(
                            dict_values, subbus, asset, asset_group[asset]["label"]
                        )
                    asset_group[asset].update({"input_bus_name": bus_list})
                else:
                    asset_group[asset].update(
                        {"input_bus_name": helpers.bus_suffix(bus)}
                    )
                    helpers.update_bus(
                        dict_values, bus, asset, asset_group[asset]["label"]
                    )
            # the bus that is connected to the outflow
            if "outflow_direction" in asset_group[asset]:
                bus = asset_group[asset]["outflow_direction"]
                if isinstance(bus, list):
                    bus_list = []
                    for subbus in bus:
                        bus_list.append(helpers.bus_suffix(subbus))
                        helpers.update_bus(
                            dict_values, subbus, asset, asset_group[asset]["label"]
                        )
                    asset_group[asset].update({"output_bus_name": bus_list})
                else:
                    asset_group[asset].update(
                        {"output_bus_name": helpers.bus_suffix(bus)}
                    )
                    helpers.update_bus(
                        dict_values, bus, asset, asset_group[asset]["label"]
                    )
        return

    def bus_suffix(bus):
        bus_label = bus + " bus"
        return bus_label

    def update_bus(dict_values, bus, asset, asset_label):
        bus_label = helpers.bus_suffix(bus)
        if bus_label not in dict_values["energyBusses"]:
            # add bus to asset group energyBusses
            dict_values["energyBusses"].update({bus_label: {}})

        # Asset should added to respective bus
        dict_values["energyBusses"][bus_label].update({asset: asset_label})
        logging.debug("Added asset %s to bus %s", asset_label, bus_label)
        return

    def define_dso_sinks_and_sources(dict_values, sector, dso):
        # define to shorten code
        number_of_pricing_periods = dict_values["energyProviders"][sector][dso][
            "peak_demand_pricing_period"
        ]["value"]
        # defines the evaluation period
        months_in_a_period = 12 / number_of_pricing_periods
        logging.info(
            "Peak demand pricing is taking place %s times per year, ie. every %s months.",
            number_of_pricing_periods,
            months_in_a_period,
        )
        dict_asset = dict_values["energyProviders"][sector][dso]
        if isinstance(dict_asset["peak_demand_pricing"]["value"], dict):
            helpers.receive_timeseries_from_csv(
                dict_values["simulation_settings"], dict_asset, "peak_demand_pricing"
            )

        peak_demand_pricing = dict_values["energyProviders"][sector][dso][
            "peak_demand_pricing"
        ]["value"]
        if isinstance(peak_demand_pricing, float) or isinstance(
            peak_demand_pricing, int
        ):
            logging.debug(
                "The peak demand pricing price of %s %s is set as capex_var of the sources of grid energy.",
                peak_demand_pricing,
                dict_values["economic_data"]["currency"],
            )
        else:
            logging.debug(
                "The peak demand pricing price of %s %s is set as capex_var of the sources of grid energy.",
                sum(peak_demand_pricing) / len(peak_demand_pricing),
                dict_values["economic_data"]["currency"],
            )

        peak_demand_pricing = {
            "value": dict_values["energyProviders"][sector][dso]["peak_demand_pricing"][
                "value"
            ],
            "unit": "currency/kWpeak",
        }

        if number_of_pricing_periods == 1:
            # if only one period: avoid suffix dso+'_consumption_period_1"
            timeseries = pd.Series(
                1, index=dict_values["simulation_settings"]["time_index"]
            )
            helpers.define_source(
                dict_values,
                dso + "_consumption",
                dict_values["energyProviders"][sector][dso]["energy_price"],
                dict_values["energyProviders"][sector][dso]["outflow_direction"],
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
                    + pd.DateOffset(
                        months=pricing_period * months_in_a_period, hours=-1
                    ),
                    freq=str(dict_values["simulation_settings"]["timestep"]["value"])
                    + "min",
                )

                timeseries = timeseries.add(
                    pd.Series(1, index=time_period), fill_value=0
                )
                helpers.define_source(
                    dict_values,
                    dso + "_consumption_period_" + str(pricing_period),
                    dict_values["energyProviders"][sector][dso]["energy_price"],
                    dict_values["energyProviders"][sector][dso]["outflow_direction"],
                    timeseries,
                    opex_fix=peak_demand_pricing,
                )

        helpers.define_sink(
            dict_values,
            dso + "_feedin",
            dict_values["energyProviders"][sector][dso]["feedin_tariff"],
            dict_values["energyProviders"][sector][dso]["inflow_direction"],
            capex_var={"value": 0, "unit": "currency/kW"},
        )

        return

    def define_source(dict_values, asset_name, price, output_bus, timeseries, **kwargs):
        # create name of bus. Check if multiple busses are given
        if isinstance(output_bus, list):
            output_bus_name = []
            for bus in output_bus:
                output_bus_name.append(helpers.bus_suffix(bus))
        else:
            output_bus_name = helpers.bus_suffix(output_bus)

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
        # for each bus, read time series for opex_var if a file name has been provided in energy price
        if isinstance(price["value"], list):
            source.update({"opex_var": {"value": [], "unit": price["unit"]}})
            values_info = []
            for element in price["value"]:
                if isinstance(element, dict):
                    source["opex_var"]["value"].append(
                        helpers.get_timeseries_multiple_flows(
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
            helpers.receive_timeseries_from_csv(
                dict_values["simulation_settings"], source, "opex_var"
            )
        else:
            source.update(
                {"opex_var": {"value": price["value"], "unit": price["unit"]}}
            )

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
                    "optimizeCap": True,
                    "timeseries_peak": {"value": max(timeseries), "unit": "kW"},
                    # todo if we have normalized timeseries hiere, the capex/opex (simulation) have changed, too
                    "timeseries_normalized": timeseries / max(timeseries),
                }
            )
            logging.warning(
                "Attention! %s is created, with a price of %s."
                "If this is DSO supply, this could be improved. Please refer to Issue #23.",
                source["label"],
                source["opex_var"]["value"],
            )
        else:
            source.update({"optimizeCap": False})

        # create new input bus if non-existent before. Check if multiple busses are provided
        if isinstance(output_bus, list):
            for bus in output_bus:
                if bus not in dict_values["energyProduction"].keys():
                    dict_values["energyProduction"].update({bus: {}})
                dict_values["energyProduction"][bus].update({asset_name: source})
                helpers.update_bus(dict_values, bus, asset_name, source["label"])
        else:
            if output_bus not in dict_values["energyProduction"].keys():
                dict_values["energyProduction"].update({output_bus: {}})
            # update dictionary
            dict_values["energyProduction"][output_bus].update({asset_name: source})
            # add to list of assets on busses
            helpers.update_bus(dict_values, output_bus, asset_name, source["label"])

        return

    def define_sink(dict_values, asset_name, price, input_bus, **kwargs):
        # create name of bus. Check if multiple busses are given
        if isinstance(input_bus, list):
            input_bus_name = []
            for bus in input_bus:
                input_bus_name.append(helpers.bus_suffix(bus))
        else:
            input_bus_name = helpers.bus_suffix(input_bus)

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
                    timeseries = helpers.get_timeseries_multiple_flows(
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
            helpers.receive_timeseries_from_csv(
                dict_values["simulation_settings"], sink, "opex_var"
            )
            if (
                asset_name[-6:] == "feedin"
            ):  # change into negative value if this is a feedin sink
                sink["opex_var"].update(
                    {"value": [-i for i in sink["opex_var"]["value"]]}
                )
        else:
            if asset_name[-6:] == "feedin":
                value = -price["value"]
            else:
                value = price["value"]
            sink.update({"opex_var": {"value": value, "unit": price["unit"]}})

        if "capex_var" in kwargs:
            sink.update({"capex_var": kwargs["capex_var"], "optimizeCap": True})
        if "opex_fix" in kwargs:
            sink.update({"opex_fix": kwargs["opex_fix"], "optimizeCap": True})
        else:
            sink.update({"optimizeCap": False})

        if isinstance(input_bus, list):
            for bus in input_bus:
                if bus not in dict_values["energyConsumption"].keys():
                    dict_values["energyConsumption"].update({bus: {}})
                dict_values["energyConsumption"][bus].update({asset_name: sink})
                helpers.update_bus(dict_values, bus, asset_name, sink["label"])
        else:
            # create new input bus if non-existent before
            if input_bus not in dict_values["energyConsumption"].keys():
                dict_values["energyConsumption"].update({input_bus: {}})

            # update dictionary
            dict_values["energyConsumption"][input_bus].update({asset_name: sink})

            # add to list of assets on busses
            helpers.update_bus(dict_values, input_bus, asset_name, sink["label"])
        return

    def evaluate_lifetime_costs(settings, economic_data, dict_asset):
        if "capex_var" not in dict_asset:
            dict_asset.update({"capex_var": 0})
        if "opex_fix" not in dict_asset:
            dict_asset.update({"opex_fix": 0})

        opex_fix = dict_asset["opex_fix"]["value"]

        # take average value is capex_var or opex_var are timeseries
        if isinstance(dict_asset["capex_var"]["value"], float) or isinstance(
            dict_asset["capex_var"]["value"], int
        ):
            capex_var = dict_asset["capex_var"]["value"]
        else:
            capex_var = sum(dict_asset["capex_var"]["value"]) / len(
                dict_asset["capex_var"]["value"]
            )

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
    def receive_timeseries_from_csv(settings, dict_asset, type):
        if type == "input":
            file_name = dict_asset[type]["file_name"]
            header = dict_asset[type]["header"]
        else:
            file_name = dict_asset[type]["value"]["file_name"]
            header = dict_asset[type]["value"]["header"]
        unit = dict_asset[type]["unit"]
        file_path = settings["path_input_folder"] + file_name
        verify.lookup_file(file_path, dict_asset["label"])

        data_set = pd.read_csv(file_path, sep=";")
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

            logging.debug(
                "Added timeseries of %s (%s).", dict_asset["label"], file_path
            )
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

            if dict_asset["optimizeCap"] == True:
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
                    logging.warning(
                        "Error, %s timeseries negative.", dict_asset["label"]
                    )

        shutil.copy(file_path, settings["path_output_folder_inputs"] + file_name)
        logging.debug("Copied timeseries %s to output folder / inputs.", file_path)
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
        file_path = settings["path_input_folder"] + file_name
        verify.lookup_file(file_path, dict_asset["label"])

        data_set = pd.read_csv(file_path, sep=";")
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
