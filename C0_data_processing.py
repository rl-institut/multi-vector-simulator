from C1_verification import verify
from C2_economic_functions import economics
import pandas as pd
import logging
import sys, shutil
import pprint as pp
from copy import deepcopy

class data_processing:
    def all(dict_values):
        ## Verify inputs
        # check whether input values can be true
        verify.check_input_values(dict_values)
        # Check, whether files (demand, generation) are existing
        helpers.evaluate_timeseries(dict_values, verify.lookup_file, 'verify')

        ## Complete data values
        # Receive data from timeseries and process their format
        helpers.evaluate_timeseries(dict_values, receive_data.timeseries_csv, 'receive_data')
        #todo add option to receive data online

        # Add symbolic costs
        dict_values['ESS'].update({'charge_controller_symbolic': deepcopy(dict_values['ESS']['charge_controller'])})
        for cost in ['capex', 'opex']:
            for suffix in ['_var' + '_fix']:
                dict_values['ESS']['charge_controller_symbolic'].update({cost+suffix: 0})
        dict_values['ESS']['charge_controller_symbolic'].update({'label': 'charge_controller_symbolic'})

        # Adds costs to each asset and sub-asset
        data_processing.economic_data(dict_values)
        return

    def economic_data(dict_values):
        # Calculate annuitiy factor
        dict_values['economic_data'].update({
            'annuity_factor': economics.annuity_factor(
                dict_values['economic_data']['project_duration'],
                dict_values['economic_data']['discount_factor'])})

        # Calculate crf
        dict_values['economic_data'].update({
            'crf': economics.crf(
                dict_values['economic_data']['project_duration'],
                dict_values['economic_data']['discount_factor'])})

        for asset_name in dict_values:
            # Main assets
            if 'lifetime' in dict_values[asset_name].keys():
                # Add lifetime capex (incl. replacement costs), calculate annuity (incl. om), and simulation annuity
                helpers.evaluate_lifetime_costs(dict_values['settings'],
                                                dict_values['economic_data'],
                                                dict_values[asset_name])

            # Sub-assets, ie. pv_installation and solar_inverter of PV plant
            for sub_asset_name in dict_values[asset_name]:
                if isinstance(dict_values[asset_name][sub_asset_name], dict):
                    if 'lifetime' in dict_values[asset_name][sub_asset_name].keys():
                        # Add lifetime capex (incl. replacement costs), calculate annuity (incl. om), and simulation annuity
                        helpers.evaluate_lifetime_costs(dict_values['settings'],
                                                        dict_values['economic_data'],
                                                        dict_values[asset_name][sub_asset_name])

        logging.info('Processed cost data and added economic values.')
        return

class helpers:
    def evaluate_lifetime_costs(settings, economic_data, dict_asset):
        if 'capex_var' not in dict_asset:
            dict_asset.update({'capex_var': 0})

        dict_asset.update({'lifetime_capex':
                                       economics.capex_from_investment(dict_asset['capex_var'],
                                                                       dict_asset['lifetime'],
                                                                       economic_data['project_duration'],
                                                                       economic_data['discount_factor'],
                                                                       economic_data['tax'])})

        # Annuities of components including opex AND capex #
        dict_asset.update({'annuity_capex_opex':
                                       economics.annuity(dict_asset['lifetime_capex'],
                                                         economic_data['crf'])
                                       + dict_asset['opex_fix']})

        # Scaling annuity to timeframe
        # Updating all annuities above to annuities "for the timeframe", so that optimization is based on more adequate
        # costs. Includes project_cost_annuity, distribution_grid_cost_annuity, maingrid_extension_cost_annuity for
        # consistency eventhough these are not used in optimization.
        dict_asset.update({'simulation_annuity':
                                       dict_asset['annuity_capex_opex'] / 365
                                       * settings['evaluated_period']})

        return

    def evaluate_timeseries(dict_values, function, use):
        input_folder = dict_values['user_input']['path_input_folder']
        # Accessing timeseries of components
        for asset_name in ['PV plant', 'Wind plant']:
            if asset_name in dict_values:
                if asset_name == 'PV plant':
                    sub_name = 'pv_installation'
                elif asset_name == 'Wind plant':
                    sub_name = 'wind_installation'
                file_path = input_folder + dict_values[asset_name][sub_name]['file_name']
                # Check if file existent
                if use == 'verify':
                    # check if specific demand timeseries exists
                    function(file_path, asset_name)
                elif use == 'receive_data':
                    # receive data and write it into dict_values
                    function(dict_values['settings'], dict_values['user_input'], dict_values[asset_name][sub_name], file_path, asset_name)

        # Accessing timeseries of demands
        for demand_type in ['Electricity demand', 'Heat demand']:
            if demand_type in dict_values:
                # Check for each
                for demand_key in dict_values['Electricity demand']:
                    file_path = input_folder + dict_values[demand_type][demand_key]['file_name']
                    if use == 'verify':
                        # check if specific demand timeseries exists
                        function(file_path, demand_key)
                    elif use == 'receive_data':
                        # receive data and write it into dict_values
                        function(dict_values['settings'], dict_values['user_input'], dict_values[demand_type][demand_key], file_path, demand_key)
        return

class receive_data:
    def timeseries_csv(settings, user_input, dict_asset, file_path, name):
        data_set = pd.read_csv(file_path, sep=';')
        if len(data_set.index) == settings['periods']:
            dict_asset.update({'timeseries': pd.DataFrame(data_set.values, index = settings['index'])})
            logging.debug('Added timeseries of %s (%s).', name, file_path)
        elif len(data_set.index) >= settings['periods']:
            dict_asset.update({'timeseries': pd.DataFrame(data_set[0:len(settings['index'])].values,
                                                          index=settings['index'])})
            logging.info('Provided timeseries of %s (%s) longer than evaluated period. '
                         'Excess data dropped.', name, file_path)

        elif len(data_set.index) <= settings['periods']:
            logging.critical('Input errror! '
                             'Provided timeseries of %s (%s) shorter then evaluated period. '
                             'Operation terminated', name, file_path)
            sys.exit()

        shutil.copy(file_path, user_input['path_output_folder_inputs']+dict_asset['file_name'])
        logging.debug('Copied timeseries %s to output folder / inputs.', file_path)
        return

    #get timeseries from online source
    def timeseries_online():
        return
