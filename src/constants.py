import os

from src.constants_json_strings import (
    UNIT,
    ENERGY_CONVERSION,
    ENERGY_CONSUMPTION,
    ENERGY_PRODUCTION,
    ENERGY_STORAGE,
    ENERGY_PROVIDERS,
    OEMOF_ASSET_TYPE,
    PROJECT_DURATION,
    DISCOUNTFACTOR,
    TAX,
    LABEL,
    VALUE,
    SIMULATION_SETTINGS,
    ECONOMIC_DATA,
    PROJECT_DATA,
    FIX_COST,
    CURR,
    SECTORS,
    INFLOW_DIRECTION,
    OUTFLOW_DIRECTION,
    ENERGY_VECTOR,
    OPTIMIZE_CAP,
    OPEX_VAR,
    OPEX_FIX,
    CAPEX_FIX,
    CAPEX_VAR,
)


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
    FIX_COST,
    SIMULATION_SETTINGS,
    PROJECT_DATA,
    ECONOMIC_DATA,
    ENERGY_CONVERSION,
    ENERGY_PRODUCTION,
    ENERGY_STORAGE,
    ENERGY_PROVIDERS,
    ENERGY_CONSUMPTION,
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
    ENERGY_CONSUMPTION: [
        "dsm",
        "file_name",
        LABEL,
        "type_asset",
        OEMOF_ASSET_TYPE,
        ENERGY_VECTOR,
        INFLOW_DIRECTION,
        UNIT,
    ],
    ENERGY_CONVERSION: [
        "age_installed",
        CAPEX_FIX,
        CAPEX_VAR,
        "efficiency",
        INFLOW_DIRECTION,
        "installedCap",
        LABEL,
        "lifetime",
        OPEX_FIX,
        OPEX_VAR,
        OPTIMIZE_CAP,
        OUTFLOW_DIRECTION,
        OEMOF_ASSET_TYPE,
        ENERGY_VECTOR,
        UNIT,
    ],
    ENERGY_STORAGE: [
        INFLOW_DIRECTION,
        LABEL,
        OPTIMIZE_CAP,
        OUTFLOW_DIRECTION,
        OEMOF_ASSET_TYPE,
        "storage_filename",
        ENERGY_VECTOR,
    ],
    ENERGY_PRODUCTION: [
        "age_installed",
        CAPEX_FIX,
        CAPEX_VAR,
        "file_name",
        "installedCap",
        LABEL,
        "lifetime",
        OPEX_FIX,
        OPEX_VAR,
        OPTIMIZE_CAP,
        OUTFLOW_DIRECTION,
        OEMOF_ASSET_TYPE,
        UNIT,
        ENERGY_VECTOR,
    ],
    ENERGY_PROVIDERS: [
        "energy_price",
        "feedin_tariff",
        INFLOW_DIRECTION,
        LABEL,
        OPTIMIZE_CAP,
        OUTFLOW_DIRECTION,
        "peak_demand_pricing",
        "peak_demand_pricing_period",
        OEMOF_ASSET_TYPE,
        ENERGY_VECTOR,
    ],
    FIX_COST: [
        "age_installed",
        CAPEX_FIX,
        CAPEX_VAR,
        LABEL,
        "lifetime",
        OPEX_FIX,
        OPEX_VAR,
    ],
    SIMULATION_SETTINGS: [
        "evaluated_period",
        LABEL,
        "output_lp_file",
        "restore_from_oemof_file",
        "display_nx_graph",
        "store_nx_graph",
        "start_date",
        "store_oemof_results",
        "timestep",
    ],
    PROJECT_DATA: [
        "country",
        LABEL,
        "latitude",
        "longitude",
        "project_id",
        "project_name",
        "scenario_id",
        "scenario_name",
    ],
    ECONOMIC_DATA: [CURR, DISCOUNTFACTOR, LABEL, PROJECT_DURATION, TAX,],
}

# list of csv filename which must be present within the CSV_ELEMENTS folder
REQUIRED_CSV_FILES = tuple(REQUIRED_CSV_PARAMETERS.keys())

# possible type of variable stored into the json file
TYPE_DATETIMEINDEX = "pandas_DatetimeIndex:"
TYPE_SERIES = "pandas_Series:"
TYPE_DATAFRAME = "pandas_Dataframe:"
TYPE_TIMESTAMP = "pandas_Timestamp:"

DEFAULT_WEIGHTS_ENERGY_CARRIERS = {
    "Electricity": {UNIT: "kWh_eleq/kWh_el", VALUE: 1},
    "H2": {UNIT: "kWh_eleq/kgH2", VALUE: 32.87},
}

# Names for KPI output

KPI_DICT = "kpi"

KPI_SCALARS_DICT = "scalars"

KPI_UNCOUPLED_DICT = "KPI individual sectors"

KPI_COST_MATRIX = "cost_matrix"

# KPI_FLOW_MATRIX

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

# key of the dict containing generated plots filesnames in results_json file
PATHS_TO_PLOTS = "paths_to_plots"
# keys' names of dict containing generated plots filenames
PLOTS_DEMANDS = "demands"
PLOTS_RESOURCES = "resources"
PLOTS_NX = "nx"
PLOTS_PERFORMANCE = "performance"
PLOTS_COSTS = "costs"
PLOTS_BUSSES = "flows_on_busses"

# structure of the dict containing generated plots filenames in results_json file
DICT_PLOTS = {
    PATHS_TO_PLOTS: {
        PLOTS_BUSSES: [],
        PLOTS_DEMANDS: [],
        PLOTS_RESOURCES: [],
        PLOTS_NX: [],
        PLOTS_PERFORMANCE: [],
        PLOTS_COSTS: [],
    }
}
