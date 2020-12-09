==============================
E-Land requirements of the MVS
==============================

Functional Requirements
-----------------------

FUN-MVS-01 - Solving an energy system optimization model
########################################################

:Description: The MVS shall solve an energy system planning optimization problem and provide the optimal sizing of individual assets.

:Rationale: Basic operation of MVS.

:Priority:  HIGH

:Progress: In progress

:Progress message:

The MVS can solve energy system planning optimization problems and identify the optimal additional capacities of chosen assets.

:ToDo:

There are still parts of the MVS that can be improved and some features are not integrated yet, but this is covered by the requirements below.
There are two benchmark tests that should be added to complete this:

* Investment optimization benchmark tests - check if expected capacities are installed, eg. for PV.
* Economic evaluation benchmark test - check if NPC and LCOE are calculated correctly

FUN-MVS-02 - Automatic setting up of an energy system optimization model
########################################################################

:Description: The MVS should accept modelling parameters regarding the LES in a specific format.

:Rationale: Currently MVS supports the Oemof model. The rationale is to support external entities or users with no experience in Oemof, by automatically generating the respective Oemof model for the agreed format

:Priority:  HIGH

:Progress: In progress

:Progress message:

The MVS accepts simulation data provided as csv files and automatically sets up an energy system.

:ToDo:

Reading data from json files can still be improved, especially as the interface of the EPA/MVS will change the json file again.

FUN-MVS-03 - Manual setting up an energy system optimization model
##################################################################

:Description: The MVS shall support adding specific components/constraints from a set of options to an energy system optimization model.

:Rationale: Basic operation of MVS

:Priority:  LOW

:Progress: Done

:Progress message:

It is possible to add as many components as needed to the energy model that is to be simulated with the MVS.
They can be divided into following types:

* Energy providers
* energy production
* energy consumption
* energy conversion
* energy storage

Details on how to model different assets are included in the model assumptions, specifically the `component models <https://mvs-eland.readthedocs.io/en/latest/Model_Assumptions.html#component-models>`__.

:ToDo: None

FUN-MVS-04 - Optimisation Results
#################################

:Description: The MVS shall provide the results of the optimisation process upon completion of calculation in a specific format, which include at least information related to asset costs (CAPEX and OPEX), sizes, as well as aggregated energy flows and overall system performance (autonomy, renewable share, losses).

:Rationale:  Basic operation of MVS.

:Priority:  HIGH

:Progress: In progress

:Progress message:

The results of the MVS simulation is post-processed. Following information is already compiled:

* Capex and opex per asset
* NPC and annuity of the energy system
* Aggregated energy flows as well as peak flows of each asset
* Renewable share of the assets
* LCOE of the energy system

:ToDo:

Open to implement is still:

* Degree of sector-coupling
* Degree of autonomy (energy balance)
* Percentage of self-supply (hourly)
* Percentage of self-consumption (hourly)
* Benchmark test for LCOE (one sector, multiple sectors with different conversion factors)
* Excess energy evaluation needs to be benchmark-tested

FUN-MVS-05 - Production Assets
##############################

:Description: The MVS should consider a diverse type of production assets in the energy model i.e. PV, BESS, CHP, Thermal Storage

:Rationale:  Enable support of multi-vector production and storage assets.

:Priority:  HIGH

:Progress: In-progress

:Progress message:

The MVS already considers

* PV plants, wind plants
* BESS

:ToDo:

Thermal storages are for now defined analogously to electrical storages.
It could be considered whether we should actually use the new oemof_thermal object.
It is not clear how this would fit into the EPA data bank.

A CHP with fix ratio between the heat and electricity output can already be simulated.
For a chp with a variable ration between those two outputs, we need to add the specific chp asset to the possible inputs.

FUN-MVS-06 - Assets of Energy Conversion
########################################

:Description: The MVS should consider assets which convert energy from one vector to another i.e. CHP, geothermal conversion (heat pump)

:Rationale:  Integration of the multi-vector approach in the MVS.

:Priority:  LOW

:Progress: In-progress

:Progress message:

The MVS already covers generic conversion assets. This includes generators, transformers, heat pumps and similar.

:ToDo:

A CHP with a variable share of heat and electricity output is currently not implemented. It could be added as a new oemof asset type.

When using two conversion objects to emulate a bidirectional conversion assets, their capacity should be interdependent. This is currently not the case.


FUN-MVS-07 - Optimisation goal
##############################

:Description: The optimisation process should take into account: Increasing the degree of autonomy of the LES, system costs minimization, and CO2 emissions reduction. Optional extension of the MVS is to allow for multi-objective optimisation.

:Rationale:  Different optimisation goal shall be supported for covering the different perspectives of the possible end-users.

:Priority:  HIGH

:Progress: In progress

:Progress message:

In general, the MVS aims to minimize the energy supply cost of the local energy system. Additionally, following constraint can be activated:

* Minimal renewable share constraint (see `here <https://mvs-eland.readthedocs.io/en/latest/Model_Assumptions.html#minimal-renewable-share-constraint>`__)

:ToDo:

Some constraints still have to be added:

* Minimal degree of autonomy
* Maximum C02 emission constraint

FUN-MVS-08 - Electricity cost model
###################################

:Description: The MVS model shall be provided with data defining electricity grid supply regarding: a) kWh prices (both import and export from/to the grid), b) kWh/h prices (time series of prices), c) Constraints of the interconnection with the main grid (e.g. substation capacity)

:Rationale:  Information necessary for building the MVS Multi-vector Model.

:Priority:  HIGH

:Progress: Done

:Progress message:

The different constraints regarding the electricity DSO can be considered:

a) The energy price as well as the feed-in tariff of a DSO can be provided as a time series
b) Peak demand pricing can be considered (see `here <https://mvs-eland.readthedocs.io/en/latest/Model_Assumptions.html#peak-demand-pricing>`__)
c) The transformer station limitation can, but does not have to be added.

:ToDo: None


FUN-MVS-09 - Load profiles
##########################

:Description: The MVS model shall be provided with annual electric/thermal demand profiles (hourly values) for each load in the LES.

:Rationale:  Information necessary for building the MVS Multi-vector Model.

:Priority:  HIGH

:Progress: Done

:Progress message: The MVS can be provided with a variable number of energy consumption profiles, that can be connected to variable busses.

:ToDo: None

FUN-MVS-10 - DH cost model
##########################

:Description: For calculations involving district heating, the MVS model shall support data on thermal distribution network supply, concerning: a) kWh prices (both import and export from/to the grid), b) kWh/h prices (time series of prices), c) optional: thermal power cap (e.g. maximum allowable feed-in per day)

:Rationale:  Information necessary for building the MVS Multi-vector Model.

:Priority:  HIGH

:Progress: Done

:Progress message: Same as for **FUN-MVS-08 - Electricity cost model**

:ToDo: None


FUN-MVS-11 - PV data
####################

:Description: For calculations involving PV assets, the MVS model shall be provided with data on PV assets: a) At minimum: Precise location (latitude and longitude), b) Optionally: performance indicators for new PV systems (efficiency - constant or time series, module technology, performance ratio), historical/tracked data (energy generated by existing PV systems, weather data), Inverter efficiency

:Rationale:  Information necessary for building the MVS Multi-vector Model.

:Priority:  HIGH

:Progress: In progress (minimal requirement met)

:Progress message:

To simulate a PV, the MVS model requires following data from the end-user:

* (Historical) specific generation profile (in kWh/kWp)

Optionally, an inverter that has specific efficiency can be connected to the PV.

:ToDo:

To ease the data input for the end-user, more processing could be included here. For example, the `pvfeedinlib` could be used with following data:

* Longitude and latitude
* Module or efficiency
* Performance ratio

This could also be implemented in the EPA.

FUN-MVS-12 - Battery data
#########################

:Description: For calculations involving battery assets, the MVS model shall be provided with data on Battery Energy Storage Systems (BESS): a) Battery type (e.g. lead-acid, lithium ion) b. Technical parameters: C-rate, max and min state of charge (SOC), max. depth of discharge (DOD), roundtrip efficiency (constant or time series), c. Inverter efficiency (optional), d. historical/tracked data from existing BESS

:Rationale:  Information necessary for building the MVS Multi-vector Model.

:Priority:  HIGH

:Progress: In progress (minimal requirement met)

:Progress message:

For the MVS, the type of the BESS does not matter. Important are the technical parameters:

* C-rate
* Max and min state of charge (SOC)
* Max. depth of discharge (DOD)
* Charge- and discharge efficiency (constant or time series)
* Self-discharge rate

Optionally, it is possible to add an inverter.

Historical data is not subject to the MVS for batteries.

:ToDo:

Defining default values for the BESS (possibly requirement a)) could also take place in the EPA.

FUN-MVS-13 - CHP data
#####################

:Description: For calculations involving CHP assets, the MVS model shall be provided with efficiency factors (electric/thermal)

:Rationale:  Information necessary for building the MVS Multi-Vector Model.

:Priority:  LOW

:Progress: In progress (minimal requirement met)

:Progress message:

A simple CHP model is already included in the MVS. It considers a fix ratio between thermal and electric output.

:ToDo:

For a variable ratio between heat and electricity output, a new, specific oemof asset would need to be added.

FUN-MVS-14 - Thermal storage data
#################################

:Description: For calculations involving Thermal Storage assets, the MVS model shall be provided with: a) Charging and discharging efficiencies, b. Max/Min SOC, initial SOC

:Rationale:  Information necessary for building the MVS Multi-Vector Model.

:Priority:  LOW

:Progress: In progress (minimal requirement met)

:Progress message:

It is possible to simulate thermal storage assets with the MVS that are simulated analogously to the BESS, which fulfills the requirement. They are defined by:

* Charging and discharging efficiencies
* Max/Min SOC


:ToDo:

The definition of an initial SOC of the thermal storages was dropped, as this does not seem relevant considering the project duration of 20 a.

The simplification of a thermal storage asset as basically a BESS can be especially difficult for the end user, in case that the input data needed can not be estimated.
One should consider using the oemof.thermal thermal storage object.

FUN-MVS-15 - Autonomous operation data
######################################

:Description: The MVS model shall be provided with information on the autonomous operation of the LES i.e. minimum/maximum time of autonomy for specific time intervals.

:Rationale:  Information necessary for building the MVS Multi-vector Model

:Priority:  HIGH

:Progress: Not started

:Progress message: This requirement was not addressed yet.

:ToDo:

This requirement can be translated into a constraint that needs to be added to the MVS.
It should be addresses after the other constraints as well as the KPI regarding autonomy are integrated.

FUN-MVS-16 - Economic data
##########################

:Description: The MVS model shall be provided with information on economic assumptions per asset: CAPEX/kW and OPEX/kWh (constant or time series), lifetime (years), Weighted Average Cost of Capital (WACC).

:Rationale: Information necessary for building the Multi-vector Model.

:Priority:  HIGH

:Progress: Done

:Progress message:

The MVS receives economic data from the end-user. This includes:

* Specific investment costs of assets (CAPEX/kW)
* Dispatch costs of assets
* Annual operation and management costs (OPEX/kWh, constant or time series))
* Currency
* Tax
* Weighted Average Cost of Capital (WACC).

:ToDo: None

FUN-MVS-17 - Constraints
########################

:Description: The MVS model shall be provided with constraints of the optimisation problem: a) Operating reserve provided by the battery (i.e. redundancy, availability), b. Sizing constraints, c. Cost constraints

:Rationale:  Information necessary for building the Multi-vector Model.

:Priority:  HIGH

:Progress: In progress

:Progress message:

To address the sizing constraint, the attribute `maximumCap` was introduced. This will limit the optimized capacity, even if this results in higher energy supply costs.

:ToDo:

It was decided at the beginning of the project that the operating reserve constraint will be developed in cooperation with the end-users.

A cost constraint is for now disregarded. As always the cheapest supply solution is identified, limiting the overall NPC would only result in infeasible solutions and a termination of the MVS.
Cost constraints considering specific technologies can be covered by adapting the `maximumCap`.

Non-Functional Requirements
---------------------------

NF-MVS-01 - MVS pre-processing tools for LES optimization model input
#####################################################################

:Description: The MVS should support Python-Pandas DataFrames as parameterization input for the LES model

:Scope: Interface, Usability

:Metric: Y/N

:Verification and Measurement: The requirement is validated by observing the system under test when an operator attempts to input/modify the model parameters.

:Target: User can adjust input parameters without any further support

:Progress: Done

:Progress message:

Internally, the MVS uses pd.DataFrames to set up the energy system model.
However, for data exchange with the end-user the input files, ie. the csv or json file is essential.
As the end user will use the MVS though the EPA, the data format that the MVS uses becomes irrelevant.
It was decided to use a json file as an exchange medium between the EPA and the MVS.

:ToDo: None

NF-MVS-02 - MVS post-processing tools for LES optimization model output/results
###############################################################################

:Description: The MVS should provide results aggregation, reports, and plots

:Scope: User Interface, Usability

:Metric: Y/N

:Verification and Measurement: The requirement is validated by observing the system under test when an operator attempts to access the output results.

:Target: User can extract the results in a way that can be directly used for the users purpose

:Progress: Done

:Progress message:

The post-processing of results ensures that important KPI can be provided for the energy system optimization.
There are three output formats of the MVS:

* For the end-user of the standalone application, an automatic report is generated that makes scenario evaluation easy
* For a developer of the standalone application, the results are also provided as excel files and pngs.
* For the EPA, the results are provided in a json format to be displayed interactively in their environment

:ToDo: Improving the outputs is a continuing task.

NF-MVS-03 - Communication interface between MVS and ESB
#######################################################

:Description: Communication functionality must be included so that ESB can send requests to MVS and vice versa. This assures that all requests can be coordinated through one platform (e.g. ESB).

:Scope: User Interface, Usability

:Metric: Y/N

:Verification and Measurement: Send a set of different requests from ESB to MVS and count received requests. Do vice versa.

:Target: Send/receive requests that can be processed without information loss

:Progress: In process

:Progress message:

After discussion, there is no direct interface of the ESB and the MVS.
The MVS is a standalone application that must be usable without the ESB.
To ease end-user use, the EPA (Energy Planning Application) is developed.
It sends inputs in json format to the MVS, and receives a json file with the results back.

:ToDo: The EPA development is a continuous process.

NF-MVS-04 - Unit commitment time step restriction
#################################################

:Description: Energy flows between selected components (Unit commitment) are simulated in hourly timesteps.

:Scope: Performance

:Metric: Timestamps

:Verification and Measurement: Subtract 2-time steps.

:Target: Timestep width of 1 hour

:Progress: Done

:Progress message: The MVS can be run for a variable number of days. The time series have to be provided on an hourly basis.

:ToDo: A wish from the end-users war a finer resolution of eg. 15-minute time steps. This possibility still has to be explored.

NF-MVS-05 - Interface for technical parameters and model
########################################################

:Description: Technical parameters are reflected in component modelling

:Scope: Performance

:Metric: Technical variable in energy system model object

:Verification and Measurement: Technical variable in ESM object being not NAN.

:Target: N/A

:Progress: Done

:Progress message: The MVS uses the input parameters to compile the component models. This is also tested using pytests and benchmark tests.

:ToDo: None


NF-MVS-06 - Interface for economic parameters and model
#######################################################

:Description: Cost parameters are reflected in component modelling

:Scope: Interface

:Metric: Cost variable in energy system model object

:Verification and Measurement: Cost variable in ESM object being not NAN.

:Target: N/A

:Progress: In progress

:Progress message: The MVS uses the input parameters to compile the component models. This is also tested using pytests and benchmark tests.

:ToDo: A benchmark tests regarding the investment model and the cost post-processing should be added.