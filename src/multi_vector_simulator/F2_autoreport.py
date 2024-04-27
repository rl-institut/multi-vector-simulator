"""
Module F2 - Autoreport
======================

This script generates a report of the simulation automatically, with all the important data.
"""

import base64
import os
import pickle

# Imports for generating pdf automatically
import threading
import time
import webbrowser

# Importing necessary packages
import dash
from dash import html
from dash import dcc
from dash import dash_table
import folium
import pandas as pd
import reverse_geocoder as rg
import staticmap
import asyncio
import copy

from pyppeteer import launch

# This removes extensive logging in the console for pyppeteer.
import logging

pyppeteer_level = logging.WARNING
logging.getLogger("pyppeteer").setLevel(pyppeteer_level)

# This removes extensive logging in the console for the dash app (it runs on Flask server)
flask_log = logging.getLogger("werkzeug")
flask_log.setLevel(logging.ERROR)

from multi_vector_simulator.utils import copy_report_assets

from multi_vector_simulator.utils.constants import (
    REPO_PATH,
    PATH_OUTPUT_FOLDER,
    PATHS_TO_PLOTS,
    PLOT_SANKEY,
    OUTPUT_FOLDER,
    INPUTS_COPY,
    CSV_ELEMENTS,
    PLOTS_ES,
    ECONOMIC_DATA,
    PROJECT_DATA,
    JSON_WITH_RESULTS,
    JSON_FILE_EXTENSION,
    LOGFILE,
)
from multi_vector_simulator.utils.constants_json_strings import (
    LES_ENERGY_VECTOR_S,
    VALUE,
    SIMULATION_SETTINGS,
    EVALUATED_PERIOD,
    START_DATE,
    TIMESTEP,
    PROJECT_NAME,
    PROJECT_ID,
    SCENARIO_NAME,
    SCENARIO_ID,
    DEMANDS,
    RESOURCES,
    LOGS,
    ERRORS,
    WARNINGS,
    SIMULATION_RESULTS,
    SCENARIO_DESCRIPTION,
    KPI,
    KPI_UNCOUPLED_DICT,
)

from multi_vector_simulator.E1_process_results import (
    convert_demand_to_dataframe,
    convert_components_to_dataframe,
    convert_scalar_matrix_to_dataframe,
    convert_cost_matrix_to_dataframe,
    convert_scalars_to_dataframe,
    convert_kpi_sector_to_dataframe,
)
from multi_vector_simulator.F1_plotting import (
    plot_timeseries,
    plot_piecharts_of_costs,
    plot_optimized_capacities,
    plot_instant_power,
    plot_sankey,
)

from multi_vector_simulator.version import version_num, version_date

OUTPUT_FOLDER = os.path.join(REPO_PATH, OUTPUT_FOLDER)
CSV_FOLDER = os.path.join(REPO_PATH, OUTPUT_FOLDER, INPUTS_COPY, CSV_ELEMENTS)


async def _print_pdf_from_chrome(path_pdf_report):
    r"""
    This function generates the PDF report from the web app rendered on a Chromium-based browser.

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
    await page.goto(
        "http://127.0.0.1:8050", {"waitUntil": "domcontentloaded", "timeout": 120000}
    )
    await page.waitForSelector(
        ".dash-cell", {"visible": "true",},
    )
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
    df: :class:`pandas.DataFrame<frame>`
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


def insert_plotly_figure(
    fig, id_plot=None, print_only=False,
):
    r"""
    Insert a plotly figure in a dash app layout

    Parameters
    ----------
    fig: :class:`plotly.graph_objs.Figure`
        figure object

    id_plot: str
        Id of the graph. Should be unique.
        Default: None

    print_only: bool
        Used to determine if a web version of the plot is to be generated or not.
        Default: False

    Returns
    -------
    `dash_html_components.Div`
        Html Div component containing an image for the print-only version and a plotly figure for
        the online (no-print) app (in the app the user can interact with plotly figure,
        whereas the image is static).

    """

    # Specific modifications for print-only version
    fig2 = copy.deepcopy(fig)
    # Make the legend horizontally oriented so as to prevent the legend from being cut off
    fig2.update_layout(legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"))

    # Static image for the pdf report
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

    # Dynamic plotly figure for the app
    if print_only is False:
        rendered_plots.append(
            dcc.Graph(className="no-print", id=id_plot, figure=fig, responsive=True,)
        )

    return html.Div(children=rendered_plots)


def ready_timeseries_plots(
    dict_values, data_type=DEMANDS, only_print=False, sector_demands=None
):
    r"""Insert the timeseries line plots in a dash html layout.

    Parameters
    ----------
    dict_values: dict
        Dict with all simulation parameters

    data_type: str
        one of DEMANDS or RESOURCES
        Default: DEMANDS

    only_print: bool
        Setting this value true results in the function creating only the plot for the PDF report,
        but not the web app version of the auto-report.
        Default: False

    sector_demands: str
        Name of the sector of the energy system
        Default: None

    Returns
    -------
    plots: list
        List containing the timeseries line plots dash components
    """

    figs = plot_timeseries(dict_values, data_type, sector_demands=sector_demands)
    plots = [
        insert_plotly_figure(fig, id_plot=comp_id, print_only=only_print)
        for comp_id, fig in figs.items()
    ]
    return plots


def ready_capacities_plots(dict_values, only_print=False):
    r"""Insert the capacities bar plots in a dash html layout

    Parameters
    ----------
    dict_values: dict
        Dict with all simulation parameters

    only_print: bool
        Setting this value true results in the function creating only the plot for the PDF report,
        but not the web app version of the auto-report.
        Default: False

    Returns
    -------
    cap_plots: list
        List containing the capacities bar plots dash components
    """

    figs = plot_optimized_capacities(dict_values)
    cap_plots = [
        insert_plotly_figure(fig, id_plot=comp_id, print_only=only_print)
        for comp_id, fig in figs.items()
    ]
    return cap_plots


def ready_flows_plots(dict_values, only_print=False):
    r"""Generate figure for each assets' flow of the energy system.

    Parameters
    ----------
    dict_values: dict
        Dict with all simulation parameters

    only_print: bool
        Setting this value true results in the function creating only the plot for the PDF report,
        but not the web app version of the auto-report.
        Default: False

    Returns
    -------
    multi_plots: list
        List containing the assets' timeseries plots as dash components
    """

    figs = plot_instant_power(dict_values)
    multi_plots = [
        insert_plotly_figure(fig, id_plot=comp_id, print_only=only_print)
        for comp_id, fig in figs.items()
    ]
    return multi_plots


def ready_costs_pie_plots(dict_values, only_print=False):
    r"""Insert the pie plots in a dash html layout

    Parameters
    ----------
    dict_values: dict
        Dict with all simulation parameters

    only_print: bool
        Setting this value true results in the function creating only the plot for the PDF report,
        but not the web app version of the auto-report.
        Default: False

    Returns
    -------
    pie_plots: list
        List containing the cost pie plots dash components
    """

    figs = plot_piecharts_of_costs(dict_values)
    pie_plots = [
        insert_plotly_figure(fig, id_plot=comp_id, print_only=only_print)
        for comp_id, fig in figs.items()
    ]
    return pie_plots


def ready_sankey_diagram(dict_values, only_print=False):
    fig = plot_sankey(dict_values)
    # Specific modifications for print-only version
    # fig2 = copy.deepcopy(fig)
    # Make the legend horizontally oriented so as to prevent the legend from being cut off
    # fig2.update_layout(legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"))

    # Static image for the pdf report
    rendered_plots = [
        html.Img(
            className="print-only dash-plot",
            src="data:image/png;base64,{}".format(
                base64.b64encode(
                    fig.to_image(format="png", height=500, width=900)
                ).decode(),
            ),
        )
    ]

    # Dynamic plotly figure for the app
    if only_print is False:
        rendered_plots.append(
            dcc.Graph(
                className="no-print",
                id="sankey-diagram",
                figure=fig,
                responsive=True,
                style={"width": "100%", "height": "900px"},
            )
        )

    return rendered_plots


def encode_image_file(img_path):
    """Encode image files to load them in the dash layout under img html tag

    Parameters
    ----------
    img_path: str
        path to the image file

    Returns
    -------
    encoded_img: bytes
        encoded bytes of the image file

    """

    try:
        with open(img_path, "rb") as ifs:
            encoded_img = base64.b64encode(ifs.read())
    except FileNotFoundError:
        encoded_img = base64.b64encode(bytes())
    return encoded_img


def create_demands_section(output_JSON_file, sectors=None):
    """This function creates a HTML Div element that holds an entire section with either the demands or the resources

    Parameters
    ----------

    output_JSON_file: dict
        Dict with all simulation parameters

    sectors: list
        List holding the names of sectors of the energy system as strings
        Default: None

    Returns
    -------
    Function call to insert_subsection() that generates the demands section of the autoreport

    """

    # Format the list of sectors
    sec_list = """"""
    for sec in sectors:
        sec_list += "\n" + f"\u2022 {sec.upper()}"

    # List of content
    content_of_section = [
        insert_body_text(
            "The simulation was performed for the energy system "
            "covering the following sectors: "
        ),
        insert_body_text(f"{sec_list}"),
    ]

    # Loop to generate the sector headings, sectoral-demands' tables and plots of the demands in each of the sectors
    for sector in sectors:

        # Determining the sector heading
        sector_heading = sector.title() + " Demands"

        # Collect the sector_specific demands in a dataframe
        df_sector_demands = convert_demand_to_dataframe(
            dict_values=output_JSON_file, sector_demands=sector
        )

        # Function call that generates a dash table from the above dataframe and saves it in a variable
        table_with_dash = make_dash_data_table(df_sector_demands)

        # Function that plots the sector-specific demands
        sector_demand_plots = html.Div(
            children=ready_timeseries_plots(
                dict_values=output_JSON_file, sector_demands=sector
            )
        )

        # Add the heading, table and plot(s) to the content list only if it is not empty
        if df_sector_demands.empty is False:
            content_of_section.extend(
                (html.H4(sector_heading), table_with_dash, sector_demand_plots)
            )

    return insert_subsection(title="Energy Demands", content=content_of_section)


# Styling of the report
def create_app(results_json, path_sim_output=None):
    r"""Initializes the app and calls all the other functions, resulting in the web app as well as pdf.

    This function specifies the layout of the web app, loads the external styling sheets, prepares the necessary data
    from the json results file, calls all the helper functions on the data, resulting in the auto-report.

    Parameters
    ----------
    results_json: json results file
        This file is the result of the simulation and contains all the data necessary to generate the auto-report.

    path_sim_output: str
        Path to the mvs simulation's output files' folder
        Default: output path saved in the result_json

    Returns
    -------
    app: instance of the Dash class within the dash library
        This app holds together all the html elements wrapped in Python, necessary for the rendering of the auto-report.
    """

    if path_sim_output is None:
        path_sim_output = results_json[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER]

    # create a "report" folder containing an "asset" folder
    asset_folder = os.path.abspath(copy_report_assets(path_sim_output))

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

    tab_name = f"{results_json[PROJECT_DATA][SCENARIO_NAME]} ({results_json[PROJECT_DATA][SCENARIO_ID]})"
    app = dash.Dash(
        assets_folder=asset_folder,
        external_stylesheets=external_stylesheets,
        title=tab_name,
    )

    # Reading the relevant user-inputs from the JSON_WITH_RESULTS.json file into Pandas dataframes

    # .iloc[0] is used as PROJECT_DATA includes LES_ENERGY_VECTOR_S, which can have multiple entries.
    # Pased to a DF, we have multiple rows - for eah sector one row.
    # This messes up reading the data from the DF later, so we only take one row which then contains all relevant data.
    dfprojectData = pd.DataFrame.from_dict(results_json[PROJECT_DATA]).iloc[0]
    dfeconomicData = pd.DataFrame.from_dict(results_json[ECONOMIC_DATA]).loc[VALUE]

    # Obtaining the latlong of the project location
    latlong = (
        float(dfprojectData.latitude),
        float(dfprojectData.longitude),
    )
    # Determining the geographical location of the project
    geo_dict_path = os.path.join(asset_folder, "geolocation")
    if os.path.exists(geo_dict_path):
        with open(geo_dict_path, "rb") as handle:
            geo_dict = pickle.load(handle)
    else:
        geoList = rg.search(latlong)
        geo_dict = geoList[0]
        with open(geo_dict_path, "wb") as handle:
            pickle.dump(geo_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    location = geo_dict["name"]

    leaflet_map_path = os.path.join(asset_folder, "proj_map.html")
    static_map_path = os.path.join(asset_folder, "proj_map_static.png")

    # Add a dynamic leaflet map to the dash app
    if not os.path.exists(leaflet_map_path):
        mapy = folium.Map(location=latlong, zoom_start=14)
        tooltip = "Click here for more info"
        folium.Marker(
            latlong,
            popup="Location of the project",
            tooltip=tooltip,
            icon=folium.Icon(color="red", icon="glyphicon glyphicon-flash"),
        ).add_to(mapy)
        mapy.save(leaflet_map_path)

    # Adds a static map for the PDF report
    MAP_STATIC = None
    if not os.path.exists(static_map_path):
        longitude = latlong[1]
        latitude = latlong[0]
        coords = longitude, latitude

        map_static = staticmap.StaticMap(600, 600, 80)
        marker = staticmap.CircleMarker(coords, "#13074f", 15)
        map_static.add_marker(marker)
        try:
            map_image = map_static.render(zoom=14)
            map_image.save(static_map_path)
            MAP_STATIC = encode_image_file(static_map_path)
        except RuntimeError as e:
            if "could not download" in repr(e):
                logging.warning(
                    "You might not be connected to internet, skipping the download of "
                    "location map for the report"
                )

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

    simDate = time.strftime("%Y-%m-%d")

    ELAND_LOGO = encode_image_file(
        os.path.join(asset_folder, "logo-eland-original.jpg")
    )

    ENERGY_SYSTEM_GRAPH = encode_image_file(results_json[PATHS_TO_PLOTS][PLOTS_ES])

    # Determining the sectors which were simulated

    sectors = list(results_json[PROJECT_DATA][LES_ENERGY_VECTOR_S].keys())
    sec_list = """"""
    for sec in sectors:
        sec_list += "\n" + f"\u2022 {sec.upper()}"

    df_comp = convert_components_to_dataframe(results_json)
    df_scalar_matrix = convert_scalar_matrix_to_dataframe(results_json)
    df_cost_matrix = convert_cost_matrix_to_dataframe(results_json)
    df_kpi_scalars = convert_scalars_to_dataframe(results_json)
    df_kpi_sectors = convert_kpi_sector_to_dataframe(results_json)

    # Obtain the scenario description text provided by the user from the JSON results file
    scenario_description = results_json[PROJECT_DATA].get(SCENARIO_DESCRIPTION, "")

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
                                className="cell imp_info2",
                                children=[]
                                if scenario_description == ""
                                else [
                                    html.Span(
                                        "Scenario description  : ",
                                        style={"font-weight": "bold"},
                                    ),
                                    f"{scenario_description}",
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
                                className="grid-x",
                                id="location-map-div",
                                children=[
                                    html.Div(
                                        className="cell small-6 location-map-column",
                                        children=[
                                            html.H4(["Project Location"]),
                                            html.Iframe(
                                                srcDoc=open(
                                                    leaflet_map_path, "r",
                                                ).read(),
                                                height="400",
                                            ),
                                            html.Div(
                                                className="staticimagepdf print-only",
                                                children=[
                                                    insert_body_text(
                                                        "The blue dot in the below map indicates "
                                                        "the location of the project."
                                                    ),
                                                    html.Img(
                                                        id="staticmapimage",
                                                        src=""
                                                        if MAP_STATIC is None
                                                        else "data:image/png;base64,{}".format(
                                                            MAP_STATIC.decode()
                                                        ),
                                                        width="400px",
                                                        style={"marginLeft": "30px"},
                                                        alt="Map of the location",
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
                            html.Div(
                                className="grid-x",
                                id="energy-system-graph-div",
                                children=[
                                    html.H4(["Energy system"]),
                                    html.Img(
                                        src="data:image/png;base64,{}".format(
                                            ENERGY_SYSTEM_GRAPH.decode()
                                        ),
                                        alt="Energy System Graph",
                                        style={"maxWidth": "100%"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        children=create_demands_section(
                            output_JSON_file=results_json, sectors=sectors
                        )
                    ),
                    insert_subsection(
                        title="Resources",
                        content=ready_timeseries_plots(
                            results_json, data_type=RESOURCES
                        ),
                    ),
                    insert_subsection(
                        title="Energy System Components",
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
                                children=ready_flows_plots(dict_values=results_json,)
                            ),
                            html.Div(
                                className="add-cap-plot",
                                children=ready_capacities_plots(
                                    dict_values=results_json
                                ),
                            ),
                            insert_body_text(
                                "This results in the following KPI of the dispatch per energy sector:"
                            ),
                            make_dash_data_table(df_kpi_sectors),
                        ],
                    ),
                    insert_subsection(
                        title="Sankey diagram",
                        content=ready_sankey_diagram(
                            dict_values=results_json, only_print=False,
                        ),
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
                                children=ready_costs_pie_plots(
                                    dict_values=results_json, only_print=False,
                                ),
                            ),
                        ],
                    ),
                    insert_subsection(
                        title="Energy System: Key Performance Indicators (KPIs)",
                        content=[
                            insert_body_text(
                                f"In the following the key performance indicators of the of {projectName}, "
                                f"scenario {scenarioName} are displayed. For more information on their definition, "
                                f"please reference `mvs-eland.readthedocs.io`."
                            ),
                            make_dash_data_table(df_kpi_scalars),
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
                                content=insert_log_messages(
                                    log_dict=results_json[SIMULATION_RESULTS][LOGS][
                                        WARNINGS
                                    ]
                                ),
                            ),
                            insert_subsection(
                                title="Error Messages",
                                content=insert_log_messages(
                                    log_dict=results_json[SIMULATION_RESULTS][LOGS][
                                        ERRORS
                                    ]
                                ),
                            ),
                        ]
                    ),
                ],
            ),
        ],
    )
    return app


if __name__ == "__main__":
    from multi_vector_simulator.utils.constants import REPO_PATH, OUTPUT_FOLDER
    from multi_vector_simulator.B0_data_input_json import load_json

    dict_values = load_json(
        os.path.join(REPO_PATH, OUTPUT_FOLDER, JSON_WITH_RESULTS + JSON_FILE_EXTENSION)
    )

    test_app = create_app(dict_values)
    # open_in_browser(test_app)
    test_app.run_server(debug=True)
