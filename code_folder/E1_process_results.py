import logging
import pandas as pd
import pprint as pp
import matplotlib.pyplot as plt

class process_results:
    def get_timeseries_per_bus(dict_values, bus_data):
        bus_data_timeseries = {}
        for bus in bus_data.keys():
            bus_data_timeseries.update({bus: pd.DataFrame(index=dict_values['simulation_settings']['time_index'])})
            to_bus = {key[0][0]: key for key in bus_data[bus]['sequences'].keys() if key[0][1] == bus and key[1] == 'flow'}
            for asset in to_bus:
                bus_data_timeseries[bus][asset] = bus_data[bus]['sequences'][to_bus[asset]]

            from_bus = {key[0][1]: key for key in bus_data[bus]['sequences'].keys() if key[0][0] == bus and key[1] == 'flow'}
            for asset in from_bus:
                bus_data_timeseries[bus][asset] = - bus_data[bus]['sequences'][from_bus[asset]]

        #todo this should be moved to f0_output
        timeseries_output_file = '/timeseries_all_busses' + '.xlsx'
        with pd.ExcelWriter(
                dict_values['simulation_settings']['path_output_folder'] + timeseries_output_file) as open_file:  # doctest: +SKIP
            for bus in bus_data_timeseries.keys():
                bus_data_timeseries[bus].to_excel(open_file, sheet_name=bus)
                bus_data_timeseries[bus].plot()
                plt.savefig(dict_values['simulation_settings']['path_output_folder'] + '/' + bus + ' flows.png',
                            bbox_inches="tight")
                #plt.show()
                plt.close()
                plt.clf()
                plt.cla()

        logging.info('Saved flows at busses to: %s.', timeseries_output_file)
        return bus_data_timeseries

        logging.debug('Accessing oemof simulation results for asset %s', dict_asset['label'])
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