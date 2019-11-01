import logging

class process_results:
    def check_for_evaluation_keys(dict_values, dict_asset, bus_data):
        if isinstance(dict_asset, dict) and ('output_bus_name' in dict_asset.keys() or 'input_bus_name' in dict_asset.keys()):#('optimize_cap' in dict_asset.keys() or 'timeseries' in dict_asset.keys()):
            process_results.asset_in_out(dict_values['settings'], bus_data,  dict_asset)
        return

    def asset_in_out(settings, bus_data, dict_asset):
        logging.debug('Accessing oemof simulation results for asset %s', dict_asset['label'])
        if dict_asset['type'] == 'storage' and 'parent' not in dict_asset:
            process_results.get_storage_results(settings, bus_data, dict_asset)

        elif dict_asset['type'] == 'transformer':
            process_results.get_transformator_results(settings, bus_data, dict_asset)

        else:
            if dict_asset['type'] == 'source':
                direction = 'output_bus_name'
            elif dict_asset['type'] == 'sink':
                direction = 'input_bus_name'
            else: logging.warning('Unknown component type %s of asset %s', dict_asset['type'], dict_asset['label'])
            bus_name = dict_asset[direction]
            helpers.get_flow(settings, bus_data[bus_name], dict_asset)
            helpers.get_optimal_cap(bus_data[bus_name], dict_asset, direction)

        return

    def get_storage_results(settings, bus_data, dict_asset):
        storage_bus = bus_data[dict_asset['label']]
        power_charge = storage_bus['sequences'][((dict_asset['input_bus_name'], dict_asset['label']), 'flow')]
        helpers.add_info_flows(settings, dict_asset['charging_power'], power_charge)

        power_discharge = storage_bus['sequences'][
            ((dict_asset['label'], dict_asset['output_bus_name']), 'flow')]
        helpers.add_info_flows(settings, dict_asset['discharging_power'], power_discharge)

        capacity = storage_bus['sequences'][((dict_asset['label'], 'None'), 'capacity')]
        helpers.add_info_flows(settings, dict_asset['capacity'], capacity)

        if 'optimizeCap' in dict_asset:
            if dict_asset['optimizeCap'] == True:
                power_charge = storage_bus['scalars'][
                    ((dict_asset['input_bus_name'], dict_asset['label']), 'invest')]
                dict_asset['charging_power'].update({'optimizedAddCap': {'value': power_charge, 'unit': dict_asset['charging_power']['unit']}})
                logging.debug('Accessed optimized capacity of asset %s: %s', dict_asset['charging_power']['label'], power_charge)

                power_discharge = storage_bus['scalars'][
                    ((dict_asset['label'], dict_asset['output_bus_name']), 'invest')]
                dict_asset['discharging_power'].update({'optimizedAddCap': {'value': power_discharge, 'unit': dict_asset['discharging_power']['unit']}})
                logging.debug('Accessed optimized capacity of asset %s: %s', dict_asset['discharging_power']['label'], power_discharge)

                capacity = storage_bus['scalars'][((dict_asset['label'], 'None'), 'invest')]
                dict_asset['capacity'].update({'optimizedAddCap': {'value': capacity, 'unit': dict_asset['capacity']['unit']}})
                logging.debug('Accessed optimized capacity of asset %s: %s', dict_asset['capacity']['label'], capacity)

            else:
                dict_asset['charging_power'].update({'optimizedAddCap': {'value': 0, 'unit': dict_asset['capacity']['unit']}})
                dict_asset['discharging_power'].update({'optimizedAddCap': {'value': 0, 'unit': dict_asset['capacity']['unit']}})
                dict_asset['capacity'].update({'optimizedAddCap': {'value': 0, 'unit': dict_asset['capacity']['unit']}})

        dict_asset.update({'timeseries_soc': dict_asset['capacity']['flow'] /
                                             (dict_asset['capacity']['installedCap']['value']
                                              + dict_asset['capacity']['optimizedAddCap']['value'])})
        return

    def get_transformator_results(settings, bus_data, dict_asset):
        input_name = 'input_bus_name'
        helpers.get_flow(settings, bus_data[dict_asset[input_name]], dict_asset, direction=input_name)

        output_name = 'output_bus_name'
        helpers.get_flow(settings, bus_data[dict_asset[output_name]], dict_asset, direction=output_name)
        helpers.get_optimal_cap(bus_data[dict_asset[output_name]], dict_asset, 'output_bus_name')
        return
'''
class storage():
    if dict_asset['label'] == 'charging_power':
        storage.get_charging_power()
    elif dict_asset['label'] == 'discharging_power':
        storage.get_discharging_power()
    elif dict_asset['label'] == 'capacity':
        storage.get_capacity()
    else:
        print('error, asset not evaluates %s', dict_asset['label'])
    return
'''

class helpers:
    def get_optimal_cap(bus, dict_asset, direction):
        if 'optimizeCap' in dict_asset:
            if dict_asset['optimizeCap'] == True:
                if direction == 'input_bus_name':
                    optimal_capacity = bus['scalars'][((dict_asset['input_bus_name'], dict_asset['label']), 'invest')]
                elif direction == 'output_bus_name':
                    optimal_capacity = bus['scalars'][((dict_asset['label'], dict_asset['output_bus_name']), 'invest')]
                else:
                    logging.error('Function get_optimal_cap has invalid value of parameter direction.')

                if 'timeseries_peak' in dict_asset:
                    if dict_asset['timeseries_peak'] > 1:
                        dict_asset.update(
                            {'optimizedAddCap': {'value': optimal_capacity * dict_asset['timeseries_peak'], 'unit': dict_asset['unit']}})

                    elif dict_asset['timeseries_peak'] > 0 and dict_asset['timeseries_peak'] < 1:
                        dict_asset.update(
                            {'optimizedAddCap': optimal_capacity / dict_asset['timeseries_peak']})
                    else:
                        logging.warning(
                            'Time series peak of asset %s negative! Check timeseries. No optimized capacity derived.',
                            dict_asset['label'])
                        pass
                else:
                    dict_asset.update({'optimizedAddCap': optimal_capacity})
            else:
                dict_asset.update({'optimizedAddCap': 0})
            logging.debug('Accessed optimized capacity of asset %s: %s', dict_asset['label'], optimal_capacity)

        return

    def get_flow(settings, bus, dict_asset, **kwargs):
        if dict_asset['type']=='transformer':
            if kwargs['direction'] == 'input_bus_name':
                flow = bus['sequences'][((dict_asset[kwargs['direction']], dict_asset['label']), 'flow')]
            elif kwargs['direction'] == 'output_bus_name':
                flow = bus['sequences'][((dict_asset['label'], dict_asset[kwargs['direction']]), 'flow')]
            else: logging.error('Invalid argument direction in get_flow')
            helpers.add_info_flows(settings, dict_asset, flow)

        else:
            if 'input_bus_name' in dict_asset:
                flow = bus['sequences'][((dict_asset['input_bus_name'], dict_asset['label']), 'flow')]
            elif 'output_bus_name' in dict_asset:
                flow = bus['sequences'][((dict_asset['label'], dict_asset['output_bus_name']), 'flow')]
            else:
                logging.warning('Neither input- nor output bus defined!')

            helpers.add_info_flows(settings, dict_asset, flow)

        logging.debug('Accessed simulated timeseries of asset %s (total sum: %s)', dict_asset['label'], round(dict_asset['total_flow']))
        return

    def add_info_flows(settings, dict_asset, flow):
        total_flow = sum(flow)
        dict_asset.update({'flow': flow,
                           'total_flow': {'value': total_flow, 'unit': 'kWh'},
                           'annual_total_flow': {'value': total_flow * 365 / settings['evaluated_period']['value'], 'unit': 'kWh'},
                           'peak_flow': {'value': max(flow), 'unit': 'kW'},
                           'average_flow': {'value': total_flow / len(flow), 'unit': 'kW'}})
        return