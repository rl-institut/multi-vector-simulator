import os.path
import timeit
import logging
import oemof.solph as solph
import pprint as pp

class modelling:
    def run_oemof(dict_values, included_assets):
        pp.pprint(included_assets)

        start = timeit.default_timer()

        logging.info('Initializing oemof simulation.')
        les = solph.EnergySystem(
            timeindex=dict_values['settings']['index'])

        dict_les = {'busses': {},
                    'sinks': {},
                    'sources': {},
                    'transformers': {}}

        logging.info('Adding all necessary busses:')
        for sector in included_assets['sectors']:
            bus = solph.Bus(label=sector)
            dict_les['busses'].update({sector: bus})
            les.add(bus)

        for component in included_assets['conversion assets']:
            logging.warning('Necessity to add additinal bus for %s?', component)

        for utility in included_assets['energy providers']:
            logging.error('Necessity to add point of coupling to external provider (%s)?', utility)

        for component in included_assets['generation']:
            logging.info('Adding all components connected to a %s to the system.', component)
            if component == 'PV plant':
                pass
            elif component == 'Wind plant':
                pass
            else:
                logging.warning('Unknown generation asset %s. '
                                'Check validity and, if necessary, add another component.', component)

        for component in included_assets['storage assets']:
            logging.info('Adding storage asset %s to the system.', component)

        for demand in included_assets['demands']:
            logging.info('Adding storage asset %s to the system.', demand)

        return