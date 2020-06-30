# This script generates a report of the simulation automatically, with all the important data.

import base64
import os

# Imports for generating pdf automatically
import threading
import time
import webbrowser
from selenium import webdriver

# Importing necessary packages
import dash
import dash_html_components as html
import dash_table
import folium
import git
import pandas as pd
import pdfkit
import reverse_geocoder as rg

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
)

OUTPUT_FOLDER = os.path.join(REPO_PATH, OUTPUT_FOLDER)
CSV_FOLDER = os.path.join(REPO_PATH, OUTPUT_FOLDER, INPUTS_COPY, CSV_ELEMENTS)


def print_pdf(app=None, path_pdf_report=os.path.join(OUTPUT_FOLDER, "out.pdf")):
    """Run the dash app in a thread an print a pdf before exiting

    Parameters
    ----------
    app: handle to a dash app
    path_pdf_report: str
        path where the pdf report should ba saved

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
    # TODO check if chromium is easier
    driver = webdriver.Firefox(executable_path=os.path.join(REPORT_PATH, "geckodriver"))
    driver.get("http://127.0.0.1:8050")

    # TODO figure a way to wait enough time for everything to load
    # waits to load the page, could alternatively wait for a certain html tag to be present
    time.sleep(5)

    # Extracts the html source code of the app and save it in a file
    html_src = driver.page_source
    html_path = os.path.join(REPORT_PATH, "report.html")
    with open(html_path, "w") as f:
        f.write(html_src)
    driver.close()

    # Convert the html file into a pdf
    pdfkit.from_url("file:///" + html_path, path_pdf_report)
    print(f"Saved the report under {path_pdf_report}")

    if app is not None:
        td.join(20)


def open_in_browser(app, timeout=600):
    """Run the dash app in a thread an open a browser window"""
    td = threading.Thread(target=app.run_server)
    td.daemon = True
    td.start()
    webbrowser.open("http://127.0.0.1:8050", new=1)
    td.join(timeout)


def make_dash_data_table(df, title=None):
    """Function that creates a Dash DataTable from a Pandas dataframe"""
    content = [
        html.Div(
            className="tableplay",
            children=dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict("records"),
                style_cell={
                    "padding": "5px",
                    "height": "auto",
                    "width": "auto",
                    "fontFamily": "Courier New",
                    "textAlign": "center",
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)",
                    }
                ],
                style_header={"fontWeight": "bold", "color": "#8c3604"},
            ),
        )
    ]

    if title is not None:
        content = [html.H4(title, className="report_table_title")] + content

    return html.Div(className="report_table", children=content)


def insert_subsection(title, content, **kwargs):
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
    """
    This function is for creating the headings such as information, input data, etc.
    parameters: string
    returns: a html element with the heading_text encsased in a container
    """
    return html.H2(
        className="cell", children=heading_text, style={"page-break-after": "avoid"}
    )


# Functions that creates paragraphs
def insert_body_text(body_of_text):
    """
    This function is for rendering blocks of text
    parameters: paragraph (string)
    returns: a html element with a paragraph
    """
    return html.P(className="cell large-11 blockoftext", children=body_of_text)


def insert_image_array(img_list, width=500):
    return html.Div(
        className="image-array",
        children=[
            html.Img(
                className="graphs_ts",
                src="data:image/png;base64,{}".format(
                    base64.b64encode(open(ts, "rb").read()).decode()
                ),
                width="{}px".format(width),
            )
            for ts in img_list
        ],
    )


def create_app(results_json):
    path_output_folder = results_json[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER]

    # Initialize the app
    app = dash.Dash(__name__)

    colors = {
        "bg-head": "#9ae6db",
        "text-head": "#000000",
        "text-body": "#000000",
        "inp-box": "#03034f",
        "font-inpbox": "#FFFFFF",
    }
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
    mapy.save(os.path.join(REPO_PATH, "src", "assets", "proj_map"))

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
        + "(ID:"
        + str(results_json[PROJECT_DATA][PROJECT_ID])
        + ")"
    )
    scenarioName = (
        results_json[PROJECT_DATA][SCENARIO_NAME]
        + "(ID:"
        + str(results_json[PROJECT_DATA][SCENARIO_ID])
        + ")"
    )

    releaseDesign = "0.0x"

    # Getting the branch ID
    repo = git.Repo(search_parent_directories=True)
    branchID = repo.head.object.hexsha

    simDate = time.strftime("%Y-%m-%d")

    ELAND_LOGO = base64.b64encode(
        open(
            os.path.join(REPO_PATH, "src", "assets", "logo-eland-original.jpg"), "rb"
        ).read()
    )

    # Determining the sectors which were simulated

    sectors = list(results_json[PROJECT_DATA][SECTORS].keys())
    sec_list = """"""
    for sec in sectors:
        sec_list += "\n" + f"\u2022 {sec.upper()}"

    # Creating a dataframe for the demands
    demands = results_json[ENERGY_CONSUMPTION]

    del demands["DSO_feedin"]
    del demands["Electricity excess"]

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
        ["index", TOTAL_FLOW, "peak_flow", "average_flow"], axis=1
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

    # Header section with logo and the title of the report, and CSS styling. Work in progress...

    app.layout = html.Div(
        [
            html.Div(
                className="header_title_logo",
                children=[
                    html.Img(
                        id="mvslogo",
                        src="data:image/png;base64,{}".format(ELAND_LOGO.decode()),
                        width="370px",
                    ),
                    html.H1("MULTI VECTOR SIMULATION - REPORT SHEET"),
                ],
            ),
            html.Div(
                className="imp_info",
                children=[
                    html.P(f"MVS Release: {releaseDesign}"),
                    html.P(f"Branch-id: {branchID}"),
                    html.P(f"Simulation date: {simDate}"),
                ],
            ),
            html.Div(
                className="imp_info2",
                children=[
                    html.Div(
                        [
                            html.Span(
                                "Project name   : ", style={"fontWeight": "bold"}
                            ),
                            f"{projectName}",
                        ]
                    ),
                    html.Br([]),
                    html.Div(
                        [
                            html.Span(
                                "Scenario name  : ", style={"fontWeight": "bold"}
                            ),
                            f"{scenarioName}",
                        ]
                    ),
                ],
            ),
            html.Div(
                className="blockoftext",
                children=[
                    html.Div(
                        [
                            "The energy system with the ",
                            html.Span(f"{projectName}", style={"fontStyle": "italic"}),
                            " for the scenario ",
                            html.Span(f"{scenarioName}", style={"fontStyle": "italic"}),
                            " was simulated with the Multi-Vector simulation tool MVS 0.0x developed from the E-LAND toolbox "
                            "developed in the scope of the Horizon 2020 European research project. The tool was developed by "
                            "Reiner Lemoine Institute and utilizes the OEMOF framework.",
                        ]
                    )
                ],
            ),
            html.Br([]),
            html.Div(
                className="inputs_simresults_box", children=[html.H2("Input Data")],
            ),
            html.Br([]),
            html.Div(
                className="heading1",
                children=[
                    html.H2("Project Data", className="heading1",),
                    html.Hr(className="horizontal_line"),
                ],
            ),
            html.Div(
                className="blockoftext",
                children=[
                    html.P(
                        "The most important simulation data will be presented below. "
                        "Detailed settings, costs, and technological parameters can "
                        "be found in the appendix."
                    )
                ],
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H4(["Project Location"], className="projdataheading"),
                            html.Iframe(
                                srcDoc=open(
                                    os.path.join(
                                        REPO_PATH, "src", "assets", "proj_map"
                                    ),
                                    "r",
                                ).read(),
                                width="70%",
                                height="700",
                            ),
                        ],
                        style={"margin": "30px", "width": "48%"},
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Br([]),
                                    html.H4(
                                        ["Project Data"], className="projdataheading"
                                    ),
                                    html.Div(
                                        className="tableplay",
                                        children=[make_dash_data_table(df_projectData)],
                                    ),
                                ],
                                className="projdata",
                            )
                        ]
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Br([]),
                                    html.H4(
                                        ["Simulation Settings"],
                                        className="projdataheading",
                                    ),
                                    html.Div(
                                        className="tableplay",
                                        children=[make_dash_data_table(df_simsettings)],
                                    ),
                                ],
                                className="projdata",
                            )
                        ]
                    ),
                ]
            ),
            html.Br(),
            html.Div(
                className="heading1",
                children=[
                    html.H2("Energy Demand"),
                    html.Hr(className="horizontal_line"),
                ],
            ),
            html.Div(
                className="blockoftext",
                children=[
                    html.P(
                        "The simulation was performed for the energy system "
                        "covering the following sectors:"
                    ),
                    html.P(f"{sec_list}"),
                ],
            ),
            html.Div(
                className="demandmatter",
                children=[
                    html.Br(),
                    html.H4("Electricity Demand", className="graph__pre-title",),
                    html.P("Electricity demands that have to be supplied are: "),
                ],
            ),
            html.Div(children=[make_dash_data_table(df_dem)]),
            html.Div(
                className="timeseriesplots",
                children=[
                    html.Div(
                        [
                            html.Img(
                                src="data:image/png;base64,{}".format(
                                    base64.b64encode(open(ts, "rb").read()).decode()
                                ),
                                width="1500px",
                            )
                            for ts in results_json[PATHS_TO_PLOTS][PLOTS_DEMANDS]
                        ]
                    ),
                    html.H4("Resources", className="graph__pre-title"),
                    html.Div(
                        [
                            html.Img(
                                src="data:image/png;base64,{}".format(
                                    base64.b64encode(open(ts, "rb").read()).decode()
                                ),
                                width="1500px",
                            )
                            for ts in results_json[PATHS_TO_PLOTS][PLOTS_RESOURCES]
                        ]
                    ),
                ],
                style={"margin": "30px"},
            ),
            html.Div(),
            html.Br(),
            html.Div(
                className="heading1",
                children=[
                    html.H2("Energy System Components"),
                    html.Hr(className="horizontal_line"),
                ],
            ),
            html.Div(
                className="blockoftext",
                children=[
                    html.P(
                        "The energy system is comprised of the following components:"
                    )
                ],
            ),
            html.Div(children=[make_dash_data_table(df_comp)]),
            html.Br([]),
            html.Div(
                className="inputs_simresults_box",
                children=[html.H2("SIMULATION RESULTS")],
            ),
            html.Br([]),
            html.Div(
                className="heading1",
                children=[
                    html.H2("Dispatch & Energy Flows"),
                    html.Hr(className="horizontal_line"),
                ],
            ),
            html.Div(
                className="blockoftext",
                children=[
                    html.P(
                        "The capacity optimization of components that were to be used resulted in:"
                    )
                ],
            ),
            html.Div(children=[make_dash_data_table(df_scalar_matrix)]),
            html.Div(
                className="blockoftext",
                children=[
                    html.P(
                        "With this, the demands are met with the following dispatch schedules:"
                    ),
                    html.P(
                        "a. Flows in the system for a duration of 14 days",
                        style={"marginLeft": "20px"},
                    ),
                ]
                + [
                    html.Div(
                        [
                            html.Img(
                                src="data:image/png;base64,{}".format(
                                    base64.b64encode(open(ts, "rb").read()).decode()
                                ),
                                width="1500px",
                            )
                            for ts in results_json[PATHS_TO_PLOTS][PLOTS_BUSSES]
                            + results_json[PATHS_TO_PLOTS][PLOTS_PERFORMANCE]
                        ]
                    ),
                ],
            ),
            html.Br(style={"marginBottom": "5px"}),
            html.P(
                "This results in the following KPI of the dispatch:",
                style={
                    "marginLeft": "50px",
                    "textAlign": "justify",
                    "fontSize": "40px",
                },
            ),
            html.Div(
                className="heading1",
                children=[
                    html.H2("Economic Evaluation"),
                    html.Hr(className="horizontal_line"),
                ],
            ),
            html.P(
                className="blockoftext",
                children=[
                    "The following installation and operation costs result from capacity and dispatch optimization:"
                ],
            ),
            html.Div(children=[make_dash_data_table(df_cost_matrix)]),
            html.Div(
                className="blockoftext",
                children=[
                    html.Img(
                        src="data:image/png;base64,{}".format(
                            base64.b64encode(open(ts, "rb").read()).decode()
                        ),
                        width="1500px",
                    )
                    for ts in results_json[PATHS_TO_PLOTS][PLOTS_COSTS]
                ],
            ),
        ]
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
