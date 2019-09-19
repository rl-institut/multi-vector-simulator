from F1_plotting import plots
import pandas as pd
import logging

class output_processing():
    def evaluate_dict(dict_values):
        logging.info('Summarizing simulation results to results_timeseries and results_scalars_assets.')
        scalars = {}

        for sector in ['electricity', 'heat']:
            results_timeseries = {'total_demand_'+sector:
                                      pd.Series([0 for i in dict_values['settings']['index']],
                                                   index = dict_values['settings']['index'])}
            results_scalars_assets = {}
            results_scalars_other = {}

            for item in dict_values.keys():
                helpers.write_results(dict_values[item], results_scalars_assets, results_scalars_other, results_timeseries, sector)
                for subitem in dict_values[item].keys():
                    helpers.write_results(dict_values[item][subitem], results_scalars_assets, results_scalars_other, results_timeseries, sector)
                    if isinstance(dict_values[item][subitem], dict):
                        for subsubitem in dict_values[item][subitem].keys():
                            helpers.write_results(dict_values[item][subitem][subsubitem], results_scalars_assets, results_scalars_other, results_timeseries, sector)

            results_timeseries = pd.DataFrame.from_dict(results_timeseries)
            results_scalars_assets = pd.DataFrame.from_dict(results_scalars_assets).transpose()
            results_scalars_other = pd.DataFrame.from_dict(results_scalars_other).transpose()

            results_timeseries_output_file = 'timeseries_'+sector+'.xlsx'
            results_timeseries.to_excel(dict_values['user_input']['path_output_folder'] + '/'+ results_timeseries_output_file)
            logging.info('Saved resulting timeseries to: %s.', results_timeseries_output_file)

            scalars.update({sector: {'results_scalars_assets': results_scalars_assets,
                                     'results_scalars_other': results_scalars_other}})

            plots.flows(dict_values['user_input'], dict_values['project_data'], results_timeseries, sector, 14)
            plots.flows(dict_values['user_input'], dict_values['project_data'], results_timeseries, sector, 365)


        # Write everything to file with multipe tabs
        results_scalar_output_file = '/scalars' + '.xlsx'
        with pd.ExcelWriter(dict_values['user_input']['path_output_folder'] + results_scalar_output_file) as open_file:  # doctest: +SKIP
            for sector in scalars.keys():
                scalars[sector]['results_scalars_assets'].to_excel(open_file, sheet_name=sector)
                logging.info('Saved scalar results to: %s, tab %s.', results_scalar_output_file, sector)
                scalars[sector]['results_scalars_other'].to_excel(open_file, sheet_name=sector+'_kpi')
                logging.info('Saved scalar results to: %s, tab %s.', results_scalar_output_file, sector+'_kpi')

        return

class helpers:
    def write_results(dict_asset, results_scalars_assets, results_scalars_other, results_timeseries, sector):
        if isinstance(dict_asset, dict):
            logging.debug('Storing results of asset %s in scalar and timeseries results.', dict_asset['label'])
            if ('input_bus_name' in dict_asset) or ('output_bus_name' in dict_asset):
                results_scalars_assets.update({dict_asset['label']: {}})
                helpers.write_scalars_assets(dict_asset, results_scalars_assets, results_timeseries, sector)
            elif dict_asset['label'] == 'project_data':
                results_scalars_other.update({dict_asset['label']: {}})
                helpers.write_scalars_other(dict_asset, results_scalars_other)
            else:
                logging.debug('Entry %s does not have a distinct bus or belongs in evaluated group.', dict_asset['label'])

        return

    def write_scalars_assets(dict_asset, results_scalars_assets, results_timeseries, sector):
        keyword_list = ['type',
                        'timeseries_soc',
                        'optimal_additional_capacity',
                        'total_flow',
                        'annual_total_flow',
                        'peak_flow',
                        'average_flow',
                        'flow',
                        'costs_investment',
                        'costs_upfront',
                        'costs_opex_var',
                        'costs_opex_fix',
                        'cost_om',
                        'costs_total',
                        'annuity_total',
                        'annuity_om']

        for key in keyword_list:
            if key in dict_asset:
                if key == 'flow':
                    if ('output_bus_name' in dict_asset and dict_asset['output_bus_name'] == sector) \
                            or ('input_bus_name' in dict_asset and dict_asset['input_bus_name'] == sector):
                        if 'parent' in dict_asset and dict_asset['parent'] == 'demand':
                            results_timeseries.update({'total_demand_'+sector:
                                                           results_timeseries['total_demand_'+sector]+dict_asset[key]})
                        elif dict_asset['label'][-3:]=='out':
                            results_timeseries.update({dict_asset['label']: -dict_asset[key]})
                        else:
                            results_timeseries.update({dict_asset['label']: dict_asset[key]})
                elif key == 'timeseries_soc':
                    results_timeseries.update({dict_asset['label'] + '_soc': dict_asset[key]})
                else:
                    results_scalars_assets[dict_asset['label']].update({key: dict_asset[key]})
        return

    def write_scalars_other(dict_asset, results_scalars_other):
        keyword_list = ['costs_investment',
                        'cost_om',
                        'costs_total',
                        'annuity_total',
                        'annuity_om'] #'costs_energy',

        for key in keyword_list:
            if key in dict_asset:
                results_scalars_other[dict_asset['label']].update({key: dict_asset[key]})
        return