"""
Defines the strings of different json parameters
Not defining parameters as strings can be helpful, ig. if
    if string in dict_values
Is used, where typos can be very bad for future handling.
"""

# Asset groups
ENERGY_CONVERSION = "energyConversion"
ENERGY_CONSUMPTION = "energyConsumption"
ENERGY_PRODUCTION = "energyProduction"
ENERGY_STORAGE = "energyStorage"
ENERGY_BUSSES = "energyBusses"

ENERGY_PROVIDERS = "energyProviders"
SIMULATION_SETTINGS = "simulation_settings"
DISPLAY_NX_GRAPH = "display_nx_graph"
STORE_NX_GRAPH = "store_nx_graph"
OUTPUT_LP_FILE = "output_lp_file"
STORE_OEMOF_RESULTS = "store_oemof_results"
PROJECT_NAME = "project_name"
SCENARIO_NAME = "scenario_name"

RESTORE_FROM_OEMOF_FILE = "restore_from_oemof_file"
COUNTRY = "country"
PROJECT_ID = "project_id"
SCENARIO_ID = "scenario_id"

# Names for KPI output
KPI = "kpi"
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

EVALUATED_PERIOD = "evaluated_period"
START_DATE = "start_date"
END_DATE = "end_date"
TIMESTEP = "timestep"
PERIODS = "periods"
LONGITUDE = "longitude"
LATITUDE = "latitude"
TIME_INDEX = "time_index"
TIMESERIES = "timeseries"
TIMESERIES_NORMALIZED = "timeseries_normalized"
TIMESERIES_PEAK = "timeseries_peak"

ENERGY_PRICE = "energy_price"
FEEDIN_TARIFF = "feedin_tariff"
ANNUITY_FACTOR = "annuity_factor"
SIMULATION_ANNUITY = "simulation_annuity"
LIFETIME_CAPEX_VAR = "lifetime_capex_var"
CRF = "crf"
ANNUITY_CAPEX_OPEX_VAR = "annuity_capex_opex_var"
LIFETIME_OPEX_FIX = "lifetime_opex_fix"
LIFETIME_OPEX_VAR = "lifetime_opex_var"
ANNUAL_TOTAL_FLOW = "annual_total_flow"
OPTIMIZED_ADD_CAP = "optimizedAddCap"

FIX_COST = "fixcost"
ECONOMIC_DATA = "economic_data"
PROJECT_DATA = "project_data"
# Parameters
SECTORS = "sectors"
OUTFLOW_DIRECTION = "outflow_direction"
INFLOW_DIRECTION = "inflow_direction"
OUTPUT_BUS_NAME = "output_bus_name"
INPUT_BUS_NAME = "input_bus_name"
ENERGY_VECTOR = "energyVector"
OEMOF_ASSET_TYPE = "type_oemof"
# Allowed types
OEMOF_TRANSFORMER = "transformer"
OEMOF_GEN_STORAGE = "storage"
OEMOF_SOURCE = "source"
OEMOF_SINK = "sink"
# OEMOF_BUSSES = "bus"

C_RATE = "c_rate"
INPUT_POWER = "input power"
OUTPUT_POWER = "output power"
STORAGE_CAPACITY = "storage capacity"
SOC_INITIAL = "soc_initial"
SOC_MAX = "soc_max"
SOC_MIN = "soc_min"
# Dict generated from above defined strings
ACCEPTED_ASSETS_FOR_ASSET_GROUPS = {
    ENERGY_CONVERSION: [OEMOF_TRANSFORMER],
    ENERGY_STORAGE: [OEMOF_GEN_STORAGE],
    ENERGY_PRODUCTION: [OEMOF_SOURCE],
    ENERGY_CONSUMPTION: [OEMOF_SINK],
}

# Central constant variables
UNIT = "unit"
VALUE = "value"

# Parameter strings in json and csv files
CURR = "currency"
DISCOUNTFACTOR = "discount_factor"
LABEL = "label"
PROJECT_DURATION = "project_duration"
TAX = "tax"
FILENAME = "file_name"
STORAGE_FILENAME = "storage_filename"

EFFICIENCY = "efficiency"
OPTIMIZE_CAP = "optimizeCap"
INSTALLED_CAP = "installedCap"
MAXIMUM_CAP = "maximumCap"
AGE_INSTALLED = "age_installed"
LIFETIME = "lifetime"
CAPEX_FIX = "capex_fix"
CAPEX_VAR = "capex_var"
OPEX_FIX = "opex_fix"
OPEX_VAR = "opex_var"
PEAK_DEMAND_PRICING = "peak_demand_pricing"
PEAK_DEMAND_PRICING_PERIOD = "peak_demand_pricing_period"
