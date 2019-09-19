import os.path
import timeit
import logging
import oemof.solph as solph
import oemof.outputlib as outputlib
import pprint as pp
from D1_model_components import define, call_component, helpers

class modelling:
    def run_oemof(dict_values):
        '''
        Creates and solves energy system model generated from excel template inputs.
        Each component is included by calling its constructor function in D1_model_components.

        :param dict values: Includes all dictionary values describing the whole project, including costs,
                            technical parameters and components. In C0_data_processing, each component was attributed
                            with a certain in/output bus.

        :return: saves and returns oemof simulation results
        '''

        # Start clock to determine total simulation time
        start = timeit.default_timer()

        logging.info('Initializing oemof simulation.')
        model = solph.EnergySystem(
            timeindex=dict_values['settings']['index'])

        #this dictionary will include all generated oemof objects
        dict_model = {'busses': {},
                    'sinks': {},
                    'sources': {},
                    'transformers': {},
                    'storages': {}}

        logging.info('Adding components to energy system model...')

        # Check all dict values and if necessary call component
        # "for loop" chosen to raise errors in case entries are not defined
        # other way would be: if key in dict_values: define/call component
        for dict_key in dict_values.keys():
            if dict_key in ['project_data', 'settings', 'economic_data', 'user_input']:
                pass
            elif dict_key == 'electricity_grid':
                # this only defines the electricity bus itself
                # todo however, distribution grid efficiency is not jet included into the model!
                # same goes for distibution costs per kWh
                define.bus(model, dict_key[:-5], **dict_model)

            elif dict_key == 'electricity_excess':
                # defines excess sink
                define.sink_dispatchable(model, dict_values[dict_key], **dict_model)

            elif dict_key == 'transformer_station':
                # Defines transformer station with all sub components:
                # two busses, sink, source, two transformers arributed with costs
                # be aware: currently, BOTH consumption and feed-in defined by default, ie. a transformer only used
                # for consumption is not implemented
                # todo in future: here, multiple transformers relative to the peak demand pricing period should be implemented
                # attibuted by actual value = timeseries, zeros and ones -> should allow sizing per pricing period
                call_component.utility_connection(model, dict_values[dict_key], **dict_model)

            elif dict_key == 'pv_plant':
                # defines pv plant including own bus, pv installation and solar inverter
                call_component.pv_plant(model, dict_values[dict_key], **dict_model)

            elif dict_key == 'wind_plant':
                logging.warning('Oemof component %s not defined!', dict_key)
                call_component.wind_plant(model, dict_values[dict_key], **dict_model)

            elif dict_key == 'electricity_storage':
                # Defines electricity storage with all sub-components:
                # bus, two transformers, storage with capacity, power in/out
                # todo reevaluate if storage_fix is properly defined - it could either be defined based on c-rate or power!
                call_component.electricity_storage(model, dict_values[dict_key], **dict_model)  # todo add sector to ess attributes

            elif dict_key == 'generator':
                # Simple generator with constant efficiency
                # add other options: linear etc
                logging.warning('Asset %s not defined for oemof integration.', dict_key)
                define.bus(model, 'Fuel', **dict_model)

            elif dict_key == 'electricity_demand':
                # add all electricity demand profiles (a number of sinks)
                call_component.demands(model, dict_values[dict_key], **dict_model)

            else:
                logging.warning('Unknown asset %s. '
                                'Check validity and, if necessary, add another oemof component definition.', dict_key)

        logging.debug('All components added.')

        logging.debug('Create oemof model based on created components and busses.')
        local_energy_system = solph.Model(model)

        logging.info('Adding constraints to oemof model...')
        # todo include constraints
        '''
        Stability constraint
        Minimal renewable share constraint
        '''
        logging.debug('All constraints added.')
        '''
        from f1_plotting import plots
        color_dict = {
            'coal': '#755d5d',
            'gas': '#c76c56',
            'oil': '#494a19',
            'lignite': '#56201d',
            'wind': '#4ca7c3',
            'pv': '#ffde32',
            'excess_el': '#9a9da1',
            'pp_coal': '#755d5d',
            'pp_gas': '#c76c56',
            'pp_chp': '#eeac7e',
            'b_heat_source': '#cd3333',
            'heat_source': '#cd3333',
            'heat_pump': '#42c77a',
            'electricity': '#0079ff',
            'demand_el': '#0079ff',
            'shortage_el': '#ff2626',
            'excess_el': '#ff2626',
            'biomass': '#01b42e',
            'pp_biomass': '#01b42e'}
        plots.draw_graph(model, node_color=color_dict)
        '''
        logging.debug('Saving to lp-file.')
        local_energy_system.write(dict_values['user_input']['path_output_folder'] + '/lp_file.lp',
                    io_options={'symbolic_solver_labels': True})

        logging.info('Starting simulation.')
        local_energy_system.solve(
                    solver='cbc',
                    solve_kwargs={'tee': False},# if tee_switch is true solver messages will be displayed
                    cmdline_options={'ratioGap': str(0.03)}
                    )  # ratioGap allowedGap mipgap
        logging.info('Problem solved.')

        # add results to the energy system to make it possible to store them.
        results_main = outputlib.processing.results(local_energy_system)
        results_meta = outputlib.processing.meta_results(local_energy_system)

        model.results['main'] = results_main
        model.results['meta'] = results_meta
        '''
                if experiment['save_lp_file'] == True:
            logging.debug('Saving lp-file to folder.')
            model.write(experiment['output_folder'] + '/lp_files/model_' + file_name + '.lp',
                        io_options={'symbolic_solver_labels': True})

        '''

        '''
        # store energy system with results
        model.dump(dpath=output_folder+'/oemof', filename = file_name + ".oemof" )
        logging.debug('Stored results in ' + output_folder+'/oemof' + '/' + file_name + ".oemof")        
        '''

        '''
        logging.debug('Restore the energy system and the results.')
        micro_grid_system = solph.EnergySystem()
        micro_grid_system.restore(dpath=output_folder+'/oemof',
                                  filename=file_name + ".oemof")
        '''

        duration = timeit.default_timer() - start

        dict_values.update({'simulation_results': {
            'label': 'simulation_results',
            'objective_value': results_meta['objective'],
            'simulation_time': results_meta['solver']['Time'],
            'modelling_time': duration }})
        logging.info('Simulation time: %s minutes.', round(dict_values['simulation_results']['simulation_time']/60, 2))
        logging.info('Moddeling time: %s minutes.', round(dict_values['simulation_results']['modelling_time'] / 60, 2))

        return results_meta, results_main, dict_model
