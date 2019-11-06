import pandas as pd
import logging
import pprint as pp
try:
    from .B1_read_excel import read_template
except ImportError:
    from code_folder.B1_read_excel import read_template

class data_input:
    def all(user_input):
        # Read from excel sheet, tab overview: Which components are used?
        included_assets = read_template.overview_energy_system(user_input)

        dict_values = {}

        logging.debug('Get all project data from tab "Project data".')
        project_data, simulation_settings, economic_data = get_values.project_data(user_input)
        dict_values.update({'project_data': project_data})
        dict_values.update({'settings': simulation_settings})
        dict_values.update({'economic_data': economic_data})

        # generate dictionary of asset parameters from needed assets in scenario
        logging.debug('Determining the data for all assets')
        pp.pprint(included_assets)
        for asset_group in included_assets.keys():
            if asset_group == 'sectors':
                logging.debug('...get data for each sector.')
                for asset_group_item in included_assets[asset_group]:
                    dict_asset_group_item = get_values.sectors(user_input, asset_group_item)
                    dict_values.update(dict_asset_group_item)
            elif asset_group == 'demands':
                # demands is directly included in sectors
                pass
            else:
                logging.debug('...get data for each asset of group %s.', asset_group)
                for asset_group_item in included_assets[asset_group]:
                    # Access each component individually
                    dict_asset_group_item = get_values.components(user_input, asset_group_item)
                    dict_values.update(dict_asset_group_item)
                    pass

        return dict_values, included_assets

class get_values:
    def project_data(user_input):
        '''
        :param user_input:
        :return:
        '''
        # Definition of data red from excel
        dict_excel_data = {'tab_name': 'Project data',
                           'first_row': 2,
                           'number_of_rows': 27,
                           'column_string': 'B:C',
                           'index_col': 0}

        data = read_template.read_excel_dict(user_input, dict_excel_data)

        data = data['Unnamed: 2'] #todo - How to avoid this?

        project_data = {'label': 'project_data',
                        'project_name': data['Project location name'],
                        'scenario_name': data['Scenario'],
                        'country': data['Country'],
                        'longitude': data['Location, longitude'],
                        'latitude': data['Location, latitude'],
                        'capex_fix': data['CAPEX \n(investment costs, 1st year)'],
                        'opex_fix': data['OPEX \n(operational costs, 1st year)']}

        simulation_settings = {'label': 'settings',
                               'evaluated_period': int(data['Evaluated timeframe']),
                               'time_step': int(data['Time step']),
                               'start_date': pd.Timestamp(data['Start date'])}

        simulation_settings.update({'index': pd.date_range(start=simulation_settings['start_date'],
                                                           end = simulation_settings['start_date']
                                                                 + pd.DateOffset(days=simulation_settings['evaluated_period'],
                                                                                 hours=-1),
                                                           freq=str(simulation_settings['time_step'])+'min')})
        simulation_settings.update({'periods': len(simulation_settings['index'])})

        economic_data = {'label': 'economic_data',
                         'discount_factor': data['WACC']/100,
                         'project_duration': data['Project duration'],
                         'tax': data['Tax']/100,
                         'currency': data['Currency']}

        return project_data, simulation_settings, economic_data

    def sectors(user_input, asset_group_item):
        '''
        :param user_input:
        :param asset_group_item:
        :return:
        '''
        logging.debug('Receiving data of sector "%s".', asset_group_item)
        # Captialization and spaces due to excel file input
        if asset_group_item == 'Electricity':
            dict_sector = assets.electricity_sector(user_input)
        elif asset_group_item == 'Heat':
            dict_sector = {}
            logging.error('Input data extraction of sector "%s" not defined!', asset_group_item)
            pass
        elif asset_group_item == 'Gas':
            logging.error('Input data extraction of sector "%s" not defined!', asset_group_item)
            pass
        elif asset_group_item == 'Electric mobility':
            logging.error('Input data extraction of sector "%s" not defined!', asset_group_item)
            pass
        elif asset_group_item == 'H2':
            logging.error('Input data extraction of sector "%s" not defined!', asset_group_item)
            pass

        return dict_sector

    def components(user_input, asset_group_item):
        '''
        :param user_input:
        :param asset_group_item:
        :return:
        '''
        logging.debug('Receiving data of asset "%s".', asset_group_item)
        # Access all data of specific asset
        if asset_group_item == 'PV plant':
            dict_value_specific = assets.pv(user_input, asset_group_item)
        elif asset_group_item == 'Wind plant':
            logging.error('Input data extraction of asset "%s" not defined!', asset_group_item)
            dict_value_specific = assets.wind(user_input, asset_group_item)
        elif asset_group_item == 'transformer_station':
            dict_value_specific = assets.transformer_station(user_input, asset_group_item)
        elif asset_group_item == 'rectifier':
            logging.error('Input data extraction of asset "%s" not defined!', asset_group_item)
            dict_value_specific = assets.rectifier(user_input, asset_group_item)
        elif asset_group_item == 'inverter':
            logging.error('Input data extraction of asset "%s" not defined!', asset_group_item)
            dict_value_specific = assets.inverter(user_input, asset_group_item)
        elif asset_group_item == 'generator':
            logging.error('Input data extraction of asset "%s" not defined!', asset_group_item)
            dict_value_specific = assets.generator(user_input, asset_group_item)
        elif asset_group_item == 'ESS':
            dict_value_specific = assets.electricity_storage(user_input, asset_group_item)
        else:
            logging.critical('Component %s can not be simulated, as it is not defined!', asset_group_item)

        return dict_value_specific

    def demand(user_input, dict_excel_data):
        '''
        :param user_input:
        :param dict_excel_data:
        :return:
        '''
        #todo this would require a test on whether or not profile exists!

        # Reading demand profiles
        data = read_template.read_excel_tab(user_input, dict_excel_data)
        data = data.transpose().to_dict(orient='dict')

        all_titles = {'Demand side management (DSM)***':   'dsm',
                      'File (csv)':     'file_name'}

        dict_demands = {'label': 'electricity_demand'}
        for demand_number in data.keys():
            demand_name = data[demand_number]['Demand name']
            demand_name = demand_name.replace("(", "")
            demand_name = demand_name.replace(")", "")
            demand_name = demand_name.replace(" ", "_")
            dict_demands.update({demand_name: {}})
            for item in all_titles.keys():
                if item in data[demand_number].keys():
                    if item == 'Demand side management (DSM)***':
                        if data[demand_number][item] == 'Yes':
                            dict_demands[demand_name].update({all_titles[item]: True})
                        elif data[demand_number][item] == 'No':
                            dict_demands[demand_name].update({all_titles[item]: False})
                        else:
                            logging.warning('Input error: %s\n'
                                            'Demand side management of an demand series can only be (Yes/No).', dict_excel_data['tab_name'])

                    else:
                        dict_demands[demand_name].update({all_titles[item]: data[demand_number][item],
                                                          'parent': 'demand',
                                                          'label': demand_name,
                                                          'type': 'sink'})

        return dict_demands

class helpers:
    def cost_info(user_input, tab_name, name_list):
        '''
        :param user_input:
        :param tab_name:
        :param name_list:
        :return:
        '''
        dict_all_cost_data = {}
        dict_excel_data = {}
        for item in range(0, len(name_list)):
            dict_excel_data.update({
                'tab_name': tab_name,
                'first_row': 4 + 3 * item,
                'number_of_rows': 3,
                'column_string': 'B,C,E',
                'index_col': 0})

            data = read_template.read_excel_dict(user_input, dict_excel_data)
            dict_all_cost_data.update({name_list[item]:
                                           {'capex_fix': data['Fix']['CAPEX \n(investment costs, 1st year)'],
                                            'capex_var': data['Var']['CAPEX \n(investment costs, 1st year)'],
                                            'opex_fix': data['Fix']['OPEX \n(operational costs, 1st year)'],
                                            'opex_var': data['Var']['OPEX \n(operational costs, 1st year)']}})

        return dict_all_cost_data

    def parameters(user_input, dict_excel_data):
        '''
        :param user_input:
        :param dict_excel_data:
        :return:
        '''
        data = read_template.read_excel_dict(user_input, dict_excel_data)
        data = data['Value']
        all_titles = {'Lifetime':                       'lifetime',
                      'Age of installed asset':         'age_installed',
                      'Installed capacity':             'installedCap',
                      'Efficiency':                     'efficiency',
                      'Inverter efficiency':            'efficiency',
                      'Distribution efficiency':        'efficiency',
                      'Feed-in tariff':                 'feedin_tariff',
                      'Optimize additional capacities': 'optimize_cap'}

        dict_asset = {}
        for item in all_titles.keys():
            if item in data.keys():
                if item == 'Optimize additional capacities':
                    if data[item] in ['yes', 'Yes', 'y']:
                        dict_asset.update({all_titles[item]:True})
                    elif data[item] in ['no', 'No', 'n']:
                        dict_asset.update({all_titles[item]: False})
                    else:
                        logging.warning('Input error: %s\n'
                                        '%s on tab %s can only be (Yes/No).',
                                        item, user_input['tab_name'])
                elif all_titles[item] == 'efficiency':
                    dict_asset.update({all_titles[item]: data[item]/100})
                else:
                    dict_asset.update({all_titles[item]: data[item]})

        return dict_asset

class assets:
    def electricity_sector(user_input):
        '''
        :param user_input:
        :return:
        '''
        tab_name = 'Electricity'
        # Definition of data cells on excel template tab
        dict_excel_data = {'electricity_grid': {'tab_name': tab_name,
                                         'first_row': 14,
                                         'number_of_rows': 4,
                                         'column_string': 'B:C',
                                         'index_col': 0},
                           'demand': {'tab_name': tab_name,
                                      'first_row': 33,
                                      'number_of_rows': 4,
                                      'column_string': 'B:E',
                                      'index_col': 0}}

        ## Retrieving all data concerning the electricity sector
        electricity_sector = {}
        # Parameters distribution grid
        dict_asset = helpers.parameters(user_input, dict_excel_data['electricity_grid'])
        electricity_sector.update(dict_asset)
        electricity_sector.update({'label': 'electricity_grid'})
        ## Retrieving all data concerning the electricity demand profiles
        demand_profiles = get_values.demand(user_input, dict_excel_data['demand'])
        dict_sector = {'electricity_grid': electricity_sector,
                       'electricity_demand': demand_profiles}

        # Retrieving cost info
        dict_costs = helpers.cost_info(user_input, tab_name, ['electricity_grid', 'transformer_station'])
        dict_sector['electricity_grid'].update(dict_costs['electricity_grid'])
        return dict_sector

    def transformer_station(user_input, tab_name):#
        '''
        :param user_input:
        :param tab_name:
        :return:
        '''
        tab_name = 'Electricity'
        # Definition of data cells on excel template tab
        dict_excel_data = {'transformer_station': {'tab_name': tab_name,
                                                   'first_row': 19,
                                                   'number_of_rows': 7,
                                                   'column_string': 'B:C',
                                                   'index_col': 0},
                           'bill_cons': {'tab_name': tab_name,
                                         'first_row': 28,
                                         'number_of_rows': 3,
                                         'column_string': 'B,C,E,G,I',
                                         'index_col': 0}}

        ## Retrieving all data concerning the electricity sector
        transformer_station = {}
        # Parameters transformer station
        dict_asset = helpers.parameters(user_input, dict_excel_data['transformer_station'])
        transformer_station.update(dict_asset)
        # electricity bill
        data = read_template.read_excel_dict(user_input, dict_excel_data['bill_cons'])
        transformer_station.update({
            'electricity_cost_fix_annual':
                data['Fix annual cost']['Electricity supplier'] + data['Fix annual cost']['DSO'] +
                12 * (data['Fix monthly cost']['Electricity supplier'] +
                      data['Fix monthly cost']['DSO']),
            'electricity_price_var_kWh':
                data['Variable cost per kWh supplied']['Electricity supplier']
                + data['Variable cost per kWh supplied']['DSO'],
            'electricity_price_var_kW_monthly':
                data['Variable cost per kW peak demand/month ']['Electricity supplier']
                + data['Variable cost per kW peak demand/month ']['DSO']})

        # Retrieving cost info
        dict_costs = helpers.cost_info(user_input, tab_name, ['electricity_grid', 'transformer_station'])
        transformer_station.update(dict_costs['transformer_station'])
        transformer_station.update({'label': 'transformer_station',
                                    'sector': 'electricity',
                                    'type': 'transformers'})
        transformer_station = {'transformer_station': transformer_station}
        return transformer_station

    # PV panels
    def pv(user_input, asset_group_item):
        tab_name = asset_group_item

        # Definition of data cells on excel template tab
        dict_excel_data = {'pv_installation': {'tab_name': tab_name,
                                                   'first_row': 14,
                                                   'number_of_rows': 5,
                                                   'column_string': 'B:C',
                                                   'index_col': 0},
                           'solar_inverter': {'tab_name': tab_name,
                                                   'first_row': 20,
                                                   'number_of_rows': 6,
                                                   'column_string': 'B:C',
                                                   'index_col': 0},
                           'file_name': {'tab_name': tab_name,
                                               'first_row': 28,
                                               'number_of_rows': 2,
                                               'column_string': 'B:C',
                                               'index_col': 0},
                           }

        ## Retrieving all data concerning the electricity sector
        dict_asset = {'pv_installation': {},
                      'solar_inverter': {}}
        # Parameters solar panels
        dict_asset_parameters = helpers.parameters(user_input, dict_excel_data['pv_installation'])
        dict_asset['pv_installation'].update(dict_asset_parameters)
        data = read_template.read_excel_tab(user_input, dict_excel_data['file_name'])
        # todo: check if exists
        dict_asset['pv_installation'].update({
            'file_name':
                data['File']['Historical electricity generation'],
            'type': 'source'})
        # Parameters solar inverter
        dict_asset_parameters = helpers.parameters(user_input, dict_excel_data['solar_inverter'])
        dict_asset['solar_inverter'].update(dict_asset_parameters)
        dict_asset['solar_inverter'].update({'type': 'transformer'})
        # Retrieving cost info
        dict_costs = helpers.cost_info(user_input, tab_name, ['pv_installation', 'solar_inverter'])
        for key in dict_costs.keys():
            dict_asset[key].update(dict_costs[key])
            dict_asset[key].update({'label': key,
                                    'parent': 'pv_plant'})

        dict_asset = {'pv_plant': dict_asset}
        dict_asset['pv_plant'].update({'label': 'pv_plant'})
        return dict_asset

    # electricity storage system
    def electricity_storage(user_input, asset_group_item):
        tab_name = asset_group_item

        # Definition of data cells on excel template tab
        dict_excel_data = {'economic_data': {'tab_name': tab_name,
                                             'first_row': 20,
                                             'number_of_rows': 5,
                                             'column_string': 'B:E',
                                             'index_col': 0},
                           'technical_data_storage_unit': {'tab_name': tab_name,
                                              'first_row': 27,
                                              'number_of_rows': 10,
                                              'column_string': 'B:C',
                                              'index_col': 0},
                           'technical_data_charge_controller': {'tab_name': tab_name,
                                              'first_row': 37,
                                              'number_of_rows': 3,
                                              'column_string': 'B:C',
                                              'index_col': 0}
                           }

        name_dict_sub_assets = {'charging_power': 'Charging power',
                                'capacity': 'Storage capacity / volume',
                                'discharging_power': 'Discharging power',
                                'charge_controller': 'Charge controller/inverter'}

        ## Retrieving all data concerning the electricity sector
        dict_asset = {}
        for sub_asset in name_dict_sub_assets.keys():
            dict_asset.update({sub_asset: {}})

        # Parameters solar panels
        all_titles = {'Lifetime (a)': 'lifetime',
                      'Age of installed asset (a)': 'age_installed',
                      'Installed capacity (kW/kWh)': 'installedCap'}

        data = read_template.read_excel_tab(user_input, dict_excel_data['economic_data'])
        for sub_asset in name_dict_sub_assets.keys():
            for item in all_titles.keys():
                dict_asset[sub_asset].update({all_titles[item]: data[item][name_dict_sub_assets[sub_asset]]})
        # Technical data
        data = read_template.read_excel_dict(user_input, dict_excel_data['technical_data_storage_unit'])
        data = data['Value']
        dict_asset['charging_power'].update({'crate': data['Inflow C-rate'],
                                            'efficiency': data['Inflow efficiency']/100,
                                             'type': 'storage'})
        dict_asset['capacity'].update({'soc_min': data['Min. charge']/100,
                                       'soc_max': data['Max. charge']/100,
                                       'self_discharge': data['Self-discharge / Charge loss per timestep']/100,
                                       'type': 'storage'})

        if data['Initial charge '] == 'None':
            dict_asset['capacity'].update({'soc_initial': None})
        else:
            dict_asset['capacity'].update({'soc_initial': data['Initial charge'] / 100})

        dict_asset['discharging_power'].update({'efficiency': data['Outflow efficiency']/100,
                                                'crate': data['Outflow C-rate'],
                                                'type': 'storage'})

        if data['Optimize additional capacities'] in ['yes', 'Yes', 'y']:
            dict_asset.update({'optimize_cap': True})
        elif data['Optimize additional capacities'] in ['no', 'No', 'n']:
            dict_asset.update({'optimize_cap': False})
        else:
            logging.warning('Input error: \n'
                            '"Optimize additional capacities" on tab %s can only be (Yes/No).',
                            user_input['tab_name'])

        dict_parameters_charge_controller = helpers.parameters(user_input, dict_excel_data['technical_data_charge_controller'])
        dict_asset['charge_controller'].update(dict_parameters_charge_controller)

        # Retrieving cost info
        dict_costs = helpers.cost_info(user_input, tab_name, list(name_dict_sub_assets.keys()))
        for key in dict_costs.keys():
            dict_asset[key].update(dict_costs[key])
            dict_asset[key].update({'label': key,
                                    'parent': 'electricity_storage'})

        dict_asset = {'electricity_storage': dict_asset}
        dict_asset['electricity_storage'].update({'label': 'electricity_storage',
                                                  'type': 'storage'})
        return dict_asset


'''

# Wind plant
    def wind(user_input, asset_group_item):
        parameters_wind = []
        dict
        return dict

    # Rectifier
    def rectifier(user_input, asset_group_item):
        #parameters_rectifier_ac_dc = ['rectifier_ac_dc_efficiency']
        dict
        return dict

    # Inverter
    def inverter(user_input, asset_group_item):
        parameters_inverter_dc_ac = ['inverter_efficiency']
        dict
        return dict

    def distribution(user_input, asset_group_item):
        dict
        return dict

    # Generator
    def generator(user_input, asset_group_item):
        parameters_generator = ['genset_efficiency',
                                'genset_max_loading',
                                'genset_min_loading',
                                'genset_oversize_factor',
                                'combustion_value_fuel']
        dict
        return dict

    # needs to use basic_parameters 3 times - capacity, power in, power out

    # General information on distribution grids for each sector
    sectors = ['electricity',
               'heat',
               'gas',
               'h2']

    # Distribution grid
    distribution_parameters = ['distribution_efficiency',
                               'renewable_share',
                               'peak_power_price',
                               'subscription_costs',
                               'energy_price',
                               'energy_price_change_annual',
                               'energy_feedin_tariff',
                               'energy_feedin_res_tariff']

    # Connection to disribution grid
    # electricity: Transformer station
    transformer_station = ['pcoupling_efficiency',
                           'pcoupling_oversize_factor']


    # heat pump?

    # h2 compressor?

    # gas compressor?


    ## Constraints

    parameters_constraints = ['min_renewable_share']

    #'shortage_max_allowed',
    #'shortage_max_timestep',
    #'shortage_penalty_costs',



'''