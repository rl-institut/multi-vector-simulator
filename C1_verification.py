import os, sys
import logging
import pandas as pd

class verify():
    def lookup_file(file_path, name):
        if os.path.isfile(file_path) == False:
            logging.critical('Missing file! '
                            '\n The timeseries file %s of asset %s can not be found. Operation terminated.', file_path, name)
            sys.exit()
        return

    def check_input_values(dict_values):
        for asset_name in dict_values:
            if not(isinstance(dict_values[asset_name], dict)):
                # checking first layer of dict_values
                verify.all_valid_intervals(asset_name, dict_values[asset_name])
            else:
                for sub_asset_name in dict_values[asset_name]:
                    if not (isinstance(dict_values[asset_name][sub_asset_name], dict)):
                        #checking second layer of dict values
                        verify.all_valid_intervals(sub_asset_name,
                                                   dict_values[asset_name][sub_asset_name])
                    else:
                        for sub_sub_asset_name in dict_values[asset_name][sub_asset_name]:
                            if not (isinstance(dict_values[asset_name][sub_asset_name][sub_sub_asset_name], dict)):
                                # checking third layer of dict values
                                verify.all_valid_intervals(sub_asset_name,
                                                           dict_values[asset_name][sub_asset_name][sub_sub_asset_name])
                            else:
                                logging.critical('Verification Error! Add another layer to evaluation.')

        logging.info('Input values have been verified. This verification not replace a manual input parameter check.')
        return

    def all_valid_intervals(name, value):
        #todo bessere darstellung

        valid_intervals =  {'project_name': 'str',
                            'scenario_name': 'str',
                            'country': 'str',
                            'longitude': [-90,90], #todo Range for lat/lon# ?!
                            'latitude': [0,1], #todo Range for lat/lon?!
                            'evaluated_period': 'int',
                            'time_step': 'str',
                            'start_date': pd.DatetimeIndex,
                            'index': pd.DatetimeIndex,
                            'periods': 'float',
                            'lifetime': ['nonzero','any'],
                            'age_installed': [0,'any'],
                            'cap_installed':[0,'any'],
                            'optimize_cap': [True, False],
                            'dsm': [True, False],
                            'soc_min': [0,1],
                            'soc_max': [0,1],
                            'soc_initial': [0,1],
                            'crate': [0,1],
                            'efficiency': [0,1],
                            'file_name': 'str',
                            'label': 'str',
                            'electricity_cost_fix_annual': [0,'any'],
                            'electricity_price_var_kWh': [0,'any'],
                            'electricity_price_var_kW_monthly': [0,'any'],
                            'feedin_tariff_res': [0, 'any'],
                            'feedin_tariff_non_res': [0,'any'],
                            'capex_fix': [0,'any'],
                            'capex_var': [0,'any'],
                            'opex_fix': [0,'any'],
                            'opex_var': [0,'any'],
                            'discount_factor': [0,1],
                            'project_duration': ['nonzero','any'],
                            'tax': [0,1],
                            'currency': 'str'}

        if valid_intervals[name] == 'str':
            if not(isinstance(value, str)):
                logging.error('Input error! Value %s is not in recommended format "string".', name)

        if valid_intervals[name] == int :
            if not(isinstance(value, str)):
                logging.error('Input error! Value %s is not in recommended format "string".', name)

        elif valid_intervals[name] == [0,1]:
            if value < 0:
                logging.error('Input error! Value %s is not in recommended to be smaller than 0.', name)
            elif 1 < value:
                logging.error('Input error! Value %s is not in recommended to be larger than 1.', name)

        elif valid_intervals[name] == [0,'any']:
            if value < 0:
                logging.error('Input error! Value %s is not in recommended to be smaller than 0.', name)

        elif valid_intervals[name] == ['nonzero', 'any']:
            if value <= 0:
                logging.error('Input error! Value %s is not in recommended to be smaller than 0.', name)

        elif valid_intervals[name] == [True, False]:
            if not(value == True or value == False):
                logging.error('Input error! Value %s is neither True nor False.', name)

        #todo int missing
        #todo type bla missing

        return
