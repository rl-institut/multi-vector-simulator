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

*Conceptual model validation* consists of looking into the underlying theories and assumptions. Therefore, the conceptual validation scheme includes a comprehensive review of the generated equations by the oemof-solph python library and the components’ models. Next step is to try and adapt them to one pilot project with specific constraints. Tracing and examining the flowchart is also considered as part of this validation type. The aim is to assess the reasonability of the model behavior through pre-requisite knowledge; this technique is known as face validity. 

*Model verification* is related to computer programming and looks into whether the code is a correct representation of the conceptual model. To accomplish this, static testing methods are used to validate the output with respect to an input. Unit tests and integration tests, using proof of correctness techniques, are integrated within the code and evaluate the output of the MVS for any change occuring as they are automated. Unit tests target a single unit such as an individual component, while integration tests target more general parts such as entire modules. Finally, it is very important to make sure that Pytest, the chosen framework for functional testing, always goes through.

*Operational validity* assesses the model’s output with respect to the required accuracy. In order to achieve that, several validation techniques are used, namely:

* Graphical display, which is the use of model generated or own graphs for result interpretation. Graphs are simultaneously used with other validation techniques to inspect the results;

*	Benchmark testing, through which scenarios are created with different constraints and component combinations, and the output is calculated and compared to the expected one to evaluate the performance of the model;
  
*	Extreme scenarios (e.g., drastic meteorological conditions, very high costs, etc.), created to make sure the simulation is through and check if the output behavior is still valid by the use of graphs and qualitative analysis;
  
*	Comparison to other validated model, which replicates one pilot project into a validated optimization model with different component representation to identify the similarities and differences in results; and
  
*	Sensitivity analysis, through which input-output transformations are studied to show the impact of changing the values of some input parameters.

