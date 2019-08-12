import os.path
import timeit
import logging
import oemof.solph as solph
import pprint as pp
from D1_model_components import define, call_component

class modelling:
    def run_oemof(dict_values, included_assets):
        pp.pprint(included_assets)

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
        for sector in included_assets['sectors']:
            define.bus(model, dict_model, sector)

        for component in included_assets['conversion assets']:
            logging.warning('Necessity to add additional bus for %s?', component)
            if component == 'generator':
                define.bus(model, dict_model, 'Fuel')

        for coupling_component in included_assets['energy providers']:
            define.bus(model, dict_model, dict_values[coupling_component]['sector'] + ' utility feedin')
            define.bus(model, dict_model, dict_values[coupling_component]['sector'] + ' utility consumption')
            call_component.utility_connection(model, dict_model, dict_values[coupling_component])

        for component in included_assets['generation assets']:
            logging.debug('Adding all components connected to a %s to the system.', component)
            if component == 'PV plant':
                define.bus(model, dict_model, 'Electricity DC (PV)')
                call_component.pv_plant(model, dict_model, dict_values[component])
            elif component == 'Wind plant':
                call_component.wind_plant(model, dict_model, dict_values[component])
            else:
                logging.warning('Unknown generation asset %s. '
                                'Check validity and, if necessary, add another component.', component)

        for component in included_assets['storage assets']:
            logging.debug('Adding storage asset %s to the system.', component)
            define.bus(model, dict_model, 'Electricity DC (Storage)')
            call_component.storage(model, dict_model, dict_values[component], component) #todo add sector to ess attributes

        for demand_type in included_assets['demands']:
            call_component.demands(model, dict_model, dict_values[demand_type], demand_type)
            logging.info('Added all %ss to the system.', demand_type)

        logging.debug('All components added.')

        logging.info('Adding constraints to energy system model...')
        logging.debug('All constraints added.')

        logging.info('Starting simulation.')
        return