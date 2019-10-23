import logging
import oemof.outputlib as outputlib
from .E1_process_results import process_results
from .E2_economics import economics

class evaluation:
    def evaluate_dict(dict_values, results_main, results_meta, dict_model):
        bus_data={}
        for bus in dict_model['busses']:
            # Read all energy flows from busses
            bus_data.update({bus: outputlib.views.node(results_main, bus)})

        for storage in dict_model['storages']:
            # Read all energy flows from storage
            bus_data.update({storage: outputlib.views.node(results_main, storage)})

        logging.info('Evaluating optimized capacities and dispatch.')
        for item in dict_values.keys():
            process_results.check_for_evaluation_keys(dict_values, dict_values[item], bus_data)
            for subitem in dict_values[item].keys():
                process_results.check_for_evaluation_keys(dict_values, dict_values[item][subitem], bus_data)
                if isinstance(dict_values[item][subitem], dict):
                    for subsubitem in dict_values[item][subitem].keys():
                        process_results.check_for_evaluation_keys(dict_values, dict_values[item][subitem][subsubitem], bus_data)

        logging.info('Calculating costs of asset investment and usage.')
        for item in dict_values.keys():
            economics.get_costs(dict_values[item], dict_values['economic_data'])
            for subitem in dict_values[item].keys():
                economics.get_costs(dict_values[item][subitem], dict_values['economic_data'])
                if isinstance(dict_values[item][subitem], dict):
                    for subsubitem in dict_values[item][subitem].keys():
                        economics.get_costs(dict_values[item][subitem][subsubitem], dict_values['economic_data'])

        return
