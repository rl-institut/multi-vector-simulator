import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

import networkx as nx
import oemof.network.graph as graph

from src.constants import (
    PATHS_TO_PLOTS,
    PLOTS_BUSSES,
    PLOTS_NX,
    PLOTS_PERFORMANCE,
    PLOTS_COSTS,
    PROJECT_DATA,
    LABEL,
    OUTPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
    PLOTS_DEMANDS,
    PLOTS_RESOURCES,
)

from src.constants_json_strings import (
    SIMULATION_SETTINGS,
    PROJECT_NAME,
    SCENARIO_NAME,
    KPI,
    KPI_COST_MATRIX,
    ENERGY_CONSUMPTION,
    TIMESERIES,
    ENERGY_PRODUCTION,
)

from src.E1_process_results import convert_demand_to_dataframe

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
    dict_values: dict
        Dict with all simulation parameters
    user_input: dict,
        part of the dict_values that includes the output folders name
    project_data: dict,
        part of the dict_values that includes Name for setting title of plots
    results_timeseries: pd Dataframe
        Timeseries that is to be plotted
    bus: str,
        sector that is to be plotted, ie. energyVectors of the energy system -
        - not each and every bus.
    interval: int,
        Time interval in days covered on the x-axis

    Returns
    -------
    Plot of "interval" duration on x-axis for all energy flows connected to the main bus supplying
    the demand of a specific sector
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
    """Determines the assets for which the optimized capacity is larger than zero and then plots
    those capacities in a bar chart.

    Parameters
    ----------
    dict_values: dict
        Dict with all simulation parameters
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
    Generates pie plot of a chosen cost parameter, and if one asset is overly present in the cost
    distribution with 90% of the costs, a pie plot of the distribution of the remaining 10% of
    the costs.

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
        dict_values[KPI][KPI_COST_MATRIX][parameter].values
    )

    if process_pie_chart is True:

        costs_perc_grouped, total = group_costs(
            dict_values[KPI][KPI_COST_MATRIX][parameter],
            dict_values[KPI][KPI_COST_MATRIX][LABEL],
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
        if element is not None and element > 0:
            process_pie_chart = True
    return process_pie_chart


def group_costs(costs, names):
    """
    Calculates the percentage of different asset of the costs and also groups them by asset/DSO
    source/others
    Parameters
    ----------
    costs: dict,
        dict relevant cost data
    names: dict,
        dict with asset name

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
    Determines whether there is one major player in the cost distribution, and if so, prepares
    plotting the remaining percent-

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
    dict_values: dict
        Dict with all simulation parameters
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


def convert_plot_data_to_dataframe(plot_data_dict, data_type):
    """

    Parameters
    ----------
    plot_data_dict: dict
        timeseries for either demand or supply
    data_type: str
        one of "demand" or "supply"

    Returns
    -------
    df: pandas:`pandas.DataFrame<frame>`,
        timeseries for plotting
    """
    # Later, this dataframe can be passed to a function directly make the graphs with Plotly
    df = pd.DataFrame.from_dict(plot_data_dict[data_type], orient="columns")

    # Change the index of the dataframe
    df.reset_index(level=0, inplace=True)
    # Rename the timestamp column from 'index' to 'timestamp'
    df = df.rename(columns={"index": "timestamp"})
    return df


def extract_plot_data_and_title(dict_values, df_dem=None):
    """Dataframe used for the plots in the report

    Parameters
    ----------
    dict_values: dict
        output values of MVS

    df_dem: :pandas:`pandas.DataFrame<frame>`
        summarized demand information for each demand

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>`

    """
    if df_dem is None:
        df_dem = convert_demand_to_dataframe(dict_values)

    # Collect the keys of various resources (PV, Wind, etc.)
    resources = dict_values[ENERGY_PRODUCTION]
    res_keys = [k for k in resources.keys() if "DSO_" not in k]

    # Gather all the keys of the various plots for later use in the graphOptions.csv
    dict_for_plots = {"demands": {}, "supplies": {}}
    dict_plot_labels = {}

    # Add all the demands to the dict_for_plots dictionary, including the timeseries values
    for demand in df_dem.Demands:
        dict_for_plots["demands"].update(
            {demand: dict_values[ENERGY_CONSUMPTION][demand][TIMESERIES]}
        )
        dict_plot_labels.update(
            {demand: dict_values[ENERGY_CONSUMPTION][demand][LABEL]}
        )

    # Add all the resources to the dict_for_plots dictionary, including the timeseries values
    for resource in res_keys:
        dict_for_plots["supplies"].update(
            {resource: dict_values[ENERGY_PRODUCTION][resource][TIMESERIES]}
        )
        dict_plot_labels.update(
            {resource: dict_values[ENERGY_PRODUCTION][resource][LABEL]}
        )

    return dict_for_plots, dict_plot_labels


def parse_simulation_log(path_log_file=None, log_type="ERROR"):
    """Gather the log message of a certain type in a given log file

    Parameters
    ----------
    path_log_file: str/None
        path to the mvs log file
        Default: None
    log_type: str
        one of "ERROR" or "WARNING"
        Default: "ERROR"

    Returns
    -------

    """
    # Dictionaries to gather non-fatal warning and error messages that appear during the simulation
    logs_dict = {}

    if path_log_file is None:
        path_log_file = os.path.join(OUTPUT_FOLDER, "mvs_logfile.log")

    with open(path_log_file) as log_messages:
        log_messages = log_messages.readlines()

    i = 0
    for line in log_messages:
        if log_type in line:
            i = i + 1
            substrings = line.split(" - ")
            message_string = substrings[-1]
            logs_dict.update({i: message_string})

    return logs_dict


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
    dict_values: dict
        Dict with all simulation parameters
    energysystem:
    user_input: dict
    edge_labels: bool
        Default: True
    node_color: str
        Default: "#eeac7e"
    edge_color: str
        Default: "#eeac7e"
    show_plot: bool
        Default: True
    save_plot: bool
        Default: True
    node_size: int
        Default: 5500
    with_labels: bool
        Default: True
    arrows: bool
        Default: True
    layout: str
        Default: "dot"

    Returns
    -------

    """

    # grph = graph.create_nx_graph(
    #    energysystem, filename=user_input[PATH_OUTPUT_FOLDER] + "network_graph.xml"
    # )

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


def plot_input_timeseries(
    dict_values,
    user_input,
    timeseries,
    asset_name,
    column_head="",
    is_demand_profile=False,
):
    r"""
    This function is called from C0 to plot the input timeseries provided to the MVS.
    This includes demand profiles, generation profiles as well as timeseries for otherwise scalar
    values.

    Parameters
    ----------
    dict_values: dict
        Dict with all simulation parameters

    user_input: dict
        Settings

    timeseries: pd.Series
        Timeseries to be plotted

    asset_name: str
        Name of the timeseries to be plotted

    column_head: str
        Column under which timeseries can be found in the csv

    is_demand_profile: bool
        Information whether or not the timeseries provided is a demand profile

    Returns
    -------
    PNG file with timeseries plot

    """
    logging.info("Creating plots for asset %s's parameter %s", asset_name, column_head)
    fig, axes = plt.subplots(nrows=1, figsize=(16 / 2.54, 10 / 2.54 / 2))
    axes_mg = axes

    timeseries.plot(
        title=asset_name, ax=axes_mg, drawstyle="steps-mid",
    )
    axes_mg.set(xlabel="Time", ylabel=column_head)
    path = os.path.join(
        user_input[PATH_OUTPUT_FOLDER],
        "input_timeseries_" + asset_name + "_" + column_head + ".png",
    )
    if is_demand_profile is True:
        dict_values[PATHS_TO_PLOTS][PLOTS_DEMANDS] += [str(path)]
    else:
        dict_values[PATHS_TO_PLOTS][PLOTS_RESOURCES] += [str(path)]
    plt.savefig(
        path, bbox_inches="tight",
    )

    plt.close()
    plt.clf()
    plt.cla()


def save_plots_to_disk(
    fig_obj, file_name, file_path="", width=None, height=None, scale=None
):
    r"""
    This function saves the plots generated using the Plotly library in this module to the outputs folder.

    Parameters
    ----------
    fig_obj: instance of the classes of the Plotly go library used to generate the plots in this auto-report
        Figure object of the plotly plots

    file_name: str
        The name of the PNG image of the plot to be saved in the output folder.

    file_path: str
        Path where the image shall be saved

    width: int or float
        The width of the picture to be saved in pixels.
        Default: None

    height: int or float
        The height of the picture to be saved in pixels.
        Default: None

    scale: int or float
        The scale by which the plotly image ought to be multiplied.
        Default: None

    Returns
    -------
    Nothing is returned. This function call results in the plots being saved as .png images to the disk.
    """

    file_name = file_name + "_plotly" + ".png"
    file_path_out = os.path.join(file_path, file_name)
    fig_obj.write_image(file_path_out, width=width, height=height, scale=scale)


def get_fig_style_dict():
    styling_dict = dict(
        showgrid=True,
        gridwidth=1.5,
        zeroline=True,
        autorange=True,
        linewidth=1,
        ticks="inside",
        title_font=dict(size=18, color="black"),
    )
    return styling_dict


def create_plotly_line_fig(
    x_data,
    y_data,
    plot_title=None,
    x_axis_name=None,
    y_axis_name=None,
    color_for_plot="#0A2342",
    file_path=None,
):
    r"""
    Create figure for generic timeseries lineplots

    Parameters
    ----------
    x_data: list, or pandas series
        The list of abscissas of the data required for plotting.

    y_data: list, or pandas series, or list of lists
        The list of ordinates of the data required for plotting.

    plot_title: str
        The title of the plot generated.
        Default: None

    x_axis_name: str
        Default: None

    y_axis_name: str
        Default: None

    file_path: str
        Path where the image shall be saved

    Returns
    -------
    fig :plotly:`plotly.graph_objs.Figure`
        figure object
    """
    fig = go.Figure()

    styling_dict = get_fig_style_dict()
    styling_dict["mirror"] = True

    fig.add_trace(
        go.Scatter(
            x=x_data,
            y=y_data,
            mode="lines",
            line=dict(color=color_for_plot, width=2.5),
        )
    )
    fig.update_layout(
        xaxis_title=x_axis_name,
        yaxis_title=y_axis_name,
        template="simple_white",
        xaxis=styling_dict,
        yaxis=styling_dict,
        font_family="sans-serif",
        title={
            "text": plot_title,
            "y": 0.90,
            "x": 0.5,
            "font_size": 23,
            "xanchor": "center",
            "yanchor": "top",
        },
    )

    name_file = "input_timeseries_" + plot_title

    if file_path is not None:

        # Function call to save the Plotly plot to the disk
        save_plots_to_disk(
            fig_obj=fig,
            file_path=file_path,
            file_name=name_file,
            width=1200,
            height=600,
            scale=5,
        )

    return fig


def create_plotly_capacities_fig(
    x_data, y_data, plot_title=None, x_axis_name=None, y_axis_name=None, file_path=None,
):
    r"""
    Create figure for specific capacities barplot

    Parameters
    ----------
    x_data: list, or pandas series
        The list of abscissas of the data required for plotting.

    y_data: list, or pandas series, or list of lists
        The list of ordinates of the data required for plotting.

    plot_title: str
        The title of the plot generated.
        Default: None

    x_axis_name: str
        Default: None

    y_axis_name: str
        Default: None

    file_path: str
        Path where the image shall be saved

    Returns
    -------
    fig :plotly:`plotly.graph_objs.Figure`
        figure object
    """
    fig = go.Figure()

    styling_dict = get_fig_style_dict()
    styling_dict["mirror"] = True

    fig.add_trace(
        go.Bar(
            name="capacities",
            x=x_data,
            y=y_data,
            marker_color=px.colors.qualitative.D3,
        )
    )

    fig.update_layout(
        xaxis_title=x_axis_name,
        yaxis_title=y_axis_name,
        template="simple_white",
        font_family="sans-serif",
        # TODO use styling dict
        xaxis=go.layout.XAxis(
            showgrid=True,
            gridwidth=1.5,
            zeroline=True,
            mirror=True,
            autorange=True,
            linewidth=1,
            ticks="inside",
            visible=True,
        ),
        yaxis=styling_dict,
        title={
            "text": plot_title,
            "y": 0.90,
            "x": 0.5,
            "font_size": 23,
            "xanchor": "center",
            "yanchor": "top",
        },
        legend_title="Components",
    )
    name_file = "optimal_additional_capacities"

    if file_path is not None:
        # Function call to save the Plotly plot to the disk
        save_plots_to_disk(
            fig_obj=fig,
            file_path=file_path,
            file_name=name_file,
            width=1200,
            height=600,
            scale=5,
        )

    return fig


def create_plotly_flow_fig(
    df_plots_data,
    x_legend=None,
    y_legend=None,
    plot_title=None,
    file_name="flows.png",
    file_path=None,
):
    r"""Generate figure an asset's flow.

    Parameters
    ----------
    df_plots_data: :pandas:`pandas.DataFrame<frame>`
        dataFrame with timeseries of the asset's energy flow
    x_legend: str
        Default: None

    y_legend: str
        Default: None

    plot_title: str
        Default: None

    file_name: str
        Name of the image file.
        Default: "flows.png"

    file_path: str
        Path where the image shall be saved
        Default: None

    Returns
    -------
        html.Div() element
        Contains the list of the flows plots generated, both for the print and web app versions.
    """

    fig = go.Figure()
    # TODO: if number of asset is larger than this list, the surnumerrous will not be plotted
    colors = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]
    styling_dict = get_fig_style_dict()
    styling_dict["gridwidth"] = 1.0

    assets_list = list(df_plots_data.columns)
    assets_list.remove("timestamp")

    for asset, new_color in zip(assets_list, colors):
        fig.add_trace(
            go.Scatter(
                x=df_plots_data["timestamp"],
                y=df_plots_data[asset],
                mode="lines",
                line=dict(color=new_color, width=2.5),
                name=asset,
            )
        )

    fig.update_layout(
        xaxis_title=x_legend,
        yaxis_title=y_legend,
        font_family="sans-serif",
        template="simple_white",
        xaxis=styling_dict,
        yaxis=styling_dict,
        title={
            "text": plot_title,
            "y": 0.90,
            "x": 0.5,
            "font_size": 23,
            "xanchor": "center",
            "yanchor": "top",
        },
        legend=dict(y=0.5, traceorder="normal", font=dict(color="black"),),
    )

    if file_path is not None:
        # Function call to save the Plotly plot to the disk
        save_plots_to_disk(
            fig_obj=fig,
            file_path=file_path,
            file_name=file_name,
            width=1200,
            height=600,
            scale=5,
        )

    return fig
