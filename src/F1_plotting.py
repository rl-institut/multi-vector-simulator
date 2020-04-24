import pandas as pd
import matplotlib.pyplot as plt
import logging
import os

r"""
Module F1 describes all the functions that create plots.

- creating graphs for energy flows
- creating bar chart for capacity
- creating bar chart for cost data
- creating network graph for the model brackets only working on Ubuntu
"""


logging.getLogger("matplotlib.font_manager").disabled = True


def flows(user_input, project_data, results_timeseries, sector, interval):
    """
    Parameters
    ----------
    user_input: dict
        part of the dict_values that includes the output folders name
    project_data: dict
        part of the dict_values that includes Name for setting title of plots
    results_timeseries: pd Dataframe
        Timeseries that is to be plotted
    sector: str
        sector that is to be plotted, ie. energyVectors of the energy system - not each and every bus.
    interval: int
        Time interval in days covered on the x-axis

    Returns
    -------
    Plot of "interval" duration on x-axis for all energy flows connected to the main bus supplying the demand of a specific sector
    """

    logging.info("Creating plots for %s sector, %s days", sector, interval)
    steps = interval * 24
    flows_les = results_timeseries[0:steps]

    includes_soc = False
    for column in results_timeseries.columns:
        if "SOC" in column:
            includes_soc = True
            soc_column_name = column

    if includes_soc == True:
        boolean_subplots = True
        flows_les = flows_les.drop([soc_column_name], axis=1)
    else:
        boolean_subplots = False

    if boolean_subplots == False:
        fig, axes = plt.subplots(nrows=1, figsize=(16 / 2.54, 10 / 2.54 / 2))
        axes_mg = axes
    else:
        fig, axes = plt.subplots(nrows=2, figsize=(16 / 2.54, 10 / 2.54))
        axes_mg = axes[0]

    flows_les.plot(
        title=sector
        + " flows in Local Energy System: "
        + project_data["project_name"]
        + ", "
        + project_data["scenario_name"],
        # color=[color_dict.get(x, "#333333") for x in flows_les.columns],
        ax=axes_mg,
        drawstyle="steps-mid",
    )
    axes_mg.set(xlabel="Time", ylabel=sector + " flow in kWh")
    axes_mg.legend(loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)

    if boolean_subplots == True:
        results_timeseries[soc_column_name][0:steps].plot(
            ax=axes[1],
            # color=color_dict.get(soc_column_name, "#333333"),
            drawstyle="steps-mid",
        )
        ylabel = sector + " SOC"

        axes[1].set(xlabel="Time", ylabel=ylabel)
        axes[1].legend(loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)

    path = os.path.join(
        user_input["path_output_folder"],
        sector + "_flows_" + str(interval) + "_days.png",
    )

    plt.savefig(
        path, bbox_inches="tight",
    )
    # plt.show()
    plt.close()
    plt.clf()
    plt.cla()

    return


def capacities(user_input, project_data, assets, capacities):
    """Determines the assets for which the optimized capacity is larger than zero and then plots those capacities in a bar chart.

    Parameters
    ----------
    user_input : dict
        Simulation settings including the output path
    project_data : dict
        Project data including project name and scenario name
    assets : list
        list of asset names
    capacities : list
        list of asset capacities

    Returns
    -------
    type
        png with bar chart of optimized capacities

    """

    # only items with an optimal added capacity over 0 are selected
    indexes = []
    capacities_added = []
    i = 0
    for capacity in capacities:
        if capacity > 0:
            indexes.append(i)
            capacities_added.append(capacity)
        i += 1
    i = 0
    assets_added = []
    for asset in assets:
        if i in indexes:
            assets_added.append(asset)
        i += 1

    # Data frame definition and plotting
    dfcapacities = pd.DataFrame()
    dfcapacities["items"] = assets_added
    dfcapacities["capacities"] = capacities_added

    logging.info("Creating bar-chart for components capacities")

    dfcapacities.plot.bar(
        x="items",
        y="capacities",
        title="Optimal additional capacities (kW/kWh/kWp): "
        + project_data["project_name"]
        + ", "
        + project_data["scenario_name"],
    )

    path = os.path.join(
        user_input["path_output_folder"], "optimal_additional_capacities.png"
    )
    plt.savefig(
        path, bbox_inches="tight",
    )

    plt.close()
    plt.clf()
    plt.cla()

    return

def evaluate_cost_parameter(dict_values, parameter, file_name_suffix):
    """
    Generates pie plot of a chosen cost parameter, and if one asset is overly present in the cost distribution with 90% of the costs,
    a pie plot of the distribution of the remaining 10% of the costs.

    Parameters
    ----------
    dict_values: dict

    parameter: cost parameter to be plotted

    file_name_suffix: file name that is to be used

    Returns
    -------
    pie plot plot of a cost parameter
    """
    # Annuity costs plot (only plot if there are values with cost over 0)
    label = file_name_suffix.replace("_", " ")

    show_annuity_total = False
    for element in dict_values["kpi"]["cost_matrix"][parameter].values:
        if element > 0:
            show_annuity_total = True
    if show_annuity_total:
        costs_perc = drop_no_cost_assets(dict_values["kpi"]["cost_matrix"][parameter],
                                         dict_values["kpi"]["cost_matrix"]["label"])
        costs_perc_grouped, total = group_costs(costs_perc)

        costs_perc_grouped_pandas = pd.Series(costs_perc_grouped)

        title = label \
                + " costs (" \
                + str(round(total, 2)) \
                + "$): " \
                + dict_values["project_data"]["project_name"] \
                + ", " \
                + dict_values["project_data"]["scenario_name"]

        plot_a_piechart(dict_values["simulation_settings"], file_name_suffix,
                        costs_perc_grouped_pandas, label, title)

        # if there is a dominant assets, another plot with the remaining assets is created
        if any(costs_perc_grouped_pandas.values > 0.9):
            for asset in costs_perc_grouped:
                if costs_perc_grouped[asset] > 0.9 and costs_perc_grouped[asset] < 1: #why should it even be larger 1?
                    major = asset
                    major_value = costs_perc_grouped[asset]

            plot_costs_rest(
                dict_values["simulation_settings"],
                dict_values["project_data"],
                major,
                major_value,
                costs_perc_grouped,
                total,
                label,
                file_name_suffix,
                )
    return

def drop_no_cost_assets(costs, names):
    """
    Pre-process the cost data, so that only assets that induce costs are displayed when plotting
    Parameters
    ----------
    costs: pd.Series
        A number of cost values
    names: pd.Series
        A number of names

    Returns
    -------
    dictionary of costs with only assets that have costs
    """
    costs = pd.DataFrame(data=costs.values, index=names.values)
    costs = costs.to_dict()[0]

    # only assets with costs over 0 are plotted
    costs_prec = {}
    for asset in costs:
        if costs[asset] > 0:
            costs_prec.update({asset: costs[asset]})
    return costs_prec

def group_costs(costs_perc):
    """
    Calculates the percentage of different asset of the costs and also groups them by asset/DSO source/others
    Parameters
    ----------
    costs_perc: pd.DataFrame
        DataFrame with relevant cost data, index is asset name

    Returns
    -------
    Dictionary with costs in groups, ie. into asset/others and DSO as well as total costs
    """
    # % is calculated
    total = sum(costs_perc.values())
    costs_perc.update({n: costs_perc[n] / total for n in costs_perc.keys()})

    # those assets which do not reach 0,5% of total cost are included in 'others'
    # if there are more than one consumption period, they are grouped in DSO_consumption
    others = 0
    DSO_consumption = 0
    costs_perc_grouped = {}
    for asset in costs_perc:
        if costs_perc[asset] > 0:
            if "DSO_consumption" in asset:
                DSO_consumption += costs_perc[asset]
            elif costs_perc[asset] < 0.005:
                others += costs_perc[asset]
            else:
                costs_perc_grouped[asset] = costs_perc[asset]

    if DSO_consumption > 0:
        costs_perc_grouped["DSO_consumption"] = DSO_consumption
    if others > 0:
        costs_perc_grouped["others"] = others
    return costs_perc_grouped, total

def plot_a_piechart(settings, path, costs, label, title):
    """
    plots a pie chart of a dataset

    Parameters
    ----------
    settings: dict
        includes output path

    path: str
        name of the plot

    costs: pd.DataFrame
        cost data

    label: str
        label of the pie chart, ie. cost type

    title: str
        title of the pie chart

    Returns
    -------
    Pie chart of a dataset

    """
    logging.info("Creating pie-chart for total " + label)
    costs.plot.pie(
        title=title,
        autopct="%1.1f%%",
        subplots=True,
    )
    plt.savefig(
        settings["path_output_folder"] + "/" + path + ".png", bbox_inches="tight",
    )

    plt.close()
    plt.clf()
    plt.cla()
    return

# the rest of costs are plotted if there is a dominant one (over 90%)
def plot_costs_rest(
    settings, project_data, major, major_value, costs_total, total, label, path
):
    """

    Parameters
    ----------
    settings : dict

    project_data: dict

    costs_total : pd.DataFrame

    label : str

    major_value :
        
    total : float
        
    path : str
        

    Returns
    -------

    """

    costs_total_rest = costs_total.copy()
    del costs_total_rest[major]
    rest = sum(costs_total_rest.values())
    costs_total_rest.update(
        {n: costs_total_rest[n] / rest for n in costs_total_rest.keys()}
    )
    costs_total_rest = pd.Series(costs_total_rest)
    # check if there are any remaining costs that could be plotted
    if costs_total_rest.empty == False:
        title = "Rest of "\
            + label\
            + "("\
            + str(round((1 - major_value) * 100))\
            + "% of "\
            + str(round(total, 2))\
            + "$): "\
            + project_data["project_name"]\
            + ", "\
            + project_data["scenario_name"]

        plot_a_piechart(settings, path, costs_total_rest, label+ " (rest)", title)
    else:
        logging.debug(
            "No plot for costs_total_rest created, as remaining costs were 0."
        )
    return

def draw_graph(
    energysystem,
    user_input,
    edge_labels=True,
    node_color="#eeac7e",
    edge_color="#eeac7e",
    show_plot=True,
    save_plot=True,
    node_size=5500,
    with_labels=True,
    arrows=True,
    layout="dot",
):
    """

    Parameters
    ----------
    energysystem :
        param edge_labels:
    node_color :
        param edge_color: (Default value = "#eeac7e")
    plot :
        param node_size:
    with_labels :
        param arrows: (Default value = True)
    layout :
        return: (Default value = "dot")
    user_input :
        
    edge_labels :
         (Default value = True)
    edge_color :
         (Default value = "#eeac7e")
    show_plot :
         (Default value = True)
    save_plot :
         (Default value = True)
    node_size :
         (Default value = 5500)
    arrows :
         (Default value = True)

    Returns
    -------

    """
    import networkx as nx
    import oemof.graph as graph

    grph = graph.create_nx_graph(energysystem)

    if type(node_color) is dict:
        node_color = [node_color.get(g, "#AFAFAF") for g in grph.nodes()]

    # set drawing options
    options = {
        "prog": "dot",
        "with_labels": with_labels,
        "node_color": node_color,
        "edge_color": edge_color,
        "node_size": node_size,
        "arrows": arrows,
        "font_size": 12,
        "font_color": "w",
    }

    # draw graph
    fig, ax = plt.subplots(figsize=(20, 10))
    pos = nx.drawing.nx_agraph.graphviz_layout(grph, prog=layout)

    nx.draw(grph, pos=pos, ax=ax, **options)

    # add edge labels for all edges
    if edge_labels is True and plt:
        labels = nx.get_edge_attributes(grph, "weight")
        nx.draw_networkx_edge_labels(grph, pos=pos, edge_labels=labels)

    if show_plot is True:
        fig.show()

    if save_plot is True:
        fig.savefig(
            user_input["path_output_folder"] + "/" + "network_graph.png",
            bbox_inches="tight",
        )
