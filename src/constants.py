import os

# path to the root of this repository (assumes this file is in src folder)
REPO_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# name of the input folder
INPUT_FOLDER = "inputs"
# name of the json extension
JSON_EXT = "json"
# name of the csv extension
CSV_EXT = "csv"
# name of the folder containing mvs model described by .csv files
CSV_ELEMENTS = "csv_elements"
# name of the json file which should be present in the input folder if option -i json was chosen
JSON_FNAME = "mvs_config.json"
# name of the json file which is should be created in the input folder if option -i csv was chosen
CSV_FNAME = "mvs_csv_config.json"
# list of csv filename which must be present within the CSV_ELEMENTS folder
REQUIRED_CSV_FILES = (
    "fixcost",
    "simulation_settings",
    "project_data",
    "economic_data",
    "energyConversion",
    "energyProduction",
    "energyStorage",
    "energyProviders",
    "energyConsumption",
)

# allowed symbols for separating values in .csv files
CSV_SEPARATORS = (",", ";", "&")
# name of the folder containing timeseries described by .csv files
TIME_SERIES = "time_series"
# name of the folder containing the output of the simulation
OUTPUT_FOLDER = "MVS_outputs"
# name of the folder containing the copied content of the input folder within the output folder
INPUTS_COPY = INPUT_FOLDER
# name of the automatically generated pdf report
PDF_REPORT = "simulation_report.pdf"


# default paths to input, output and sequences folders
DEFAULT_INPUT_PATH = os.path.join(REPO_PATH, INPUT_FOLDER)
DEFAULT_OUTPUT_PATH = os.path.join(REPO_PATH, OUTPUT_FOLDER)

USER_INPUT_ARGUMENTS = (
    "path_input_file",
    "path_output_folder",
    "input_type" "path_input_sequences",
    "overwrite",
    "display_output",
)

DEFAULT_MAIN_KWARGS = dict(
    overwrite=False,
    pdf_report=False,
    input_type=JSON_EXT,
    path_input_folder=DEFAULT_INPUT_PATH,
    path_output_folder=DEFAULT_OUTPUT_PATH,
    display_output="info",
    lp_file_output=False,
)
# list of csv filename which must be present within the CSV_ELEMENTS folder with the parameters
# associated to each of these filenames
REQUIRED_CSV_PARAMETERS = {
    "energyConsumption": [
        "dsm",
        "file_name",
        "label",
        "type_asset",
        "type_oemof",
        "energyVector",
        "inflow_direction",
        "unit",
    ],
    "energyConversion": [
        "age_installed",
        "capex_fix",
        "capex_var",
        "efficiency",
        "inflow_direction",
        "installedCap",
        "label",
        "lifetime",
        "opex_fix",
        "opex_var",
        "optimizeCap",
        "outflow_direction",
        "type_oemof",
        "energyVector",
        "unit",
    ],
    "energyStorage": [
        "inflow_direction",
        "label",
        "optimizeCap",
        "outflow_direction",
        "type_oemof",
        "storage_filename",
        "energyVector",
    ],
    "energyProduction": [
        "age_installed",
        "capex_fix",
        "capex_var",
        "file_name",
        "installedCap",
        "label",
        "lifetime",
        "opex_fix",
        "opex_var",
        "optimizeCap",
        "outflow_direction",
        "type_oemof",
        "unit",
        "energyVector",
    ],
    "energyProviders": [
        "energy_price",
        "feedin_tariff",
        "inflow_direction",
        "label",
        "optimizeCap",
        "outflow_direction",
        "peak_demand_pricing",
        "peak_demand_pricing_period",
        "type_oemof",
        "energyVector",
    ],
    "fixcost": [
        "age_installed",
        "capex_fix",
        "capex_var",
        "label",
        "lifetime",
        "opex_fix",
        "opex_var",
    ],
    "simulation_settings": [
        "evaluated_period",
        "label",
        "oemof_file_name",
        "output_lp_file",
        "restore_from_oemof_file",
        "display_nx_graph",
        "store_nx_graph",
        "start_date",
        "store_oemof_results",
        "timestep",
    ],
    "project_data": [
        "country",
        "label",
        "latitude",
        "longitude",
        "project_id",
        "project_name",
        "scenario_id",
        "scenario_name",
    ],
    "economic_data": [
        "currency",
        "discount_factor",
        "label",
        "project_duration",
        "tax",
    ],
}

# list of csv filename which must be present within the CSV_ELEMENTS folder
REQUIRED_CSV_FILES = tuple(REQUIRED_CSV_PARAMETERS.keys())

KPI_SCALARS = (
    "annuity_om",
    "annuity_total",
    "costs_investment",
    "costs_om",
    "costs_opex_fix",
    "costs_opex_var",
    "costs_total",
    "costs_upfront",
)
