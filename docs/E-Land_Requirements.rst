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

:Progress: Done

:Progress message:

The MVS can solve energy system planning optimization problems and identify the optimal additional capacities of chosen assets. In-code validation checks, unit tests and benchmark tests were added to ensure that the simulation runs smoothly and correctly.

:Notes:

As with all simulation tools, there are always possibilities to improve the tool, specifically to address current limitations (comp. :ref:`table_limitations_label`).

FUN-MVS-02 - Automatic setting up of an energy system optimization model
########################################################################

:Description: The MVS should accept modelling parameters regarding the LES in a specific format.

:Rationale: Currently MVS supports the Oemof model. The rationale is to support external entities or users with no experience in Oemof, by automatically generating the respective Oemof model for the agreed format

:Priority:  HIGH

:Progress: Done

:Progress message:

The MVS accepts simulation data provided as csv files and automatically sets up an energy system. It also supports the integration into the Energy Planning Application (EPA) by providing a parser for the interfaces of the two tools.

FUN-MVS-03 - Manual setting up an energy system optimization model
##################################################################

:Description: The MVS shall support adding specific components/constraints from a set of options to an energy system optimization model.

:Rationale: Basic operation of MVS

:Priority:  LOW

:Progress: Done

:Progress message:

It is possible to add as many components as needed to the energy model that is to be simulated with the MVS.
They can be divided into following asset types:

* :ref:`Energy providers <energy_providers>`
* :ref:`Energy production <energy_production>`
* :ref:`Energy consumption <energy_consumption>`
* :ref:`Energy conversion <energy_conversion>`
* :ref:`Energy storage <energy_storage>`

Details on how to model different assets are included in the model assumptions.

:Notes:

Energy excess sinks are automatically added by the MVS to enable energy system optimization and do not have to be added by the energy system planners.

In the future, it may be possible to add energy shortage sources, which would allow energy systems with a defined annual supply shortage. While this mostly will not result in an energy system many operators would require, it would also have benefits for the debugging of energy systems, as infeasible energy systems would be easier to evaluate and specific debug messages could be displayed.

FUN-MVS-04 - Optimisation Results
#################################

:Description: The MVS shall provide the results of the optimisation process upon completion of calculation in a specific format, which include at least information related to asset costs (CAPEX and OPEX), sizes, as well as aggregated energy flows and overall system performance (autonomy, renewable share, losses).

:Rationale:  Basic operation of MVS.

:Priority:  HIGH

:Progress: Done

:Progress message:

The results of the MVS simulation are post-processed, and result in numberous key performance indicators (KPI). Following information is calculated for an economic evaluation of the energy system:

* Capital and operational expenditures (capex, opex) per asset, both as annuities as well as present costs. This includes also the first-time investment costs (FIC), the replacement costs minus residual values, and the costs for asset dispatch (equations compare :ref:`economic_precalculation-label`).
* :ref:`NPC <net_present_costs>` and annuity of the whole energy system
* :ref:`Levelized cost of energy (LCOE) <lcoe>` of the energy system, in electricity equivalent
* :ref:`Levelized cost of an energy carrier <lcoe>` in electricity equivalent (LCOEleq) for each energy carrier in the energy system
* :ref:`Levelized cost of asset dispatch <lcoe_asset>`, calculated from the annuity of an asset and their throughput

Additionaly, a number of technical parameters are calculated both the energy system and the individual energy vectors:

* Dispatch, :ref:`aggregated energy flows <aggregated_flow>` as well as :ref:`peak flows <peak_flow>` of each asset
* :ref:`Renewable share <kpi_renewable_factor>`
* :ref:`Renewable share of local generation <kpi_renewable_share_of_local_generation>`
* :ref:`Degree of autonomy <kpi_degree_of_autonomy>`
* :ref:`Degree of net zero energy <kpi_degree_of_net_zero_energy>`
* :ref:`Onsite Energy Matching (OEM) <kpi_onsite_energy_fraction>`
* :ref:`Onsite Energy Fraction (OEF) <kpi_onsite_energy_matching>`
* Annual excess energy
* :ref:`Annual GHGeq emissions <emissions>` and specific emissions per electricity equivalent

:Notes:

Currently in discussion is the implementation of a so-called :ref:`degree of sector-coupling <kpi_degree_of_sector_coupling>` (`see issue 702 <https://github.com/rl-institut/multi-vector-simulator/issues/702>`__). This is a novel key performance indicator and would be integrated in addition to above mentioned parameters.

FUN-MVS-05 - Production Assets
##############################

:Description: The MVS should consider a diverse type of production assets in the energy model i.e. PV, BESS, CHP, Thermal Storage

:Rationale:  Enable support of multi-vector production and storage assets.

:Priority:  HIGH

:Progress: In-progress

:Progress message:

The MVS is able to simulate a wide range of assets:

* :ref:`PV plants, wind plants <dispatchable_sources>`
* :ref:`Battery Electricity Storage Systems (BESS) <battery_storage>`, via generic storage object
* :ref:`Thermal storages <thermal_storage>`, via generic or thermal storage object
* :ref:`Power plants <power_plants>` as simple generators.
* And many more (see below)

:ToDo:

A CHP with fix ratio between the heat and electricity output can already be simulated, but has not been tested. For a CHP with a variable ration between those two outputs, we need to add the specific chp asset to the possible inputs.

FUN-MVS-06 - Assets of Energy Conversion
########################################

:Description: The MVS should consider assets which convert energy from one vector to another i.e. CHP, geothermal conversion (heat pump)

:Rationale:  Integration of the multi-vector approach in the MVS.

:Priority:  LOW

:Progress: Done

:Progress message:

The MVS already covers generic conversion assets. How the generic definition can be applied to the individual assets is explained :ref:`here <energy_conversion`. This includes

* :ref:`Electric transformers <_energyconversion_electric_transformers>`
* :ref:`Power plants (Condensing power plants and Combined heat and power) <power_plants>`
* :ref:`Heat pumps and Heating, Ventilation, and Air Conditioning (HVAC) assets <energyconversion_hvac>`
* :ref:`Electrolyzers <energyconversion_electrolyzers>`

:ToDo:

A CHP with a variable share of heat and electricity output is currently not implemented. It could be added as a new oemof asset type.

When using two conversion objects to emulate a bidirectional conversion assets (eg. charge controllers, bi-directional inverters), their capacity should be interdependent. This is currently not the case, as explained in the :ref:`limitations <limitations-real-life-constraint>`


FUN-MVS-07 - Optimisation goal
##############################

:Description: The optimisation process should take into account: Increasing the degree of autonomy of the LES, system costs minimization, and CO2 emissions reduction. Optional extension of the MVS is to allow for multi-objective optimisation.

:Rationale:  Different optimisation goal shall be supported for covering the different perspectives of the possible end-users.

:Priority:  HIGH

:Progress: Done

:Progress message:

In general, the MVS aims to minimize the energy supply cost of the local energy system. Additionally, a number of :ref:`constraints <constraints-label>` can be activated:

* :ref:`Minimal renewable share constraint <constraint_minimal_renewable_factor>`
* :ref:`Minimal degree of autonomy <constraint_minimal_degree_of_autonomy>`
* :ref:`Maximum GHG emission constraint <constraint_maximum_emissions>`
* :ref:`Net zero energy constraint <>`
* :ref:`Limited maximum capacities of assets to be optimized <maxcap-label>`

.. _fun_mvs_08:

FUN-MVS-08 - Electricity cost model
###################################

:Description: The MVS model shall be provided with data defining electricity grid supply regarding: a) kWh prices (both import and export from/to the grid), b) kWh/h prices (time series of prices), c) Constraints of the interconnection with the main grid (e.g. substation capacity)

:Rationale:  Information necessary for building the MVS Multi-vector Model.

:Priority:  HIGH

:Progress: Done

:Progress message:

The different constraints regarding the electricity DSO can be considered:

a) The energy price as well as the feed-in tariff of a DSO can be provided as a time series (see :ref:`time_series_folder`)
b) :ref:`Peak demand pricing <energy_providers_peak_demand_pricing>` can be considered
c) The transformer station limitation can, but does not have to, be added.

FUN-MVS-09 - Load profiles
##########################

:Description: The MVS model shall be provided with annual electric/thermal demand profiles (hourly values) for each load in the LES.

:Rationale:  Information necessary for building the MVS Multi-vector Model.

:Priority:  HIGH

:Progress: Done

:Progress message:

The MVS can be provided with a variable number of energy consumption profiles, that can be connected to variable busses. Details on how this works can be found in :ref:`these instructions <time_series_folder>`.

FUN-MVS-10 - DH cost model
##########################

:Description: For calculations involving district heating, the MVS model shall support data on thermal distribution network supply, concerning: a) kWh prices (both import and export from/to the grid), b) kWh/h prices (time series of prices), c) optional: thermal power cap (e.g. maximum allowable feed-in per day)

:Rationale:  Information necessary for building the MVS Multi-vector Model.

:Priority:  HIGH

:Progress: Done

:Progress message: Same as for :ref:`fun_mvs_08`.


FUN-MVS-11 - PV data
####################

:Description: For calculations involving PV assets, the MVS model shall be provided with data on PV assets: a) At minimum: Precise location (latitude and longitude), b) Optionally: performance indicators for new PV systems (efficiency - constant or time series, module technology, performance ratio), historical/tracked data (energy generated by existing PV systems, weather data), Inverter efficiency

:Rationale:  Information necessary for building the MVS Multi-vector Model.

:Priority:  HIGH

:Progress: Done for option (b), no automization (minimal requirement met)

:Progress message:

To simulate a PV, the MVS model requires following data from the end-user:

* (Historical) Specific PV generation profile (in kWh/kWp)
* Inverter efficiencies can be considered with an additional energyConversion asset

:ToDo:

To ease the data input for the end-user, more processing could be included here (option a)). For example, the `pvfeedinlib` could be used to fetch the specific PV generation profiles with following data:

* Longitude and latitude
* Module or efficiency
* Performance ratio

This could also be implemented in the EPA.

FUN-MVS-12 - Battery data
#########################

:Description: For calculations involving battery assets, the MVS model shall be provided with data on Battery Energy Storage Systems (BESS): a) Battery type (e.g. lead-acid, lithium ion) b. Technical parameters: C-rate, max and min state of charge (SOC), max. depth of discharge (DOD), roundtrip efficiency (constant or time series), c. Inverter efficiency (optional), d. historical/tracked data from existing BESS

:Rationale:  Information necessary for building the MVS Multi-vector Model.

:Priority:  HIGH

:Progress: Done for option (b), no default inputs, no historical data (minimal requirement met)

:Progress message:

For the MVS, the type of the BESS does not matter. Important are the technical parameters:

* :ref:`C-rate <crate-label>`
* :ref:`Maximum <socmax-label>` and :ref:`minimum <socmin-label>` state of charge (SOC), wherear the latter is inverse to the maximum depth of discharge (DOD)
* Charge- and discharge (constant or time series, equivalent to roundtrip-efficiency) as well as self-discharge rate (comp. :ref:`efficiency <efficiency-label>`)
* It is possible to define :ref:`socin-label`, the initial storage charge at the beginning of the optimization period, which is most immportant for short-term optimizations.
* An inverter or charge controller can be defined by defining an additional energyConversion asset

:Notes:

It may be preferrable for the end-users to have default input values for different battery types (option a)), which is not implemented. This would best be addressed in the EPA with a database of default values, but is currently not being discussed.

Historical dispatch data of batteries is not considered, as the MVS is supposed to determine the optimal dispatch rather then only the performance of a current energy system with determined operational schedules.

FUN-MVS-13 - CHP data
#####################

:Description: For calculations involving CHP assets, the MVS model shall be provided with efficiency factors (electric/thermal)

:Rationale:  Information necessary for building the MVS Multi-Vector Model.

:Priority:  LOW

:Progress: In progress (minimal requirement met)

:Progress message:

A simple CHP model is already included in the MVS (compare :ref:`power_plants`). It considers a fix ratio between thermal and electric output.

:ToDo:

For a variable ratio between heat and electricity output, a new, specific oemof asset would need to be added to the MVS.

FUN-MVS-14 - Thermal storage data
#################################

:Description: For calculations involving Thermal Storage assets, the MVS model shall be provided with: a) Charging and discharging efficiencies, b. Max/Min SOC, initial SOC

:Rationale:  Information necessary for building the MVS Multi-Vector Model.

:Priority:  LOW

:Progress: Done

:Progress message:

It is possible to simulate thermal storage assets with the MVS. Their model is analogous to the BESS, which fulfills the requirement. They are defined by:

* :ref:`C-rate <crate-label>`
* :ref:`Maximum <socmax-label>` and :ref:`minimum <socmin-label>` state of charge (SOC)
* Charge- and discharge (constant or time series, equivalent to roundtrip-efficiency) as well as self-discharge rate (comp. :ref:`efficiency <efficiency-label>`)
* It is possible to define :ref:`socin-label`, the initial storage charge at the beginning of the optimization period, which is most immportant for short-term optimizations.

Adding another level of detail, it is possible to model a :ref:`stratified_tes`, with additional parameters :ref:`fixed_thermal_losses_relative-label` and :ref:`fixed_thermal_losses_absolute-label`.

FUN-MVS-15 - Autonomous operation data
######################################

:Description: The MVS model shall be provided with information on the autonomous operation of the LES i.e. minimum/maximum time of autonomy for specific time intervals.

:Rationale:  Information necessary for building the MVS Multi-vector Model

:Priority:  HIGH

:Progress: Done

:Progress message:

This requirement is addressed by the :ref:`degree of autonomy constraint <kpi_degree_of_autonomy`. It is related to the aggregated demand of the energy system and the required consumption from the grid (comp. :ref:`DOA <kpi_degree_of_autonomy>`), and not minimum or maximum time of autonomous operation.

:Notes:

A constraint of time-related autonomous operation is not possible in the current MVS, as it would introduced a mixed-integer constraint, which would extend simulation times too much. It would be possible in the future to add KPI that quantify the behaviour.

FUN-MVS-16 - Economic data
##########################

:Description: The MVS model shall be provided with information on economic assumptions per asset: CAPEX/kW and OPEX/kWh (constant or time series), lifetime (years), Weighted Average Cost of Capital (WACC).

:Rationale: Information necessary for building the Multi-vector Model.

:Priority:  HIGH

:Progress: Done

:Progress message:

The MVS receives economic data from the end-user. This includes:

* :ref:`Specific investment costs of assets (CAPEX/kW) <specificcosts-label>`
* :ref:`Dispatch price of assets <dispatchprice-label>`
* :ref:`Specific annual operation and management costs (OPEX/kWh, constant or time serie)) <specificomcosts-label>`
* :ref:`Currency <currency-label>`
* :ref:`Tax <tax-label>`
* :ref:`Weighted Average Cost of Capital (WACC) <discountfactor-label>`
* :ref:`Lifetime of the project <_projectduration-label>`
* :ref:`Liftetime of assets <lifetime-label>`

FUN-MVS-17 - Constraints
########################

:Description: The MVS model shall be provided with constraints of the optimisation problem: a) Operating reserve provided by the battery (i.e. redundancy, availability), b. Sizing constraints, c. Cost constraints

:Rationale:  Information necessary for building the Multi-vector Model.

:Priority:  HIGH

:Progress: In progress

:Progress message:

To address the sizing constraint, the attribute `maximumCap` was introduced. This will limit the optimized capacity, even if this results in higher energy supply costs.

A cost constraint is for now disregarded, as always the cheapest supply solution is identified. Limiting the overall NPC would only result in infeasible solutions and a termination of the MVS. Cost constraints considering specific technologies can be covered by adapting the `maximumCap`.

:ToDo:

It was decided at the beginning of the project that the operating reserve constraint may be developed in cooperation with the end-users. This constraint would still need to be defined with the stakeholders.

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

Internally, the MVS uses dictionaries (`dict`) in combination with pandas (`pd.DataFrame`) to set up the energy system model. However, for data exchange with the end-user the input files, ie. the csv or json file is essential. To be able to use all features of the MVS, the user should consider the terminal-based MVS with csv input files. For a more comfortable and interactive usage, the end user can use the MVS though the user interface of the Energy Planning Application (EPA). Here, the data format becomes irrelevant for the user.


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

* For the end-user of the standalone application, an :ref:`automatic report <output_report>` is generated that makes scenario evaluation easy
* For a developer of the standalone application, the results are also provided as excel files and pngs
* For the EPA, the results are provided in a json format to be displayed interactively in their environment

:Notes:

Improving the outputs is a continuing task. Following improvements can be considered in the future:

* Move all KPI connected to the individual energy vectors into a seperate table and display in the report
* Add-on requested by end-users: Cash flow projections

NF-MVS-03 - Communication interface between MVS and ESB
#######################################################

:Description: Communication functionality must be included so that ESB can send requests to MVS and vice versa. This assures that all requests can be coordinated through one platform (e.g. ESB).

:Scope: User Interface, Usability

:Metric: Y/N

:Verification and Measurement: Send a set of different requests from ESB to MVS and count received requests. Do vice versa.

:Target: Send/receive requests that can be processed without information loss

:Progress: Done

:Progress message:

After discussion, there is no direct interface of the ESB and the MVS. The MVS is a standalone application that must be usable without the ESB. To ease end-user use, the EPA (Energy Planning Application) is developed. It sends inputs in json format to the MVS, and receives a json file with the results back. The integration betwe

:Notes:

The EPA development is a continuous process, and currently the MVS has more features than the EPA. Mainly, the EPA does not feature:

* Any constraints of the MVS
* GHG emission calculation
* Set of energy assets of different energy vectors (as EPA explicitly names the assets)

NF-MVS-04 - Unit commitment time step restriction
#################################################

:Description: Energy flows between selected components (Unit commitment) are simulated in hourly timesteps.

:Scope: Performance

:Metric: Timestamps

:Verification and Measurement: Subtract 2-time steps.

:Target: Timestep width of 1 hour

:Progress: Done

:Progress message: The MVS can be run for a variable number of days. The time series have to be provided on an hourly basis.

:Notes: A wish from the end-users war a finer resolution of eg. 15-minute time steps. This possibility still has to be explored.

NF-MVS-05 - Interface for technical parameters and model
########################################################

:Description: Technical parameters are reflected in component modelling

:Scope: Performance

:Metric: Technical variable in energy system model object

:Verification and Measurement: Technical variable in ESM object being not NAN.

:Target: N/A

:Progress: Done

:Progress message: The MVS uses the input parameters to compile the component models. This is also tested using pytests and benchmark tests.


NF-MVS-06 - Interface for economic parameters and model
#######################################################

:Description: Cost parameters are reflected in component modelling

:Scope: Interface

:Metric: Cost variable in energy system model object

:Verification and Measurement: Cost variable in ESM object being not NAN.

:Target: N/A

:Progress: Done

:Progress message:

The MVS uses the input parameters to compile the component models. This is also tested using pytests and benchmark tests.