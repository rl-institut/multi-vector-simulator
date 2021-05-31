=================
About the Project
=================

H2020 Project E-Land
--------------------




Flowchart
---------
 

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
The simulation is executed by uploading the simulation files (by clicking the 'Browse' button) and then hitting the 'Run simulation' button. One can also visualize the log messages (error/warning) during the simulation.

The code for the implementation of the MVS E-Land API is hosted in this `github repository <https://github.com/rl-institut/mvs_eland_api>`__.
