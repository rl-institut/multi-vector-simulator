=================
About the Project
=================

H2020 Project E-Land
--------------------

License
-------

The MVS is licensed with the **GNU General Public License v2.0**. The GNU GPL is the most widely used free software license and has a strong copyleft requirement. When distributing derived works, the source code of the work must be made available under the same license. There are multiple variants of the GNU GPL, each with different requirements.

Flowchart
---------
 
The MVS' global flowchart, or graphical model, is divided into three connected blocks that trace the logic sequence: inputs, system model, and outputs. This is a typical representation of a simulation model.

.. image:: images/MVS_flowchart.png
 :width: 200

The user is asked to enter the required data through a web interface. In developer mode, the data is submitted as a number of csv files. This input data is split into  four categories:

1.	Project description, which entails the general information regarding the project (country, coordinates, etc.), as well as the economic data such as the discount factor, project duration, or tax;

2.	Energy consumption, which is expressed as times series based on the type of energy (in this case: electrical and therma);

3.	System configuration, in which the user specifies the technical and financial data of each asset; and

4.	Meteorological data, which is related to the components that generate electricity by harnessing an existing source of energy that is weather- and time-dependent (e.g., solar and wind power).

This set of input data is then translated to a linear programming problem, also known as a constrained optimization problem. The MVS is based on the oemof-solph python library that describes the problem by specifying the objective function, the decision variables and the bounds and constraints. The goal is to (1) minimize the production costs by determining the generating units' optimal output, which meets the total demand, and (2) optimize near-future investments in generation and storage assets with the least possible cost of energy.
The simulation outputs are also separated into categories: the economic results used for the financial evaluation, such as the levelized cost of electricity or heat or the net present value of the projected investments, the technical results that include the optimized capacities and dispatch of each asset for instance, and the system’s environmental contribution in terms of CO2 emissions. All these results are valuable for the decision making.

MVS Validation Plan
-------------------

The adopted validation plan is part of the MVS’ entire development process and is based on three main validation types: conceptual model validation, model verification and operational validity. Following some in-depth research, a validation approach is chosen for the MVS, through which the most appropriate validation techniques are applied to the MVS so that it gains the necessary credibility.

**Conceptual model validation** consists of looking into the underlying theories and assumptions. Therefore, the conceptual validation scheme includes a comprehensive review of the generated equations by the oemof-solph python library and the components’ models. Next step is to try and adapt them to one pilot project with specific constraints. Tracing and examining the flowchart is also considered as part of this validation type. The aim is to assess the reasonability of the model behavior through pre-requisite knowledge; this technique is known as face validity. 

**Model verification** is related to computer programming and looks into whether the code is a correct representation of the conceptual model. To accomplish this, static testing methods are used to validate the output with respect to an input. Unit tests and integration tests, using proof of correctness techniques, are integrated within the code and evaluate the output of the MVS for any change occuring as they are automated. Unit tests target a single unit such as an individual component, while integration tests target more general parts such as entire modules. Both tests are implemented as pytests for the MVS, which allows automatized testing. 

**Operational validity** assesses the model’s output with respect to the required accuracy. In order to achieve that, several validation techniques are used, namely:

* Graphical display, which is the use of model generated or own graphs for result interpretation. Graphs are simultaneously used with other validation techniques to inspect the results;

*	**Benchmark testing**, through which scenarios are created with different constraints and component combinations, and the output is calculated and compared to the expected one to evaluate the performance of the model
  
*	**Extreme scenarios** (e.g., drastic meteorological conditions, very high costs, etc.) are created to make sure the simulation runs through and check if the output behavior is still valid by the use of graphs and qualitative analysis
  
*	**Comparison to other validated model**, which compares the results of a case study simulated with both the model to be validates as well as with a validated optimization model to identify the similarities and differences in results
  
*	**Sensitivity analysis**, through which input-output transformations are studied to show the impact of changing the values of some input parameters.

Validation techniques applied to the MVS
###############################

Unit tests and integration tests are gauged by using test coverage measurement. The MVS covers so far 80% of the modules and sub-modules as seen in the next figure. Since those tests are automated, this coverage is updated for any changes in the model.

.. image:: images/Test_coverage.png
 :width: 200

A benchmark is a point of reference against which results are compared to assess the operational validity of a model. Benchmark tests are not automated like unit and integration tests, hence it is necessary to check that they are passing for any implemented changes in the model. The following table lists the implemented benchmark tests which cover several features and functionalities of the MVS.

.. list-table:: Benchmark Tests
   :widths: 25 25
   :header-rows: 1

   * - Benchmark Test
     - Expected Result
   * - Electrical Grid + PV
     - Maximum use of PV to serve the demand and the rest is compensated from the grid
   * - Electrical Grid + PV + Battery
     - Reduced excess energy compared to Grid + PV scenario to charge the battery
   * - Electrical Grid + Diesel Generator
     - The diesel generator is only used if its LCOE is less than the grid price
   * - Electrical Grid + Battery
     - The grid is only used to feed the load
   * - Electrical Grid + Battery + Peak Demand Pricing
     - Battery is charged at times of peak demand and used when demand is larger
   * - Electrical Grid (Price as Time Series) + Heat Pump + Heat Grid
     - Heat pump is used when electricity_price/COP is less than the heat grid price
     
More tests can still be implemented with regard to the investment model within the MVS. Also, components with two input sources can also be tested.

For sensitivity analysis, the behaviour of the MVS is studied by testing the effect of changing the value of the feed-in tariff for a fixed value of an asset's LCOE such that LCOE_ASSET is less than the electricity price. More input-output transformations can be investigated such as checking the randomness of supply between the electrical grid and a diesel generator when fuel_price/generator_efficiency is equal to electricity_price/transformer_efficiency. Another sensitivity analysis case could be used to know if a diesel generator actually replaces the consumption from the grid at times of peak demand--i.e., dispatch_price is less or equal to peak_demand_charge. The table below lists the implemented sensitivity analysis tests.

.. list-table:: Sensitivity Analyses
   :widths: 25 25
   :header-rows: 1

   * - Sensitivity Analysis Test
     - Expected Result
   * - Comparing FIT to LCOE_ASSET
     - Invest is maximum allowed capacity of asset for FIT values larger than LCOE_ASSET
     
Comparison to Other Models
##########################

So far, the MVS' results for a sector coupled system (electricity + hydrogen) are compared to those of HOMER for the same exact system. This comparison is important to highlight the similarities and differences between the two optimization models. On the electricity side, most of the values are comparable and in the same order of magnitude. The differences mainly show on the hydrogen part in terms of investment in an electrolyzer capacity (component linking the two sectors) and the values related to that. On another note, both models have different approaches for calculating the value of the levelized cost of a certain energy carrier and therefore the values are apart. 

This validation method is very much in practice. However, one model cannot absolutely validate another model or claim that one is better than the other. This is why the focus should be on testing the correctness, appropriateness and accuracy of a model vis-à-vis its purpose. Since the MVS is an open source tool, it is important to use a validated model for comparison, but also similar open source tools like urbs and Calliope for instance.
