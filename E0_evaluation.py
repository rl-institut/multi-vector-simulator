import logging
import oemof.outputlib as outputlib
from E1_process_results import process_results

class evaluation:

    def evaluate_dict(dict_values, results_main, results_meta, dict_model):
        bus_data={}
        for bus in dict_model['busses']:
            # Read all energy flows from busses
            bus_data.update({bus: outputlib.views.node(results_main, bus)})

        for storage in dict_model['storages']:
            # Read all energy flows from storage
            bus_data.update({storage: outputlib.views.node(results_main, storage)})

        for item in dict_values.keys():
            process_results.check_for_evaluation_keys(dict_values, dict_values[item], bus_data)
            for subitem in dict_values[item].keys():
                process_results.check_for_evaluation_keys(dict_values, dict_values[item][subitem], bus_data)

        return

