=======================================
Parameters and Definitions in CSVs/JSON
=======================================

Below is the list of all the parameters of MVS, sorted in alphabetical order. Each parameter is provided with the definition, unit, type and example values as well to make it easy for users to provide custom values for their systems.

.. _age_ins-label:

age_installed
#############

:Definition: The number of years the asset has already been in operation.
:Type: Numeric
:Unit: None
:Example: 12
:Restrictions: None
:Default: None

|

.. _cost_om-label:

cost_om
#######

:Definition: Specific annual OPEX of the asset.
:Type: Numeric
:Unit: €/kW/year
:Example: None
:Restrictions: None
:Default: None

|

.. _country-label:

country
#######

:Definition: Name of the country where the project is being deployed
:Type: str
:Unit: None
:Example: Norway
:Restrictions: None
:Default: None

|

.. _currency-label:

currency
########

:Definition: The currency of the country where the project is implemented.
:Type: str
:Unit: None
:Example: EUR (if the country is Germany)
:Restrictions: None
:Default: None

|

.. _crate-label:

c-rate
######

:Definition: C-rate is the rate at which the storage can charge or discharge relative to the nominal capacity of the storage. A c-rate of 1 implies that the battery can discharge or charge completely in a single timestep.
:Type:
:Unit:
:Example:
:Restrictions: Only the columns "input power" and "output power" require a value, in column "storage capacity" c_rate should be set to NaN.
:Default: None

|

.. _developmentcosts-label:

development_costs
#################

:Definition: A fixed cost to implement the asset, eg. planning costs which do not depend on the (optimized) asset capacity
:Type: Numerical
:Unit:  €
:Example: 200
:Restrictions: None
:Default: None

|

.. _discountfactor-label:

discount_factor
###############

:Definition: Discount factor is the factor which accounts for the depreciation in the value of money in the future, compared to the current value of the same money. The common method is to calculate the weighted average cost of capital (WACC) and use it as the discount rate.
:Type: str
:Unit: None
:Example: EUR (if the country is Germany)
:Restrictions: None
:Default: None

|

.. _dispatchprice-label:

dispatch_price
##############

:Definition: Variable cost associated with a flow through/from the asset (€/kWh).
:Type: numeric value
:Unit: currency/kWh
:Example:
:Restrictions: In "storage_xx.csv" only the columns "input power" and "output power" require a value, in column "storage capacity" dispatch_price should be set to NaN.
:Default: None

|

.. _displayoutput-label:

display_output
##############

:Definition: [Developer setting]
:Type: str
:Unit: None
:Example:
:Restrictions: None
:Default: debug

|

.. _dsm-label:

dsm
###

:Definition: Stands for Demand Side Management. Currently, not implemented.
:Type:
:Unit:
:Example:
:Restrictions: Acceptable values are either True or False
:Default:

|

.. _efficiency-label:

efficiency
##########

:Definition: Ratio of energy output/energy input
:Type: str
:Unit: None
:Example: None
:Restrictions: None
:Default: None

|

.. _energyprice-label:

energy_price
############

:Definition: Price of electricity sourced from the utility grid (€/kWh)
:Type:
:Unit:
:Example:
:Restrictions:
:Default:

|

.. _evaluatedperiod-label:

evaluated_period
################

:Definition: The number of days for which the simulation is to be run.
:Type: str
:Unit: None
:Example:
:Restrictions: None
:Default:

|

.. _energyvector-label:

energyVector
############

:Definition: Energy commodity. E.g.: Electricity, heat, bio-gas, etc.
:Type:
:Unit:
:Example:
:Restrictions:
:Default:

|

.. _feedintariff-label:

feedin_tariff
#############

:Definition: Price received for feeding electricity into the grid (€/kWh)
:Type:
:Unit:
:Example:
:Restrictions:
:Default:

|

.. _filename-label:

file_name
#########

:Definition: Name of the csv file containing the input PV generation time-series. E.g.: filename.csv
:Type:
:Unit:
:Example:
:Restrictions:
:Default:

|

.. _inflowdirection-label:

inflow_direction
################

:Definition: The bus/component from which the energyVector is arriving into the asset.
:Type: str
:Unit: None
:Example: None
:Restrictions: None
:Default: None

|

.. _installedcap-label:

installedCap
############

:Definition: The already existing installed capacity in-place, which will also be replaced after its lifetime
:Type: None
:Unit: kW
:Example: None
:Restrictions: None
:Default: None

|

.. _labl-label:

label
#####

:Definition: Name of the asset
:Type: str
:Unit: None
:Example: None
:Restrictions: Input the names in a computer readable format, i.e., with underscores instead of spaces, no special characters (eg. pv_plant_01)
:Default: None

|

.. _latitude-label:

latitude
########

:Definition: Latitude coordinate of the project’s geographical location
:Type: str
:Unit: None
:Example: 45.641603
:Restrictions: Numerical values
:Default: None

|

.. _lifetime-label:

lifetime
########

:Definition: Number of operational years of the asset until it has to be replaced.
:Type: None
:Unit: None
:Example: None
:Restrictions: None
:Default: None

|

.. _longitude-label:

longitude
#########

:Definition: Longitude coordinate of the project’s geographical location
:Type: str
:Unit: None
:Example: 5.875387
:Restrictions: Numerical values
:Default: None

|

.. _maxcap-label:

maximumCap
##########

:Definition: The maximum installable capacity.
:Type: None
:Unit: kW
:Example: None
:Restrictions: None
:Default: None

|

.. _minrenshare-label:

minimal_renewable_share
#######################

:Definition: The minimum share of energy supplied by renewable generation in the optimized energy system.
:Type: Numeric
:Unit: factor
:Example: 0.7
:Restrictions: Between 0 and 1
:Default: None

|

.. _optimizecap-label:

optimizeCap
###########

:Definition: ‘True’ if the user wants to perform capacity optimization for various components
:Type:
:Unit:
:Example:
:Restrictions: Permissible values are either True or False
:Default:

|

.. _outputlpfile-label:

output_lp_file
##############

:Definition: Entering True would result in the generation of a file with the linear equation system describing the simulation, ie., with the objective function and all the constraints. This lp file enables the user to peer ‘under the hood’ to understand how the program optimizes for the solution.
:Type: str
:Unit: None
:Example:
:Restrictions: Acceptable values are either True or False
:Default:

|

.. _outflowdirec-label:

outflow_direction
#################

:Definition: The bus/component to which the energyVector is leaving, from the asset.
:Type:
:Unit:
:Example:
:Restrictions:
:Default:

|

.. _peakdemand-label:

peak_demand_pricing
###################

:Definition: Price to be paid additionally for energy-consumption based on the peak demand of a period (€/kW).
:Type:
:Unit:
:Example:
:Restrictions:
:Default:

|

.. _peakdemandperiod-label:

Peak_demand_pricing_period
##########################

:Definition: Number of reference periods in one year for the peak demand pricing. Only one of the following are acceptable values: 1 (yearly), 2, 3 ,4, 6, 12 (monthly).
:Type:
:Unit:
:Example:
:Restrictions:
:Default:

|

.. _projectduration-label:

Project_duration
################

:Definition: The name of years the project is intended to be operational. The project duration also sets the installation time of the assets used in the simulation. After the project ends these assets are 'sold' and the refund is charged against the initial investment costs.
:Type: str
:Unit: None
:Example:
:Restrictions: None
:Default: None

|

.. _projectid-label:

Project_id
##########

:Definition: Users can assign a project ID as per their preference
:Type: Alphanumeric
:Unit: None
:Example: Borg Havn
:Restrictions: None
:Default: 1

|

.. _projectname-label:

Project_name
############

:Definition: Users can assign a project name as per their preference
:Type: Alphanumeric
:Unit: None
:Example:
:Restrictions: None
:Default: None

|

.. _scenarioid-label:

scenario_id
###########

:Definition: Users can assign a scenario id as per their preference
:Type: Alphanumeric
:Unit: None
:Example: 1
:Restrictions: None
:Default: None

|

.. _scenarioname-label:

scenario_name
#############

:Definition: Users can assign a scenario name as per their preference
:Type: Alphanumeric
:Unit: None
:Example: Warehouse 14
:Restrictions: None
:Default: None

|

.. _socin-label:

soc_initial
###########

:Definition: The level of charge (as a factor of the actual capacity) in the storage in the zeroth time-step.
:Type:
:Unit:
:Example:
:Restrictions: Acceptable values are either None or the factor. Only the column "storage capacity" requires a value, in column "input power" and "output power" soc_initial should be set to NaN.
:Default: None

|

.. _socmax-label:

soc_max
#######

:Definition: The maximum permissible level of charge in the battery (generally, it is when the battery is filled to its nominal capacity), represented by the value 1.0. Users can  also specify a certain value as a factor of the actual capacity.
:Type:
:Unit:
:Example:
:Restrictions: Only the column "storage capacity" requires a value, in column "input power" and "output power" soc_max should be set to NaN.
:Default: None

|

.. _socmin-label:

soc_min
#######

:Definition: The minimum permissible level of charge in the battery as a factor of the nominal capacity of the battery.
:Type:
:Unit:
:Example:
:Restrictions: Only the column "storage capacity" requires a value, in column "input power" and "output power" soc_min should be set to NaN.
:Default: None

|

.. _specificcosts-label:

specific_costs
##############

:Definition: Actual CAPEX of the asset, i.e., specific investment costs
:Type: str
:Unit: €/kW
:Example: None
:Restrictions: None
:Default: None

|

.. _startdate-label:

start_date
##########

:Definition: The data and time on which the simulation starts at the first step.
:Type: str
:Unit: None
:Example: 2018-01-01 00:00:00
:Restrictions: Acceptable format is YYYY-MM-DD HH:MM:SS
:Default: None

|

.. _storagefilename-label:

storage_filename
################

:Definition: Corresponding to the values in C1, D1, E1… cells, enter the correct CSV filename which hosts the parameters of the corresponding storage component.
:Type:
:Unit:
:Example:
:Restrictions:
:Default:

|

.. _storeoemoefresults-label:

store_oemof_results
###################

:Definition: [Developer setting] Assigning True would enable the results to be stored in a OEMOF file.
:Type: str
:Unit: None
:Example: 2018-01-01 00:00:00
:Restrictions: Acceptable values are either True or False
:Default:

|

.. _tax-label:

tax
###

:Definition: Tax factor
:Type: str
:Unit: None
:Example:
:Restrictions: None
:Default: None

|

.. _timestep-label:

timestep
########

:Definition: Length of the time-steps.
:Type: str
:Unit: None
:Example: None
:Restrictions: None
:Default: None

|

.. _typeasset-label:

type_asset
##########

:Definition:
:Type: str
:Unit: None
:Example: None
:Restrictions: None
:Default: None

|

.. _typeoemof-label:

type_oemof
##########

:Definition: Input the type of OEMOF component. For example, a PV plant would be a source, a solar inverter would be a transformer, etc.  The “type_oemof” will later on be determined through the EPA.
:Type:
:Unit:
:Example:
:Restrictions:
:Default:

|

.. _unit-label:

unit
####

:Definition: Unit associated with the capacity of the component.
:Type:
:Unit: None
:Example: Storage could have units like kW or kWh, transformer station could have kVA, and so on.
:Restrictions: Appropriate scientific unit
:Default: None

---------------
constraints.csv
---------------

The file `constraints.csv` includes the following parameter(s):

* :ref:`minrenshare-label`

-----------------
economic_data.csv
-----------------

The file `economic_data.csv` includes the following parameters:

* :ref:`labl-label`
* :ref:`currency-label`
* :ref:`projectduration-label`
* :ref:`discountfactor-label`
* :ref:`tax-label`

---------------------
energyConsumption.csv
---------------------

The file `energyConsumption.csv` includes the following parameters:

* :ref:`labl-label`
* :ref:`unit-label`
* :ref:`inflowdirection-label`
* :ref:`energyvector-label`
* :ref:`filename-label`
* :ref:`typeasset-label`
* :ref:`typeoemof-label`
* :ref:`dsm-label`

----------------
project_data.csv
----------------

The file `project_data.csv` includes the following parameters:

* :ref:`labl-label`
* :ref:`country-label`
* :ref:`latitude-label`
* :ref:`longitude-label`
* :ref:`projectid-label`
* :ref:`projectname-label`
* :ref:`scenarioid-label`
* :ref:`scenarioname-label`

-----------------------
simulation_settings.csv
-----------------------

The file `simulation_settings.csv` includes the following parameters:

* :ref:`labl-label`

start_date
evaluated_period
timestep
output_lp_file
store_oemof_results





Common Parameters in the CSV/JSON files and in energyConversion.csv:
--------------------------------------------------------------------

First row of the csv (C1, E1, D1...)
------------------------------------

Input the names of the conversion components in a computer readable format, ie. with underscores instead of spaces, no special characters (eg. pv_plant_01)

energyProduction.csv
--------------------

**First row of the csv (C1, E1, D1...)**: Input the names of the production components in a computer readable format, ie. with underscores instead of spaces, no special characters (eg. pv_plant_01)

energyProviders.csv
-------------------

energyStorage.csv
-----------------

**First row of the csv (C1, E1, D1...)**: Input the names of the storage components in a computer readable format, ie. with underscores instead of spaces, no special characters (eg. pv_plant_01)

storage_xx.csv
--------------

**efficiency**: The battery efficiency is the ratio of the energy taken out from the battery, to the energy put in the battery. It means that it is not possible to retrieve as much energy as provided to the battery due to the discharge losses. The efficiency of the "input power" and "ouput power" columns should be set equal to the charge and dischage efficiencies respectively, while the "storage capacity" efficiency should be equal to the storage self-discharge/decay, which is usually in the range of 0 to 0.05.
