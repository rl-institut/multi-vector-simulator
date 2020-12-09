=================
About the Project
=================

H2020 Project E-Land
--------------------

License
-------

The MVS is licensed with the **GNU General Public License v2.0**. The GNU GPL is the most widely used free software license and has a strong copyleft requirement. When distributing derived works, the source code of the work must be made available under the same license. There are multiple variants of the GNU GPL, each with different requirements.

.. _Flowchart:

Flowchart
---------
 
The MVS' global flowchart, or graphical model, is divided into three connected blocks that trace the logic sequence: inputs, system model, and outputs. This is a typical representation of a simulation model.

.. image:: images/MVS_flowchart.png
 :width: 600

The user is asked to enter the required data through a web interface. In developer mode, the data is submitted as a number of csv files. This input data is split into  four categories:

1.	Project description, which entails the general information regarding the project (country, coordinates, etc.), as well as the economic data such as the discount factor, project duration, or tax;

2.	Energy consumption, which is expressed as times series based on the type of energy (in this case: electrical and therma);

3.	System configuration, in which the user specifies the technical and financial data of each asset; and

4.	Meteorological data, which is related to the components that generate electricity by harnessing an existing source of energy that is weather- and time-dependent (e.g., solar and wind power).

This set of input data is then translated to a linear programming problem, also known as a constrained optimization problem. The MVS is based on the oemof-solph python library that describes the problem by specifying the objective function, the decision variables and the bounds and constraints. The goal is to (1) minimize the production costs by determining the generating units' optimal output, which meets the total demand, and (2) optimize near-future investments in generation and storage assets with the least possible cost of energy.
The simulation outputs are also separated into categories: the economic results used for the financial evaluation, such as the levelized cost of electricity or heat or the net present value of the projected investments, the technical results that include the optimized capacities and dispatch of each asset for instance, and the system’s environmental contribution in terms of CO2 emissions. All these results are valuable for the decision making.

.. _validation-plan:

MVS Validation Plan
-------------------

The adopted validation plan is part of the MVS’ entire development process and is based on three main validation types: conceptual model validation, model verification and operational validity. Following some in-depth research, a validation approach is chosen for the MVS, through which the most appropriate validation techniques are applied to the MVS so that it gains the necessary credibility.

The validation techniques used are listed here below and expanded in :ref:`validation-methodology`:

* Face validity

* Static testing

* Graphical displays

* Benchmark tests

* Extreme input parameters

* Sensitivity analysis

* Comparison to other model


Access MVS Server API
---------------------

The Multi-Vector Simulator can be used to simulate energy systems via the browser using the `API on the RLI server <https://mvs-eland.rl-institut.de/>`__. It processes the parsed JSON input file, and returns the JSON result file.
It is as simple as uploading the simulation files (by clicking the 'Browse' button) and then hitting the 'Run simulation' button. One can also visualize the log messages (error/warning) during the simulation.

The code for the implementation of the MVS E-Land API is hosted in this `github repository <https://github.com/rl-institut/mvs_eland_api>`__.
