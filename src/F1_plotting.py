import logging
import os

import matplotlib.pyplot as plt
import pandas as pd

from src.constants import (
    PATHS_TO_PLOTS,
    PLOTS_BUSSES,
    PLOTS_NX,
    PLOTS_PERFORMANCE,
    PLOTS_COSTS,
    PROJECT_DATA,
    LABEL,
    PATH_OUTPUT_FOLDER,
)
from src.constants_json_strings import (
    SIMULATION_SETTINGS,
    PROJECT_NAME,
    SCENARIO_NAME,
    KPI,
)

r"""
Module F1 describes all the functions that create plots.

- creating graphs for energy flows
- creating bar chart for capacity
- creating pie chart for cost data
- creating network graph for the model brackets only working on Ubuntu
"""


logging.getLogger("matplotlib.font_manager").disabled = True


def flows(dict_values, user_input, project_data, results_timeseries, bus, interval):
    """
    Parameters
    ----------
    user_input: dict
        part of the dict_values that includes the output folders name
    project_data: dict
        part of the dict_values that includes Name for setting title of plots
    results_timeseries: pd Dataframe
        Timeseries that is to be plotted
    bus: str
        sector that is to be plotted, ie. energyVectors of the energy system - not each and every bus.
    interval: int
        Time interval in days covered on the x-axis

    Returns
    -------
    Plot of "interval" duration on x-axis for all energy flows connected to the main bus supplying the demand of a specific sector
    """

    logging.info("Creating plots for %s sector, %s days", bus, interval)
    steps = interval * 24
    flows_les = results_timeseries[0:steps]

    includes_soc = False
    for column in results_timeseries.columns:
        if "SOC" in column:
            includes_soc = True
            soc_column_name = column

    if includes_soc is True:
        flows_les = flows_les.drop([soc_column_name], axis=1)
        fig, axes = plt.subplots(nrows=2, figsize=(16 / 2.54, 10 / 2.54))
        axes_mg = axes[0]
    else:
        fig, axes = plt.subplots(nrows=1, figsize=(16 / 2.54, 10 / 2.54 / 2))
        axes_mg = axes

    flows_les.plot(
        title=bus
        + " flows in LES: "
        + project_data[PROJECT_NAME]
        + ", "
        + project_data[SCENARIO_NAME],
        ax=axes_mg,
        drawstyle="steps-mid",
    )
    axes_mg.set(xlabel="Time", ylabel=bus + " flow in kWh")
    axes_mg.legend(loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)

    if includes_soc is True:
        results_timeseries[soc_column_name][0:steps].plot(
            ax=axes[1], drawstyle="steps-mid",
        )
        ylabel = bus + " SOC"

        axes[1].set(xlabel="Time", ylabel=ylabel)
        axes[1].legend(loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)

    path = os.path.join(
        user_input[PATH_OUTPUT_FOLDER], bus + "_flows_" + str(interval) + "_days.png",
    )

    plt.savefig(
        path, bbox_inches="tight",
    )
    # update_list = dict_values[PATHS_TO_PLOTS][PLOTS_BUSSES] + [path]
    if interval != 14:
        dict_values[PATHS_TO_PLOTS][PLOTS_BUSSES] += [str(path)]

    plt.close()
    plt.clf()
    plt.cla()

    return


def capacities(dict_values, user_input, project_data, assets, capacities):
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
        + project_data[PROJECT_NAME]
        + ", "
        + project_data[SCENARIO_NAME],
    )

    path = os.path.join(
        user_input[PATH_OUTPUT_FOLDER], "optimal_additional_capacities.png"
    )
    plt.savefig(
        path, bbox_inches="tight",
    )

    dict_values[PATHS_TO_PLOTS][PLOTS_PERFORMANCE] += [str(path)]
    plt.close()
    plt.clf()
    plt.cla()

    return


def evaluate_cost_parameter(dict_values, parameter, file_name):
    """
    Generates pie plot of a chosen cost parameter, and if one asset is overly present in the cost distribution with 90% of the costs,
    a pie plot of the distribution of the remaining 10% of the costs.

    Parameters
    ----------
    dict_values: dict

    parameter: cost parameter to be plotted

    file_name: file name that is to be used

    Returns
    -------
    pie plot plot of a cost parameter
    """
    # Annuity costs plot (only plot if there are values with cost over 0)
    label = file_name.replace("_", " ")

    process_pie_chart = determine_if_plotting_necessary(
        dict_values[KPI]["cost_matrix"][parameter].values
    )

    if process_pie_chart is True:

        costs_perc_grouped, total = group_costs(
            dict_values[KPI]["cost_matrix"][parameter],
            dict_values[KPI]["cost_matrix"][LABEL],
        )

        costs_perc_grouped_pandas = pd.Series(costs_perc_grouped)

        title = (
            label
            + " costs ("
            + str(round(total, 2))
            + "$): "
            + dict_values[PROJECT_DATA][PROJECT_NAME]
            + ", "
            + dict_values[PROJECT_DATA][SCENARIO_NAME]
        )

        plot_a_piechart(
            dict_values,
            dict_values[SIMULATION_SETTINGS],
            file_name,
            costs_perc_grouped_pandas,
            label,
            title,
        )

        # if there is a dominant assets, another plot with the remaining assets is created
        (
            plot_minor_costs_pie,
            costs_perc_grouped_minor,
            rest,
        ) = recalculate_distribution_of_rest_costs(costs_perc_grouped_pandas)
        if plot_minor_costs_pie is True:
            title = (
                "Minor part of "
                + label
                + "("
                + str(round(rest * 100))
                + "% of "
                + str(round(total, 2))
                + "$): "
                + dict_values[PROJECT_DATA][PROJECT_NAME]
                + ", "
                + dict_values[PROJECT_DATA][SCENARIO_NAME]
            )

            plot_a_piechart(
                dict_values,
                dict_values[SIMULATION_SETTINGS],
                file_name + "_minor",
                costs_perc_grouped_minor,
                label + " (minor)",
                title,
            )
    return


def determine_if_plotting_necessary(parameter_values):
    """
    Determines whether pie plot of a parameter is necessary
    Parameters
    ----------
    parameter_values: list
        Values of the parameter

    Returns
    -------
    True or False
    """
    process_pie_chart = False
    for element in parameter_values:
        if element > 0:
            process_pie_chart = True
    return process_pie_chart


def group_costs(costs, names):
    """
    Calculates the percentage of different asset of the costs and also groups them by asset/DSO source/others
    Parameters
    ----------
    costs_perc: dict
        dict relevant cost data, and asset name

    Returns
    -------
    Dictionary with costs in groups, ie. into asset/others and DSO as well as total costs
    """
    costs = pd.DataFrame(data=costs.values, index=names.values)
    costs = costs.to_dict()[0]

    # % is calculated
    total = sum(costs.values())
    costs_perc = costs.copy()
    costs_perc.update({n: costs_perc[n] / total for n in costs_perc.keys()})

    # those assets which do not reach 0,5% of total cost are included in 'others'
    # if there are more than one consumption period, they are grouped in DSO_consumption
    others = 0
    DSO_consumption = 0
    costs_perc_grouped = {}
    for asset in costs_perc:
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


def recalculate_distribution_of_rest_costs(costs_perc_grouped_pandas):
    """
    Determines whether there is one major player in the cost distribution, and if so, prepares plotting the remaining percent-

    Parameters
    ----------
    costs_perc_grouped_pandas: pd.Series
        Dataframe with all assets and their share of costs in percent


    Returns
    -------
    Data frame with minor costs
    """
    plot_minor_costs_pie = False
    for asset in costs_perc_grouped_pandas.index:
        if costs_perc_grouped_pandas[asset] > 0.8:
            plot_minor_costs_pie = True
            major = asset

    if plot_minor_costs_pie is True:
        costs_perc_grouped_pandas = costs_perc_grouped_pandas.drop([major])
        rest = costs_perc_grouped_pandas.values.sum()
        costs_perc_grouped_minor = pd.Series(
            [
                costs_perc_grouped_pandas[n] / rest
                for n in costs_perc_grouped_pandas.index
            ],
            index=costs_perc_grouped_pandas.index,
        )
    else:
        costs_perc_grouped_minor = pd.Series()
        rest = 0

    return plot_minor_costs_pie, costs_perc_grouped_minor, rest


def plot_a_piechart(dict_values, settings, file_name, costs, label, title):
    """
    plots a pie chart of a dataset

    Parameters
    ----------
    settings: dict
        includes output path

    file_name: str
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
    if costs.empty is False:
        logging.info("Creating pie-chart for total " + label)
        costs.plot.pie(
            title=title, autopct="%1.1f%%", subplots=True,
        )
        path = os.path.join(settings[PATH_OUTPUT_FOLDER], file_name + ".png")
        plt.savefig(
            path, bbox_inches="tight",
        )
        dict_values[PATHS_TO_PLOTS][PLOTS_COSTS] += [str(path)]
        plt.close()
        plt.clf()
        plt.cla()
    else:
        logging.debug("No plot for costs created, as remaining costs were 0.")
    return


def draw_graph(
    dict_values,
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
        path = os.path.join(user_input[PATH_OUTPUT_FOLDER], "network_graph.png")
        dict_values[PATHS_TO_PLOTS][PLOTS_NX] += [str(path)]

        fig.savefig(
            path, bbox_inches="tight",
        )
