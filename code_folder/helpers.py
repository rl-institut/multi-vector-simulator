
def evaluate_dict(dict_values, bus_data):
    for item in dict_values.keys():
        print(item)
        helpers.check_for_evaluation_keys(dict_values, dict_values[item], bus_data)

        for subitem in dict_values[item].keys():
            helpers.check_for_evaluation_keys(dict_values, dict_values[item][subitem], bus_data)

            # dict_values[item].update({'type': 'source'})
            #dict_values[item][subitem].update({'parent': item})
            # helpers.check_for_evaluation_keys(dict_values[item][subitem])

class helpers:
    def check_for_evaluation_keys(dict_values, dict_asset, bus_data):
        if 'optimize_cap' in dict_asset.keys() or 'timeseries' in dict_asset.keys():
                bus_name = dict_asset['output_bus_name']
                process_results.asset_in_out(dict_values['settings'],
                                     bus_data[bus_name],
                                     dict_asset['label'],
                                     dict_asset)

        return

class process_results:
    def asset_in_out(settings, bus, type, dict_asset):
        logging.debug('Accessing oemof simulation results for asset %s', dict_asset['label'])
        if type != 'storage':
            helpers.get_flow_and_optimal_cap(settings, bus, dict_asset)

        else:
            print(dict_asset)
            helpers.get_flow(settings, bus, dict_asset['power_charge'])
            helpers.get_flow(settings, bus, dict_asset['power_discharge'])
            helpers.get_flow(settings, bus, dict_asset['capacity'])

            helpers.get_flow_and_optimal_cap(settings, bus, dict_asset)
            if 'optimize_cap' in dict_asset:

                if dict_asset['optimize_cap'] == True:
                    power_charge = bus['sequences'][((dict_asset['power_charge']['input_bus_name'], dict_asset['label']), 'flow')]
                    dict_asset['power_charge'].update({'optimizedAddCap': power_charge})

                    power_discharge = bus['sequences'][
                        ((dict_asset['label'], dict_asset['power_discharge']['output_bus_name']), 'flow')]
                    dict_asset['power_charge'].update({'optimizedAddCap': power_discharge})

                    capacity = bus['sequences'][((dict_asset['label'], 'None'), 'capacity')]
                    dict_asset['capacity'].update({'optimizedAddCap': capacity})

                else:
                    dict_asset['power_charge'].update({'optimizedAddCap': 0})
                    dict_asset['power_charge'].update({'optimizedAddCap': 0})
                    dict_asset['capacity'].update({'optimizedAddCap': 0})

            dict_asset.update({'timeseries_soc': dict_asset['capacity']['flow'] /
                                                 (dict_asset['capacity']['installedCap']
                                                  + dict_asset['capacity']['optimizedAddCap'])})

        logging.info('Accessed simulation results of %s', dict_asset['label'])

        return