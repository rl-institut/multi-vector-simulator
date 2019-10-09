import logging
import oemof.solph as solph
import pprint as pp

class helpers():
    def check_optimize_cap(model, dict_asset, func_constant, func_optimize, **kwargs):
        '''
        Determines whether or not a component should be implemented with fix capactiy or be optimized
        Might be possible to drop invest/non invest optimization in favour for invest optimization if max_capactiy
        attributes ie. are set to 0 for fix (but less beautiful, and in case of generator even blocks nonconvex opt.)

        :param model: oemof energy system object
        :param dict_asset: entry in dict_values describing a specific component
        :param func_constant: function to be applied if optimization not intended
        :param func_optimize: function to be applied if optimization is intended
        :param kwargs: named dictionary with all component objects of the energy system
        :return: indirectly updated dictionary of all component objects (kwargs, initially dict_model)
        '''
        if dict_asset['optimize_cap']==False:
            logging.info('Added: Component %s, excluded from optimization.', dict_asset['label'])
            func_constant(model, dict_asset, **kwargs)
        elif dict_asset['optimize_cap']==True:
            logging.info('Added: Component %s, to be optimized.', dict_asset['label'])
            func_optimize(model, dict_asset, **kwargs)
        else:
            logging.warning('Input error! '
                            '"optimize_cap" of asset %s not True/False.', dict_asset['label'])
        return

class call_component:

    def utility_connection(model, dict_asset, **kwargs):
        '''
        function defining an utlity connection, including consumption from and feed in to utility grid.
        Should be adaptable to all energy sectors
        Defines a multitude of components.

        :param dict_asset: Dict entry of one asset in dict_values, here with sub-assets 'in', 'out', 'sink', 'source'
        :param kwargs: dictionary of oemof component objects included in energy system model
        :return: updated dictionary of omeof component objects included in energy system model
        '''
        define.bus(model, dict_asset['in']['sector'] + '_utility_consumption', **kwargs)
        define.bus(model, dict_asset['out']['sector'] + '_utility_feedin', **kwargs)

        helpers.check_optimize_cap(model, dict_asset['in'],
                                                    func_constant=define.transformer_constant_efficiency_fix,
                                                    func_optimize=define.transformer_constant_efficiency_optimize, **kwargs)

        define.source_dispatchable(model, dict_asset['source'], **kwargs)

        helpers.check_optimize_cap(model, dict_asset['out'],
                                                     func_constant=define.transformer_constant_efficiency_fix,
                                                     func_optimize=define.transformer_constant_efficiency_optimize, **kwargs)

        define.sink_dispatchable(model, dict_asset['sink'], **kwargs)
        logging.info('Added busses for in/output to utilityy, sink, source and transformers in/out.')
        return

    def genset_fix_efficiency(model, dict_asset, **kwargs):
        helpers.check_optimize_cap(model, dict_asset,
                                   func_constant=define.transformer_constant_efficiency_fix,
                                   func_optimize=define.transformer_constant_efficiency_optimize, **kwargs)
        logging.info('Added generator.')
        return

    def demands(model, dict_asset, **kwargs):
        for demand in dict_asset.keys():
            if demand != 'label':
                define.sink_non_dispatchable(model, dict_asset[demand], **kwargs)
                logging.info('Added: Demand profile for %s on bus %s', demand, dict_asset[demand]['input_bus_name'])
        return

    def electricity_storage(model, dict_asset, **kwargs):
        define.bus(model, 'electricity_dc_storage', **kwargs)

        helpers.check_optimize_cap(model, dict_asset,
                                   func_constant=define.storage_fix,
                                   func_optimize=define.storage_optimize, **kwargs)

        #todo this would actually require a bi-directional inverter -> link charge controller in/out capacities to each other
        helpers.check_optimize_cap(model, dict_asset['charge_controller']['in'],
                                   func_constant=define.transformer_constant_efficiency_fix,
                                   func_optimize=define.transformer_constant_efficiency_optimize, **kwargs)

        # symbolic charge controller has no costs attributed! ie - discharge is not connected to charge controller sizing
        helpers.check_optimize_cap(model, dict_asset['charge_controller']['out'],
                                   func_constant=define.transformer_constant_efficiency_fix,
                                   func_optimize=define.transformer_constant_efficiency_optimize, **kwargs)

        logging.info('Added electricity storage including storage capacity, input and output power as well as charge controller in/out.')
        return

    def pv_plant(model, dict_asset, **kwargs):
        define.bus(model, 'electricity_dc_pv', **kwargs)

        helpers.check_optimize_cap(model, dict_asset['pv_installation'],
                                   func_constant=define.source_non_dispatchable_fix,
                                   func_optimize=define.source_non_dispatchable_optimize, **kwargs)

        helpers.check_optimize_cap(model, dict_asset['solar_inverter'],
                                   func_constant=define.transformer_constant_efficiency_fix,
                                   func_optimize=define.transformer_constant_efficiency_optimize, **kwargs)
        logging.info('Added PV bus, pv installation and solar inverter.')
        return

    def wind_plant(model, dict_asset, **kwargs):
        helpers.check_optimize_cap(model, dict_asset['wind_installation'],
                                   func_constant=define.source_non_dispatchable_fix,
                                   func_optimize=define.source_non_dispatchable_optimize, **kwargs)
        return

class define():

    def bus(model, name, **kwargs):
        logging.debug('Added: Bus %s', name)
        bus = solph.Bus(label=name)
        kwargs['busses'].update({name: bus})
        model.add(bus)
        return

    def transformer_constant_efficiency_fix(model, dict_asset, **kwargs):
        transformer = solph.Transformer(label=dict_asset['label'],
                                   inputs={kwargs['busses'][dict_asset['input_bus_name']]: solph.Flow()},
                                   outputs={kwargs['busses'][dict_asset['output_bus_name']]: solph.Flow(
                                       nominal_value=dict_asset['cap_installed'],
                                       variable_costs=dict_asset['opex_var'])},
                                   conversion_factors={
                                       kwargs['busses']['electricity']: dict_asset['efficiency']}
                                   )
        model.add(transformer)
        kwargs['transformers'].update({dict_asset['label']: transformer})
        return

    def transformer_constant_efficiency_optimize(model, dict_asset, **kwargs):
        transformer = solph.Transformer(label=dict_asset['label'],
                                   inputs={kwargs['busses'][dict_asset['input_bus_name']]: solph.Flow()},
                                   outputs={kwargs['busses'][dict_asset['output_bus_name']]: solph.Flow(
                                       investment=solph.Investment(
                                           ep_costs=dict_asset['simulation_annuity']),
                                       existing=dict_asset['cap_installed'],
                                       variable_costs=dict_asset['opex_var'])},
                                   conversion_factors={
                                       kwargs['busses']['electricity']: dict_asset['efficiency']}
                                   )
        model.add(transformer)
        kwargs['transformers'].update({dict_asset['label']: transformer})
        return

    def storage_fix(model, dict_asset, **kwargs):
        storage = solph.components.GenericStorage(
            label=dict_asset['label'],
            nominal_storage_capacity=dict_asset['capacity']['cap_installed'],
            inputs={kwargs['busses'][dict_asset['input_bus_name']]: solph.Flow(
                nominal_value= dict_asset['discharging_power']['cap_installed'], #limited through installed capacity, NOT c-rate
                variable_costs=dict_asset['charging_power']['opex_var']
            )},  # maximum charge possible in one timestep
            outputs={kwargs['busses'][dict_asset['output_bus_name']]: solph.Flow(
                nominal_value= dict_asset['discharging_power']['cap_installed'], #limited through installed capacity, NOT c-rate #todo actually, if we only have a lithium battery... crate should suffice? i mean, with crate fixed AND fixed power, this is defined two times
                variable_costs = dict_asset['discharging_power']['opex_var']
            )},  # maximum discharge possible in one timestep
            loss_rate=dict_asset['capacity']['self_discharge'],  # from timestep to timestep
            min_storage_level=dict_asset['capacity']['soc_min'],
            max_storage_level=dict_asset['capacity']['soc_max'],
            initial_storage_level=dict_asset['capacity']['soc_initial'],  # in terms of SOC
            inflow_conversion_factor=dict_asset['charging_power']['efficiency'],  # storing efficiency
            outflow_conversion_factor=dict_asset['discharging_power']['efficiency'])  # efficiency of discharge
        model.add(storage)
        kwargs['storages'].update({dict_asset['label']: storage})
        return

    def storage_optimize(model, dict_asset, **kwargs):
        storage = solph.components.GenericStorage(
            label=dict_asset['label'],
            existing=dict_asset['capacity']['cap_installed'],
            investment=solph.Investment(ep_costs=dict_asset['capacity']['simulation_annuity']),
            inputs={kwargs['busses'][dict_asset['input_bus_name']]: solph.Flow(
                existing= dict_asset['charging_power']['cap_installed'],
                investment = solph.Investment(ep_costs=dict_asset['charging_power']['simulation_annuity']),
                variable_costs=dict_asset['charging_power']['opex_var']
            )},  # maximum charge power
            outputs={kwargs['busses'][dict_asset['output_bus_name']]: solph.Flow(
                existing=dict_asset['discharging_power']['cap_installed'],
                investment=solph.Investment(ep_costs=dict_asset['discharging_power']['simulation_annuity']),
                variable_costs=dict_asset['discharging_power']['opex_var']
            )},  # maximum discharge power
            loss_rate=dict_asset['capacity']['self_discharge'],  # from timestep to timestep
            min_storage_level=dict_asset['capacity']['soc_min'],
            max_storage_level=dict_asset['capacity']['soc_max'],
            initial_storage_level=dict_asset['capacity']['soc_initial'],  # in terms of SOC #implication: balanced = True, ie. start=end
            inflow_conversion_factor=dict_asset['charging_power']['efficiency'],  # storing efficiency
            outflow_conversion_factor=dict_asset['discharging_power']['efficiency'], # efficiency of discharge
            invest_relation_input_capacity=dict_asset['charging_power']['crate'],
            # storage can be charged with invest_relation_output_capacity*capacity in one timeperiod
            invest_relation_output_capacity=dict_asset['discharging_power']['crate']
            # storage can be emptied with invest_relation_output_capacity*capacity in one timeperiod
        )
        model.add(storage)
        kwargs['storages'].update({dict_asset['label']: storage})
        return

    def sink_non_dispatchable(model, dict_asset, **kwargs):
        # create and add demand sink to micro_grid_system - fixed
        sink_demand = solph.Sink(label=dict_asset['label'],
                                    inputs={kwargs['busses'][dict_asset['input_bus_name']]:
                                        solph.Flow(
                                            actual_value=dict_asset['timeseries'],
                                            nominal_value=1,
                                            fixed=True)})
        model.add(sink_demand)
        kwargs['sinks'].update({dict_asset['label']: sink_demand})
        return

    def source_non_dispatchable_fix(model, dict_asset, **kwargs):
        source_non_dispatchable = solph.Source(label=dict_asset['label'],
                                 outputs={kwargs['busses'][dict_asset['output_bus_name']]:
                                              solph.Flow(label=dict_asset['label'],
                                                         actual_value=dict_asset['timeseries'],
                                                         fixed=True,
                                                         nominal_value=dict_asset['cap_installed'],
                                                         variable_costs=dict_asset['opex_var']
                                                         )})

        model.add(source_non_dispatchable)
        kwargs['sources'].update({dict_asset['label']: source_non_dispatchable})
        return

    def source_non_dispatchable_optimize(model, dict_asset, **kwargs):
        peak_timeseries = max(dict_asset['timeseries'])
        logging.debug('Normalizing timeseries of %s.', dict_asset['label'])
        dict_asset.update({'timeseries_normalized': dict_asset['timeseries'] / peak_timeseries})
        # just to be sure!
        if any(dict_asset['timeseries_normalized'].values) > 1:
            logging.warning("Error, %s timeseries not normalized, greater than 1.", dict_asset['label'])
        if any(dict_asset['timeseries_normalized'].values) < 0:
            logging.warning("Error, %s timeseries negative.", dict_asset['label'])
        source_non_dispatchable = solph.Source(label=dict_asset['label'],
                                 outputs={kwargs['busses'][dict_asset['output_bus_name']]:
                                              solph.Flow(label=dict_asset['label'],
                                                         actual_value=dict_asset['timeseries_normalized'],
                                                         fixed=True,
                                                         existing = dict_asset['cap_installed'],
                                                         investment=solph.Investment(
                                                             ep_costs=dict_asset['simulation_annuity'] / peak_timeseries),
                                                         variable_costs=dict_asset['opex_var'] / peak_timeseries
                                                         )})

        model.add(source_non_dispatchable)
        kwargs['sources'].update({dict_asset['label']: source_non_dispatchable})
        return

    def source_dispatchable(model, dict_asset, **kwargs):
        source_dispatchable = solph.Source(label=dict_asset['label'],
                                 outputs={kwargs['busses'][dict_asset['output_bus_name']]:
                                              solph.Flow(label=dict_asset['label'],
                                                         variable_costs=dict_asset['price'])})

        model.add(source_dispatchable)
        kwargs['sources'].update({dict_asset['label']: source_dispatchable})
        logging.info('Added: Dispatchable source %s', dict_asset['label'])
        return


    def sink_dispatchable(model, dict_asset, **kwargs):
        # create and add excess electricity sink to micro_grid_system - variable
        sink_dispatchable = solph.Sink(label=dict_asset['label'],
                                 inputs={kwargs['busses'][dict_asset['input_bus_name']]:
                                             solph.Flow(label=dict_asset['label'],
                                                         variable_costs=dict_asset['price'])})
        model.add(sink_dispatchable)
        kwargs['sinks'].update({dict_asset['label']: sink_dispatchable})
        logging.info('Added: Dispatchable sink %s', dict_asset['label'])
        return
