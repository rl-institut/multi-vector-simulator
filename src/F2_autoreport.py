# This script generates a report of the simulation automatically, with all the important data.

import base64
import os

# Imports for generating pdf automatically
import threading
import time
import webbrowser

# Importing necessary packages
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import plotly.express as px
import dash_table
import folium
import git
import pandas as pd
import reverse_geocoder as rg
import staticmap
import asyncio
import textwrap
import copy

import pyppdf.patch_pyppeteer
from pyppeteer import launch

# This removes extensive logging in the console for pyppeteer.
import logging

pyppeteer_level = logging.WARNING
logging.getLogger("pyppeteer").setLevel(pyppeteer_level)

from src.constants import (
    PLOTS_BUSSES,
    PATHS_TO_PLOTS,
    PATH_OUTPUT_FOLDER,
    PLOTS_DEMANDS,
    PLOTS_RESOURCES,
    PLOTS_PERFORMANCE,
    PLOTS_COSTS,
    REPO_PATH,
    REPORT_PATH,
    OUTPUT_FOLDER,
    INPUTS_COPY,
    CSV_ELEMENTS,
    ECONOMIC_DATA,
    PROJECT_DATA,
    INSTALLED_CAP,
)
from src.constants_json_strings import (
    UNIT,
    ENERGY_CONVERSION,
    ENERGY_CONSUMPTION,
    ENERGY_PRODUCTION,
    OEMOF_ASSET_TYPE,
    LABEL,
    SECTORS,
    VALUE,
    ENERGY_VECTOR,
    OPTIMIZE_CAP,
    SIMULATION_SETTINGS,
    EVALUATED_PERIOD,
    START_DATE,
    TIMESTEP,
    TIMESERIES_PEAK,
    TOTAL_FLOW,
    ANNUAL_TOTAL_FLOW,
    OPTIMIZED_ADD_CAP,
    KPI,
    KPI_SCALAR_MATRIX,
    KPI_COST_MATRIX,
    COST_TOTAL,
    COST_OM_TOTAL,
    COST_INVESTMENT,
    COST_DISPATCH,
    COST_OM_FIX,
    COST_UPFRONT,
    PROJECT_NAME,
    PROJECT_ID,
    SCENARIO_NAME,
    SCENARIO_ID,
    PEAK_FLOW,
    AVERAGE_FLOW,
    TIMESERIES,
    ANNUITY_TOTAL,
    ENERGY_PROVIDERS,
    DSO_FEEDIN,
    AUTO_SINK,
    EXCESS,
)

# TODO link this to the version and date number @Bachibouzouk
from src.utils import get_version_info

version_num, version_date = get_version_info()

OUTPUT_FOLDER = os.path.join(REPO_PATH, OUTPUT_FOLDER)
CSV_FOLDER = os.path.join(REPO_PATH, OUTPUT_FOLDER, INPUTS_COPY, CSV_ELEMENTS)


async def _print_pdf_from_chrome(path_pdf_report):
    r"""
    This function generates the PDF report from the web app rendered on a Chromimum-based browser.

    Parameters
    ----------
    path_pdf_report: os.path
        Path and filename to which the pdf report should be stored
        Default: Default: os.path.join(OUTPUT_FOLDER, "out.pdf")

    Returns
    -------
    Does not return anything, but saves a PDF file in file path provided by the user.
    """

    browser = await launch()
    page = await browser.newPage()
    await page.goto("http://127.0.0.1:8050", {"waitUntil": "networkidle0"})
    await page.waitForSelector("#main-div")
    await page.pdf({"path": path_pdf_report, "format": "A4", "printBackground": True})
    await browser.close()
    print("*" * 10)
    print("The report was saved under {}".format(path_pdf_report))
    print("You can now quit with ctlr+c")
    print("*" * 10)


def print_pdf(app=None, path_pdf_report=os.path.join(OUTPUT_FOLDER, "out.pdf")):
    r"""Runs the dash app in a thread and print a pdf before exiting

    Parameters
    ----------
    app: instance of the Dash class of the dash library
        Default: None

    path_pdf_report: str
        Path where the pdf report should be saved.

    Returns
    -------
    None, but saves a pdf printout of the provided app under the provided path
    """

    # if an app handle is provided, serve it locally in a separated thread
    if app is not None:
        td = threading.Thread(target=app.run_server)
        td.daemon = True
        td.start()

    # Emulates a webdriver
    asyncio.get_event_loop().run_until_complete(_print_pdf_from_chrome(path_pdf_report))

    if app is not None:
        td.join(20)


def open_in_browser(app, timeout=600):
    r"""Runs the dash app in a thread an open a browser window

    Parameters
    ----------
    app: instance of the Dash class, part of the dash library

    timeout: int or float
        Specifies the number of seconds that the web app should be open in the browser before timing out.

    Returns
    -------
    Nothing, but the web app version of the auto-report is displayed in a browser.
    """

    td = threading.Thread(target=app.run_server)
    td.daemon = True
    td.start()
    webbrowser.open("http://127.0.0.1:8050", new=1)
    td.join(timeout)


def make_dash_data_table(df, title=None):
    r"""
    Function that creates a Dash DataTable from a Pandas dataframe.

    Parameters
    ----------
    df: :pandas:`pandas.DataFrame<frame>`
        This dataframe holds the data from which the dash table is to be created.

    title: str
        An optional title for the table.
        Default: None

    Returns
    -------
    html.Div()
        This element contains the title of the dash table and the dash table itself encased in a
        child html.Div() element.

    """
    content = [
        html.Div(
            className="tableplay",
            children=dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict("records"),
                style_cell={
                    "padding": "8px",
                    "height": "auto",
                    "width": "auto",
                    "fontFamily": "Courier New",
                    "textAlign": "center",
                    "whiteSpace": "normal",
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)",
                    }
                ],
                style_header={
                    "fontWeight": "bold",
                    "color": "#8c3604",
                    "whiteSpace": "normal",
                    "height": "auto",
                },
            ),
        )
    ]

    if title is not None:
        content = [html.H4(title, className="report_table_title")] + content

    return html.Div(className="report_table", children=content)


def insert_subsection(title, content, **kwargs):
    r"""
    Inserts sub-sections within the Dash app layout, such as Input data, simulation results, etc.

    Parameters
    ----------
    title : str
        This is the title or heading of the subsection.

    content : list
        This is typically a list of html elements or function calls returning html elements, that make up the
        body of the sub-section.

    kwargs : Any possible optional arguments such as styles, etc.

    Returns
    -------
    html.Div()
        This returns the sub-section of the report including the tile and other information within the sub-section.


    """
    if "className" in kwargs:
        className = "cell subsection {}".format(kwargs.pop("className"))
    else:
        className = "cell subsection"

    # TODO if content is a list

    if not isinstance(content, list):
        content = [content]

    return html.Div(
        className=className,
        children=[html.H3(title), html.Hr(className="cell small-12 horizontal_line")]
        + content,
        **kwargs,
    )


# Function that creates the headings
def insert_headings(heading_text):
    r"""
    This function is for creating the headings such as information, input data, etc.

    Parameters
    ----------
    heading_text: str
        Big headings for several sub-sections.

    Returns
    -------
    html.P()
        A html element with the heading text encased container.
    """

    return html.H2(
        className="cell", children=heading_text, style={"page-break-after": "avoid"}
    )


# Functions that creates paragraphs
def insert_body_text(body_of_text):
    r"""
    This function is for rendering blocks of text within the sub-sections.

    Parameters
    ----------
    body_of_text: str
        Typically a single-line or paragraph of text.

    Returns
    -------
    html.P()
        A html element that renders the paragraph of text in the Dash app layout.
    """

    return html.P(className="cell large-11 blockoftext", children=body_of_text)


def insert_log_messages(log_dict):
    r"""
    This function inserts logging messages that arise during the simulation, such as warnings and error messages,
    into the auto-report.
    
    Parameters
    ----------
    log_dict: dict
        A dictionary containing the logging messages collected during the simulation.

    Returns
    -------
    html.Div()
        This html element holds the children html elements that produce the lists of warnings and error messages
        for both print and screen versions of the auto-report.
    """

    return html.Div(
        children=[
            # this will be displayed only in the app
            html.Div(
                className="grid-x no-print",
                children=[
                    html.Div(
                        className="cell grid-x",
                        children=[
                            html.Div(children=k, className="cell small-1 list-marker"),
                            html.Div(children=v, className="cell small-11 list-log"),
                        ],
                    )
                    for k, v in log_dict.items()
                ],
            ),
            # this will be displayed only in the printed version
            html.Div(
                className="list-log print-only",
                children=html.Ul(children=[html.Li(v) for k, v in log_dict.items()]),
            ),
        ],
    )


def save_plots_to_disk(
    fig_obj, file_name, file_path_dict, width=None, height=None, scale=None
):
    r"""
    This function saves the plots generated using the Plotly library in this module to the outputs folder.

    Parameters
    ----------
    fig_obj: instance of the classes of the Plotly go library used to generate the plots in this auto-report
        Figure object of the plotly plots

    file_name: str
        The name of the PNG image of the plot to be saved in the output folder.

    file_path_dict: json
        This is the results JSON file which also has the path to the output folder, given by the user.

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

    file_path = file_path_dict[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER]
    file_name = file_name + "_plotly" + ".png"
    file_path_out = os.path.join(os.path.abspath(file_path), file_name)
    fig_obj.write_image(file_path_out, width=width, height=height, scale=scale)
    return


def insert_single_plot(
    x_data,
    y_data,
    plot_type=None,
    plot_title=None,
    x_axis_name=None,
    y_axis_name=None,
    id_plot=None,
    print_only=False,
    color_for_plot="#0A2342",
    path_file=None,
):
    r"""
    Creates single line plots or bar plots using the Plotly library.

    Parameters
    ----------
    x_data: list, or pandas series
        The list of abscissas of the data required for plotting.

    y_data: list, or pandas series, or list of lists
        The list of ordinates of the data required for plotting.

    plot_type: str, "line" or "bar"
        This parameter decides which type of plot will be plotted by this function.
        Default: None

    plot_title: str
        The title of the plot generated.
        Default: None

    x_axis_name: str
        Default: None

    y_axis_name: str
        Default: None

    id_plot: str
        Id of the graph. Each plot gets an unique ID which can be used to manipulate the plot later.
        Default: None

    print_only: bool
        Used to determine if a web version of the plot is to be generated or not.
        Default: False

    color_for_plot: str
        This is string of the hex value of the color to be applied for the plot.
        Default: "#0A2342"

    path_file: json results file
        The .json results file containing the user-specified output folde path needed to save the plots to disk.
        Default: None

    Returns
    -------
    html.Div()
        This html element contains the plot objects generated by this function in a list.

    """
    fig = go.Figure()

    styling_dict = dict(
        showgrid=True,
        gridwidth=1.5,
        zeroline=True,
        mirror=True,
        autorange=True,
        linewidth=1,
        ticks="inside",
        title_font=dict(size=18, color="black"),
    )

    if plot_type == "line":
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

    elif plot_type == "bar":
        # Loop through the label column of the df
        # Plot bars for each parameter with the corresponding value
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

    # Function call to save the Plotly plot to the disk
    save_plots_to_disk(
        fig_obj=fig,
        file_path_dict=path_file,
        file_name=name_file,
        width=1200,
        height=600,
        scale=5,
    )

    # Specific modifications for print version
    fig2 = copy.deepcopy(fig)
    # Make the legend horizontally oriented so as to prevent the legend from being cut off
    fig2.update_layout(legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"))

    rendered_plots = [
        html.Img(
            className="print-only dash-plot",
            src="data:image/png;base64,{}".format(
                base64.b64encode(
                    fig2.to_image(format="png", height=500, width=900)
                ).decode(),
            ),
        )
    ]
    if print_only is False:
        rendered_plots.append(
            dcc.Graph(className="no-print", id=id_plot, figure=fig, responsive=True,)
        )

    return html.Div(children=rendered_plots)


def ready_single_plots(df_pd, dict_of_labels, only_print=False, results_file=None):
    r"""
    This function prepares the data for and calls insert_single_plot for plotting line and bar plots.

    Parameters
    ----------
    df_pd: :pandas:`pandas.DataFrame<frame>`
        The dataframe containing all of the data to be plotted.

    dict_of_labels: dict
        Dictionary holding the titles to be used for the plots generated.

    only_print: bool
        Default: False

    results_file: json results file
        This is the JSON results file that contains the user-specified path where the plots are to be saved as images.
        Default: None

    Returns
    -------
    plots: list
        This list holds the html.Div elements which have the plots encased.
    """

    list_of_keys = list(df_pd.columns)
    list_of_keys.remove("timestamp")
    plots = []
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
        plots.append(
            insert_single_plot(
                x_data=df_pd["timestamp"],
                y_data=df_pd[component],
                plot_type="line",
                plot_title=dict_of_labels[component],
                x_axis_name="Time",
                y_axis_name="kW",
                id_plot=comp_id,
                print_only=only_print,
                color_for_plot=color_plot,
                path_file=results_file,
            )
        )
    return plots


def ready_capacities_plots(df_kpis, json_results_file, only_print=False):
    r""" Call function to produce capacities bar plot and return the plot.

    This function prepares the data to be used for plotting the capacities bar plots, from the simulation results
    and calls the appropriate plotting function that generates the plots.

    Parameters
    ----------
    df_kpis: :pandas:`pandas.DataFrame<frame>`
        This dataframe holds the data required for the capacities bar plot.

    json_results_file: json
        This is the results file, output of the simulation.

    only_print: bool
        Setting this value true results in the function creating only the plot for the PDF report, but not the web app
        version of the auto-report.
        Default: False

    Returns
    -------
    plot: list
        This list holds the html.Div element(s) which themselves contain the plotly plots.
    """

    x_values = []
    y_values = []

    for kpi, cap in zip(list(df_kpis["label"]), list(df_kpis["optimizedAddCap"])):
        if cap > 0:
            x_values.append(kpi)
            y_values.append(cap)

    plot = insert_single_plot(
        x_data=x_values,
        y_data=y_values,
        plot_type="bar",
        plot_title="Optimal additional capacities (kW/kWh/kWp): "
        + json_results_file[PROJECT_DATA][PROJECT_NAME]
        + ", "
        + json_results_file[PROJECT_DATA][SCENARIO_NAME],
        x_axis_name="Items",
        y_axis_name="Capacities",
        id_plot="capacities-plot",
        print_only=only_print,
        path_file=json_results_file,
    )
    return plot


def insert_flows_plots(
    df_plots_data,
    x_legend=None,
    y_legend=None,
    plot_title=None,
    pdf_only=False,
    plot_id=None,
    results_file=None,
    name_of_file=None,
):
    r"""This function creates the line plots for the flows through the various assets of the energy system.

    Parameters
    ----------
    df_plots_data: :pandas:`pandas.DataFrame<frame>`

    x_legend: str
        Default: None

    y_legend: str
        Default: None

    plot_title: str
        Default: None

    pdf_only: bool
        Default: False

    plot_id: str
        Unique alphanumeric value assigned to each pie plot, which can be used for further manipulations such as styling,
        etc., of the plot generated.
        Default: None

    results_file: json file
        The simulation results file that contains the data needed for the production of the plots, determination of the
        path to save outputs and other information necessary for generating the auto-report.
        Default: None

    name_of_file: str
        File name to be used when saving the image file of the plot produced in the output folder.
        Default: None

    Returns
    -------
        html.Div() element
        Contains the list of the flows plots generated, both for the print and web app versions.
    """

    fig = go.Figure()
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
    styling_dict = dict(
        showgrid=True,
        gridwidth=1,
        zeroline=True,
        mirror=True,
        title_font=dict(size=18, color="black"),
        ticks="inside",
        linewidth=1,
    )

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

    # Function call to save the Plotly plot to the disk
    save_plots_to_disk(
        fig_obj=fig,
        file_path_dict=results_file,
        file_name=name_of_file,
        width=1200,
        height=600,
        scale=5,
    )

    # Specific modifications for print version
    fig2 = copy.deepcopy(fig)
    # Make the legend horizontally oriented so as to prevent the legend from being cut off
    fig2.update_layout(legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"))

    plot_created = [
        html.Img(
            className="print-only dash-plot",
            src="data:image/png;base64,{}".format(
                base64.b64encode(
                    fig2.to_image(format="png", height=500, width=900)
                ).decode(),
            ),
        )
    ]
    if pdf_only is False:
        plot_created.append(
            dcc.Graph(className="no-print", id=plot_id, figure=fig, responsive=True,)
        )
    return html.Div(children=plot_created)


def ready_flows_plots(dict_dataseries, json_results_file):
    r"""This function prepares the data from the results JSON file and then calls the appropriate plotting function.

    Parameters
    ----------
    dict_dataseries: dict
        This dictionary holds the data for the flows through various assets.

    json_results_file: json file
        This folds stores all the simulation results.

    Returns
    -------
        multi_plots: list
        This list holds all the plots generated by the function calls to the function insert_flows_plots
    """

    buses_list = list(dict_dataseries.keys())
    multi_plots = []
    for bus in buses_list:
        comp_id = bus + "-plot"
        title = (
            bus
            + " flows in LES: "
            + json_results_file[PROJECT_DATA][PROJECT_NAME]
            + ", "
            + json_results_file[PROJECT_DATA][SCENARIO_NAME]
        )

        df_data = json_results_file["optimizedFlows"][bus]
        df_data.reset_index(level=0, inplace=True)
        df_data = df_data.rename(columns={"index": "timestamp"})

        multi_plots.append(
            insert_flows_plots(
                df_plots_data=df_data,
                x_legend="Time",
                y_legend=bus + " flow in kWh",
                plot_title=title,
                pdf_only=False,
                plot_id=comp_id,
                results_file=json_results_file,
                name_of_file=bus + "_flows_in_LES",
            )
        )

    return multi_plots


def insert_pie_plots(
    title_of_plot,
    names,
    values,
    color_scheme,
    plot_id,
    print_only=False,
    name_file=None,
    path_file_dict=None,
):
    r"""Function that creates and returns a html.Div element with a list of the pie plots.

    Parameters
    ----------
    title_of_plot: str

    names: list
        List containing the labels of the pies in the pie plot.

    values: list
        List containing the values of the labels to be plotted in the pie plot.

    color_scheme: instance of the px.colors class of the Plotly express library
        This parameter holds the color scheme which is palette of colors (list of hex values) to be applied to the pie
        plot to be created.

    plot_id: str
        Unique alphanumeric value assigned to each pie plot, which can be used for further manipulation of the pie plot.

    print_only: bool
        Setting this value true results in the function creating only the plot for the PDF report, but not the web app
        version of the auto-report.
        Default: False

    name_file: str
        This forms part of the name of the file to be used when saving the image of the plot generated to disk.
        Default: None

    path_file_dict: json
        This is the results json file which contains the path defined by the user using which the images of the plots
        generated are saved in the output folder.
        Default: None

    Returns
    -------
    html.Div() element
        Contains the list of the pie plots generated, both for the print and web app versions.
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

    # Function call to save the Plotly plot to the disk
    save_plots_to_disk(
        fig_obj=fig,
        file_path_dict=path_file_dict,
        file_name=name_file,
        width=1200,
        height=600,
        scale=6,
    )

    # Specific modifications for print version
    fig2 = copy.deepcopy(fig)
    # Make the legend horizontally oriented so as to prevent the legend from being cut off
    fig2.update_layout(legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"))

    plot_created = [
        html.Img(
            className="print-only dash-plot",
            src="data:image/png;base64,{}".format(
                base64.b64encode(
                    fig2.to_image(format="png", height=500, width=900)
                ).decode(),
            ),
        )
    ]

    if print_only is False:
        plot_created.append(
            dcc.Graph(className="no-print", id=plot_id, figure=fig, responsive=True,)
        )
    return html.Div(children=plot_created)


def ready_pie_plots(df_pie_data, json_results_file, only_print=False):
    r"""Process data for the pie plots and call the relevant functions, resulting in the generation of the pie plots.
    
    Parameters
    ----------
    df_pie_data: :pandas:`pandas.DataFrame<frame>`
        This dataframe contains the costs data necessary to create the pie plots.


    json_results_file: json
        This is json file with all the results necessary to create the elements of the autoreport. In this case, it is
        required to determine the user-provided outputs folder path.


    only_print: bool
        Setting this value true results in the function creating only the plot for the PDF report, but not the web app
        version of the auto-report.
        Default: False

    Returns
    -------

    """
    # Initialize an empty list and a dict for use later in the function
    pie_plots = []
    pie_data_dict = {}

    # df_pie_data.reset_index(drop=True, inplace=True)
    columns_list = list(df_pie_data.columns)
    columns_list.remove(LABEL)

    # Loop to iterate through the list of columns of the DF which are nothing but the KPIs to be plotted
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
            scheme_choosen = px.colors.diverging.BrBG
            file_name = "upfront_investment_costs"
        elif "om" in kp_indic:
            kpi_part = "Operation and Maintenance Costs ("
            scheme_choosen = px.colors.sequential.RdBu
            file_name = "operation_and_maintainance_costs"

        # Title of the pie plot
        plot_title = (
            kpi_part
            + str(round(total_for_title, 2))
            + "$): "
            + json_results_file[PROJECT_DATA][PROJECT_NAME]
            + ", "
            + json_results_file[PROJECT_DATA][SCENARIO_NAME]
        )

        # Append the plot to the list by calling the plotting function directly
        pie_plots.append(
            insert_pie_plots(
                title_of_plot=plot_title,
                names=names_plot,
                values=values_plot,
                color_scheme=scheme_choosen,
                plot_id=comp_id,
                print_only=only_print,
                name_file=file_name,
                path_file_dict=json_results_file,
            )
        )
    return pie_plots


# Styling of the report


def create_app(results_json):
    r"""Initializes the app and calls all the other functions, resulting in the web app as well as pdf.

    This function specifies the layout of the web app, loads the external styling sheets, prepares the necessary data
    from the json results file, calls all the helper functions on the data, resulting in the auto-report.

    Parameters
    ----------
    results_json: json results file
        This file is the result of the simulation and contains all the data necessary to generate the auto-report.

    Returns
    -------
    app: instance of the Dash class within the dash library
        This app holds together all the html elements wrapped in Python, necessary for the rendering of the auto-report.
    """

    # external CSS stylesheets
    external_stylesheets = [
        {
            "href": "https://cdnjs.cloudflare.com/ajax/libs/foundation/6.6.3/css/foundation.min.css",
            "rel": "stylesheet",
            "integrity": "sha256-ogmFxjqiTMnZhxCqVmcqTvjfe1Y/ec4WaRj/aQPvn+I=",
            "crossorigin": "anonymous",
            "media": "screen",
        },
    ]

    app = dash.Dash(
        __name__,
        assets_folder=os.path.join(REPORT_PATH, "assets"),
        external_stylesheets=external_stylesheets,
    )

    # Reading the relevant user-inputs from the json_with_results.json file into Pandas dataframes
    dfprojectData = pd.DataFrame.from_dict(results_json[PROJECT_DATA])
    dfeconomicData = pd.DataFrame.from_dict(results_json[ECONOMIC_DATA]).loc[VALUE]

    # Obtaining the coordinates of the project location
    coordinates = (
        float(dfprojectData.latitude),
        float(dfprojectData.longitude),
    )

    # Determining the geographical location of the project
    geoList = rg.search(coordinates)
    geoDict = geoList[0]
    location = geoDict["name"]

    # Adds a map to the Dash app
    mapy = folium.Map(location=coordinates, zoom_start=14)
    tooltip = "Click here for more info"
    folium.Marker(
        coordinates,
        popup="Location of the project",
        tooltip=tooltip,
        icon=folium.Icon(color="red", icon="glyphicon glyphicon-flash"),
    ).add_to(mapy)
    mapy.save(os.path.join(REPORT_PATH, "assets", "proj_map"))

    # Adds a staticmap to the PDF

    longitude = coordinates[1]
    latitude = coordinates[0]
    coords = longitude, latitude

    map_static = staticmap.StaticMap(600, 600, 80)
    marker = staticmap.CircleMarker(coords, "#13074f", 15)
    map_static.add_marker(marker)
    map_image = map_static.render(zoom=14)
    map_image.save(os.path.join(REPORT_PATH, "assets", "proj_map_static.png"))

    dict_projectdata = {
        "Country": dfprojectData.country,
        "Project ID": dfprojectData.project_id,
        "Scenario ID": dfprojectData.scenario_id,
        "Currency": dfeconomicData.currency,
        "Project Location": location,
        "Discount Factor": dfeconomicData.discount_factor,
        "Tax": dfeconomicData.tax,
    }

    df_projectData = pd.DataFrame(
        list(dict_projectdata.items()), columns=["Label", "Value"]
    )

    dict_simsettings = {
        "Evaluated period": results_json[SIMULATION_SETTINGS][EVALUATED_PERIOD][VALUE],
        "Start date": results_json[SIMULATION_SETTINGS][START_DATE],
        "Timestep length": results_json[SIMULATION_SETTINGS][TIMESTEP][VALUE],
    }

    df_simsettings = pd.DataFrame(
        list(dict_simsettings.items()), columns=["Setting", "Value"]
    )

    projectName = (
        results_json[PROJECT_DATA][PROJECT_NAME]
        + " (ID: "
        + str(results_json[PROJECT_DATA][PROJECT_ID])
        + ")"
    )
    scenarioName = (
        results_json[PROJECT_DATA][SCENARIO_NAME]
        + " (ID: "
        + str(results_json[PROJECT_DATA][SCENARIO_ID])
        + ")"
    )

    releaseDesign = "0.0x"

    # Getting the branch ID
    repo = git.Repo(search_parent_directories=True)
    # TODO: also extract branch name
    branchID = repo.head.object.hexsha

    simDate = time.strftime("%Y-%m-%d")

    ELAND_LOGO = base64.b64encode(
        open(
            os.path.join(REPORT_PATH, "assets", "logo-eland-original.jpg"), "rb"
        ).read()
    )

    MAP_STATIC = base64.b64encode(
        open(os.path.join(REPORT_PATH, "assets", "proj_map_static.png"), "rb").read()
    )

    # Determining the sectors which were simulated

    sectors = list(results_json[PROJECT_DATA][SECTORS].keys())
    sec_list = """"""
    for sec in sectors:
        sec_list += "\n" + f"\u2022 {sec.upper()}"

    # Creating a dataframe for the demands
    demands = results_json[ENERGY_CONSUMPTION]

    # Removing all columns that are not actually from demands
    drop_list = []
    for column_label in demands:
        # Identifies excess sink in demands for removal
        if EXCESS in column_label:
            drop_list.append(column_label)
        # Identifies DSO_feedin sink in demands for removal
        elif DSO_FEEDIN + AUTO_SINK in column_label:
            drop_list.append(column_label)
        elif DSO_FEEDIN in column_label:
            drop_list.append(column_label)

    # Remove some elements from drop_list (ie. sinks that are not demands) from data
    for item in drop_list:
        del demands[item]

    dem_keys = list(demands.keys())
    demand_data = {}

    for dem in dem_keys:
        demand_data.update(
            {
                dem: [
                    demands[dem][UNIT],
                    demands[dem][TIMESERIES_PEAK][VALUE],
                    demands[dem]["timeseries_average"][VALUE],
                    demands[dem]["timeseries_total"][VALUE],
                ]
            }
        )

    df_dem = pd.DataFrame.from_dict(
        demand_data,
        orient="index",
        columns=[UNIT, "Peak Demand", "Mean Demand", "Total Demand per annum"],
    )
    df_dem.index.name = "Demands"
    df_dem = df_dem.reset_index()
    df_dem = df_dem.round(2)

    # Creating a DF for the components table

    components1 = results_json[ENERGY_PRODUCTION]
    components2 = results_json[ENERGY_CONVERSION]

    comp1_keys = list(components1.keys())
    comp2_keys = list(components2.keys())

    components = {}

    for comps in comp1_keys:
        components.update(
            {
                comps: [
                    components1[comps][OEMOF_ASSET_TYPE],
                    "Electricity",
                    # components1[comps][ENERGY_VECTOR],
                    components1[comps][UNIT],
                    components1[comps][INSTALLED_CAP][VALUE],
                    components1[comps][OPTIMIZE_CAP][VALUE],
                ]
            }
        )
    for comps in comp2_keys:
        components.update(
            {
                comps: [
                    components2[comps][OEMOF_ASSET_TYPE],
                    components2[comps][ENERGY_VECTOR],
                    components2[comps][UNIT],
                    components2[comps][INSTALLED_CAP][VALUE],
                    components2[comps][OPTIMIZE_CAP][VALUE],
                ]
            }
        )

    df_comp = pd.DataFrame.from_dict(
        components,
        orient="index",
        columns=[
            "Type of Component",
            "Energy Vector",
            UNIT,
            "Installed Capcity",
            "Optimization",
        ],
    )
    df_comp.index.name = "Component"
    df_comp = df_comp.reset_index()

    for i in range(len(df_comp)):
        if df_comp.at[i, "Optimization"]:
            df_comp.iloc[i, df_comp.columns.get_loc("Optimization")] = "Yes"
        else:
            df_comp.iloc[i, df_comp.columns.get_loc("Optimization")] = "No"

    # Creating a Pandas dataframe for the components optimization results table

    # Read in the scalar matrix as pandas dataframe
    df_scalar_matrix = results_json[KPI][KPI_SCALAR_MATRIX]

    # Changing the index to a sequence of 0,1,2...
    df_scalar_matrix = df_scalar_matrix.reset_index()

    # Dropping irrelevant columns from the dataframe
    df_scalar_matrix = df_scalar_matrix.drop(
        ["index", TOTAL_FLOW, PEAK_FLOW, AVERAGE_FLOW], axis=1
    )

    # Renaming the columns
    df_scalar_matrix = df_scalar_matrix.rename(
        columns={
            LABEL: "Component/Parameter",
            OPTIMIZED_ADD_CAP: "CAP",
            ANNUAL_TOTAL_FLOW: "Aggregated Flow",
        }
    )
    # Rounding the numeric values to two significant digits
    df_scalar_matrix = df_scalar_matrix.round(2)

    # Creating a Pandas dataframe for the costs' results

    # Read in the cost matrix as a pandas dataframe
    df_cost_matrix = results_json[KPI][KPI_COST_MATRIX]

    # Changing the index to a sequence of 0,1,2...
    df_cost_matrix = df_cost_matrix.reset_index()

    # Drop some irrelevant columns from the dataframe
    df_cost_matrix = df_cost_matrix.drop(
        ["index", COST_OM_TOTAL, COST_INVESTMENT, COST_DISPATCH, COST_OM_FIX,], axis=1,
    )

    # Rename some of the column names
    df_cost_matrix = df_cost_matrix.rename(
        columns={
            LABEL: "Component",
            COST_TOTAL: "CAP",
            COST_UPFRONT: "Upfront Investment Costs",
        }
    )

    # Round the numeric values to two significant digits
    df_cost_matrix = df_cost_matrix.round(2)

    # Dictionaries to gather non-fatal warning and error messages that appear during the simulation
    warnings_dict = {}
    errors_dict = {}

    log_file = os.path.join(OUTPUT_FOLDER, "mvs_logfile.log")
    # log_file = "/home/mr/Projects/mvs_eland/MVS_outputs/mvs_logfile.log"

    with open(log_file) as log_messages:
        log_messages = log_messages.readlines()

    i = 0
    for line in log_messages:
        if "WARNING" in line:
            i = i + 1
            substrings = line.split(" - ")
            message_string = substrings[-1]
            warnings_dict.update({i: message_string})
        elif "ERROR" in line:
            i = i + 1
            substrings = line.split(" - ")
            message_string = substrings[-1]
            errors_dict.update({i: message_string})

    # Build a pandas dataframe with the data for the various demands

    # The below dict will gather all the keys of the various plots for later use in the graphOptions.csv
    dict_for_plots = {"demands": {}, "supplies": {}}
    dict_plot_labels = {}

    # demands is a dict with all the info for the demands
    # dem_keys is a list of keys of the demands dict

    # The below loop will add all the demands to the dict_for_plots dictionary, including the timeseries values
    for demand in dem_keys:
        dict_for_plots["demands"].update(
            {demand: results_json[ENERGY_CONSUMPTION][demand][TIMESERIES]}
        )
        dict_plot_labels.update(
            {demand: results_json[ENERGY_CONSUMPTION][demand]["label"]}
        )

    # Later, this dataframe can be passed to a function directly make the graphs with Plotly
    df_all_demands = pd.DataFrame.from_dict(dict_for_plots["demands"], orient="columns")

    # Change the index of the dataframe
    df_all_demands.reset_index(level=0, inplace=True)
    # Rename the timestamp column from 'index' to 'timestamp'
    df_all_demands = df_all_demands.rename(columns={"index": "timestamp"})

    # Collect the keys of various resources (PV, Wind, etc.)
    resources = results_json[ENERGY_PRODUCTION]

    # List of resources (includes DSOs, which need to be removed)
    res_keys = list(resources.keys())
    for res in res_keys:
        if "DSO_" in res:
            del resources[res]

    # List of resources (with the DSOs deleted)
    res_keys = list(resources.keys())

    # The below loop will add all the resources to the dict_for_plots dictionary, including the timeseries values
    for resource in res_keys:
        dict_for_plots["supplies"].update(
            {resource: results_json[ENERGY_PRODUCTION][resource][TIMESERIES]}
        )
        dict_plot_labels.update(
            {resource: results_json[ENERGY_PRODUCTION][resource]["label"]}
        )

    # Later, this dataframe can be passed to a function directly make the graphs with Plotly
    df_all_res = pd.DataFrame.from_dict(dict_for_plots["supplies"], orient="columns")

    # Change the index of the dataframe
    df_all_res.reset_index(level=0, inplace=True)
    # Rename the timestamp column from 'index' to 'timestamp'
    df_all_res = df_all_res.rename(columns={"index": "timestamp"})

    # Dict that gathers all the flows through various buses
    data_flows = results_json["optimizedFlows"]

    # Add dataframe to hold all the KPIs and optimized additional capacities
    df_capacities = results_json[KPI][KPI_SCALAR_MATRIX]
    df_capacities.drop(
        columns=["total_flow", "annual_total_flow", "peak_flow", "average_flow"],
        inplace=True,
    )
    df_capacities.reset_index(drop=True, inplace=True)

    # Data preparation operations for generating the pie charts with Plotly

    # Get the cost matrix from the results JSON file into a pandas DF
    df_kpis = results_json[KPI][KPI_COST_MATRIX]

    # List of the needed parameters
    costs_needed = [LABEL, ANNUITY_TOTAL, COST_INVESTMENT, COST_OM_TOTAL]

    # Drop all the irrelevant columns
    df_kpis = df_kpis[costs_needed]

    # Add a row with total of each column, except label
    df_kpis = df_kpis.append(df_kpis.sum(numeric_only=True), ignore_index=True)

    # Add a label for the row holding the sum of each column
    df_kpis.iloc[-1, 0] = "Total"

    # App layout and populating it with different elements

    app.layout = html.Div(
        id="main-div",
        className="grid-x align-center",
        children=[
            html.Div(
                className="cell small-10 small_offset-1 header_title_logo",
                children=[
                    html.Img(
                        id="mvslogo",
                        src="data:image/png;base64,{}".format(ELAND_LOGO.decode()),
                        width="500px",
                    ),
                    html.H1("MULTI VECTOR SIMULATION - REPORT SHEET"),
                ],
            ),
            html.Section(
                className="cell small-10 small_offset-1 grid-x",
                children=[
                    insert_headings("Information"),
                    html.Div(
                        className="cell imp_info",
                        children=[
                            html.P(f"MVS Release: {version_num} ({version_date})"),
                            html.P(f"Branch-id: {branchID}"),
                            html.P(f"Simulation date: {simDate}"),
                            html.Div(
                                className="cell imp_info2",
                                children=[
                                    html.Span(
                                        "Project name   : ",
                                        style={"font-weight": "bold"},
                                    ),
                                    f"{projectName}",
                                ],
                            ),
                            html.Div(
                                className="cell imp_info2",
                                children=[
                                    html.Span(
                                        "Scenario name  : ",
                                        style={"font-weight": "bold"},
                                    ),
                                    f"{scenarioName}",
                                ],
                            ),
                            html.Div(
                                className="blockoftext",
                                children=[
                                    "The energy system with the ",
                                    html.Span(
                                        f"{projectName}", style={"font-style": "italic"}
                                    ),
                                    " for the scenario ",
                                    html.Span(
                                        f"{scenarioName}",
                                        style={"font-style": "italic"},
                                    ),
                                    " was simulated with the Multi-Vector simulation tool MVS 0.0x developed from the E-LAND toolbox "
                                    "developed in the scope of the Horizon 2020 European research project. The tool was developed by "
                                    "Reiner Lemoine Institute and utilizes the OEMOF framework.",
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Section(
                className="cell small-10 small_offset-1 grid-x",
                style={"pageBreakBefore": "always"},
                children=[
                    insert_headings("Input Data"),
                    insert_subsection(
                        title="Project Data",
                        content=[
                            insert_body_text(
                                "The most important simulation data will be presented below. "
                                "Detailed settings, costs, and technological parameters can "
                                "be found in the appendix."
                            ),
                            html.Div(
                                className="grid-x ",
                                id="location-map-div",
                                children=[
                                    html.Div(
                                        className="cell small-6 location-map-column",
                                        children=[
                                            html.H4(["Project Location"]),
                                            html.Iframe(
                                                srcDoc=open(
                                                    os.path.join(
                                                        REPORT_PATH,
                                                        "assets",
                                                        "proj_map",
                                                    ),
                                                    "r",
                                                ).read(),
                                                height="400",
                                                style={
                                                    "margin": "30px",
                                                    "width": "30%",
                                                    "marginBottom": "1.5cm",
                                                },
                                            ),
                                            html.Div(
                                                className="staticimagepdf",
                                                children=[
                                                    insert_body_text(
                                                        "The blue dot in the below map indicates "
                                                        "the location of the project."
                                                    ),
                                                    html.Img(
                                                        id="staticmapimage",
                                                        src="data:image/png;base64,{}".format(
                                                            MAP_STATIC.decode()
                                                        ),
                                                        width="400px",
                                                        style={"marginLeft": "30px"},
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="cell small-6 location-map-column",
                                        children=make_dash_data_table(
                                            df_projectData, "Project at a Glance"
                                        ),
                                    ),
                                ],
                            ),
                            make_dash_data_table(df_simsettings, "Simulation Settings"),
                        ],
                    ),
                    insert_subsection(
                        title="Energy demand",
                        content=[
                            insert_body_text(
                                "The simulation was performed for the energy system "
                                "covering the following sectors: "
                            ),
                            insert_body_text(f"{sec_list}"),
                            html.H4("Electricity Demand"),
                            insert_body_text(
                                "Electricity demands " "that have to be supplied are:"
                            ),
                            make_dash_data_table(df_dem),
                            html.Div(
                                children=ready_single_plots(
                                    df_all_demands,
                                    dict_plot_labels,
                                    results_file=results_json,
                                )
                            ),
                            html.H4("Resources"),
                            html.Div(
                                children=ready_single_plots(
                                    df_all_res,
                                    dict_plot_labels,
                                    results_file=results_json,
                                )
                            ),
                        ],
                    ),
                    insert_subsection(
                        title="Energy system components",
                        content=[
                            insert_body_text(
                                "The energy system is comprised of "
                                "the following components:"
                            ),
                            make_dash_data_table(df_comp),
                        ],
                    ),
                ],
            ),
            html.Section(
                className="cell small-10 small_offset-1 grid-x",
                style={"pageBreakBefore": "always"},
                children=[
                    html.H2(className="cell", children="Simulation Results"),
                    insert_subsection(
                        title="Dispatch & Energy Flows",
                        content=[
                            insert_body_text(
                                "The capacity optimization of components that were to be used resulted in:"
                            ),
                            make_dash_data_table(df_scalar_matrix),
                            insert_body_text(
                                "With this, the demands are met with the following dispatch schedules:"
                            ),
                            html.Div(
                                children=ready_flows_plots(
                                    dict_dataseries=data_flows,
                                    json_results_file=results_json,
                                )
                            ),
                            html.Div(
                                className="add-cap-plot",
                                children=ready_capacities_plots(
                                    df_kpis=df_capacities,
                                    json_results_file=results_json,
                                    only_print=False,
                                ),
                            ),
                            insert_body_text(
                                "This results in the following KPI of the dispatch:"
                            ),
                            # TODO the table with renewable share, emissions, total renewable generation, etc.
                        ],
                    ),
                    insert_subsection(
                        title="Economic Evaluation",
                        content=[
                            insert_body_text(
                                "The following installation and operation costs "
                                "result from capacity and dispatch optimization:"
                            ),
                            make_dash_data_table(df_cost_matrix),
                            html.Div(
                                className="add-pie-plots",
                                children=ready_pie_plots(
                                    df_pie_data=df_kpis,
                                    json_results_file=results_json,
                                    only_print=False,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
            html.Section(
                className="cell small-10 small_offset-1 grid-x",
                children=[
                    html.Div(
                        className="cell",
                        children=[insert_headings(heading_text="Logging Messages"),],
                    ),
                    html.Div(
                        children=[
                            insert_subsection(
                                title="Warning Messages",
                                content=insert_log_messages(log_dict=warnings_dict),
                            ),
                            insert_subsection(
                                title="Error Messages",
                                content=insert_log_messages(log_dict=errors_dict),
                            ),
                        ]
                    ),
                ],
            ),
        ],
    )
    return app


if __name__ == "__main__":
    from src.constants import REPO_PATH, OUTPUT_FOLDER
    from src.B0_data_input_json import load_json

    dict_values = load_json(
        os.path.join(REPO_PATH, OUTPUT_FOLDER, "json_with_results.json")
    )

    test_app = create_app(dict_values)
    open_in_browser(test_app)
