"""
Parameter constants
===================

Defines the strings of different json parameters
Using variables rather than strings is helpful for typo prevention. A typo in a variable will
raise an error where the variable was misspelled, whereas a typo in a string (dictionnary key)
do not nessarily raise an error immediately, making the typo harder to fix.
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
OEMOF_BUSSES = "bus"

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
DATA = "data"

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
OUTPUT_LP_FILE = "output_lp_file"
STORE_OEMOF_RESULTS = "store_oemof_results"
PROJECT_NAME = "project_name"
SCENARIO_NAME = "scenario_name"
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
EMISSION_FACTOR = "emission_factor"

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
THERM_LOSSES_REL = "fixed_thermal_losses_relative"
THERM_LOSSES_ABS = "fixed_thermal_losses_absolute"

# Constraints
CONSTRAINTS = "constraints"
MINIMAL_RENEWABLE_FACTOR = "minimal_renewable_factor"
MAXIMUM_EMISSIONS = "maximum_emissions"

#######################################
# Parameters added in pre-processing #
#######################################
# Units
UNIT_YEAR = "year"
UNIT_HOUR = "hour"
UNIT_MINUTE = "min"
UNIT_EMISSIONS = "kgCO2eq/a"
UNIT_SPECIFIC_EMISSIONS = "kgCO2eq/kWheleq"

# Preprocessing: Time
END_DATE = "end_date"
TIME_INDEX = "time_index"
TIMESERIES = "timeseries"
TIMESERIES_NORMALIZED = "timeseries_normalized"
TIMESERIES_PEAK = "timeseries_peak"
TIMESERIES_TOTAL = "timeseries_total"
TIMESERIES_AVERAGE = "timeseries_average"

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

SPECIFIC_REPLACEMENT_COSTS_INSTALLED = (
    "Specific_replacement_costs_of_installed_capacity"
)
SPECIFIC_REPLACEMENT_COSTS_OPTIMIZED = (
    "Specific_replacement_costs_of_optimized_capacity"
)

# Other Parameters
LES_ENERGY_VECTOR_S = "energy_vectors_of_the_local_energy_system"
OUTFLOW_DIRECTION = "outflow_direction"
INFLOW_DIRECTION = "inflow_direction"
ENERGY_VECTOR = "energyVector"
EXCESS = "_excess"

# DSO
DSO_CONSUMPTION = "_consumption"
DSO_FEEDIN = "_feedin"
DSO_PEAK_DEMAND_SUFFIX = "_pdp"  # short for peak demand pricing
DSO_PEAK_DEMAND_PERIOD = "_period"
CONNECTED_CONSUMPTION_SOURCE = "connected_consumption_sources"
CONNECTED_PEAK_DEMAND_PRICING_TRANSFORMERS = (
    "connected_peak_demand_pricing_transformers"
)
CONNECTED_FEEDIN_SINK = "connected_feedin_sink"

# Autogenerated assets
AUTO_SOURCE = "_source"
AUTO_SINK = "_sink"
DISPATCHABILITY = "dispatchable"
AVAILABILITY_DISPATCH = "availability_timeseries"

# Sinks
EXCESS_SINK_POSTFIX = "_excess_sink"

ASSET_DICT = "Asset_list"
#######################################
# Parameters added in post-processing #
#######################################

SIMULATION_RESULTS = "simulation_results"

# oemof simulation parameters:
OBJECTIVE_VALUE = "objective_value"
SIMULTATION_TIME = "simulation_time"

# Logs
LOGS = "logs"
ERRORS = "errors"
WARNINGS = "warnings"

# Names for KPI output
KPI = "kpi"
KPI_SCALARS_DICT = "scalars"
KPI_UNCOUPLED_DICT = "KPI individual sectors"
KPI_COST_MATRIX = "cost_matrix"
KPI_SCALAR_MATRIX = "scalar_matrix"

# Flows
FLOW = "flow"
OPTIMIZED_FLOWS = "optimizedFlows"
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
COST_OPERATIONAL_TOTAL = "costs_om_total"
COST_OM = "costs_cost_om"  # Fix asset operation/management costs per year, not depending on use
COST_DISPATCH = (
    "costs_dispatch"  # Variable asset operation/management costs, depending on dispatch
)
COST_INVESTMENT = "costs_investment_over_lifetime"
COST_UPFRONT = "costs_upfront_in_year_zero"
COST_REPLACEMENT = "Replacement_costs_during_project_lifetime"

# Levelized cost of electricity
LCOE_ASSET = "levelized_cost_of_energy_of_asset"

# Other KPI
TOTAL_RENEWABLE_GENERATION_IN_LES = "Total internal renewable generation"
TOTAL_NON_RENEWABLE_GENERATION_IN_LES = "Total internal non-renewable generation"
TOTAL_GENERATION_IN_LES = "Total internal generation"
TOTAL_RENEWABLE_ENERGY_USE = "Total renewable energy use"
TOTAL_NON_RENEWABLE_ENERGY_USE = "Total non-renewable energy use"
RENEWABLE_FACTOR = "Renewable factor"
RENEWABLE_SHARE_OF_LOCAL_GENERATION = "Renewable share of local generation"
TOTAL_EMISSIONS = "Total emissions"
SPECIFIC_EMISSIONS_ELEQ = "Specific emissions per electricity equivalent"

TOTAL_DEMAND = "Total_demand"
TOTAL_EXCESS = "Total_excess"
TOTAL_FEEDIN = "Total_feedin"
SUFFIX_ELECTRICITY_EQUIVALENT = "_electricity_equivalent"
ATTRIBUTED_COSTS = "Attributed costs"
LCOeleq = "Levelized costs of electricity equivalent"

DEGREE_OF_SECTOR_COUPLING = "Degree of sector coupling"
DEGREE_OF_AUTONOMY = "Degree of autonomy"
ONSITE_ENERGY_FRACTION = "Onsite energy fraction"
ONSITE_ENERGY_MATCHING = "Onsite energy matching"


# KPI_FLOW_MATRIX
KPI_SCALARS = (
    ANNUITY_OM,
    ANNUITY_TOTAL,
    COST_INVESTMENT,
    COST_OPERATIONAL_TOTAL,
    COST_OM,
    COST_DISPATCH,
    COST_TOTAL,
    COST_UPFRONT,
)

DEMANDS = "demands"
RESOURCES = "resources"
