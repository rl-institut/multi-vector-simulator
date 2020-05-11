=================
About the Project
=================

H2020 Project E-Land
--------------------

License
-------

MVS Validation Plan
-------

The adopted validation plan is part of the MVS’ entire development process and is based on three main validation types: conceptual model validation, model verification and operational validity. Following some in-depth research, a validation approach is chosen for the MVS, through which the most appropriate validation techniques are applied to the MVS so that it gains the necessary credibility.

Conceptual model validation consists of looking into the underlying theories and assumptions. Therefore, the conceptual validation scheme includes a comprehensive review of the generated equations by the oemof python library and the components’ models. Next step is to try and adapt them to one pilot project with specific constraints. Tracing and examining the flowchart is also considered as part of this validation type. The aim is to assess the reasonability of the model behavior through pre-requisite knowledge. 

Model verification is related to computer programming and looks into whether the code is a correct representation of the conceptual model. To accomplish that, integration tests for each module will be written to assert that the output is as expected. The simulation will also be run several times for the same input data to double check the results. 

Operational validity determines if the model’s output is within the required accuracy. In order to achieve that, several validation techniques are used, namely:

  *	Benchmark testing, through which scenarios are created with different constraints and component combinations, and the output is calculated and compared to the expected one;
  
  *	Extreme scenarios (e.g., drastic meteorological conditions), created to make sure the simulation is through, then evaluate the output behavior by the use of graphs and qualitative analysis;
  
  *	Replication of one pilot project, with a validated optimization model with different component representation to compare and assess the results; and
  
  *	Sensitivity analysis, through which input-output transformations are studied to show the impact of changing the values of some input parameters.
