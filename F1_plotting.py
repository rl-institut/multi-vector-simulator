import pandas as pd
import matplotlib.pyplot as plt

import logging

class plots():
    def flows(user_input, project_data, results_timeseries, sector, interval):
        logging.info('Creating plots for %s sector', sector)
        steps = interval*24 #si interval es 14, agafa 14 dies.
        flows_les = results_timeseries[0:steps] #sembla que segueix sent un DataFrame, com a minim està estructurat de la mateixa manera, amb files, columnes i data
                                                # simplement està agafant les dades que li interessen de results_timeseries, que conté tots els flows per tots els invervals
        if sector+'_storage_soc' in results_timeseries.columns:
            boolean_subplots = True
            flows_les = flows_les.drop([sector+'_storage_soc'], axis=1) #es confirma que es un DataFrame pel drop, que elimina la columna o fila que tingui el nom que li diem
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
            sector+'_excess_sink': '#996600',  # brown
            'transformer_station_out': '#ff33cc',  # pink
            'charge_controller_out': '#ccccff',  # pidgeon blue
            #'Demand shortage': '#ff3300',  # bright red
            sector+'_storage_soc': '#0033cc'  # blue
            #'Grid availability': '#cc0000'  # red
        }

        # imprimeix el time_series directament, perque ja està ben col·locat, nomes li cal donar color amb color_dict i una mica d'estil
        flows_les.plot(title= sector +' flows in Local Energy System: '
                                       + project_data['project_name'] + ', '
                                       + project_data['scenario_name'],
                      color=[color_dict.get(x, '#333333') for x in flows_les.columns],
                      ax=axes_mg,
                      drawstyle='steps-mid')
        axes_mg.set(xlabel='Time', ylabel=sector+' flow in kWh')
        axes_mg.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)

        if boolean_subplots == True:
            results_timeseries[sector+'_storage_soc'][0:steps].plot(ax=axes[1],
                                               color=color_dict.get(sector+'_storage_soc', '#333333'),
                                               drawstyle='steps-mid')
            ylabel = sector+'_storage_soc'

            axes[1].set(xlabel='Time', ylabel=ylabel)
            axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)

        plt.savefig(user_input['path_output_folder'] + '/' + sector + '_flows_' + str(interval) + '_days.png', bbox_inches="tight")
        #plt.show()
        plt.close()
        plt.clf()
        plt.cla()

        return

    def capacities(user_input,project_data,capacities):
        capacities = pd.Series(capacities)

        logging.info('Creating bar-chart for components capacities')
        capacities.plot.bar(title='Optimal additional capacities: '
                                  + project_data['project_name'] + ', '
                                  + project_data['scenario_name'])

        plt.savefig(user_input['path_output_folder'] + '/optimal_additional_capacities.png', bbox_inches="tight")

        plt.close()
        plt.clf()
        plt.cla()

        return

    def costs(user_input,project_data,annuity_costs):
        # cost percentages are calculated
        total = sum(annuity_costs.values())
        annuity_costs.update({n: annuity_costs[n] / total for n in annuity_costs.keys()})

        # those assets which do not reach 0,5% of total cost are included in others
        annuity_total = {'others':0}
        for asset in annuity_costs:
            if annuity_costs[asset] > 0:
                if annuity_costs[asset] < 0.005:
                    annuity_total['others'] += annuity_costs[asset]
                else:
                    annuity_total[asset] = annuity_costs[asset]

        # if one asset is clearly the most expensive, another pie chart is shown with the rest
        for asset in annuity_total:
            if annuity_total[asset] > 0.9:
                major = asset
                major_value = annuity_total[asset]
                plots.costs_rest(user_input, project_data, major, major_value, annuity_total,total)

        annuity_total = pd.Series(annuity_total)
        logging.info('Creating pie-chart for total annuity costs')
        annuity_total.plot.pie(title='Total annuity costs ('+str(round(total,2))+'$): '
                                  + project_data['project_name'] + ', '
                                  + project_data['scenario_name'],autopct='%1.1f%%',subplots=True)

        plt.savefig(user_input['path_output_folder'] + '/total_annuity_costs.png', bbox_inches="tight")

        plt.close()
        plt.clf()
        plt.cla()

        return

    def costs_rest(user_input,project_data,major,major_value,annuity_total,total):
        # the rest of costs are plotted
        annuity_total_rest = annuity_total.copy()
        del(annuity_total_rest[major])
        rest = sum(annuity_total_rest.values())
        annuity_total_rest.update({n: annuity_total_rest[n] / rest for n in annuity_total_rest.keys()})
        annuity_total_rest = pd.Series(annuity_total_rest)
        annuity_total_rest.plot.pie(title='Rest of total annuity costs (' + str(round((1-major_value)*100)) + '% of '+str(round(total,2))+'$): '
                                     + project_data['project_name'] + ', '
                                     + project_data['scenario_name'], autopct='%1.1f%%', subplots=True)

        plt.savefig(user_input['path_output_folder'] + '/total_annuity_costs_rest.png', bbox_inches="tight")

        plt.close()
        plt.clf()
        plt.cla()

        return
    '''
    def draw_graph(energysystem, edge_labels=True, node_color='#eeac7e',
                   edge_color='#eeac7e', plot=True, node_size=5500,
                   with_labels=True, arrows=True, layout='dot'):
        import networkx as nx
        import oemof.graph as graph
        grph = graph.create_nx_graph(energysystem)

        if type(node_color) is dict:
            node_color = [node_color.get(g, '#AFAFAF') for g in grph.nodes()]

        # set drawing options
        options = {
            'prog': 'dot',
            'with_labels': with_labels,
            'node_color': node_color,
            'edge_color': edge_color,
            'node_size': node_size,
            'arrows': arrows,
            'font_size': 12,
            'font_color': 'w'
        }

        # draw graph
        pos = nx.drawing.nx_agraph.graphviz_layout(grph, prog=layout)

        nx.draw(grph, pos=pos, **options)

        # add edge labels for all edges
        if edge_labels is True and plt:
            labels = nx.get_edge_attributes(grph, 'weight')
            nx.draw_networkx_edge_labels(grph, pos=pos, edge_labels=labels)

        # show output
        if plot is True:
            plt.show()
    '''