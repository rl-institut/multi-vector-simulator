import logging
import oemof.outputlib as outputlib
import pandas as pd
import pprint as pp
try:
    from .code_folder.E1_process_results import process_results
    from .code_folder.E2_economics import economics
    from .code_folder.F0_output import helpers as output
except ImportError:
    from code_folder.E1_process_results import process_results
    from code_folder.E2_economics import economics
    from code_folder.F0_output import helpers as output

class evaluation:
    def evaluate_dict(dict_values, results_main, results_meta):
        bus_data={}
        # Store all information related to busses in bus_data
        for bus in dict_values['energyBusses']:
            # Read all energy flows from busses
            bus_data.update({bus: outputlib.views.node(results_main, bus)})

        # Evaluate timeseries and store to a large DataFrame for each bus:
        bus_data_timeseries = process_results.get_timeseries_per_bus(dict_values, bus_data)

        # Store all information related to storages in bus_data, as storage capacity acts as a bus
        for sector in dict_values['energyStorage']:
            for storage in dict_values['energyStorage'][sector]:
                bus_data.update({dict_values['energyStorage'][sector][storage]['label']:
                    outputlib.views.node(results_main, dict_values['energyStorage'][sector][storage]['label'])})
                process_results.get_storage_results(dict_values['simulation_settings'],
                                                    bus_data[dict_values['energyStorage'][sector][storage]['label']],
                                                    dict_values['energyStorage'][sector][storage])
                economics.get_costs(dict_values['energyStorage'][sector][storage], dict_values['economic_data'])

        for asset in dict_values['energyConversion']:
            process_results.get_results(dict_values['simulation_settings'], bus_data, dict_values['energyConversion'][asset])
            economics.get_costs(dict_values['energyConversion'][asset], dict_values['economic_data'])

        for group in ['energyProduction', 'energyConsumption']:
            for sector in dict_values[group]:
                for asset in dict_values[group][sector]:
                    process_results.get_results(dict_values['simulation_settings'], bus_data, dict_values[group][sector][asset])
                    economics.get_costs(dict_values[group][sector][asset], dict_values['economic_data'])

        logging.info('Evaluating optimized capacities and dispatch.')
        output.store_as_json(dict_values, 'json_with_results')
        return