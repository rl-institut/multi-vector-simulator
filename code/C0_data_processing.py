from .C1_verification import verify
from .C2_economic_functions import economics
import pandas as pd
import logging
import sys, shutil
import json
import numpy
import pandas as pd

from copy import deepcopy

class data_processing:
    def all(dict_values):
        data_processing.simulation_settings(dict_values['simulation_settings'])

        ## Verify inputs
        # check whether input values can be true
        verify.check_input_values(dict_values)
        # Check, whether files (demand, generation) are existing
        helpers.evaluate_timeseries(dict_values, verify.lookup_file, 'verify')
        ## Complete data values
        # Receive data from timeseries and process their format
        helpers.evaluate_timeseries(dict_values, receive_data.timeseries_csv, 'receive_data')
        #todo add option to receive data online

        for sector in dict_values['project_data']['sectors']:
            helpers.define_sink(dict_values, 'excess', None, sector)

        # Add symbolic costs
        if 'electricity_storage' in dict_values:
            helpers.create_twins_in_out(dict_values['electricity_storage'], 'charge_controller', drop_symbolic_costs=True)
        if 'transformer_station' in dict_values:
            helpers.create_twins_in_out(dict_values, 'transformer_station', drop_symbolic_costs=True)
            helpers.define_source(dict_values, 'transformer_station', 'electricity_price_var_kWh')
            helpers.define_sink(dict_values, 'transformer_station', 'feedin_tariff')

        helpers.add_input_output_busses(dict_values)

        # Adds costs to each asset and sub-asset
        data_processing.economic_data(dict_values)

        data_processing.store_as_json(dict_values)
        return

    def simulation_settings(simulation_settings):
        simulation_settings.update({'start_date': pd.to_datetime(simulation_settings['start_date'])})
        simulation_settings.update({'end_date': simulation_settings['start_date']
                                                               +pd.DateOffset(
                                            days=simulation_settings['evaluated_period']['value'],
                                            hours=-1)})

        simulation_settings.update({
            'time_index': pd.date_range(start=simulation_settings['start_date'],
                                        end=simulation_settings['end_date'],
                                        freq=str(simulation_settings['timestep']['value']) + 'min')})

        simulation_settings.update({'periods': len(simulation_settings['time_index'])})
        return simulation_settings

    def economic_data(dict_values):
        # Calculate annuitiy factor
        dict_values['economic_data'].update({
            'annuity_factor':
                {'value': economics.annuity_factor(dict_values['economic_data']['project_duration']['value'],
                dict_values['economic_data']['discount_factor']['value']),
                'unit': '?'}})

        # Calculate crf
        dict_values['economic_data'].update({
            'crf':
                {'value': economics.crf(
                dict_values['economic_data']['project_duration']['value'],
                dict_values['economic_data']['discount_factor']['value']),
                'unit': "?"}})

        # add sources and sinks depending on items in energy providers as pre-processing
        for sector in dict_values['energyProviders']:
            for dso in dict_values['energyProviders'][sector]:
                helpers.define_dso_sinks_and_sources(dict_values, sector, dso)

        # Add lifetime capex (incl. replacement costs), calculate annuity (incl. om), and simulation annuity to each asset
        for asset in dict_values['energyConversion']:
            print(asset)
            helpers.define_missing_cost_data(dict_values['economic_data'],
                                            dict_values['energyConversion'][asset])
            helpers.evaluate_lifetime_costs(dict_values['simulation_settings'],
                                            dict_values['economic_data'],
                                            dict_values['energyConversion'][asset])

        # Add lifetime capex (incl. replacement costs), calculate annuity (incl. om), and simulation annuity to each asset
        list_asset_groups = ['fixCost', 'energyConsumption', 'energyStorage', 'energyProduction', 'energyProviders']
        for group in list_asset_groups:
            for sector in dict_values[group]:
                for asset in dict_values[group][sector]:
                    print(group, sector, asset)
                    helpers.define_missing_cost_data(dict_values['economic_data'],
                                                     dict_values[group][sector][asset])
                    helpers.evaluate_lifetime_costs(dict_values['simulation_settings'],
                                                    dict_values['economic_data'],
                                                    dict_values[group][sector][asset])

        logging.info('Processed cost data and added economic values.')
        return

    def store_as_json(dict_values):
        # This converts all data stored in dict_values that is not compatible with the json format to a format that is compatible.
        def convert(o):
            if isinstance(o, numpy.int64): return int(o)
            # todo this actually dropt the date time index, which could be interesting
            if isinstance(o, pd.DatetimeIndex): return "date_range"
            if isinstance(o, pd.datetime): return str(o)
            # todo this also drops the timeindex, which is unfortunate.
            if isinstance(o, pd.Series): return "pandas timeseries" #o.values
            if isinstance(o, numpy.ndarray): return "numpy timeseries" #o.tolist()
            if isinstance(o, pd.DataFrame): return "pandas dataframe" #o.to_json(orient='records')
            logging.error('An error occurred when converting the simulation data (dict_values) to json, as the type is not recognized: \n'
                          'Type: '+str(type(o)) +' \n'
                          'Value(s): ' + str(o) + '\n'
                          'Please edit function CO_data_processing.dataprocessing.store_as_json.')
            raise TypeError

        myfile = open(dict_values['simulation_settings']['path_output_folder'] + '/json_input_processed.json', 'w')
        json_data = json.dumps(dict_values, skipkeys=True, sort_keys=True, default=convert, indent=4)
        myfile.write(json_data)
        myfile.close()
        return

class helpers:
    def define_missing_cost_data(economic_data, dict_asset):
        basic_costs = {"capex_fix": {"value": 0, "unit": "currency"},
                       "capex_var": {"value": 0, "unit": "currency/unit"},
                       "opex_fix": {"value": 0, "unit": "currency/year"},
                       "opex_var": {"value": 0, "unit": "currency/unit/year"},
                       "lifetime": {"value": economic_data['project_duration']['value'],
                                    "unit": "year"}}

        for cost in basic_costs:
            if cost not in dict_asset:
                dict_asset.update({cost: basic_costs[cost]})
        return

    def define_dso_sinks_and_sources(dict_values, sector, dso):
        number_of_pricing_periods = dict_values['energyProviders'][sector][dso]['peak_demand_pricing_period']['value']
        months_in_a_period = 12/number_of_pricing_periods
        if number_of_pricing_periods == 1:
            timeseries = pd.Series(1, index=dict_values['simulation_settings']['time_index'])
            helpers.define_source(dict_values,
                                  dso + '_consumption',
                                  dict_values['energyProviders'][sector][dso]['energy_price']['value'],
                                  dict_values['energyProviders'][sector][dso]['outflow_direction'],
                                  timeseries)
        else:
            for pricing_period in range(1, number_of_pricing_periods+1):
                timeseries = pd.Series(0, index=dict_values['simulation_settings']['time_index'])
                time_period = pd.date_range(
                    start=dict_values['simulation_settings']['start_date']
                          + pd.DateOffset(months=(pricing_period-1)*months_in_a_period),
                    end=dict_values['simulation_settings']['start_date']
                          + pd.DateOffset(months=pricing_period*months_in_a_period),
                    freq=str(dict_values['simulation_settings']['timestep']['value']) + 'min')

                timeseries = timeseries.add(pd.Series(1, index=time_period), fill_value=0)

                helpers.define_source(dict_values,
                                      dso + '_consumption_period_'+str(pricing_period),
                                      dict_values['energyProviders'][sector][dso]['energy_price']['value'],
                                      dict_values['energyProviders'][sector][dso]['outflow_direction'],
                                      timeseries)

        helpers.define_sink(dict_values,
                            dso + '_feedin',
                            -dict_values['energyProviders'][sector][dso]['feedin_tariff']['value'],
                            dict_values['energyProviders'][sector][dso]['inflow_direction'])

        return

    def create_twins_in_out(dict_asset, name_subasset, drop_symbolic_costs):
        subasset = dict_asset[name_subasset]
        subasset.update({'label': name_subasset + '_in'})
        subasset_symbolic = deepcopy(subasset)
        subasset_symbolic.update({'label': name_subasset + '_out'})
        if drop_symbolic_costs == True:
            for cost in ['capex', 'opex']:
                for suffix in ['_var', '_fix']:
                    subasset_symbolic.update({cost + suffix: 0})
        elif drop_symbolic_costs == False:
            pass
        else:
            logging.error('Coding error: drop_symbolic_costs has to be True/False.')

        del dict_asset[name_subasset]
        dict_asset.update({name_subasset: {'label': name_subasset+'_in_out',
                                           'in': subasset,
                                           'out': subasset_symbolic}})

        dict_asset[name_subasset]['in'].update({'type': 'transformer'})
        dict_asset[name_subasset]['out'].update({'type': 'transformer'})
        return

    def define_source(dict_values, asset_name, price, output_bus_name, timeseries):
        source = {'type': 'source',
                'label': asset_name + '_source',
                'output_bus_name': output_bus_name,
                'timeseries': timeseries,
                "opex_var": {"value": price, "unit": "currency/unit"},
                "lifetime": {"value": dict_values['economic_data']['project_duration']['value'],
                             "unit": "year"}
                }

        # create new input bus if non-existent before
        if output_bus_name not in dict_values['energyProduction'].keys():
            dict_values['energyProduction'].update({output_bus_name: {}})

        # update dictionary
        dict_values['energyProduction'][output_bus_name].update({asset_name: source})
        return

    def define_sink(dict_values, asset_name, price, input_bus_name):
        # create a dictionary for the sink
        sink = {'type': 'sink',
                'label': asset_name + '_sink',
                'input_bus_name': input_bus_name,
                "opex_var": {"value": price, "unit": "currency/kWh"},
                "lifetime": {"value": dict_values['economic_data']['project_duration']['value'],
                             "unit": "year"}
                }

        # create new input bus if non-existent before
        if input_bus_name not in dict_values['energyConsumption'].keys():
            dict_values['energyConsumption'].update({input_bus_name: {}})

        # update dictionary
        dict_values['energyConsumption'][input_bus_name].update({asset_name: sink})
        return

    def add_input_output_busses(dict_values):
        for asset in dict_values.keys():
            if asset in ['project_data', 'settings', 'economic_data', 'simulation_settings', ]:
                pass
            elif asset == 'electricity_grid':
                logging.warning('%s has not been included in model jet, specifically efficiency.', asset)

            elif asset == 'electricity_excess':
                dict_values[asset].update({'input_bus_name': 'electricity'})

            elif asset == 'transformer_station':
                dict_values[asset]['in'].update({'input_bus_name': dict_values[asset]['in']['sector'] + '_utility_consumption',
                                                 'output_bus_name': dict_values[asset]['in']['sector']})
                dict_values[asset]['source'].update({'output_bus_name': dict_values[asset]['in']['sector'] + '_utility_consumption'})
                dict_values[asset]['out'].update({'input_bus_name': dict_values[asset]['out']['sector'],
                                                  'output_bus_name': dict_values[asset]['out']['sector'] + '_utility_feedin'})
                dict_values[asset]['sink'].update({'input_bus_name': dict_values[asset]['in']['sector'] + '_utility_feedin'})

            elif asset == 'pv_plant':
                dict_values[asset]['pv_installation'].update({'output_bus_name': 'electricity_dc_pv'})
                dict_values[asset]['solar_inverter'].update({'input_bus_name': 'electricity_dc_pv',
                                                             'output_bus_name': 'electricity'})
            elif asset == 'wind_plant':
                dict_values[asset]['wind_installation'].update({'output_bus_name': 'electricity'})

            elif asset == 'electricity_storage':
                dict_values[asset].update({'input_bus_name': 'electricity_dc_storage',
                                           'output_bus_name': 'electricity_dc_storage'})
                dict_values[asset]['charge_controller']['in'].update({'input_bus_name': 'electricity',
                                                              'output_bus_name': 'electricity_dc_storage'})
                dict_values[asset]['charge_controller']['out'].update({'input_bus_name': 'electricity_dc_storage',
                                                                       'output_bus_name': 'electricity'})

            elif asset == 'generator':
                dict_values[asset].update({'input_bus_name': 'Fuel',
                                   'output_bus_name': 'electricity'})

            elif asset == 'electricity_demand':
                for demand in dict_values[asset].keys():
                    if demand != 'label':
                        dict_values[asset][demand].update({'input_bus_name': 'electricity'})

            else:
                logging.warning('Asset %s undefined, no input/output busses added.', asset)

        return

    def evaluate_lifetime_costs(settings, economic_data, dict_asset):
        if 'capex_var' not in dict_asset:
            dict_asset.update({'capex_var': 0})

        dict_asset.update({'lifetime_capex_var':
                               {'value':
                                    economics.capex_from_investment(dict_asset['capex_var']['value'],
                                                                    dict_asset['lifetime']['value'],
                                                                    economic_data['project_duration']['value'],
                                                                    economic_data['discount_factor']['value'],
                                                                    economic_data['tax']['value']),
                                'unit': dict_asset['capex_var']['unit']}
                           })

        # Annuities of components including opex AND capex #
        dict_asset.update({'annuity_capex_opex_var':
                               {'value':
                                    economics.annuity(dict_asset['lifetime_capex_var']['value'],
                                                         economic_data['crf']['value'])
                                    + dict_asset['opex_fix']['value'],
                                'unit': dict_asset['lifetime_capex_var']['unit']+'/a'}
                           })


        dict_asset.update({'lifetime_opex_fix':
                               {'value': dict_asset['opex_fix']['value'] * economic_data['annuity_factor']['value'],
                                'unit': dict_asset['opex_fix']['unit'][:-2]}
                            })

        dict_asset.update({'lifetime_opex_var':
                               {'value': dict_asset['opex_var']['value'] * economic_data['annuity_factor']['value'],
                                'unit': "?"}
                                       })

        # Scaling annuity to timeframe
        # Updating all annuities above to annuities "for the timeframe", so that optimization is based on more adequate
        # costs. Includes project_cost_annuity, distribution_grid_cost_annuity, maingrid_extension_cost_annuity for
        # consistency eventhough these are not used in optimization.
        dict_asset.update({'simulation_annuity':
                                       dict_asset['annuity_capex_opex_var']['value'] / 365
                                       * settings['evaluated_period']['value']})

        return

    def evaluate_timeseries(dict_values, function, use):
        input_folder = dict_values['simulation_settings']['path_input_folder']
        # Accessing timeseries of components
        for asset_name in ['pv_plant', 'wind_plant']:
            if asset_name in dict_values:
                if asset_name == 'pv_plant':
                    sub_name = 'pv_installation'
                elif asset_name == 'wind_plant':
                    sub_name = 'wind_installation'
                file_path = input_folder + dict_values[asset_name][sub_name]['file_name']
                # Check if file existent
                if use == 'verify':
                    # check if specific demand timeseries exists
                    function(file_path, asset_name)
                elif use == 'receive_data':
                    # receive data and write it into dict_values
                    function(dict_values['settings'], dict_values['simulation_settings'], dict_values[asset_name][sub_name], file_path, asset_name)

        # Accessing timeseries of demands
        for demand_type in ['electricity_demand', 'heat_demand']:
            if demand_type in dict_values:
                # Check for each
                for demand_key in dict_values['electricity_demand']:
                    if demand_key != 'label':
                        file_path = input_folder + dict_values[demand_type][demand_key]['file_name']
                        if use == 'verify':
                            # check if specific demand timeseries exists
                            function(file_path, demand_key)
                        elif use == 'receive_data':
                            # receive data and write it into dict_values
                            function(dict_values['settings'], dict_values['simulation_settings'], dict_values[demand_type][demand_key], file_path, demand_key)
        return

class receive_data:
    def timeseries_csv(settings, user_input, dict_asset, file_path, name):
        data_set = pd.read_csv(file_path, sep=';')
        if len(data_set.index) == settings['periods']:
            dict_asset.update({'timeseries': pd.Series(data_set['kW'].values, index = settings['index'])})
            logging.debug('Added timeseries of %s (%s).', name, file_path)
        elif len(data_set.index) >= settings['periods']:
            dict_asset.update({'timeseries': pd.Series(data_set['kW'][0:len(settings['index'])].values,
                                                          index=settings['index'])})
            logging.info('Provided timeseries of %s (%s) longer than evaluated period. '
                         'Excess data dropped.', name, file_path)

        elif len(data_set.index) <= settings['periods']:
            logging.critical('Input errror! '
                             'Provided timeseries of %s (%s) shorter then evaluated period. '
                             'Operation terminated', name, file_path)
            sys.exit()

        dict_asset.update({'timeseries_peak': max(dict_asset['timeseries']),
                           'timeseries_total': sum(dict_asset['timeseries']),
                           'timeseries_average': sum(dict_asset['timeseries'])/len(dict_asset['timeseries'])})

        shutil.copy(file_path, user_input['path_output_folder_inputs']+dict_asset['file_name'])
        logging.debug('Copied timeseries %s to output folder / inputs.', file_path)
        return

    #get timeseries from online source
    def timeseries_online():
        return
