================================
Moddeling Assumptions of the MVS
================================

Component models
----------------

The component models of the MVS result from the used python-library `oemof-solph` for energy modeling.

It requires component models to be simplified and linearized.
This is the reason that the MVS can provide a pre-feasibility study of a specific system setup,
but not the final sizing and system design.
The types of assets are presented below.

Non-dispatchable sources of generation
######################################

`Examples`:

    - PV plant
    - Wind plant

Dispatchable sources of generation
##################################

`Examples`:

    - Fuel sources
    - Run-of-the-river hydro power plant
    - Deep-ground geothermal plant (ground assumed to allow unlimited extraction of heat, not depending on season)

Fuel sources are added as dispatchable sources, which still can have development, investment, operational and dispatch costs.
They are added by adding a column in `energyProviders.CSV`, and setting file_name to `None`.

DSOs, eventhough also dispatchable sources of generation, should be added via `energyProviders.csv`,
as there are some additional features available then.

Both DSOs and the additional fuel sources are limited to following options:
- Electricity
- Heat
- H2
- Diesel
- Gas

This is as the default weighting factors to translate the energy carrier into electricity equivalent need to be defined. This definition is currently hard-coded in `constants.py` with `DEFAULT_WEIGHTS_ENERGY_CARRIERS`. With new energy carriers necessary, the list can easily be extended. Please see below for more information.

Dispatchable conversion assets
##############################

`Examples`:

    - Diesel generator
    - Electric transformers (rectifiers, inverters)

Energy excess
#############

An energy excess sink is placed on each of the LES energy busses, and therefore energy excess is allowed to take place on each bus of the LES.
This means that there are assumed to be sufficient vents (heat) or transistors (electricity) to dump excess (waste) generation.
Excess generation can only take place when a non-dispatchable source is present or if an asset can supply energy without any fuel or dispatch costs.

In case of excessive excess energy, a warning is given that it seems to be cheaper to have high excess generation than investing into more capacities.
High excess energy can for example result into an optimized inverter capacity that is smaller than the peak generation of installed PV.
This becomes unrealistic when the excess is very high.

Energy providers (DSOs)
-----------------------

The energy providers are the most complex assets in the MVS model. They are composed of a number of sub-assets

    - Energy consumption source, providing the energy required from the system with a certain price
    - Energy peak demand pricing "transformers", which represent the costs induced due to peak demand
    - Bus connecting energy consumption source and energy peak demand pricing transformers
    - Energy feed-in sink, able to take in generation that is provided to the DSO for revenue
    - Optionally: Transformer Station connecting the DSO bus to the energy bus of the LES

With all these components, the DSO can be vizualized as follows:

.. image:: images/Model_Assumptions_energyProvider_assets.png
 :width: 600

Variable energy consumption prices (timeseries)
###############################################

- Link to howto

Peak demand pricing
###################

A peak demand pricing scheme is based on an electricity tariff,
that requires the consumer not only to pay for the aggregated energy consumption in a time period (eg. kWh electricity),
but also for the maximum peak demand (load, eg. kW power) towards the DSO grid within a specific pricing period.

In the MVS, this information is gathered for the `energyProviders` with:

    - :const:`mvs_eland.utils.constants_json_strings.PEAK_DEMAND_PRICING_PERIOD` as the period used in peak demand pricing. Possible is 1 (yearly), 2 (half-yearly), 3 (each trimester), 4 (quaterly), 6 (every 2 months) and 12 (each month). If you have a `simulation_duration` < 365 days, the periods will still be set up assuming a year! This means, that if you are simulating 14 days, you will never be able to have more than one peak demand pricing period in place.

    - :const:`mvs_eland.utils.constants_json_strings.PEAK_DEMAND_PRICING` as the costs per peak load unit, eg. kW

To repesent the peak demand pricing, the MVS adds a "transformer" that is optimized with specific operation and maintainance costs per year equal to the PEAK_DEMAND_PRICING for each of the pricing periods.
For two peak demand pricing persiods, the resulting dispatch could look as following:

.. image:: images/Model_Assumptions_Peak_Demand_Pricing_Dispatch_Graph.png
 :width: 600

Constraints
-----------

Constraints are controlled with the file `constraints.csv`.

Minimal renewable share constraint
##################################

The minimal renewable share constraint requires the capacity and dispatch optimization of the MVS to reach at least the minimal renewable share defined within the constraint. The renewable share of the optimized energy system may also be higher then the minimal renewable share.

The minimal renewable share is applied to the minimal renewable share of the whole, sector-coupled energy system, but not specific sectors. As such, energy carrier weighting plays a role and may lead to unexpected results. The constraint reads as follows:

.. math:
        minimal renewable factor <= \frac{\sum renewable generation \cdot weighting factor}{\sum renewable generation \cdot weighting factor + \sum non-renewable generation \cdot weighting factor}


:Deactivating the constraint:

The minimal renewable share constraint is deactivated by defining following row in `constraints.csv` as follows:

```minimal_renewable_share,factor,0```

:Activating the constraint:

The constraint is enabled when the value of the minimal renewable share factor is above 0 in `constraints.csv`:

```minimal_renewable_share,factor,0.3```


Depending on the energy system, especially when working assets which are not to be capacity-optimized, it is possible that the minimal renewable share criterion can not be met. The simulation terminates in that case. If you are not sure if your energy system can meet the constraint, set all `optimize_Cap` to `True`, and then investigate further.
Also, if you are aiming at very high minimal renewable shares, the simulation time can increase drastically. If you do not get a result after a maximum of 20 Minutes, you should consider terminating the simulation and trying with a lower minimum renewable share.

The minimum renewable share is introduced to the energy system by `D2.constraint_minimal_renewable_share()` and a validation test is performed with `E4.minimal_renewable_share_test()`.

Weighting of energy carriers
----------------------------

To be able to calculate sector-wide key performance indicators, it is necessary to weight energy carriers depending on their usable potential. With the conference paper handed in to the CIRED workshop we propose a methodolgy comparable to Gasoline Gallon Equivalents. This definition is currently hard-coded in `constants.py` with `DEFAULT_WEIGHTS_ENERGY_CARRIERS`. New energy carriers should be atted to its list. Unknown carriers raise an `UnknownEnergyCarrier` Error.

Following conversion factors and energy carriers are defined:

.. list-table:: Weights of energy carriers
   :widths: 50 25 25 25
   :header-rows: 1

   * - Energy carrier
     - Energy carrier unit
     - Conversion factor unit
     - Value of conversion factor
   * - Electricity
     - kWh_el
     - kWh_eleq/kWh_el
     - 1
   * - Heat
     - kWh_therm
     - kWh_eleq/kWh_therm
     - 1
   * - H2
     - kg
     - kWh_eleq/kg
     - 32.87
   * - Diesel
     - l
     - kWh_eleq/l
     - 8.20
   * - Gas
     - l
     - kWh_eleq/l
     - 5.38

The confersion factors are derived from their `Gasoline Gallon Equivalents.<https://epact.energy.gov/fuel-conversion-factors>`_


Limitations
-----------

When running simulations with the MVS, there are certain peculiarities to be aware of.
The peculiarities can be considered as limitations, some of which are merely model assumptions and others are drawbacks of the model.
A number of those are inherited due to the nature of the MVS and its underlying modules,
and others can still be addressed in the future during the MVS development process, which is still ongoing.
The following table lists the MVS limitations based on their type.

.. list-table:: Limitations
   :widths: 25 25
   :header-rows: 1

   * - Inherited
     - Can be addressed
   * - :ref:`limitations-real-life-constraint`
     - :ref:`limitations-missing-kpi`
   * - :ref:`limitations-simplified_model`
     - :ref:`limitations-random-excess`
   * - :ref:`limitations-degradation`
     - :ref:`limitations-renewable-share-definition`
   * - :ref:`limitations-perfect_foresight`
     - :ref:`limitations-energy_carrier_weighting`
   * - 
     - :ref:`limitations-energy_shortage`
   * - 
     - :ref:`limitations-bidirectional-transformers`

.. _limitations-real-life-constraint:

Infeasible bi-directional flow in one timestep
##############################################

:Limitation: 
The real life constraint of the dispatch of assets,
that it is not possible to have two flows in opposite directions at the same time step, is not adhered to in the MVS.

:Reason: 
The MVS is based on the python library `oemof-solph`. Its generic components are used to set up the energy system.
As a ground rule, the components of `oemof-solph` are unidirectional.
This means that for an asset that is bidirectional two transformer objects have to be used. Examples for this are:

* Physical bi-directional assets, eg. inverters
* Logical bi-directional assets, eg. consumption from the grid and feed-in to the grid

To archieve the real-life constraint one flow has to be zero when the other is larger zero,
one would have to implement following relation:

.. math:: 
        E_{in} \cdot E_{out} = 0

However, this relation creates a non-linear problem and can not be implemented in `oemof-solph`.

:Implications: 
This limitation means that the MVS might result in infeasible dispatch of assets.
For instance, a bus might be supplied by a rectifier and itself supplying an inverter at the same time step t,
which cannot logically happen if these assets are part of one physical bi-directional inverter.
Another case that could occur is feeding the grid and consuming from it at the same time t.

Under certain conditions, including an excess generation as well as dispatch costs of zero,
the infeasibe dispatch can also be observed for batteries and result in a parallel charge and discharge of the battery.
If this occurs, a solution may be to set a marginal dispatch cost of battery charge.

.. _limitations-simplified_model:

Simplified linear component models
##################################

:Limitation:
The MVS simplifies the component model of some assets.

    * Generators have an efficiency that is not load-dependent
    * Storage have a charging efficiency that is not SOC-dependent
    * Turbines are implemented without ramp rates

:Reason:
The MVS is based oemof-solph python library and uses its generic components to set up an energy system.
Transformers and storages cannot have variable efficiencies.

:Implications:
Simplifying the implementation of some component specifications can be beneficial for the ease of the model,
however, it contributes to the lack of realism and might result in less accurate values.
The MVS accepts the decreased level of detail in return for a quick evaluation of its scenarios,
which are often only used for a pre-feasibility analysis.

.. _limitations-degradation:

No degradation of efficiencies over a component lifetime
########################################################

:Limitation:
The MVS does not degrade the efficiencies of assets over the lifetime of the project,
eg. in the case of production assets like PV panels.

:Reason:
The simulation of the MVS is only based on a single reference year,
and it is not possible to take into account multi-year degradation of asset efficiency.

:Implications:
This results in an overestimation of the energy generated by the asset,
which implies that the calculation of some other results might also be overestimated (e.g. overestimation of feed-in energy).
The user can circumvent this by applying a degradation factor manually to the generation time series used as an input for the MVS.

.. _limitations-perfect_foresight:

Perfect foresight
#################

:Limitation:
The optimal solution of the energy system is based on perfect foresight.

:Reason:
As the MVS and thus oemof-solph, which is handling the energy system model,
know the generation and demand profiles for the whole simulation time
and solve the optimization problem based on a linear equation system,
the solver knows their dispatch for certain, whereas in reality the generation and demand could only be forecasted.

:Implications:
The perfect foresight can lead to suspicious dispatch of assets,
for example charging of a battery right before a (in real-life) random blackout occurs.
The systems optimized with the MVS therefore, represent their optimal potential, which in reality could not be reached.
The MVS has thus a tendency to underestimate the needed battery capacity or the minimal state of charge for backup purposes,
and also designs the PV system and backup power according to perfect forecasts.
In reality, operational margins would need to be added.

.. _limitations-missing-kpi:

Extension of KPIs necessary
###########################

:Limitation:
Some important KPIs usually required by developers are currently not implemented in the MVS:

* Internal rate of return (IRR)
* Payback period
* Return on equity (ROE),

:Reason:
The MVS tool is a work in progress and this can still be addressed in the future.

:Implications:
The absence of such indicators might affect decision-making.

.. _limitations-random-excess:

Random excess energy distribution
#################################

:Limitation:
There is random excess distribution between the feed-in sink and the excess sink when no feed-in-tariff is assumed in the system.

:Reason:
Since there is no feed-in-tariff to benefit from, the MVS randomly distributes the excess energy between the feed-in and excess sinks.
As such, the distribution of excess energy changes when running several simulations for the same input files.

:Implications:
On the first glance, the distribution of excess energy onto both feed-in sink and excess sink may seem off to the end-user.
Other than these inconveniences, there are no real implications that affect the capacity and dispatch optimization.
When a degree of self-supply and self-consumption is defined, the limitation might tarnish these results.

.. _limitations-renewable-share-definition:

Renewable energy share defintion relative to energy carriers
############################################################

:Limitation:
The current renewable energy share depends on the share of renewable energy production assets directly feeding the load.
The equation to calculate the share also includes the energy carrier rating as described here below:

.. math:: 
        RES &= \frac{\sum_i E_{RE,generation}(i) \cdot w_i}{\sum_i E_{RE,generation}(i) \cdot w_i + \sum_k E_{nonRE,generation}(k) \cdot w_k}

        \text{with~} & i \text{: renewable energy asset}

        & k \text{: non-renewable energy asset}

:Reason:
The MVS tool is a work in progress and this can still be addressed in the future.

:Implications:
This might result in different values when comparing them to other models.
Another way to calculate it is by considering the share of energy consumption supplied from renewable sources.

.. _limitations-energy_carrier_weighting:

Energy carrier weighting
########################

:Limitation: 
The MVS assumes a usable potential/energy content rating for every energy carrier.
The current version assumes that 1 kWh thermal is equivalent to 1 kWh electricity.

:Reason: 
This is an approach that the MVS currently uses.

:Implications:
By weighing the energy carriers according to their energy content (Gasoline Gallon Equivalent (GGE)),
the MVS might result in values that can't be directly assessed.
Those ratings affect the calaculation of the levelized cost of the energy carriers,
but also the minimum renewable energy share constraint.

.. _limitations-energy_shortage:

Events of energy shortage or grid interruption can not be modelled
##################################################################

:Limitation: 
The MVS assumes no shortage or grid interruption in the system.

:Reason: 
The aim of the MVS does not cover this scenario.

:Implications:
Electricity shortages due to power cuts might happen in real life and the MVS currently omits this scenario.
If a system is self-sufficient but relies on grid-connected PV systems,
the latter stop feeding the load if any power cuts occur
and the battery storage systems might not be enough to serve the load (energy shortage).

.. _limitations-bidirectional-transformers:

Need of two transformer assets for of one technical unit
########################################################

:Limitation:
Two transformer objects representing one technical unit in real life are currently unlinked in terms of capacity and attributed costs.

:Reason:
The MVS uses oemof-solph's generic components which are unidirectional so for a bidirectional asset,
two transformer objects have to be used.

:Implications: 
Since one input is only allowed, such technical units are modelled as two separate transformers that are currently unlinked in the MVS
(e.g., hybrid inverter, heat pump, distribution transformer, etc.).
This raises a difficulty to define costs in the input data.
It also results in two optimized capacities for one logical unit.

This limitation is to be addressed with a constraint which links both capacities of one logical unit,
and therefore solves both the problem to attribute costs and the previously differing capacities.

.. _validation-methodology:

Validation Methodology
----------------------

As mentioned in :ref:`validation-plan`, the MVS is validated using three validation methods: conceptual model validation, model verification and operational validity.

**Conceptual model validation** consists of looking into the underlying theories and assumptions. Therefore, the conceptual validation scheme includes a comprehensive review of the generated equations by the oemof-solph python library and the components’ models. Next step is to try and adapt them to a sector coupled example with specific constraints. Tracing and examining the flowchart is also considered as part of this validation type which can be found in :ref:`Flowchart`. The aim is to assess the reasonability of the model behavior through pre-requisite knowledge; this technique is known as face validity. 

**Model verification** is related to computer programming and looks into whether the code is a correct representation of the conceptual model. To accomplish this, static testing methods are used to validate the output with respect to an input. Unit tests and integration tests, using proof of correctness techniques, are integrated within the code and evaluate the output of the MVS for any change occuring as they are automated. Unit tests target a single unit such as an individual component, while integration tests target more general parts such as entire modules. Both tests are implemented as pytests for the MVS, which allows automatized testing. 

**Operational validity** assesses the model’s output with respect to the required accuracy. In order to achieve that, several validation techniques are used, namely:

* **Graphical display**, which is the use of model generated or own graphs for result interpretation. Graphs are simultaneously used with other validation techniques to inspect the results;

*	**Benchmark testing**, through which scenarios are created with different constraints and component combinations, and the output is calculated and compared to the expected one to evaluate the performance of the model;
  
*	**Extreme scenarios** (e.g., drastic meteorological conditions, very high costs, etc.) are created to make sure the simulation runs through and check if the output behavior is still valid by the use of graphs and qualitative analysis;
  
*	**Comparison to other validated model**, which compares the results of a case study simulated with the model at hand to the results of a validated optimization model in order to identify the similarities and differences in results;
  
*	**Sensitivity analysis**, through which input-output transformations are studied to show the impact of changing the values of some input parameters.

Unit and Integration Tests
##########################

The goal is to have unit tests for each single function of the MVS, and integration tests for the larger modules. As previously mentioned, pytests are used for those kind of tests as they always assert that an externally determined output is archieved when applying a specific function. Unit tests and integration tests are gauged by using test coverage measurement. Examples of those tests can be found `here <https://github.com/rl-institut/multi-vector-simulator/tree/validation_plan/tests>`_  and it is possible to distinguish them from other tests from the nomination that refers to the names of the source modules (e.g., A0, A1, B0, etc.). The MVS covers so far 80% of the modules and sub-modules as seen in the next figure. Since those tests are automated, this coverage is updated for any changes in the model.

.. image:: images/Test_coverage.png
 :width: 200

Benchmark Tests
###############

A benchmark is a point of reference against which results are compared to assess the operational validity of a model. Benchmark tests are also automated like unit and integration tests, hence it is necessary to check that they are always passing for any implemented changes in the model. The implemented benchmark tests, which cover several features and functionalities of the MVS, are listed here below.

* Electricity Grid + PV (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/AB_grid_PV>`_/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/d5a06f913fa2449e3d9f9966d3362dc7e8e4c874/tests/test_benchmark_scenarios.py#L63>`_): Maximum use of PV to serve the demand and the rest is compensated from the grid
   
* Electricity Grid + PV + Battery (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/ABE_grid_PV_battery>`_/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/d5a06f913fa2449e3d9f9966d3362dc7e8e4c874/tests/test_benchmark_scenarios.py#L124>`_): Reduced excess energy compared to Grid + PV scenario to charge the battery
   
* Electricity Grid + Diesel Generator (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/AD_grid_diesel>`_/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/d5a06f913fa2449e3d9f9966d3362dc7e8e4c874/tests/test_benchmark_scenarios.py#L157>`_): The diesel generator is only used if its LCOE is less than the grid price
   
* Electricity Grid + Battery (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/AE_grid_battery>`_/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/d5a06f913fa2449e3d9f9966d3362dc7e8e4c874/tests/test_benchmark_scenarios.py#L96>`_): The grid is only used to feed the load
   
* Electricity Grid + Battery + Peak Demand Pricing (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/AE_grid_battery_peak_pricing>`_/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/d5a06f913fa2449e3d9f9966d3362dc7e8e4c874/tests/test_benchmark_scenarios.py#L192>`_): Battery is charged at times of peak demand and used when demand is larger
   
* Electricity Grid (Price as Time Series) + Heat Pump + Heat Grid (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/AFG_grid_heatpump_heat>`_/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/d5a06f913fa2449e3d9f9966d3362dc7e8e4c874/tests/test_benchmark_scenarios.py#L276>`_): Heat pump is used when electricity_price/COP is less than the heat grid price
     
More tests can still be implemented with regard to:

* The investment model within the MVS

* Components with two input sources

Sensitivity Analysis Tests
##########################

For sensitivity analysis, the behaviour of the MVS is studied by testing the effect of changing the value of the feed-in tariff (FIT) for a fixed value of an asset's LCOE such that LCOE_ASSET is less than the electricity price. The implemented sensitivity analysis test is shown here below with the resulting graph. More information can be found `here <https://repository.tudelft.nl/islandora/object/uuid%3A50c283c7-64c9-4470-8063-140b56f18cfe?collection=education>`_ on pages 54-55.

* Comparing FIT to LCOE_ASSET: Investment in maximum allowed capacity of asset for FIT values larger than LCOE_ASSET

.. image:: images/Sensitivity_1.png
 :width: 200

The previous graph is not generated by the MVS itself and the results are drawn and interpreted subjectively from it, which points back to the use of graphical displays validation technique with another one simultaneously. This sensitivity analysis test can be translated into a benchmark test so that it becomes automatized. The idea is to check that for every value of FIT greater than LCOE_ASSET, the MVS is investing in the entire allowed maximum capacity of the asset. More input-output transformations for sensitivity analyses can be investigated such as:

* Checking the randomness of supply between the electricity grid and a diesel generator when fuel_price/generator_efficiency is equal to electricity_price/transformer_efficiency

* Checking if a diesel generator actually replaces the consumption from the grid at times of peak demand--i.e., dispatch_price is less or equal to peak_demand_charge

Comparison to Other Models
##########################

So far, the MVS' results for a sector coupled system (electricity + hydrogen) are compared to those of HOMER for the same exact system. This comparison is important to highlight the similarities and differences between the two optimization models. On the electricity side, most of the values are comparable and in the same range. The differences mainly show on the hydrogen part in terms of investment in an electrolyzer capacity (component linking the two sectors) and the values related to that. On another note, both models have different approaches for calculating the value of the levelized cost of a certain energy carrier and therefore the values are apart. Details regarding the comparison drawn between the two models can be found `here <https://repository.tudelft.nl/islandora/object/uuid%3A50c283c7-64c9-4470-8063-140b56f18cfe?collection=education>`_ on pages 55-63.

This validation method is commonly used. However, one model cannot absolutely validate another model or claim that one is better than the other. This is why the focus should be on testing the correctness, appropriateness and accuracy of a model vis-à-vis its purpose. Since the MVS is an open source tool, it is important to use a validated model for comparison, but also similar open source tools like urbs and Calliope for instance. The following two articles list some of the models that could be used for comparison to the MVS: `A review of modelling tools for energy and electricity systems with large shares of variable renewables <https://doi.org/10.1016/j.rser.2018.08.002>`_ and `Power-to-heat for renewable energy integration: A review of technologies, modeling approaches, and flexibility potentials <https://doi.org/10.1016/j.apenergy.2017.12.073>`_.

