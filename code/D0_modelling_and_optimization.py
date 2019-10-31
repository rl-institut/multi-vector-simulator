import timeit
import logging
import oemof.solph as solph
import oemof.outputlib as outputlib

try:
    from .D1_model_components import define_oemof_component, call_component, helpers
except ImportError:
    from code.D1_model_components import define_oemof_component, call_component, helpers

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
            timeindex=dict_values['simulation_settings']['time_index'])

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
        for bus in dict_values['energyBusses']:
            define_oemof_component.bus(model, bus, **dict_model)

        def warning_asset_type(asset, type, assetGroup):
            logging.error('Asset %s has type %s, '
                          'but this type is not an asset type attributed to asset group %s for oemof model generation.',
                          asset, type, assetGroup)
            return

        for asset in dict_values['energyConversion']:
            type = dict_values['energyConversion'][asset]['type_oemof']
            if type == 'transformer':
                call_component.transformer(model, dict_values['energyConversion'][asset], **dict_model)
            else:
                warning_asset_type(asset, type, 'energyConversion')

        for sector in dict_values['energyConsumption']:
            for asset in dict_values['energyConsumption'][sector]:
                type = dict_values['energyConsumption'][sector][asset]['type_oemof']
                if type == 'sink':
                    call_component.sink(model, dict_values['energyConsumption'][sector][asset], **dict_model)
                else:
                    warning_asset_type(asset, type, 'energyConsumption')

        for sector in dict_values['energyProduction']:
            for asset in dict_values['energyProduction'][sector]:
                type = dict_values['energyProduction'][sector][asset]['type_oemof']
                if type == 'source':
                    call_component.source(model, dict_values['energyProduction'][sector][asset], **dict_model)
                else:
                    warning_asset_type(asset, type, 'energyProduction')

        for sector in dict_values['energyStorage']:
            for asset in dict_values['energyStorage'][sector]:
                type = dict_values['energyStorage'][sector][asset]['type_oemof']
                if type == 'storage':
                    call_component.storage(model, dict_values['energyStorage'][sector][asset], **dict_model)
                else:
                    warning_asset_type(asset, type, 'energyStorage')

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
        if dict_values['simulation_settings']['output_lp_file'] == True:
            logging.debug('Saving to lp-file.')
            local_energy_system.write(dict_values['simulation_settings']['path_output_folder'] + '/lp_file.lp',
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
