r"""
Module F1 - Plotting
====================

Module F1 describes all the functions that create plots.

- creating graphs for energy flows
- creating bar chart for capacity
- creating pie chart for cost data
- creating network graph for the model brackets only working on Ubuntu
"""

import logging
import os
import textwrap

import pandas as pd

PLOTLY_INSTALLED = False
try:
    import plotly.graph_objs as go
    import plotly.express as px

    PLOTLY_INSTALLED = True
except ModuleNotFoundError:
    logging.warning(
        "You have installed the minimal configuration, if you want to output images "
        "please run the command <TODO>"
    )

import graphviz
import oemof

from multi_vector_simulator.utils.constants import (
    PROJECT_DATA,
    ECONOMIC_DATA,
    LABEL,
    OUTPUT_FOLDER,
    SOC,
)

from multi_vector_simulator.utils.constants_json_strings import (
    PROJECT_NAME,
    SCENARIO_NAME,
    CURR,
    KPI,
    UNIT,
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

from multi_vector_simulator.E1_process_results import (
    convert_demand_to_dataframe,
    convert_costs_to_dataframe,
)


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

    df_dem: :class:`pandas.DataFrame<frame>`
        summarized demand information for each demand

    Returns
    -------
    :class:`pandas.DataFrame<frame>`

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


def fixed_width_text(text, char_num=10):
    """Add linebreaks every char_num characters in a given text.

    Parameters
    ----------
    text: obj:'str'
        text to apply the linebreaks
    char_num: obj:'int'
        max number of characters in a line before a line break
        Default: 10
    Returns
    -------
    obj:'str'
        the text with line breaks after every char_num characters

    """
    # total number of characters in the text
    text_length = len(text)
    # integer number of lines of `char_num` character
    n_lines = int(text_length / char_num)
    # number of character in the last line
    last_line_length = text_length % char_num

    # split the text in lines of `char_num` character
    split_text = []
    for i in range(n_lines):
        split_text.append(text[(i * char_num) : ((i + 1) * char_num)])

    # I if the last line is not empty
    if n_lines > 0:
        if last_line_length > 0:
            split_text.append(text[((i + 1) * char_num) :])
        answer = "\n".join(split_text)
    else:
        answer = text
    return answer


class ESGraphRenderer:
    def __init__(
        self,
        energy_system=None,
        filepath="network",
        img_format=None,
        legend=True,
        txt_width=10,
        txt_fontsize=10,
        **kwargs,
    ):
        """Draw the energy system with Graphviz.

        Parameters
        ----------
        energy_system: `oemof.solph.network.EnergySystem`
            The oemof energy stystem

        filepath: str
            path, where the rendered result shall be saved, if an extension is provided, the format
            will be automatically adapted except if the `img_format` argument is provided
            Default: "network"

        img_format: str
            extension of the available image formats of graphviz (e.g "png", "svg", "pdf", ... )
            Default: "pdf"

        legend: bool
            specify, whether a legend will be added to the graph or not
            Default: False

        txt_width: int
            max number of characters in a line before a line break
            Default: 10

         txt_fontsize: int
            fontsize of the image's text (components labels)
            Default: 10

        Returns
        -------
        None:
        render the generated dot graph in the filepath

        Notes
        -----
        When new oemof-solph asset types are added to the available types in the MVS, this function needs to be updated, so that it can render the asset in the graph.
        """
        file_name, file_ext = os.path.splitext(filepath)

        if img_format is None:
            if file_ext != "":
                img_format = file_ext.replace(".", "")
            else:
                img_format = "pdf"

        self.dot = graphviz.Digraph(filename=file_name, format=img_format, **kwargs)
        self.txt_width = txt_width
        self.txt_fontsize = str(txt_fontsize)
        self.busses = []

        if legend is True:
            with self.dot.subgraph(name="cluster_1") as c:
                # color of the legend box
                c.attr(color="black")
                # title of the legend box
                c.attr(label="Legends")
                self.add_bus(subgraph=c)
                self.add_sink(subgraph=c)
                self.add_source(subgraph=c)
                self.add_transformer(subgraph=c)
                self.add_storage(subgraph=c)

        # draw a node for each of the network's component. The shape depends on the component's type
        for nd in energy_system.nodes:
            if isinstance(nd, oemof.solph.network.Bus):
                self.add_bus(nd.label)
                # keep the bus reference for drawing edges later
                self.busses.append(nd)
            elif isinstance(nd, oemof.solph.network.Sink):
                self.add_sink(nd.label)
            elif isinstance(nd, oemof.solph.network.Source):
                self.add_source(nd.label)
            elif isinstance(nd, oemof.solph.network.Transformer):
                self.add_transformer(nd.label)
            elif isinstance(nd, oemof.solph.components.GenericStorage):
                self.add_storage(nd.label)
            else:
                logging.warning(
                    "The component {} of type {} is not implemented in the rendering "
                    "function of the energy model network graph drawer. It will be "
                    "rendered as an ellipse".format(nd.label, type(nd))
                )
                self.add_component(nd.label)

        # draw the edges between the nodes based on each bus inputs/outputs
        for bus in self.busses:
            for component in bus.inputs:
                # draw an arrow from the component to the bus
                self.connect(component, bus)
            for component in bus.outputs:
                # draw an arrow from the bus to the component
                self.connect(bus, component)

    def add_bus(self, label="Bus", subgraph=None):
        if subgraph is None:
            dot = self.dot
        else:
            dot = subgraph
        dot.node(
            label,
            shape="rectangle",
            fontsize="10",
            fixedsize="shape",
            width="4.1",
            height="0.3",
            style="filled",
            color="lightgrey",
        )

    def add_sink(self, label="Sink", subgraph=None):
        if subgraph is None:
            dot = self.dot
        else:
            dot = subgraph
        dot.node(
            fixed_width_text(label, char_num=self.txt_width),
            shape="trapezium",
            fontsize=self.txt_fontsize,
        )

    def add_source(self, label="Source", subgraph=None):
        if subgraph is None:
            dot = self.dot
        else:
            dot = subgraph
        dot.node(
            fixed_width_text(label, char_num=self.txt_width),
            shape="invtrapezium",
            fontsize=self.txt_fontsize,
        )

    def add_transformer(self, label="Transformer", subgraph=None):
        if subgraph is None:
            dot = self.dot
        else:
            dot = subgraph
        dot.node(
            fixed_width_text(label, char_num=self.txt_width),
            shape="rectangle",
            fontsize=self.txt_fontsize,
        )

    def add_storage(self, label="Storage", subgraph=None):
        if subgraph is None:
            dot = self.dot
        else:
            dot = subgraph
        dot.node(
            fixed_width_text(label, char_num=self.txt_width),
            shape="rectangle",
            style="rounded",
            fontsize=self.txt_fontsize,
        )

    def add_component(self, label="component", subgraph=None):
        if subgraph is None:
            dot = self.dot
        else:
            dot = subgraph
        dot.node(
            fixed_width_text(label, char_num=self.txt_width),
            fontsize=self.txt_fontsize,
        )

    def connect(self, a, b):
        """Draw an arrow from node a to node b

        Parameters
        ----------
        a: `oemof.solph.network.Node`
            An oemof node (usually a Bus or a Component)

        b: `oemof.solph.network.Node`
            An oemof node (usually a Bus or a Component)
        """
        if not isinstance(a, oemof.solph.network.Bus):
            a = fixed_width_text(a.label, char_num=self.txt_width)
        else:
            a = a.label
        if not isinstance(b, oemof.solph.network.Bus):
            b = fixed_width_text(b.label, char_num=self.txt_width)
        else:
            b = b.label

        self.dot.edge(a, b)

    def view(self, **kwargs):
        """Call the view method of the DiGraph instance"""
        self.dot.view(**kwargs)

    def render(self, **kwargs):
        """Call the render method of the DiGraph instance"""
        self.dot.render(**kwargs)


def get_color(idx_line, color_list=None):
    """Pick a color within a color list with periodic boundary conditions

    Parameters
    ----------
    idx_line: int
        index of the line in a plot for which a color is required

    colors: list of str or list to tuple (hexadecimal or rbg code)
        list of colors
        Default: None

    Returns
    -------
    The color in the color list corresponding to the index modulo the color list length

    """
    if color_list is None:
        color_list = (
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
        )
    n_colors = len(color_list)
    return color_list[idx_line % n_colors]


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
    fig :class:`plotly.graph_objs.Figure`
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


def plot_timeseries(
    dict_values,
    data_type=DEMANDS,
    sector_demands=None,
    max_days=None,
    color_list=None,
    file_path=None,
):
    r"""Plot timeseries as line chart.

    Parameters
    ----------
    dict_values :
        dict Of all input and output parameters up to F0

    data_type: str
        one of DEMANDS or RESOURCES
        Default: DEMANDS

    sector_demands: str
        Name of the sector of the energy system
        Default: None

    max_days: int
        maximal number of days the timeseries should be displayed for

    color_list: list of str or list to tuple (hexadecimal or rbg code)
        list of colors
        Default: None

    file_path: str
        Path where the image shall be saved if not None
        Default: None

    Returns
    -------
    Dict with html DOM id for the figure as key and :class:`plotly.graph_objs.Figure` as value
    """

    df_dem = convert_demand_to_dataframe(
        dict_values=dict_values, sector_demands=sector_demands
    )
    dict_for_plots, dict_plot_labels = extract_plot_data_and_title(
        dict_values, df_dem=df_dem
    )

    df_pd = convert_plot_data_to_dataframe(dict_for_plots, data_type)

    list_of_keys = list(df_pd.columns)
    list_of_keys.remove("timestamp")
    plots = {}

    if max_days is not None:
        if df_pd["timestamp"].empty:
            logging.warning("The timeseries for {} are empty".format(data_type))
        else:
            max_date = df_pd["timestamp"][0] + pd.Timedelta("{} day".format(max_days))
            df_pd = df_pd.loc[df_pd["timestamp"] < max_date]
        title_addendum = " ({} days)".format(max_days)
    else:
        title_addendum = ""

    for i, component in enumerate(list_of_keys):
        comp_id = component + "-plot"
        fig = create_plotly_line_fig(
            x_data=df_pd["timestamp"],
            y_data=df_pd[component],
            plot_title="{}{}".format(dict_plot_labels[component], title_addendum),
            x_axis_name="Time",
            y_axis_name="kW",
            color_for_plot=get_color(i, color_list),
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
    legends=None,
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

    legends: list, or pandas series
        The list of the text written within the bars and on hover below the trace_name
        Default: None

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
    fig: :class:`plotly.graph_objs.Figure`
        figure object
    """
    fig = go.Figure()

    styling_dict = get_fig_style_dict()
    styling_dict["mirror"] = True

    opts = {}
    if legends is not None:
        opts.update(dict(text=legends, textposition="auto"))

    fig.add_trace(
        go.Bar(
            name=trace_name,
            x=x_data,
            y=y_data,
            marker_color=px.colors.qualitative.D3,
            **opts,
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
    Dict with html DOM id for the figure as key and :class:`plotly.graph_objs.Figure` as value
    """

    # Add dataframe to hold all the KPIs and optimized additional capacities
    df_capacities = dict_values[KPI][KPI_SCALAR_MATRIX].copy(deep=True)
    df_capacities.drop(
        columns=[TOTAL_FLOW, ANNUAL_TOTAL_FLOW, PEAK_FLOW, AVERAGE_FLOW], inplace=True,
    )
    df_capacities.reset_index(drop=True, inplace=True)

    x_values = []
    y_values = []
    legends = []

    for kpi, cap, unit in zip(
        list(df_capacities[LABEL]),
        list(df_capacities[OPTIMIZED_ADD_CAP]),
        list(df_capacities[UNIT]),
    ):
        if cap > 0:
            x_values.append(kpi)
            y_values.append(cap)
            if unit == "?":
                unit = "kW"
            legends.append("{:.0f} {}".format(cap, unit))

    # Title to add to plot titles
    project_title = ": {}, {}".format(
        dict_values[PROJECT_DATA][PROJECT_NAME],
        dict_values[PROJECT_DATA][SCENARIO_NAME],
    )

    name_file = "optimal_additional_capacities"

    fig = create_plotly_barplot_fig(
        x_data=x_values,
        y_data=y_values,
        plot_title="Optimal additional capacities" + project_title,
        trace_name="capacities",
        legends=legends,
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
    color_list=None,
    file_name="flows.png",
    file_path=None,
):
    r"""Generate figure of an asset's flow.

    Parameters
    ----------
    df_plots_data: :class:`pandas.DataFrame<frame>`
        dataFrame with timeseries of the asset's energy flow
    x_legend: str
        Default: None

    y_legend: str
        Default: None

    plot_title: str
        Default: None

    color_list: list of str or list to tuple (hexadecimal or rbg code)
        list of colors
        Default: None

    file_name: str
        Name of the image file.
        Default: "flows.png"

    file_path: str
        Path where the image shall be saved if not None
        Default: None

    Returns
    -------
    fig: :class:`plotly.graph_objs.Figure`
        figure object
    """

    fig = go.Figure()
    styling_dict = get_fig_style_dict()
    styling_dict["gridwidth"] = 1.0

    assets_list = list(df_plots_data.columns)
    assets_list.remove("timestamp")

    for i, asset in enumerate(assets_list):
        fig.add_trace(
            go.Scatter(
                x=df_plots_data["timestamp"],
                y=df_plots_data[asset],
                mode="lines",
                line=dict(color=get_color(i, color_list), width=2.5),
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


def plot_instant_power(dict_values, file_path=None):
    """Plotting timeseries of instantaneous power for each assets within the energy system

    Parameters
    ----------
    dict_values : dict
        all simulation input and output data up to this point

    file_path: str
        Path where the image shall be saved if not None
        Default: None

    Returns
    -------
    multi_plots: dict
       Dict with html DOM id for the figure as keys and :class:`plotly.graph_objs.Figure` as values
    """
    buses_list = list(dict_values[OPTIMIZED_FLOWS].keys())
    multi_plots = {}
    for bus in buses_list:
        df_data = dict_values[OPTIMIZED_FLOWS][bus].copy(deep=True)
        df_data.reset_index(level=0, inplace=True)
        df_data = df_data.rename(columns={"index": "timestamp"})

        # In case SOC of a storage is in df_data the SOC is plotted separately and is
        # removed from the df_data as the plot that shows absolute flows should not
        # contain SOC in %
        if any(SOC in item for item in df_data):
            # if any(SOC in item for item in df_data):
            comp_id = f"{SOC}-{bus}-plot"
            title = (
                bus
                + " storage SOC in LES: "
                + dict_values[PROJECT_DATA][PROJECT_NAME]
                + ", "
                + dict_values[PROJECT_DATA][SCENARIO_NAME]
            )
            # get columns containing SOC and plot SOC
            soc_cols = [s for s in df_data.keys() if SOC in s]
            soc_cols.extend(["timestamp"])
            fig = create_plotly_flow_fig(
                df_plots_data=df_data[soc_cols],
                x_legend="Time",
                y_legend="SOC",
                plot_title=title,
                file_path=file_path,
                file_name=f"SOC_{bus}_power.png",
            )
            if file_path is None:
                multi_plots[comp_id] = fig

            # remove SOC as it is provided in % and does not fit with flow plot
            soc_cols.remove("timestamp")
            df_data.drop(soc_cols, inplace=True, axis=1)

        # create flow plot
        comp_id = f"{bus}-plot"
        title = (
            bus
            + " power in LES: "
            + dict_values[PROJECT_DATA][PROJECT_NAME]
            + ", "
            + dict_values[PROJECT_DATA][SCENARIO_NAME]
        )

        fig = create_plotly_flow_fig(
            df_plots_data=df_data,
            x_legend="Time",
            y_legend=bus + " in kW",
            plot_title=title,
            file_path=file_path,
            file_name=bus + "_power.png",
        )
        if file_path is None:
            multi_plots[comp_id] = fig

    return multi_plots


def create_plotly_piechart_fig(
    title_of_plot,
    names,
    values,
    color_scheme=None,
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
        Default: None

    file_name: str
        Name of the image file.
        Default: "costs.png"

    file_path: str
        Path where the image shall be saved if not None
        Default: None

    Returns
    -------
    fig: :class:`plotly.graph_objs.Figure`
        figure object
    """

    if color_scheme is None:
        color_scheme = px.colors.qualitative.Set1

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
       Dict with html DOM id for the figure as keys and :class:`plotly.graph_objs.Figure` as values
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
        plot_title = (
            kpi_part
            + str(round(total_for_title))
            + " "
            + dict_values[ECONOMIC_DATA][CURR]
            + ") "
            + project_title
        )

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
