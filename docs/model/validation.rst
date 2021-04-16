
.. _validation-methodology:

Validation Methodology
----------------------

As mentioned in OLD REF (validation-plan in owerview.rst), the MVS is validated using three validation methods: conceptual model validation, model verification and operational validity.

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

The goal is to have unit tests for each single function of the MVS, and integration tests for the larger modules. As previously mentioned, pytests are used for those kind of tests as they always assert that an externally determined output is archieved when applying a specific function. Unit tests and integration tests are gauged by using test coverage measurement. Examples of those tests can be found `here <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests>`__  and it is possible to distinguish them from other tests from the nomination that refers to the names of the source modules (e.g., A0, A1, B0, etc.). The MVS covers so far 80% of the modules and sub-modules as seen in the next figure.

.. image:: ../images/Test_coverage.png
 :width: 200

Since those tests are automated, this coverage is updated for any changes in the model.

Benchmark Tests
###############

A benchmark is a point of reference against which results are compared to assess the operational validity of a model. Benchmark tests are also automated like unit and integration tests, hence it is necessary to check that they are always passing for any implemented changes in the model. The implemented benchmark tests, which cover several features and functionalities of the MVS, are listed here below.

* Electricity Grid + PV (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/AB_grid_PV>`__/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/d5a06f913fa2449e3d9f9966d3362dc7e8e4c874/tests/test_benchmark_scenarios.py#L63>`__): Maximum use of PV to serve the demand and the rest is compensated from the grid

* Electricity Grid + PV + Battery (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/ABE_grid_PV_battery>`__/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/d5a06f913fa2449e3d9f9966d3362dc7e8e4c874/tests/test_benchmark_scenarios.py#L124>`__): Reduced excess energy compared to Grid + PV scenario to charge the battery

* Electricity Grid + Diesel Generator (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/AD_grid_diesel>`__/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/d5a06f913fa2449e3d9f9966d3362dc7e8e4c874/tests/test_benchmark_scenarios.py#L157>`__): The diesel generator is only used if its LCOE is less than the grid price

* Electricity Grid + Battery (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/AE_grid_battery>`__/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/d5a06f913fa2449e3d9f9966d3362dc7e8e4c874/tests/test_benchmark_scenarios.py#L96>`__): The grid is only used to feed the load

* Electricity Grid + Battery + Peak Demand Pricing (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/AE_grid_battery_peak_pricing>`__/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/d5a06f913fa2449e3d9f9966d3362dc7e8e4c874/tests/test_benchmark_scenarios.py#L192>`__): Battery is charged at times of peak demand and used when demand is larger

* Electricity Grid (Price as Time Series) + Heat Pump + Heat Grid (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/AFG_grid_heatpump_heat>`__/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/d5a06f913fa2449e3d9f9966d3362dc7e8e4c874/tests/test_benchmark_scenarios.py#L276>`__): Heat pump is used when electricity_price/COP is less than the heat grid price

* Maximum emissions constraint: Grid + PV + Diesel Generator (data: `set 1 <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/Constraint_maximum_emissions_None>`__, `set 2 <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/Constraint_maximum_emissions_low>`__, `set 3 <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/Constraint_maximum_emissions_low_grid_RE_100>`__/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/f459b35da6c46445e8294845604eb2b683e43680/tests/test_benchmark_constraints.py#L121>`__): Emissions are limited by constraint, more PV is installed to reduce emissions. For RE share of 100 % in grid, more electricity from the grid is used

* Parser converting an energy system model from EPA to MVS (`data <https://github.com/rl-institut/multi-vector-simulator/blob/dev/tests/benchmark_test_inputs/epa_benchmark.json>`__/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/dev/tests/test_benchmark_scenarios.py>`__)

* Stratified thermal energy storage (`data <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/Feature_stratified_thermal_storage>`__/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/dev/tests/test_benchmark_stratified_thermal_storage.py>`__): With fixed thermal losses absolute and relative reduced storage capacity only if these losses apply

* Net zero energy (NZE) constraint: Grid + PV and Grid + PV + Heat Pump (data `set 1 <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/Constraint_net_zero_energy_true>`__, `set 2 <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/Constraint_net_zero_energy_False>`__, `set 3 <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/Constraint_net_zero_energy_sector_coupled_true>`__, `set 4 <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/benchmark_test_inputs/Constraint_net_zero_energy_sector_coupled_False>`__/`pytest <https://github.com/rl-institut/multi-vector-simulator/blob/dev/tests/test_benchmark_constraints.py>`__): Degree of NZE >= 1 when constraint is used and degree of NZE < 1 when constraint is not used.

More tests can still be implemented with regard to:

* The investment model within the MVS

* Components with two input sources

Sensitivity Analysis Tests
##########################

For sensitivity analysis, the behaviour of the MVS is studied by testing the effect of changing the value of the feed-in tariff (FIT) for a fixed value of an asset's LCOE such that LCOE_ASSET is less than the electricity price. The implemented sensitivity analysis test is shown here below with the resulting graph. More information can be found `here <https://repository.tudelft.nl/islandora/object/uuid%3A50c283c7-64c9-4470-8063-140b56f18cfe?collection=education>`__ on pages 54-55.

* Comparing FIT to LCOE_ASSET: Investment in maximum allowed capacity of asset for FIT values larger than LCOE_ASSET

.. image:: ../images/Sensitivity_1.png
 :width: 600

The previous graph is not generated by the MVS itself and the results are drawn and interpreted subjectively from it, which points back to the use of graphical displays validation technique with another one simultaneously. This sensitivity analysis test can be translated into a benchmark test so that it becomes automatized. The idea is to check that for every value of FIT greater than LCOE_ASSET, the MVS is investing in the entire allowed maximum capacity of the asset.

More input-output transformations for sensitivity analyses can be investigated such as:

* Checking the randomness of supply between the electricity grid and a diesel generator when fuel_price/generator_efficiency is equal to electricity_price/transformer_efficiency

* Checking if a diesel generator actually replaces the consumption from the grid at times of peak demand--i.e., dispatch_price is less or equal to peak_demand_charge

Comparison to Other Models
##########################

So far, the MVS' results for a sector coupled system (electricity + hydrogen) are compared to those of HOMER for the same exact system. This comparison is important to highlight the similarities and differences between the two optimization models. On the electricity side, most of the values are comparable and in the same range. The differences mainly show on the hydrogen part in terms of investment in an electrolyzer capacity (component linking the two sectors) and the values related to that. On another note, both models have different approaches for calculating the value of the levelized cost of a certain energy carrier and therefore the values are apart. Details regarding the comparison drawn between the two models can be found `here <https://repository.tudelft.nl/islandora/object/uuid%3A50c283c7-64c9-4470-8063-140b56f18cfe?collection=education>`__ on pages 55-63.

This validation method is commonly used. However, one model cannot absolutely validate another model or claim that one is better than the other. This is why the focus should be on testing the correctness, appropriateness and accuracy of a model vis-à-vis its purpose. Since the MVS is an open source tool, it is important to use a validated model for comparison, but also similar open source tools like urbs and Calliope for instance. The following two articles list some of the models that could be used for comparison to the MVS: `A review of modelling tools for energy and electricity systems with large shares of variable renewables <https://doi.org/10.1016/j.rser.2018.08.002>`__ and `Power-to-heat for renewable energy integration: A review of technologies, modeling approaches, and flexibility potentials <https://doi.org/10.1016/j.apenergy.2017.12.073>`__.


.. _verification-tests:

Automatic output verification
#############################

There is a suite of functions within the MVS codebase module E4_verification.py that run a few checks on some of the outputs of the simulation in order to make sure that the results are meaningful and if something like an excessive excess energy flow is noteworthy. These are valuable tests that act as a safeguard for the user, as the model is not only validated for benchmark tests but for every run simulation.
The following is the list of functions in E4_verification.py that carry out the verification tests:

* detect_excessive_excess_generation_in_bus
* maximum_emissions_test
* minimal_renewable_share_test
* verify_state_of_charge

The first test serves as an alert to the energy system modeler to check their inputs again, whereas if there are any errors raised within the other functions, it is an indication of something seriously wrong.

detect_excessive_excess_generation_in_bus
=========================================

This test is here to notify to the modeler in case there is an excess generation within a bus in the energy system. Precisely, the modeler is given a heads-up when the ratio of total outflows to total inflows for one or more buses is less than 0.9

maximum_emissions_test
======================

Other than renewables, source components in the energy system have a certain emissions value associated with the generation of energy. The user is able to apply a constraint on the maximum allowed emissions in the energy mix of the output energy system. This function runs a verification test on the output energy system data to determine if the user-supplied constraint on maximum emissions is correctly applied or not. If not, then the modeler is notified.

minimal_renewable_share_test
============================

This test is carried out on the energy system model after optimization of its capacities. It verifies whether the user-provided constraint for the minimal share of renewables in the energy mix of the optimized system was respected or not. In case this lower bound constraint is not met, the user is notified.

verify_state_of_charge
======================

This test is intended to check the time-series of the state of charge values for storages in the energy system simulation results to notify of a serious error in case, the SoC value at any time-step is not between 0 and 1, which is physically not feasible.
