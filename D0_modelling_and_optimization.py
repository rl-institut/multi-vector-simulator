import os.path
import timeit
import logging
import oemof.solph as solph
import pprint as pp
from D1_model_components import define, call_component, helpers

class modelling:
    def run_oemof(dict_values):
        start = timeit.default_timer()

        logging.info('Initializing oemof simulation.')
        model = solph.EnergySystem(
            timeindex=dict_values['settings']['index'])

        dict_model = {'busses': {},
                    'sinks': {},
                    'sources': {},
                    'transformers': {},
                    'storages': {}}

        logging.info('Adding components to energy system model...')
        for dict_key in dict_values.keys():
            if dict_key in ['project_data', 'settings', 'economic_data', 'user_input']:
                pass
            elif dict_key == 'electricity_grid':
                define.bus(model, dict_key[:-5], **dict_model)

            elif dict_key == 'electricity_excess':
                define.sink_dispatchable(model, dict_values[dict_key], **dict_model)

            elif dict_key == 'transformer_station':
                call_component.utility_connection(model, dict_values[dict_key], **dict_model)

            elif dict_key == 'pv_plant':
                call_component.pv_plant(model, dict_values[dict_key], **dict_model)

            elif dict_key == 'wind_plant':
                call_component.wind_plant(model, dict_values[dict_key], **dict_model)

            elif dict_key == 'electricity_storage':
                call_component.storage(model, dict_values[dict_key], **dict_model)  # todo add sector to ess attributes

            elif dict_key == 'generator':
                logging.warning('Asset %s not defined for oemof integration.', dict_key)
                define.bus(model, 'Fuel', **dict_model)

            elif dict_key == 'electricity_demand':
                call_component.demands(model, dict_values[dict_key], **dict_model)

            else:
                logging.warning('Unknown asset %s. '
                                'Check validity and, if necessary, add another oemof component definition.', asset)


        logging.debug('All components added.')
        pp.pprint(model)
        pp.pprint(dict_model['busses']['electricity'])
        logging.debug('Create oemof model based on created components and busses.')
        local_energy_system = solph.Model(model)

        logging.info('Adding constraints to oemof model...')
        logging.debug('All constraints added.')

        logging.info('Starting simulation.')
        local_energy_system.solve(
                    solver='cbc',
                    solve_kwargs={'tee': False},# if tee_switch is true solver messages will be displayed
                    cmdline_options={'ratioGap': str(0.03)}
                    )  # ratioGap allowedGap mipgap
        logging.info('Problem solved.')
        duration = timeit.default_timer() - start
        logging.info('Simulation time: %s minutes.', round(duration/60, 2))


        return
