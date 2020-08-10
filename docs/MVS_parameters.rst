======================================
Parameters and Definitions in CSV/JSON 
======================================

Each parameter is provided with the definition, unit, type and example values as well to make it easy for users to provide custom values for their systems.

project_data.csv
----------------
country
#######

:Definition: Name of the country where the project is being deployed
:Type: str
:Unit: None
:Example: Norway
:Restrictions: None
:Default: None

|

latitude
########

:Definition: Latitude coordinate of the project’s geographical location
:Type: str
:Unit: None
:Example: 45.641603
:Restrictions: Numerical values
:Default: None

|

longitude
#########

:Definition: Longitude coordinate of the project’s geographical location
:Type: str
:Unit: None
:Example: 5.875387
:Restrictions: Numerical values
:Default: None

|

Project_id
##########

:Definition: Users can assign a project ID as per their preference
:Type: str
:Unit: None
:Example: Borg Havn
:Restrictions: None
:Default: 1

|

Project_name
############

:Definition: Users can assign a project name as per their preference
:Type: str
:Unit: None
:Example:
:Restrictions: None
:Default: None

|

scenario_id
###########

:Definition: Users can assign a scenario id as per their preference
:Type: str
:Unit: None
:Example: 1
:Restrictions: None
:Default: None

|

scenario_name
#############

:Definition: Users can assign a scenario name as per their preference
:Type: str
:Unit: None
:Example: Warehouse 14
:Restrictions: None
:Default: None

|

economic_data.csv
-----------------

currency
########

:Definition: The currency of the country where the project is implemented.
:Type: str
:Unit: None
:Example: EUR (if the country is Germany)
:Restrictions: None
:Default: None

|

discount_factor
###############

:Definition: Discount factor is the factor which accounts for the depreciation in the value of money in the future, compared to the current value of the same money. The common method is to calculate the weighted average cost of capital (WACC) and use it as the discount rate.
:Type: str
:Unit: None
:Example: EUR (if the country is Germany)
:Restrictions: None
:Default: None

|

Project_duration
################

:Definition: The name of years the project is intended to be operational. The project duration also sets the installation time of the assets used in the simulation. After the project ends these assets are 'sold' and the refund is charged against the initial investment costs.
:Type: str
:Unit: None
:Example:
:Restrictions: None
:Default: None

|

tax
###

:Definition: Tax factor
:Type: str
:Unit: None
:Example:
:Restrictions: None
:Default: None

|

simulation_settings.csv
-----------------------

display_output
##############

:Definition: [Developer setting]
:Type: str
:Unit: None
:Example:
:Restrictions: None
:Default: debug

|

evaluated_period
################

:Definition: The number of days for which the simulation is to be run.
:Type: str
:Unit: None
:Example:
:Restrictions: None
:Default:

|

output_lp_file
##############

:Definition: Entering True would result in the generation of a file with the linear equation system describing the simulation, ie., with the objective function and all the constraints. This lp file enables the user to peer ‘under the hood’ to understand how the program optimizes for the solution.
:Type: str
:Unit: None
:Example:
:Restrictions: Acceptable values are either True or False
:Default:

|

start_date
##########

:Definition: The data and time on which the simulation starts at the first step.
:Type: str
:Unit: None
:Example: 2018-01-01 00:00:00
:Restrictions: Acceptable format is YYYY-MM-DD HH:MM:SS
:Default:

|

store_oemof_results
###################

:Definition: [Developer setting] Assigning True would enable the results to be stored in a OEMOF file.
:Type: str
:Unit: None
:Example: 2018-01-01 00:00:00
:Restrictions: Acceptable values are either True or False
:Default:

|

timestep
########

:Definition: Length of the timesteps.
:Type: str
:Unit: None
:Example: None
:Restrictions: None
:Default: None

|

Common Parameters in the CSV/JSON files and in energyConversion.csv:
--------------------------------------------------------------------

First row of the csv (C1, E1, D1...)
####################################

Input the names of the conversion components in a computer readable format, ie. with underscores instead of spaces, no special characters (eg. pv_plant_01)

age_installed
#############

:Definition: The number of years the asset has already been in operation.
:Type: str
:Unit: None
:Example:
:Restrictions:
:Default:

|

development_costs
#################

:Definition: A fixed cost to implement the asset, eg. planning costs which do not depend on the (optimized) asset capacity
:Type: Numerical
:Unit:  €
:Example: 200
:Restrictions: None
:Default: None

|

specific_costs
##############

:Definition: Actual CAPEX of the asset, i.e., specific investment costs
:Type: str
:Unit: €/kW
:Example: None
:Restrictions: None
:Default: None

|

efficiency
##########

:Definition: Ratio of energy output/energy input
:Type: str
:Unit: None
:Example: None
:Restrictions: None
:Default: None

|

Inflow_direction
################

:Definition: The bus/component from which the energyVector is arriving into the asset.
:Type: str
:Unit: None
:Example: None
:Restrictions: None
:Default: None

|

installedCap
############

:Definition: The already existing installed capacity in-place, which will also be replaced after its lifetime
:Type: None
:Unit: kW
:Example: None
:Restrictions: None
:Default: None

|


maximumCap
##########

:Definition: The maximum installable capacity.
:Type: None
:Unit: kW
:Example: None
:Restrictions: None
:Default: None

|

label
#####

:Definition: Name of the asset
:Type: str
:Unit: None
:Example: None
:Restrictions: None
:Default: None

|

lifetime
########

:Definition: Number of operational years of the asset until it has to be replaced.
:Type: None
:Unit: None
:Example: None
:Restrictions: None
:Default: None

|

cost_om
#######

:Definition: Specific annual OPEX of the asset.
:Type: None
:Unit: €/kW/year
:Example: None
:Restrictions: None
:Default: None

|


**dispatch_price**: Variable cost associated with a flow through/from the asset (€/kWh). In "storage_xx.csv" only the columns "input power" and "output power"
require a value, in column "storage capacity" dispatch_price should be set to NaN.

**optimizeCap**: Permissible values are either True or False; ‘True’ if the user wants to perform capacity optimization for various components

**outflow_direction**: The bus/component to which the energyVector is leaving, from the asset

**energyVector**: Energy commodity. E.g.: Electricity, heat, bio-gas, etc. 

**type_oemof**: Input the type of OEMOF component. For example, a PV plant would be a source, a solar inverter would be a transformer, etc.  The “type_oemof” will later on be determined through the EPA.

**unit**: Unit associated with the capacity of the component. For example, storage could have units like kW or kWh, transformer station could have kVA, and so on. 


energyProduction.csv
--------------------

**First row of the csv (C1, E1, D1...)**: Input the names of the production components in a computer readable format, ie. with underscores instead of spaces, no special characters (eg. pv_plant_01)

**file_name**: Name of the csv file containing the input PV generation time-series. E.g.: filename.csv 


energyProviders.csv
-------------------

**energy_price**: Price of electricity sourced from the utility grid (€/kWh)

**feedin_tariff**: Price received for feeding electricity into the grid (€/kWh)

**peak_demand_pricing**: Price to be paid additionally for energy-consumption based on the peak demand of a period (€/kW)

**Peak_demand_pricing_period**: Number of reference periods in one year for the peak demand pricing. Only one of the following are acceptable values: 1 (yearly), 2, 3 ,4, 6, 12 (monthly).


energyConsumption.csv
---------------------

**First row of the csv (C1, E1, D1...)**: Input the names of the consumption components in a computer readable format, ie. with underscores instead of spaces, no special characters (eg. pv_plant_01)

**dsm**: Demand Side Management. Acceptable values are either True or False. Currently, not implemented. 

**type_asset**: [Depreciated in the current version of MVS E-Lands]


energyStorage.csv
-----------------

**First row of the csv (C1, E1, D1...)**: Input the names of the storage components in a computer readable format, ie. with underscores instead of spaces, no special characters (eg. pv_plant_01)

**storage_filename**: Corresponding to the values in C1, D1, E1… cells, enter the correct CSV filename which hosts the parameters of the corresponding storage component.

storage_xx.csv
--------------
**c_rate**: C-rate is the rate at which the storage can charge or discharge relative to the nominal capacity of the storage.
A c-rate of 1 implies that the battery can discharge or charge completely in a single timestep.
Only the columns "input power" and "output power" require a value, in column "storage capacity" c_rate should be set to NaN.

**soc_initial**: The level of charge (as a factor of the actual capacity) in the storage in the zeroth timestep. Acceptable values are either None or the factor. Only the column "storage capacity" require a value, in column "input power" and "output power" soc_initial should be set to NaN.

**soc_max**: The maximum permissible level of charge in the battery (generally, it is when the battery is filled to its nominal capacity), represented by the value 1.0. Users can  also specify a certain value as a factor of the actual capacity. Only the column "storage capacity" requires a value, in column "input power" and "output power" soc_max should be set to NaN.

**soc_min**: The minimum permissible level of charge in the battery as a factor of the nominal capacity of the battery. Only the column "storage capacity" requires a value, in column "input power" and "output power" soc_min should be set to NaN.

**efficiency**: The battery efficiency is the ratio of the energy taken out from the battery, to the energy put in the battery. It means that it is not possible to retrieve as much energy as provided to the battery due to the discharge losses. The efficiency of the "input power" and "ouput power" columns should be set equal to the charge and dischage efficiencies respectively, while the "storage capacity" efficiency should be equal to the storage self-discharge/decay, which is usually in the range of 0 to 0.05.
