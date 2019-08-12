import logging
import oemof.solph as solph

class helpers():
    def check_optimize_cap(model, dict_model, dict_asset, func_constant, func_optimize):
        if dict_asset['optimize_cap']==False:
            logging.info('Added: Component %s, excluded from optimization.', dict_asset['label'])
            func_constant(model, dict_model, dict_asset)
        elif dict_asset['optimize_cap']==True:
            logging.info('Added: Component %s, to be optimized.', dict_asset['label'])
            func_optimize(model, dict_model, dict_asset)
        else:
            logging.warning('Input error! '
                            '"optimize_cap" of asset %s not True/False.', dict_asset['label'])
        return


class call_component:

    def utility_connection(model, dict_model, dict_asset):
        dict_asset.update({'input_bus_name': dict_asset['sector'],
                           'output_bus_name': dict_asset['sector'] + ' utility feedin'})

        helpers.check_optimize_cap(model, dict_model, dict_asset,
                                            func_constant=define.transformer_constant_efficiency_fix,
                                            func_optimize=define.transformer_constant_efficiency_optimize)

        define.source_dispatchable(model, dict_model, dict_asset)

        dict_asset.update({'input_bus_name': dict_asset['sector'] + ' utility consumption',
                           'output_bus_name': dict_asset['sector']})

        helpers.check_optimize_cap(model, dict_model, dict_asset,
                                            func_constant=define.transformer_constant_efficiency_fix,
                                            func_optimize=define.transformer_constant_efficiency_optimize)
        return

    def genset_fix_efficiency(model, dict_model, dict_asset):
        dict_asset.update({'input_bus_name': 'Fuel',
                           'output_bus_name': 'Electricity'})

        helpers.check_optimize_cap(model, dict_model, dict_asset,
                                            func_constant=define.transformer_constant_efficiency_fix,
                                            func_optimize=define.transformer_constant_efficiency_optimize)
        return

    def demands(model, dict_model, dict_asset, demand_type):
        sector = demand_type[:-7]
        dict_model['sinks'].update({sector: {}})
        for demand in dict_asset.keys():
            dict_asset[demand].update({'input_bus_name': sector})
            define.sink_non_dispatchable(model, dict_model, dict_asset[demand])
            logging.info('Added: Demand profile for %s on bus %s', demand, sector)

    def storage(model, dict_model, dict_asset, component_name):
        if component_name == 'ESS':
            dict_asset.update({'input_bus_name': 'Electricity DC (Storage)',
                               'output_bus_name': 'Electricity DC (Storage)'})


        helpers.check_optimize_cap(model, dict_model, dict_asset,
                                   func_constant=define.storage_fix,
                                   func_optimize=define.storage_optimize)

        #todo this would actually require a bi-directional inverter -> link charge controller in/out capacities to each other
        dict_asset['charge_controller'].update({'input_bus_name': 'Electricity',
                                                'output_bus_name': 'Electricity DC (Storage)'})

        helpers.check_optimize_cap(model, dict_model, dict_asset['charge_controller'],
                                   func_constant=define.transformer_constant_efficiency_fix,
                                   func_optimize=define.transformer_constant_efficiency_optimize)

        # symbolic charge controller has no costs attributed! ie - discharge is not connected to charge controller sizing
        dict_asset['charge_controller_symbolic'].update({'input_bus_name': 'Electricity DC (Storage)',
                                                         'output_bus_name': 'Electricity'})

        helpers.check_optimize_cap(model, dict_model, dict_asset['charge_controller_symbolic'],
                                   func_constant=define.transformer_constant_efficiency_fix,
                                   func_optimize=define.transformer_constant_efficiency_optimize)

    def pv_plant(model, dict_model, dict_asset):
        dict_asset['pv_installation'].update({'output_bus_name': 'Electricity DC (PV)'})

        helpers.check_optimize_cap(model, dict_model, dict_asset['pv_installation'],
                                   func_constant=define.source_non_dispatchable_fix,
                                   func_optimize=define.source_non_dispatchable_optimize)

        dict_asset['solar_inverter'].update({'input_bus_name': 'Electricity DC (PV)',
                                             'output_bus_name': 'Electricity'})

        helpers.check_optimize_cap(model, dict_model, dict_asset['solar_inverter'],
                                   func_constant=define.transformer_constant_efficiency_fix,
                                   func_optimize=define.transformer_constant_efficiency_optimize)

    def wind_plant(model, dict_model, dict_asset):
        dict_asset['wind_installation'].update({'output_bus_name': 'Electricity'})

        helpers.check_optimize_cap(model, dict_model, dict_asset['wind_installation'],
                                   func_constant=define.source_non_dispatchable_fix,
                                   func_optimize=define.source_non_dispatchable_optimize)

class define():

    def bus(model, dict_model, name):
        logging.debug('Added: Bus %s', name)
        bus = solph.Bus(label=name)
        dict_model['busses'].update({bus.label: bus})
        model.add(bus)
        return

    def transformer_constant_efficiency_fix(model, dict_model, dict_asset):
        transformer = solph.Transformer(label=dict_asset['label'],
                                   inputs={dict_model['busses'][dict_asset['input_bus_name']]: solph.Flow()},
                                   outputs={dict_model['busses'][dict_asset['output_bus_name']]: solph.Flow(
                                       nominal_value=dict_asset['cap_installed'],
                                       variable_costs=dict_asset['opex_var'])},
                                   conversion_factors={
                                       dict_model['busses']['Electricity']: dict_asset['efficiency']}
                                   )
        model.add(transformer)
        dict_model['transformers'].update({dict_asset['label']: transformer})
        return

    def transformer_constant_efficiency_optimize(model, dict_model, dict_asset):
        transformer = solph.Transformer(label=dict_asset['label'],
                                   inputs={dict_model['busses'][dict_asset['input_bus_name']]: solph.Flow()},
                                   outputs={dict_model['busses'][dict_asset['output_bus_name']]: solph.Flow(
                                       investment=solph.Investment(
                                           ep_costs=dict_asset['simulation_annuity']),
                                       existing=dict_asset['cap_installed'],
                                       variable_costs=dict_asset['opex_var'])},
                                   conversion_factors={
                                       dict_model['busses']['Electricity']: dict_asset['efficiency']}
                                   )
        model.add(transformer)
        dict_model['transformers'].update({dict_asset['label']: transformer})
        return

    def storage_fix(model, dict_model, dict_asset):
        storage = solph.components.GenericStorage(
            label=dict_asset['label'],
            nominal_capacity=dict_asset['capacity']['cap_installed'],
            inputs={dict_model['busses'][dict_asset['input_bus_name']]: solph.Flow( #todo create  but electricity dc
                nominal_value=capacity_storage * experiment['storage_Crate_charge'],
                variable_costs=dict_asset['charging_power']['opex_var']
            )},  # maximum charge possible in one timestep
            outputs={dict_model['busses'][dict_asset['output_bus_name']]: solph.Flow(
                nominal_value= capacity_storage*experiment['storage_Crate_discharge'], #todo actually, if we only have a lithium battery... crate should suffice? i mean, with crate fixed AND fixed power, this is defined two times
                variable_costs = dict_asset['discharging_power']['opex_var']
            )},  # maximum discharge possible in one timestep
            capacity_loss=dict_asset['capacity']['efficiency'],  # from timestep to timestep
            capacity_min=dict_asset['capacity']['soc_min'],
            capacity_max=dict_asset['capacity']['soc_max'],
            initial_capacity=dict_asset['capacity']['soc_initial'],  # in terms of SOC
            inflow_conversion_factor=dict_asset['charging_power']['efficiency'],  # storing efficiency
            outflow_conversion_factor=dict_asset['discharging_power']['efficiency'])  # efficiency of discharge
        model.add(storage)
        dict_model['storages'].update({dict_asset['label']: storage})
        return

    def storage_optimize(model, dict_model, dict_asset):
        storage = solph.components.GenericStorage(
            label=dict_asset['label'],
            existing=dict_asset['capacity']['cap_installed'],
            investment=solph.Investment(ep_costs=dict_asset['capacity']['simulation_annuity']),
            inputs={dict_model['busses'][dict_asset['input_bus_name']]: solph.Flow(  # todo create  but electricity dc
                existing= dict_asset['charging_power']['cap_installed'],
                investment = solph.Investment(ep_costs=dict_asset['charging_power']['simulation_annuity']),
                variable_costs=dict_asset['charging_power']['opex_var']
            )},  # maximum charge power
            outputs={dict_model['busses'][dict_asset['output_bus_name']]: solph.Flow(
                existing=dict_asset['discharging_power']['cap_installed'],
                investment=solph.Investment(ep_costs=dict_asset['discharging_power']['simulation_annuity']),
                variable_costs=dict_asset['discharging_power']['opex_var']
            )},  # maximum discharge power
            loss_rate=dict_asset['capacity']['efficiency'],  # from timestep to timestep
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
        dict_model['storages'].update({dict_asset['label']: storage})
        return

    def sink_non_dispatchable(model, dict_model, dict_asset):
        # create and add demand sink to micro_grid_system - fixed
        sink_demand = solph.Sink(label=dict_asset['label'],
                                    inputs={dict_model['busses'][dict_asset['input_bus_name']]:
                                        solph.Flow(
                                            actual_value=dict_asset['timeseries'],
                                            nominal_value=1,
                                            fixed=True)})

        model.add(sink_demand)
        dict_model['sinks'][dict_asset['input_bus_name']].update({dict_asset['label']: sink_demand})
        return


    def sink_dispatchable(model, dict_model, dict_asset):
        # create and add excess electricity sink to micro_grid_system - variable
        sink_excess = solph.Sink(label=dict_asset['label'],
                                 inputs={dict_model['busses'][dict_asset['input_bus_name']]: solph.Flow()})
        model.add(sink_excess)
        dict_model['sinks'].update({dict_asset['label']: sink_excess})
        return

    def source_non_dispatchable_fix(model, dict_model, dict_asset):
        source_non_dispatchable = solph.Source(label=dict_asset['label'],
                                 outputs={dict_model['busses'][dict_asset['output_bus_name']]:
                                              solph.Flow(label=dict_asset['label'],
                                                         actual_value=dict_asset['timeseries'],
                                                         fixed=True,
                                                         nominal_value=dict_asset['cap_installed'],
                                                         variable_costs=dict_asset['opex_var']
                                                         )})

        model.add(source_non_dispatchable)
        dict_model['sources'].update({dict_asset['label']: source_non_dispatchable})
        return

    def source_non_dispatchable_optimize(model, dict_model, dict_asset):
        peak_timeseries = max(dict_asset['timeseries'].values)
        logging.debug('Normalizing timeseries of %s.', dict_asset['label'])
        dict_asset.update({'timeseries_normalized': dict_asset['timeseries'] / peak_timeseries})
        # just to be sure!
        if any(dict_asset['timeseries_normalized'].values) > 1:
            logging.warning("Error, %s timeseries not normalized, greater than 1.", dict_asset['label'])
        if any(dict_asset['timeseries_normalized'].values) < 0:
            logging.warning("Error, %s timeseries negative.", dict_asset['label'])

        source_non_dispatchable = solph.Source(label=dict_asset['label'],
                                 outputs={dict_model['busses'][dict_asset['output_bus_name']]:
                                              solph.Flow(label=dict_asset['label'],
                                                         actual_value=dict_asset['timeseries_normalized'],
                                                         fixed=True,
                                                         existing = dict_asset['cap_installed'],
                                                         investment=solph.Investment(
                                                             ep_costs=dict_asset['simulation_annuity'] / peak_timeseries),
                                                         variable_costs=dict_asset['opex_var'] / peak_timeseries
                                                         )})

        model.add(source_non_dispatchable)
        dict_model['sources'].update({dict_asset['label']: source_non_dispatchable})
        logging.debug('Added: Component %s', dict_asset['label'])
        return

    def source_dispatchable(model, dict_model, dict_asset):
        source_dispatchable = solph.Source(label=dict_asset['label'],
                                 outputs={dict_model['busses'][dict_asset['output_bus_name']]:
                                              solph.Flow(label=dict_asset['label'],
                                                         variable_costs=dict_asset['opex_var']
                                                         )})

        model.add(source_dispatchable)
        dict_model['sources'].update({dict_asset['label']: source_dispatchable})
        return
'''.
    def genset_var_efficiency(dict_asset):
        return

    # This could be used for wind plants and pv plants alike
    

    def shortage(dict_asset):
        return

    

'''