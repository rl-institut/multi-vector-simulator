"""
Defines the strings of different json parameters
Not defining parameters as strings can be helpful, ig. if
    if string in dict_values
Is used, where typos can be very bad for future handling.
"""
#####################
# 1st level of json #
#####################

ECONOMIC_DATA = "economic_data"
PROJECT_DATA = "project_data"
FIX_COST = "fixcost"

# Asset groups
ENERGY_CONVERSION = "energyConversion"
ENERGY_CONSUMPTION = "energyConsumption"
ENERGY_PRODUCTION = "energyProduction"
ENERGY_STORAGE = "energyStorage"
ENERGY_BUSSES = "energyBusses"
ENERGY_PROVIDERS = "energyProviders"

##### For D1 ######################
# Definition of allowed oemof types
OEMOF_TRANSFORMER = "transformer"
OEMOF_GEN_STORAGE = "storage"
OEMOF_SOURCE = "source"
OEMOF_SINK = "sink"
# OEMOF_BUSSES = "bus"

# Dict generated from above defined strings
ACCEPTED_ASSETS_FOR_ASSET_GROUPS = {
    ENERGY_CONVERSION: [OEMOF_TRANSFORMER],
    ENERGY_STORAGE: [OEMOF_GEN_STORAGE],
    ENERGY_PRODUCTION: [OEMOF_SOURCE],
    ENERGY_CONSUMPTION: [OEMOF_SINK],
}

##############################################
# Constant variable definitions (csv + json) #
##############################################

# Central constant variables
UNIT = "unit"
VALUE = "value"

# Economic parameters
CURR = "currency"
DISCOUNTFACTOR = "discount_factor"
LABEL = "label"
PROJECT_DURATION = "project_duration"
TAX = "tax"
FILENAME = "file_name"
STORAGE_FILENAME = "storage_filename"

# Simulation settings: Place and time
EVALUATED_PERIOD = "evaluated_period"
START_DATE = "start_date"
TIMESTEP = "timestep"
PERIODS = "periods"
LONGITUDE = "longitude"
LATITUDE = "latitude"

# Project data and simulation settings (true/false)
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

# Asset definitions
DSM = "dsm"
TYPE_ASSET = "type_asset"
EFFICIENCY = "efficiency"
OPTIMIZE_CAP = "optimizeCap"
INSTALLED_CAP = "installedCap"
MAXIMUM_CAP = "maximumCap"
AGE_INSTALLED = "age_installed"
LIFETIME = "lifetime"
DEVELOPMENT_COSTS = "development_costs"
SPECIFIC_COSTS = "specific_costs"
SPECIFIC_COSTS_OM = "specific_costs_om"
DISPATCH_PRICE = "dispatch_price"
OEMOF_ASSET_TYPE = "type_oemof"

# Specific parameters
RENEWABLE_ASSET_BOOL = "renewableAsset"
RENEWABLE_SHARE_DSO = "renewable_share"

# Asset definitions: Providers
ENERGY_PRICE = "energy_price"
FEEDIN_TARIFF = "feedin_tariff"
PEAK_DEMAND_PRICING = "peak_demand_pricing"
PEAK_DEMAND_PRICING_PERIOD = "peak_demand_pricing_period"

# Asset definitions: Storage
C_RATE = "c_rate"
INPUT_POWER = "input power"
OUTPUT_POWER = "output power"
STORAGE_CAPACITY = "storage capacity"
SOC_INITIAL = "soc_initial"
SOC_MAX = "soc_max"
SOC_MIN = "soc_min"

#######################################
# Parameters added in pre-processing #
#######################################
# Preprocessing: Time
END_DATE = "end_date"
TIME_INDEX = "time_index"
TIMESERIES = "timeseries"
TIMESERIES_NORMALIZED = "timeseries_normalized"
TIMESERIES_PEAK = "timeseries_peak"

# Pre-processing cost parameters
ANNUITY_FACTOR = "annuity_factor"
CRF = "CRF"

# Processed cost parameters
LIFETIME_SPECIFIC_COST_OM = "lifetime_specific_cost_om"
LIFETIME_PRICE_DISPATCH = "lifetime_price_dispatch"
LIFETIME_SPECIFIC_COST = "lifetime_specific_cost"
ANNUITY_SPECIFIC_INVESTMENT_AND_OM = (
    "annuity_of_specific_investment_costs_and_specific_annual_om"
)
SIMULATION_ANNUITY = "simulation_annuity"

# Other Parameters
SECTORS = "sectors"
OUTFLOW_DIRECTION = "outflow_direction"
INFLOW_DIRECTION = "inflow_direction"
OUTPUT_BUS_NAME = "output_bus_name"
INPUT_BUS_NAME = "input_bus_name"
ENERGY_VECTOR = "energyVector"

#######################################
# Parameters added in post-processing #
#######################################

# Names for KPI output
KPI = "kpi"
KPI_SCALARS_DICT = "scalars"
KPI_UNCOUPLED_DICT = "KPI individual sectors"
KPI_COST_MATRIX = "cost_matrix"
KPI_SCALAR_MATRIX = "scalar_matrix"

# Flows
TOTAL_FLOW = "total_flow"
ANNUAL_TOTAL_FLOW = "annual_total_flow"
PEAK_FLOW = "peak_flow"
AVERAGE_FLOW = "average_flow"

# Capacity
OPTIMIZED_ADD_CAP = "optimizedAddCap"

# Costs - Annuities
ANNUITY_OM = "annuity_om"
ANNUITY_TOTAL = "annuity_total"

# Costs - Total per asset
COST_TOTAL = "costs_total"
COST_OM_TOTAL = "costs_om_total"
COST_OM_FIX = "costs_cost_om"  # Fix asset operation/management costs per year, not depending on use
COST_DISPATCH = (
    "costs_dispatch"  # Variable asset operation/management costs, depending on dispatch
)
COST_UPFRONT = "costs_upfront_in_year_zero"
COST_INVESTMENT = "costs_investment_over_lifetime"

# Levelized cost of electricity
LCOE_ASSET = "levelized_cost_of_energy_of_asset"

# KPI_FLOW_MATRIX
KPI_SCALARS = (
    ANNUITY_OM,
    ANNUITY_TOTAL,
    COST_INVESTMENT,
    COST_OM_TOTAL,
    COST_OM_FIX,
    COST_DISPATCH,
    COST_TOTAL,
    COST_UPFRONT,
)
