import matplotlib as plt

class plots():
    def save_mg_flows(experiment, case_dict, e_flows_df, filename):
        logging.debug('Saving flows MG.')
        flows_connected_to_electricity_mg_bus = [
            'Demand AC',
            'Demand DC',
            'Demand shortage',
            'Demand shortage AC',
            'Demand shortage DC',
            'Demand supplied',
            'PV generation',
            'PV generation AC',
            'PV generation DC',
            'Wind generation',
            'Excess generation',
            'Consumption from main grid (MG side)',
            'Feed into main grid (MG side)',
            'Storage discharge',
            'Storage discharge AC',
            'Storage discharge DC',
            'Storage SOC',
            'Storage charge',
            'Storage charge AC',
            'Storage charge DC',
            'Genset generation',
            'Grid availability']

        negative_list = ['Demand shortage',
                         'Demand shortage AC',
                         'Demand shortage DC',
                         'Storage discharge',
                         'Storage discharge AC',
                         'Storage discharge DC',
                         'Feed into main grid (MG side)']

        droplist = [
            'Demand AC',
            'Demand DC',
            'Demand shortage AC',
            'Demand shortage DC',
            'PV generation AC',
            'PV generation DC',
            'Storage discharge AC',
            'Storage discharge DC',
            'Storage charge AC',
            'Storage charge DC']

        mg_flows = pd.DataFrame(e_flows_df['Demand'].values, columns=['Demand'], index=e_flows_df['Demand'].index)
        for entry in flows_connected_to_electricity_mg_bus:
            if entry in e_flows_df.columns:
                # do not add energyflow of shortage/supplied demand, if no shortage occurs
                if not((entry == 'Demand supplied' or entry == 'Demand shortage')
                       and (sum(e_flows_df['Demand'].values)==sum(e_flows_df['Demand supplied'].values))):

                    if entry in negative_list:
                        # Display those values as negative in graphs/files
                        if entry == 'Feed into main grid (MG side)':
                            new_column = pd.DataFrame(-e_flows_df[entry].values,
                                                      columns=['Feed into main grid'],
                                                      index=e_flows_df[entry].index)
                        else:
                            new_column = pd.DataFrame(-e_flows_df[entry].values, columns=[entry], index=e_flows_df[entry].index) # Display those values as negative in graphs/files
                    elif entry == 'Consumption from main grid (MG side)':
                        new_column = pd.DataFrame(e_flows_df[entry].values,
                                                  columns=['Consumption from main grid'],
                                                  index=e_flows_df[entry].index)
                    else:
                        new_column = pd.DataFrame(e_flows_df[entry].values, columns=[entry], index=e_flows_df[entry].index)

                    mg_flows = mg_flows.join(new_column)

        if experiment['save_to_csv_flows_electricity_mg'] == True:
            mg_flows.to_csv(experiment['output_folder'] + '/electricity_mg/' + case_dict['case_name'] + filename + '_electricity_mg.csv')

        if experiment['save_to_png_flows_electricity_mg'] == True:
            number_of_subplots = 0

            for item in droplist:
                if item in mg_flows.columns:
                    mg_flows = mg_flows.drop([item], axis=1)

            if 'Storage SOC' in mg_flows.columns:
                mg_flows = mg_flows.drop(['Storage SOC'], axis=1)
                if case_dict['storage_fixed_capacity'] != None:
                    number_of_subplots += 1
            if 'Grid availability' in mg_flows.columns:
                mg_flows = mg_flows.drop(['Grid availability'], axis=1)
                if (case_dict['pcc_consumption_fixed_capacity'] != None) or (case_dict['pcc_feedin_fixed_capacity'] != None):
                    number_of_subplots += 1

            for timeframe in ['year', 'days']:
                if timeframe == 'year':
                    output.plot_flows(case_dict, experiment, mg_flows, e_flows_df, number_of_subplots)
                    plt.savefig(experiment['output_folder'] + '/electricity_mg/' + case_dict[
                        'case_name'] + filename + '_electricity_mg.png', bbox_inches="tight")

                elif timeframe == 'days' and (len(mg_flows['Demand']) >= 5 * 24):
                    output.plot_flows(case_dict, experiment, mg_flows[24:5 * 24], e_flows_df[24:5 * 24], number_of_subplots)
                    plt.savefig(experiment['output_folder'] + '/electricity_mg/' + case_dict[
                        'case_name'] + filename + '_electricity_mg_4days.png', bbox_inches="tight")
                plt.close()
                plt.clf()
                plt.cla()

        return



    def plot_flows(case_dict, experiment, mg_flows, e_flows_df, number_of_subplots):
        if number_of_subplots < 1:
            fig, axes = plt.subplots(nrows=1, figsize=(16 / 2.54, 10 / 2.54 / 2))
            axes_mg = axes
        else:
            fig, axes = plt.subplots(nrows=2, figsize=(16 / 2.54, 10 / 2.54))
            axes_mg = axes[0]

        # website with websafe hexacolours: https://www.colorhexa.com/web-safe-colors
        color_dict = {
            'Demand': '#33ff00',  # dark green
            'Demand supplied': '#66cc33',  # grass green
            'PV generation': '#ffcc00',  # orange
            'Wind generation': '#33ccff',  # light blue
            'Genset generation': '#000000',  # black
            'Consumption from main grid': '#990099',  # violet
            'Storage charge': '#0033cc',  # light green
            'Excess generation': '#996600',  # brown
            'Feed into main grid': '#ff33cc',  # pink
            'Storage discharge': '#ccccff',  # pidgeon blue
            'Demand shortage': '#ff3300',  # bright red
            'Storage SOC': '#0033cc',  # blue
            'Grid availability': '#cc0000'  # red
        }

        mg_flows.plot(title='MG Operation of case ' + case_dict['case_name'] + ' in ' + experiment['project_site_name'],
                      color=[color_dict.get(x, '#333333') for x in mg_flows.columns],
                      ax=axes_mg,
                      drawstyle='steps-mid')
        axes_mg.set(xlabel='Time', ylabel='Electricity flow in kWh')
        axes_mg.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)

        if number_of_subplots >= 1:
            ylabel = ''
            if ((case_dict['pcc_consumption_fixed_capacity'] != None) or (case_dict['pcc_feedin_fixed_capacity'] != None)) \
                    and ('Grid availability' in e_flows_df.columns):
                e_flows_df['Grid availability'].plot(ax=axes[1],
                                                     color=color_dict.get('Grid availability', '#333333'),
                                                     drawstyle='steps-mid')
                ylabel += 'Grid availability'

            if number_of_subplots > 1:
                ylabel += ',\n '

            if (case_dict['storage_fixed_capacity'] != None) \
                    and ('Storage SOC' in e_flows_df.columns):
                e_flows_df['Storage SOC'].plot(ax=axes[1],
                                               color=color_dict.get('Storage SOC', '#333333'),
                                               drawstyle='steps-mid')
                ylabel += 'Storage SOC'

            axes[1].set(xlabel='Time', ylabel=ylabel)
            if number_of_subplots > 1:
                axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)

        return