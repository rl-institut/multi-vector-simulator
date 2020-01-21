import logging
import oemof.solph as solph
import pprint as pp


class call_component:
    def transformer(model, dict_asset, **kwargs):
        helpers.check_optimize_cap(
            model,
            dict_asset,
            func_constant=define_oemof_component.transformer_constant_efficiency_fix,
            func_optimize=define_oemof_component.transformer_constant_efficiency_optimize,
            **kwargs
        )
        return

    def storage(model, dict_asset, **kwargs):
        helpers.check_optimize_cap(
            model,
            dict_asset,
            func_constant=define_oemof_component.storage_fix,
            func_optimize=define_oemof_component.storage_optimize,
            **kwargs
        )
        return

    def sink(model, dict_asset, **kwargs):
        if "timeseries" in dict_asset:
            define_oemof_component.sink_non_dispatchable(model, dict_asset, **kwargs)
        else:
            define_oemof_component.sink_dispatchable(model, dict_asset, **kwargs)
        return

    def source(model, dict_asset, **kwargs):
        if "dispatchable" in dict_asset and dict_asset["dispatchable"] == True:
            helpers.check_optimize_cap(
                model,
                dict_asset,
                func_constant=define_oemof_component.source_dispatchable_fix,
                func_optimize=define_oemof_component.source_dispatchable_optimize,
                **kwargs
            )

        else:
            helpers.check_optimize_cap(
                model,
                dict_asset,
                func_constant=define_oemof_component.source_non_dispatchable_fix,
                func_optimize=define_oemof_component.source_non_dispatchable_optimize,
                **kwargs
            )
        return


class helpers:
    def check_optimize_cap(model, dict_asset, func_constant, func_optimize, **kwargs):
        """
        Determines whether or not a component should be implemented with fix capactiy or be optimized
        Might be possible to drop invest/non invest optimization in favour for invest optimization if max_capactiy
        attributes ie. are set to 0 for fix (but less beautiful, and in case of generator even blocks nonconvex opt.)

        :param model: oemof energy system object
        :param dict_asset: entry in dict_values describing a specific component
        :param func_constant: function to be applied if optimization not intended
        :param func_optimize: function to be applied if optimization is intended
        :param kwargs: named dictionary with all component objects of the energy system
        :return: indirectly updated dictionary of all component objects (kwargs, initially dict_model)
        """
        if dict_asset["optimizeCap"] == False:
            func_constant(model, dict_asset, **kwargs)
            logging.debug(
                "Defined asset %s as %s (fix capacity)",
                dict_asset["label"],
                dict_asset["type_oemof"],
            )

        elif dict_asset["optimizeCap"] == True:
            func_optimize(model, dict_asset, **kwargs)
            logging.debug(
                "Defined asset %s as %s (to be optimized)",
                dict_asset["label"],
                dict_asset["type_oemof"],
            )
        else:
            logging.warning(
                "Input error! " '"optimize_cap" of asset %s not True/False.',
                dict_asset["label"],
            )
        return


class define_oemof_component:
    def bus(model, name, **kwargs):
        logging.debug("Added: Bus %s", name)
        bus = solph.Bus(label=name)
        kwargs["busses"].update({name: bus})
        model.add(bus)
        return

    def transformer_constant_efficiency_fix(model, dict_asset, **kwargs):
        """
        Defines a transformer with constant efficiency, with multiple or single input or output busses, and with fixed capacity
        Parameters
        ----------
        dict_asset:
        dictionary of the asset
        kwargs:
        other parameters, basically the busses components

        Returns
        -------

        """
        # check if the transformer has multiple input or multiple outpus busses
        if isinstance(dict_asset["input_bus_name"], list) or isinstance(
            dict_asset["output_bus_name"], list
        ):
            if isinstance(dict_asset["input_bus_name"], list):
                inputs = {}
                index = 0
                for bus in dict_asset["input_bus_name"]:
                    variable_costs = dict_asset["opex_var"]["value"][index]
                    inputs[kwargs["busses"][bus]] = solph.Flow(
                        nominal_value=dict_asset["installedCap"]["value"],
                        variable_costs=variable_costs,
                    )
                    index += 1
                outputs = {
                    kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow()
                }
                efficiencies = {}
                for i in range(len(dict_asset["efficiency"]["value"])):
                    efficiencies[kwargs["busses"][dict_asset["input_bus_name"][i]]] = (
                        1 / dict_asset["efficiency"]["value"][i]
                    )

            else:
                inputs = {kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow()}
                outputs = {}
                index = 0
                for bus in dict_asset["output_bus_name"]:
                    variable_costs = dict_asset["opex_var"]["value"][index]
                    outputs[kwargs["busses"][bus]] = solph.Flow(
                        nominal_value=dict_asset["installedCap"]["value"],
                        variable_costs=variable_costs,
                    )
                    index += 1
                efficiencies = {}
                for i in range(len(dict_asset["efficiency"]["value"])):
                    efficiencies[
                        kwargs["busses"][dict_asset["output_bus_name"][i]]
                    ] = dict_asset["efficiency"]["value"][i]

        else:
            inputs = {kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow()}
            outputs = {
                kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                    nominal_value=dict_asset["installedCap"]["value"],
                    variable_costs=dict_asset["opex_var"]["value"],
                )
            }
            efficiencies = {
                kwargs["busses"][dict_asset["output_bus_name"]]: dict_asset[
                    "efficiency"
                ]["value"]
            }

        transformer = solph.Transformer(
            label=dict_asset["label"],
            inputs=inputs,
            outputs=outputs,
            conversion_factors=efficiencies,
        )

        model.add(transformer)
        kwargs["transformers"].update({dict_asset["label"]: transformer})
        return

    def transformer_constant_efficiency_optimize(model, dict_asset, **kwargs):
        """
        Defines a transformer with constant efficiency, with multiple or single input or output busses, to be optimized
        Parameters
        ----------
        dict_asset:
        dictionary of the asset
        kwargs:
        other parameters, basically the busses components

        Returns
        -------

        """
        # check if the transformer has multiple input or multiple outpus busses
        # the investment object is always in the output bus
        if isinstance(dict_asset["input_bus_name"], list) or isinstance(
            dict_asset["output_bus_name"], list
        ):
            if isinstance(dict_asset["input_bus_name"], list):
                inputs = {}
                index = 0
                for bus in dict_asset["input_bus_name"]:
                    variable_costs = dict_asset["opex_var"]["value"][index]
                    inputs[kwargs["busses"][bus]] = solph.Flow(
                        existing=dict_asset["installedCap"]["value"],
                        variable_costs=variable_costs,
                    )
                    index += 1
                outputs = {
                    kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                        investment=solph.Investment(
                            ep_costs=dict_asset["simulation_annuity"]["value"]
                        ),
                        existing=dict_asset["installedCap"]["value"],
                        variable_costs=dict_asset["opex_var"]["value"],
                    )
                }
                efficiencies = {}
                for i in range(len(dict_asset["efficiency"]["value"])):
                    efficiencies[
                        kwargs["busses"][dict_asset["input_bus_name"][i]]
                    ] = 1 / (dict_asset["efficiency"]["value"][i])

            else:
                inputs = {kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow()}
                outputs = {}
                index = 0
                for bus in dict_asset["output_bus_name"]:
                    variable_costs = dict_asset["opex_var"]["value"][index]
                    outputs[kwargs["busses"][bus]] = solph.Flow(
                        investment=solph.Investment(
                            ep_costs=dict_asset["simulation_annuity"]["value"]
                        ),
                        existing=dict_asset["installedCap"]["value"],
                        variable_costs=variable_costs,
                    )
                    index += 1
                efficiencies = {}
                for i in range(len(dict_asset["efficiency"]["value"])):
                    efficiencies[
                        kwargs["busses"][dict_asset["output_bus_name"][i]]
                    ] = dict_asset["efficiency"]["value"][i]

        else:
            inputs = {kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow()}
            outputs = {
                kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                    investment=solph.Investment(
                        ep_costs=dict_asset["simulation_annuity"]["value"]
                    ),
                    existing=dict_asset["installedCap"]["value"],
                    variable_costs=dict_asset["opex_var"]["value"],
                )
            }
            efficiencies = {
                kwargs["busses"][dict_asset["output_bus_name"]]: dict_asset[
                    "efficiency"
                ]["value"]
            }

        transformer = solph.Transformer(
            label=dict_asset["label"],
            inputs=inputs,
            outputs=outputs,
            conversion_factors=efficiencies,
        )

        model.add(transformer)
        kwargs["transformers"].update({dict_asset["label"]: transformer})
        return

    def storage_fix(model, dict_asset, **kwargs):
        storage = solph.components.GenericStorage(
            label=dict_asset["label"],
            nominal_storage_capacity=dict_asset["capacity"]["installedCap"]["value"],
            inputs={
                kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow(
                    nominal_value=dict_asset["discharging_power"]["installedCap"][
                        "value"
                    ],  # limited through installed capacity, NOT c-rate
                    variable_costs=dict_asset["charging_power"]["opex_var"]["value"],
                )
            },  # maximum charge possible in one timestep
            outputs={
                kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                    nominal_value=dict_asset["discharging_power"]["installedCap"][
                        "value"
                    ],  # limited through installed capacity, NOT c-rate #todo actually, if we only have a lithium battery... crate should suffice? i mean, with crate fixed AND fixed power, this is defined two times
                    variable_costs=dict_asset["discharging_power"]["opex_var"]["value"],
                )
            },  # maximum discharge possible in one timestep
            loss_rate=dict_asset["capacity"]["efficiency"][
                "value"
            ],  # from timestep to timestep
            min_storage_level=dict_asset["capacity"]["soc_min"]["value"],
            max_storage_level=dict_asset["capacity"]["soc_max"]["value"],
            initial_storage_level=dict_asset["capacity"]["soc_initial"][
                "value"
            ],  # in terms of SOC
            inflow_conversion_factor=dict_asset["charging_power"]["efficiency"][
                "value"
            ],  # storing efficiency
            outflow_conversion_factor=dict_asset["discharging_power"]["efficiency"][
                "value"
            ],
        )  # efficiency of discharge
        model.add(storage)
        kwargs["storages"].update({dict_asset["label"]: storage})
        return

    def storage_optimize(model, dict_asset, **kwargs):
        storage = solph.components.GenericStorage(
            label=dict_asset["label"],
            existing=dict_asset["capacity"]["installedCap"]["value"],
            investment=solph.Investment(
                ep_costs=dict_asset["capacity"]["simulation_annuity"]["value"]
            ),
            inputs={
                kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow(
                    existing=dict_asset["charging_power"]["installedCap"]["value"],
                    investment=solph.Investment(
                        ep_costs=dict_asset["charging_power"]["simulation_annuity"][
                            "value"
                        ]
                    ),
                    variable_costs=dict_asset["charging_power"]["opex_var"]["value"],
                )
            },  # maximum charge power
            outputs={
                kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                    existing=dict_asset["discharging_power"]["installedCap"]["value"],
                    investment=solph.Investment(
                        ep_costs=dict_asset["discharging_power"]["simulation_annuity"][
                            "value"
                        ]
                    ),
                    variable_costs=dict_asset["discharging_power"]["opex_var"]["value"],
                )
            },  # maximum discharge power
            loss_rate=dict_asset["capacity"]["efficiency"][
                "value"
            ],  # from timestep to timestep
            min_storage_level=dict_asset["capacity"]["soc_min"]["value"],
            max_storage_level=dict_asset["capacity"]["soc_max"]["value"],
            initial_storage_level=dict_asset["capacity"]["soc_initial"][
                "value"
            ],  # in terms of SOC #implication: balanced = True, ie. start=end
            inflow_conversion_factor=dict_asset["charging_power"]["efficiency"][
                "value"
            ],  # storing efficiency
            outflow_conversion_factor=dict_asset["discharging_power"]["efficiency"][
                "value"
            ],  # efficiency of discharge
            invest_relation_input_capacity=dict_asset["charging_power"]["crate"][
                "value"
            ],
            # storage can be charged with invest_relation_output_capacity*capacity in one timeperiod
            invest_relation_output_capacity=dict_asset["discharging_power"]["crate"][
                "value"
            ]
            # storage can be emptied with invest_relation_output_capacity*capacity in one timeperiod
        )
        model.add(storage)
        kwargs["storages"].update({dict_asset["label"]: storage})
        return

    def source_non_dispatchable_fix(model, dict_asset, **kwargs):
        # check if the source has multiple output busses
        if isinstance(dict_asset["output_bus_name"], list):
            outputs = {}
            index = 0
            for bus in dict_asset["output_bus_name"]:
                outputs[kwargs["busses"][bus]] = solph.Flow(
                    label=dict_asset["label"],
                    actual_value=dict_asset["timeseries"],
                    fixed=True,
                    nominal_value=dict_asset["installedCap"]["value"],
                    variable_costs=dict_asset["opex_var"][0],
                )
                index += 1
        else:
            outputs = {
                kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                    label=dict_asset["label"],
                    actual_value=dict_asset["timeseries"],
                    fixed=True,
                    nominal_value=dict_asset["installedCap"]["value"],
                    variable_costs=dict_asset["opex_var"],
                )
            }

        source_non_dispatchable = solph.Source(
            label=dict_asset["label"], outputs=outputs
        )

        model.add(source_non_dispatchable)
        kwargs["sources"].update({dict_asset["label"]: source_non_dispatchable})
        return

    def source_non_dispatchable_optimize(model, dict_asset, **kwargs):
        # check if the source has multiple output busses
        if isinstance(dict_asset["output_bus_name"], list):
            outputs = {}
            index = 0
            for bus in dict_asset["output_bus_name"]:
                outputs[kwargs["busses"][bus]] = solph.Flow(
                    label=dict_asset["label"],
                    actual_value=dict_asset["timeseries_normalized"],
                    fixed=True,
                    existing=dict_asset["installedCap"]["value"],
                    investment=solph.Investment(
                        ep_costs=dict_asset["simulation_annuity"]["value"]
                        / dict_asset["timeseries_peak"]["value"]
                    ),
                    variable_costs=dict_asset["opex_var"]["value"][0]
                    / dict_asset["timeseries_peak"]["value"],
                )
                index += 1
        else:
            outputs = {
                kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                    label=dict_asset["label"],
                    actual_value=dict_asset["timeseries_normalized"],
                    fixed=True,
                    existing=dict_asset["installedCap"]["value"],
                    investment=solph.Investment(
                        ep_costs=dict_asset["simulation_annuity"]["value"]
                        / dict_asset["timeseries_peak"]["value"]
                    ),
                    variable_costs=dict_asset["opex_var"]["value"]
                    / dict_asset["timeseries_peak"]["value"],
                )
            }

        source_non_dispatchable = solph.Source(
            label=dict_asset["label"], outputs=outputs
        )

        model.add(source_non_dispatchable)
        kwargs["sources"].update({dict_asset["label"]: source_non_dispatchable})
        return

    def source_dispatchable_optimize(model, dict_asset, **kwargs):
        if "timeseries_normalized" in dict_asset:
            # check if the source has multiple output busses
            if isinstance(dict_asset["output_bus_name"], list):
                outputs = {}
                index = 0
                for bus in dict_asset["output_bus_name"]:
                    outputs[kwargs["busses"][bus]] = solph.Flow(
                        label=dict_asset["label"],
                        max=dict_asset["timeseries_normalized"],
                        investment=solph.Investment(
                            ep_costs=dict_asset["simulation_annuity"]["value"]
                            / dict_asset["timeseries_peak"]["value"]
                        ),
                        variable_costs=dict_asset["opex_var"]["value"][0]
                        / dict_asset["timeseries_peak"]["value"],
                    )
                    index += 1
            else:
                outputs = {
                    kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                        label=dict_asset["label"],
                        max=dict_asset["timeseries_normalized"],
                        investment=solph.Investment(
                            ep_costs=dict_asset["simulation_annuity"]["value"]
                            / dict_asset["timeseries_peak"]["value"]
                        ),
                        variable_costs=dict_asset["opex_var"]["value"]
                        / dict_asset["timeseries_peak"]["value"],
                    )
                }

            source_dispatchable = solph.Source(
                label=dict_asset["label"], outputs=outputs,
            )
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
                        label=dict_asset["label"],
                        investment=solph.Investment(
                            ep_costs=dict_asset["simulation_annuity"]["value"]
                        ),
                        variable_costs=dict_asset["opex_var"]["value"][index],
                    )
                    index += 1
            else:
                outputs = {
                    kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                        label=dict_asset["label"],
                        investment=solph.Investment(
                            ep_costs=dict_asset["simulation_annuity"]["value"]
                        ),
                        variable_costs=dict_asset["opex_var"]["value"],
                    )
                }

            source_dispatchable = solph.Source(
                label=dict_asset["label"], outputs=outputs,
            )
        model.add(source_dispatchable)
        kwargs["sources"].update({dict_asset["label"]: source_dispatchable})
        logging.info("Added: Dispatchable source %s", dict_asset["label"])
        return

    def source_dispatchable_fix(model, dict_asset, **kwargs):
        # todo 'timeseries_normalized' is correct term?
        if "timeseries_normalized" in dict_asset:
            # check if the source has multiple output busses
            if isinstance(dict_asset["output_bus_name"], list):
                outputs = {}
                index = 0
                for bus in dict_asset["output_bus_name"]:
                    outputs[kwargs["busses"][bus]] = solph.Flow(
                        label=dict_asset["label"],
                        max=dict_asset["timeseries_normalized"],
                        existing=dict_asset["installedCap"]["value"],
                        variable_costs=dict_asset["opex_var"]["value"][index],
                    )
                    index += 1
            else:
                outputs = {
                    kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                        label=dict_asset["label"],
                        max=dict_asset["timeseries_normalized"],
                        existing=dict_asset["installedCap"]["value"],
                        variable_costs=dict_asset["opex_var"]["value"],
                    )
                }
            source_dispatchable = solph.Source(
                label=dict_asset["label"], outputs=outputs,
            )
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
                        label=dict_asset["label"],
                        existing=dict_asset["installedCap"]["value"],
                        variable_costs=dict_asset["opex_var"]["value"][index],
                    )
                    index += 1
            else:
                outputs = {
                    kwargs["busses"][dict_asset["output_bus_name"]]: solph.Flow(
                        label=dict_asset["label"],
                        existing=dict_asset["installedCap"]["value"],
                        variable_costs=dict_asset["opex_var"]["value"],
                    )
                }
            source_dispatchable = solph.Source(
                label=dict_asset["label"], outputs=outputs,
            )
        model.add(source_dispatchable)
        kwargs["sources"].update({dict_asset["label"]: source_dispatchable})
        logging.info("Added: Dispatchable source %s", dict_asset["label"])
        return

    def sink_dispatchable(model, dict_asset, **kwargs):
        # check if the sink has multiple input busses
        if isinstance(dict_asset["input_bus_name"], list):
            inputs = {}
            index = 0
            for bus in dict_asset["input_bus_name"]:
                inputs[kwargs["busses"][bus]] = solph.Flow(
                    label=dict_asset["label"],
                    variable_costs=dict_asset["opex_var"]["value"][index],
                )
                index += 1
        else:
            inputs = {
                kwargs["busses"][dict_asset["input_bus_name"]]: solph.Flow(
                    label=dict_asset["label"],
                    variable_costs=dict_asset["opex_var"]["value"],
                )
            }

        # create and add excess electricity sink to micro_grid_system - variable
        sink_dispatchable = solph.Sink(label=dict_asset["label"], inputs=inputs,)
        model.add(sink_dispatchable)
        kwargs["sinks"].update({dict_asset["label"]: sink_dispatchable})
        logging.info("Added: Dispatchable sink %s", dict_asset["label"])
        return

    def sink_non_dispatchable(model, dict_asset, **kwargs):
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
        sink_demand = solph.Sink(label=dict_asset["label"], inputs=inputs,)
        model.add(sink_demand)
        kwargs["sinks"].update({dict_asset["label"]: sink_demand})
        return
