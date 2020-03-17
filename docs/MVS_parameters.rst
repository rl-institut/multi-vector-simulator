======================================
Parameters and Definitions in CSV/JSON 
======================================

project_data.csv
----------------

**country**: Name of the country where the project is being deployed. E.g.: Germany

**latitude**: Latitude coordinate of the project’s geographical location

**longitude**: Longitude coordinate of the project’s geographical location

**Project_id**: Users can assign a project ID as per their preference. 

**Project_name**: Users can assign a project name as per their preference.

**scenario_id**: Users can assign a scenario id as per their preference.

**scenario_name**: Users can assign a scenario name as per their preference.


economic_data.csv
-----------------

**currency**: The currency of the country where the project is implemented. For example, in the case of Germany, the value is EUR. For Norway, it is NOK. 

**discount_factor**: Discount factor is the factor which accounts for the depreciation in the value of money in the future, compared to the current value of the same money. 

**Project_duration**: The name of years the project is intended to be operational. 

**tax**: Tax factor. 

simulation_settings.csv
-----------------------

**display_output**: [Developer setting] Default value is "debug"

**evaluated_period**: The number of days for which the simulation is to be run.

**oemof_file_name**: The name of the OEMOF file in which the simulation results are stored. 

**output_lp_file**: Acceptable values are either True or False. Entering True would result in the generation of a file with the linear equation system describing the simulation, ie., with the objective function and all the constraints. This lp file enables the user to peer ‘under the hood’ to understand how the program optimizes for the solution.

**restore_from_oemof_file**: [Developer setting] Allows the developer to check the OEMOF file where the results are stored and edit the simulation parameters in it. (not integrated yet!)

**start_date**: The data and time on which the simulation starts at the first step. Acceptable format is YYYY-MM-DD HH:MM:SS. E.g.: 2018-01-01 00:00:00

**store_oemof_results**: [Developer setting] Acceptable values are either True or False. Assigning True would enable the results to be stored in a OEMOF file. 

**timestep**: Length of the timesteps. Acceptable values in minutes. This is currently only tested for 60-minute intervals.

Common Parameters in the CSV/JSON files and in energyConversion.csv:
--------------------------------------------------------------------

**First row of the csv (C1, E1, D1...)**: Input the names of the conversion components in a computer readable format, ie. with underscores instead of spaces, no special characters (eg. pv_plant_01)

**age_installed**: The number of years the asset has already been in operation

**capex_fix**: A fixed cost to implement the asset, eg. planning costs which do not depend on the (optimized) asset capacity (€)

**capex_var**: Actual CAPEX of the asset (€/kW), ie. specific investment costs

**efficiency**: Ratio of energy output/energy input

**Inflow_direction**: The bus/component from which the energyVector is arriving into the asset

**installedCap**: The already existing installed capacity in-place, which will also be replaced after its lifetime (kW)

**label**: Name of the asset

**lifetime**: Number of operational years of the asset until it has to be replaced

**opex_fix**: Specific annual OPEX of the asset (€/kW/year)

**opex_var**: Variable cost associated with a flow through/from the asset (€/kWh)

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

**crate**: C-rate is the rate at which the storage can charge or discharge relative to the nominal capacity of the storage.
A c-rate of 1 implies that the battery can discharge or charge completely in a single timestep. 

**soc_initial**: The level of charge (as a factor of the actual capacity)  in the storage in the zeroth timestep. Acceptable values are either None or the factor. 

**soc_max**: The maximum permissible level of charge in the battery (generally, it is when the battery is filled to its nominal capacity), represented by the value 1.0. Users can  also specify a certain value as a factor of the actual capacity. 

**soc_min**: The minimum permissible level of charge in the battery as a factor of the nominal capacity of the battery. 
