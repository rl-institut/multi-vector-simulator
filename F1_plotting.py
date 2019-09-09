import pandas as pd
import matplotlib.pyplot as plt

import logging

class plots():
    def flows(user_input, project_data, results_timeseries, sector, interval):
        logging.info('Creating plots for %s sector', sector)
        steps = interval*24
        flows_les = results_timeseries[0:steps]

        if sector+'_storage_soc' in results_timeseries.columns:
            boolean_subplots = True
            flows_les = flows_les.drop([sector+'_storage_soc'], axis=1)
        else:
            boolean_subplots = False

        if boolean_subplots == False:
            fig, axes = plt.subplots(nrows=1, figsize=(16 / 2.54, 10 / 2.54 / 2))
            axes_mg = axes
        else:
            fig, axes = plt.subplots(nrows=2, figsize=(16 / 2.54, 10 / 2.54))
            axes_mg = axes[0]

        # website with websafe hexacolours: https://www.colorhexa.com/web-safe-colors
        color_dict = {
            'total_demand_'+sector: '#33ff00',  # dark green
            'solar_inverter': '#ffcc00',  # orange
            #'Wind generation': '#33ccff',  # light blue
            #'Genset generation': '#000000',  # black
            'transformer_station_in': '#990099',  # violet
            'charge_controller_in': '#0033cc',  # light green
            'electricity_excess_sink': '#996600',  # brown
            'transformer_station_out': '#ff33cc',  # pink
            'charge_controller_out': '#ccccff',  # pidgeon blue
            #'Demand shortage': '#ff3300',  # bright red
            'electricity_storage_soc': '#0033cc'  # blue
            #'Grid availability': '#cc0000'  # red
        }

        flows_les[0:steps].plot(title= sector +' flows in Local Energy System: '
                                       + project_data['project_name'] + ', '
                                       + project_data['scenario_name'],
                      color=[color_dict.get(x, '#333333') for x in flows_les.columns],
                      ax=axes_mg,
                      drawstyle='steps-mid')
        axes_mg.set(xlabel='Time', ylabel=sector+' flow in kWh')
        axes_mg.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)

        if boolean_subplots == True:
            results_timeseries[sector+'_storage_soc'].plot(ax=axes[1],
                                               color=color_dict.get(sector+'_storage_soc', '#333333'),
                                               drawstyle='steps-mid')
            ylabel = sector+'_storage_soc'

            axes[1].set(xlabel='Time', ylabel=ylabel)
            axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)

        plt.savefig(user_input['path_output_folder'] + '/' + sector + '_flows_' + str(interval) + '_days.png', bbox_inches="tight")
        plt.close()
        plt.clf()
        plt.cla()

        return