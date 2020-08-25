import logging
import os
import textwrap

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

import networkx as nx
import oemof.network.graph as graph

from src.constants import (
    PATHS_TO_PLOTS,
    PLOTS_NX,
    PROJECT_DATA,
    LABEL,
    OUTPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
    PLOTS_DEMANDS,
    PLOTS_RESOURCES,
    LOGFILE
)

from src.constants_json_strings import (
    PROJECT_NAME,
    SCENARIO_NAME,
    KPI,
    ENERGY_CONSUMPTION,
    TIMESERIES,
    DISPATCHABILITY,
    ENERGY_PRODUCTION,
    OPTIMIZED_ADD_CAP,
    TOTAL_FLOW,
    ANNUAL_TOTAL_FLOW,
    PEAK_FLOW,
    AVERAGE_FLOW,
    KPI_SCALAR_MATRIX,
    OPTIMIZED_FLOWS,
    DEMANDS,
    RESOURCES,
)

from src.E1_process_results import (
    convert_demand_to_dataframe,
    convert_costs_to_dataframe,
)

r"""
Module F1 describes all the functions that create plots.

- creating graphs for energy flows
- creating bar chart for capacity
- creating pie chart for cost data
- creating network graph for the model brackets only working on Ubuntu
"""


logging.getLogger("matplotlib.font_manager").disabled = True


def convert_plot_data_to_dataframe(plot_data_dict, data_type):
    """

    Parameters
    ----------
    plot_data_dict: dict
        timeseries for either demand or supply

    data_type: str
        one of DEMANDS or RESOURCES

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
    """Dataframe used for the plots of demands and resources timeseries in the report

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
    resources = dict_values[ENERGY_PRODUCTION].copy()
    res_keys = [k for k in resources.keys() if resources[k][DISPATCHABILITY] is False]

    # Gather all the keys of the various plots for later use in the graphOptions.csv
    dict_for_plots = {DEMANDS: {}, RESOURCES: {}}
    dict_plot_labels = {}

    # Add all the demands to the dict_for_plots dictionary, including the timeseries values
    for demand in df_dem.Demands:
        dict_for_plots[DEMANDS].update(
            {demand: dict_values[ENERGY_CONSUMPTION][demand][TIMESERIES]}
        )
        dict_plot_labels.update(
            {demand: dict_values[ENERGY_CONSUMPTION][demand][LABEL]}
        )

    # Add all the resources to the dict_for_plots dictionary, including the timeseries values
    for resource in res_keys:
        dict_for_plots[RESOURCES].update(
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
        path_log_file = os.path.join(OUTPUT_FOLDER, LOGFILE)

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

    if not file_name.endswith("png"):
        file_name = file_name + ".png"

    logging.info("Saving {} under {}".format(file_name, file_path))

    file_path_out = os.path.join(file_path, file_name)
    with open(file_path_out, "wb") as fp:
        fig_obj.write_image(fp, width=width, height=height, scale=scale)


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
        Path where the image shall be saved if not None

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

    name_file = "input_timeseries_" + plot_title + ".png"

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


def plot_timeseries(dict_values, data_type=DEMANDS, file_path=None):
    r"""Plot timeseries as line chart.

    Parameters
    ----------
    dict_values :
        dict Of all input and output parameters up to F0

    data_type: str
        one of DEMANDS or RESOURCES
        Default: DEMANDS

    file_path: str
        Path where the image shall be saved if not None
        Default: None

    Returns
    -------
    Dict with html DOM id for the figure as key and :plotly:`plotly.graph_objs.Figure` as value
    """

    df_dem = convert_demand_to_dataframe(dict_values)
    dict_for_plots, dict_plot_labels = extract_plot_data_and_title(
        dict_values, df_dem=df_dem
    )

    df_pd = convert_plot_data_to_dataframe(dict_for_plots, data_type)

    list_of_keys = list(df_pd.columns)
    list_of_keys.remove("timestamp")
    plots = {}
    # TODO if the number of plots is larger than this list, it will not plot more
    colors_list = [
        "royalblue",
        "#3C5233",
        "firebrick",
        "#002500",
        "#DEB841",
        "#4F3130",
    ]
    for (component, color_plot) in zip(list_of_keys, colors_list):
        comp_id = component + "-plot"
        fig = create_plotly_line_fig(
            x_data=df_pd["timestamp"],
            y_data=df_pd[component],
            plot_title=dict_plot_labels[component],
            x_axis_name="Time",
            y_axis_name="kW",
            color_for_plot=color_plot,
            file_path=file_path,
        )
        if file_path is None:
            plots[comp_id] = fig

    return plots


def create_plotly_barplot_fig(
    x_data,
    y_data,
    plot_title=None,
    trace_name="",
    x_axis_name=None,
    y_axis_name=None,
    file_name="barplot.png",
    file_path=None,
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

    trace_name: str
        Sets the trace name. The trace name appear as the legend item and on hover.
        Default: ""

    x_axis_name: str
        Default: None

    y_axis_name: str
        Default: None

    file_name: str
        Name of the image file.
        Default: "barplot.png"

    file_path: str
        Path where the image shall be saved if not None

    Returns
    -------
    fig: :plotly:`plotly.graph_objs.Figure`
        figure object
    """
    fig = go.Figure()

    styling_dict = get_fig_style_dict()
    styling_dict["mirror"] = True

    fig.add_trace(
        go.Bar(
            name=trace_name, x=x_data, y=y_data, marker_color=px.colors.qualitative.D3,
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


def plot_optimized_capacities(
    dict_values, file_path=None,
):
    """Plot capacities as a bar chart.

    Parameters
    ----------
    dict_values :
        dict Of all input and output parameters up to F0

    file_path: str
        Path where the image shall be saved if not None
        Default: None

    Returns
    -------
    Dict with html DOM id for the figure as key and :plotly:`plotly.graph_objs.Figure` as value
    """

    # Add dataframe to hold all the KPIs and optimized additional capacities
    df_capacities = dict_values[KPI][KPI_SCALAR_MATRIX]
    df_capacities.drop(
        columns=[TOTAL_FLOW, ANNUAL_TOTAL_FLOW, PEAK_FLOW, AVERAGE_FLOW], inplace=True,
    )
    df_capacities.reset_index(drop=True, inplace=True)

    x_values = []
    y_values = []

    for kpi, cap in zip(
        list(df_capacities[LABEL]), list(df_capacities[OPTIMIZED_ADD_CAP])
    ):
        if cap > 0:
            x_values.append(kpi)
            y_values.append(cap)

    # Title to add to plot titles
    project_title = ": {}, {}".format(
        dict_values[PROJECT_DATA][PROJECT_NAME],
        dict_values[PROJECT_DATA][SCENARIO_NAME],
    )

    name_file = "optimal_additional_capacities"

    fig = create_plotly_barplot_fig(
        x_data=x_values,
        y_data=y_values,
        plot_title="Optimal additional capacities (kW/kWh/kWp)" + project_title,
        trace_name="capacities",
        x_axis_name="Items",
        y_axis_name="Capacities",
        file_name=name_file,
        file_path=file_path,
    )

    return {"capacities_plot": fig}


def create_plotly_flow_fig(
    df_plots_data,
    x_legend=None,
    y_legend=None,
    plot_title=None,
    file_name="flows.png",
    file_path=None,
):
    r"""Generate figure of an asset's flow.

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
        Path where the image shall be saved if not None
        Default: None

    Returns
    -------
    fig: :plotly:`plotly.graph_objs.Figure`
        figure object
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


def plot_flows(dict_values, file_path=None):
    """Plotting timeseries of each assets' flow of the energy system

    Parameters
    ----------
    dict_values : dict
        all simulation input and output data up to this point

    file_path: str
        Path where the image shall be saved if not None
        Default: None

    Returns
    -------
    pie_plots: dict
       Dict with html DOM id for the figure as keys and :plotly:`plotly.graph_objs.Figure` as values
    """
    buses_list = list(dict_values[OPTIMIZED_FLOWS].keys())
    multi_plots = {}
    for bus in buses_list:
        comp_id = bus + "-plot"
        title = (
            bus
            + " flows in LES: "
            + dict_values[PROJECT_DATA][PROJECT_NAME]
            + ", "
            + dict_values[PROJECT_DATA][SCENARIO_NAME]
        )

        df_data = dict_values[OPTIMIZED_FLOWS][bus]
        df_data.reset_index(level=0, inplace=True)
        df_data = df_data.rename(columns={"index": "timestamp"})

        fig = create_plotly_flow_fig(
            df_plots_data=df_data,
            x_legend="Time",
            y_legend=bus + " flow in kWh",
            plot_title=title,
            file_path=file_path,
            file_name=bus + "_flow.png",
        )
        if file_path is None:
            multi_plots[comp_id] = fig

    return multi_plots


def create_plotly_piechart_fig(
    title_of_plot,
    names,
    values,
    color_scheme=px.colors.qualitative.Set1,
    file_name="costs.png",
    file_path=None,
):
    r"""Generate figure with piechart plot.

    Parameters
    ----------
    title_of_plot: str
        title of the figure

    names: list
        List containing the labels of the slices in the pie plot.

    values: list
        List containing the values of the labels to be plotted in the pie plot.

    color_scheme: instance of the px.colors class of the Plotly express library
        This parameter holds the color scheme which is palette of colors (list of hex values) to be
        applied to the pie plot to be created.

    file_name: str
        Name of the image file.
        Default: "costs.png"

    file_path: str
        Path where the image shall be saved if not None
        Default: None

    Returns
    -------
    fig: :plotly:`plotly.graph_objs.Figure`
        figure object
    """

    # Wrap the text of the title into next line if it exceeds the length given below
    title_of_plot = textwrap.wrap(title_of_plot, width=75)
    title_of_plot = "<br>".join(title_of_plot)

    fig = go.Figure(
        go.Pie(
            labels=names,
            values=values,
            textposition="inside",
            insidetextorientation="radial",
            texttemplate="%{label} <br>%{percent}",
            marker=dict(colors=color_scheme),
        ),
    )

    fig.update_layout(
        title={
            "text": title_of_plot,
            "y": 0.9,
            "x": 0.5,
            "font_size": 23,
            "xanchor": "center",
            "yanchor": "top",
            "pad": {"r": 5, "l": 5, "b": 5, "t": 5},
        },
        font_family="sans-serif",
        height=500,
        width=700,
        autosize=True,
        legend=dict(orientation="v", y=0.5, yanchor="middle", x=0.95, xanchor="right",),
        margin=dict(l=10, r=10, b=50, pad=2),
        uniformtext_minsize=18,
    )
    fig.update_traces(hoverinfo="label+percent", textinfo="label", textfont_size=18)

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


def plot_piecharts_of_costs(dict_values, file_path=None):
    """Plotting piecharts of different cost parameters (ie. annuity, total cost, etc...)

    Parameters
    ----------
    dict_values : dict
        all simulation input and output data up to this point

    file_path: str
        Path where the image shall be saved if not None
        Default: None

    Returns
    -------
    pie_plots: dict
       Dict with html DOM id for the figure as keys and :plotly:`plotly.graph_objs.Figure` as values
    """

    df_pie_data = convert_costs_to_dataframe(dict_values)

    # Initialize an empty list and a dict for use later in the function
    pie_plots = {}
    pie_data_dict = {}

    # df_pie_data.reset_index(drop=True, inplace=True)
    columns_list = list(df_pie_data.columns)
    columns_list.remove(LABEL)

    # Iterate through the list of columns of the DF which are the KPIs to be plotted
    for kp_indic in columns_list:

        # Assign an id for the plot
        comp_id = kp_indic + "plot"

        kpi_part = ""

        # Make a copy of the DF to make various manipulations for the pie chart plotting
        df_temp = df_pie_data.copy()

        # Get the total value for each KPI to use in the title of the respective pie chart
        df_temp2 = df_temp.copy()
        df_temp2.set_index(LABEL, inplace=True)
        total_for_title = df_temp2.at["Total", kp_indic]

        # Drop the total row in the dataframe
        df_temp.drop(df_temp.tail(1).index, inplace=True)

        # Gather the data for each asset for the particular KPI, in a dict
        for row_index in range(0, len(df_temp)):
            pie_data_dict[df_temp.at[row_index, LABEL]] = df_temp.at[
                row_index, kp_indic
            ]

        # Remove negative values (such as the feed-in sinks) from the dict
        pie_data_dict = {k: v for (k, v) in pie_data_dict.items() if v > 0}

        # Get the names and values for the pie chart from the above dict
        names_plot = list(pie_data_dict.keys())
        values_plot = list(pie_data_dict.values())

        # Below loop determines the first part of the plot title, according to the kpi being plotted
        if "annuity" in kp_indic:
            kpi_part = "Annuity Costs ("
            file_name = "annuity"
            scheme_choosen = px.colors.qualitative.Set1
        elif "investment" in kp_indic:
            kpi_part = "Upfront Investment Costs ("
            file_name = "upfront_investment_costs"
            scheme_choosen = px.colors.diverging.BrBG
        elif "om" in kp_indic:
            kpi_part = "Operation and Maintenance Costs ("
            file_name = "operation_and_maintainance_costs"
            scheme_choosen = px.colors.sequential.RdBu

        # Title to add to plot titles
        project_title = ": {}, {}".format(
            dict_values[PROJECT_DATA][PROJECT_NAME],
            dict_values[PROJECT_DATA][SCENARIO_NAME],
        )

        # Title of the pie plot
        plot_title = kpi_part + str(round(total_for_title, 2)) + "$) " + project_title

        fig = create_plotly_piechart_fig(
            title_of_plot=plot_title,
            names=names_plot,
            values=values_plot,
            color_scheme=scheme_choosen,
            file_name=file_name,
            file_path=file_path,
        )

        if file_path is None:
            pie_plots[comp_id] = fig

    return pie_plots
