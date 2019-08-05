import pandas as pd
import logging
import pprint as pp
from B1_read_excel import read_template



class data_input:
    def all(user_input):
        # Read from excel sheet, tab overview: Which components are used?
        included_assets = read_template.overview_energy_system(user_input)
        dict_of_values = {}

        logging.debug('Get all project data from tab "Project data".')
        project_data, simulation_settings, economic_data = get_values.project_data(user_input)
        dict_of_values.update({'project_data': project_data})
        dict_of_values.update({'simulation_settings': simulation_settings})
        dict_of_values.update({'economic_data': economic_data})



        # generate list of assets from needed assets in scenario
        # Create dict of assets
        dict_of_assets = {}
        for asset_group in included_assets.keys():
            if asset_group == 'sectors':
                logging.debug('Get data for each sector (ie. fix costs and parameters)')
                for asset_group_item in included_assets[asset_group]:
                   get_values.sectors(asset_group_item)
            else:
                logging.debug('Get data for each asset (ie. costs and technical parameters)')
                for asset_group_item in included_assets[asset_group]:
                    #value_extend.components(asset_group_item)
                    pass

        pp.pprint(dict_of_values)
        return dict_of_assets

class get_values:
    def project_data(user_input):
        # Definition of data red from excel
        dict_excel_data = {'title': 'Project data',
                           'tab_name': 'Project data',
                           'first_row': 2,
                           'number_of_rows': 25,
                           'column_string': 'B:C',
                           'index_col': 0}

        data = read_template.read_excel_dict(user_input, dict_excel_data)

        data = data['Unnamed: 2'] #todo - How to avoid this?

        project_data = {'project_name':data['Project location name'],
                        'scenario_name':data['Scenario'],
                        'country': data['Country'],
                        'longitude': data['Location, longitude'],
                        'latitude': data['Location, latitude'],
                        'capex_fix': data['CAPEX \n(investment costs, 1st year)'],
                        'opex_fix': data['OPEX \n(operational costs, 1st year)']}

        simulation_settings = {'time_period': data['Evaluated timeframe'],
                               'time_step': data['Time step']}

        economic_data = {'discount_factor': data['WACC'],
                         'project_duration': data['Project duration'],
                         'currency': data['Currency']}

        return project_data, simulation_settings, economic_data

    def sectors(asset_group_item):
        if asset_group_item == 'Electricity':
            pass
        elif asset_group_item == 'Heat':
            pass
        elif asset_group_item == 'Gas':
            pass
        elif asset_group_item == 'Electric mobility':
            pass
        elif asset_group_item == 'H2':
            #todo excel tab not defined
            pass
        print(asset_group_item)
        return

'''
    def components(dict_of_assets, asset_name, asset_type, data_array):
        # Basic parameters for each asset
        parameters_basic = ['asset_type',
                            'sectors',
                            'capex_fix',
                            'capex_var',
                            'opex_fix',
                            'opex_var',
                            'lifetime',
                            'cap_exist',
                            'cap_additional']

        if asset_type != 'ess':
            dict_of_assets.update({asset_name: {}}) # add parameters basic by accessing data_array values. cap additional: yes/no
        else:
            for item in ['charging_power', 'capacity', 'discharging_power']:
                dict_of_assets.update({asset_name: {item: {}}})
        dict_value_specific = value_extend.assets_specific(asset_type, data_array) # specific parameters is a list
        dict_of_assets.update({asset_name: dict_value_specific})
        return

    def assets_specific(asset_type, data_array):
        # Access all data of specific asset
        if asset_type == 'pv':
            dict_value_specific = value_extend.asset_pv(data_array)
        elif asset_type == 'wind':
            dict_value_specific = value_extend.asset_wind(data_array)
        elif asset_type == 'rectifier':
            dict_value_specific = value_extend.asset_rectifier(data_array)
        elif asset_type == 'inverter':
            dict_value_specific = value_extend.asset_inverter(data_array)
        elif asset_type == 'generator':
            dict_value_specific = value_extend.asset_generator(data_array)
        elif asset_type == 'ess':
            dict_value_specific = value_extend.asset_ess(data_array)

        return dict_value_specific

    # PV panels
    def asset_pv(data_array):
        parameters_pv = []
        dict
        return dict

    # Wind plant
    def asset_wind(data_array):
        parameters_wind = []
        dict
        return dict

    # Electricity storage system
    def asset_ess(data_array):
        parameters_ess = ['storage_Crate_charge',
                          'storage_Crate_discharge',
                          'storage_efficiency_charge',
                          'storage_efficiency_discharge',
                          'storage_loss_timestep',
                          'storage_soc_initial',
                          'storage_soc_max',
                          'storage_soc_min']
        dict
        return dict

    # Rectifier
    def asset_rectifier(data_array):
        #parameters_rectifier_ac_dc = ['rectifier_ac_dc_efficiency']
        dict
        return dict

    # Inverter
    def asset_inverter(data_array):
        parameters_inverter_dc_ac = ['inverter_efficiency']
        dict
        return dict

    def asset_distribution(data_array):
        dict
        return dict

    # Generator
    def asset_generator(data_array):
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


    parameters_economic = ['tax',
                           'discounting_factor',
                           'annuity_factor',
                           'crf']

    parameters_project = ['longitude',
                          'latitude',
                          'country',
                          'currency',
                          'project_name',
                          'scenario_name']
'''