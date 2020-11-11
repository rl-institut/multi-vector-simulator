.. _installation-steps:

========================
Getting started with MVS
========================

Rights: `Reiner Lemoine Institut (Berlin) <https://reiner-lemoine-institut.de/en/>`_

The multi-vector simulator (MVS) allows the evaluation of local sector-coupled energy systems that include the energy carriers electricity, heat and/or gas. The MVS has three main features:

Firstly, an analysis of the current energy system, which can be set up automatically from a choice of components, including its costs and performance parameters. As a second step, near-future investments into power generation and storage assets can be optimized aiming at a least-cost supply of electricity and heat. Lastly, future energy supply scenarios that integrate emerging technologies helping to meet sustainability goals and decrease adverse climate effects, e.g. through high renewable energy shares or sector-coupling technologies, can be evaluated.

The tool is being developed within the scope of the H2020 project E-LAND (Integrated multi-vector management system for Energy isLANDs, project homepage `here <https://elandh2020.eu/>`_). A graphical user interface for the MVS will be integrated.

**Latest release**: Check the `latest release <https://github.com/rl-institut/multi-vector-simulator/releases/tag/v0.1.1>`_, and includes the working code of the MVS using json as an input. It is not validated and test coverage is still 0%. Please check the `CHANGELOG.md <https://github.com/rl-institut/multi-vector-simulator/blob/master/CHANGELOG.md>`_ for past updates and changes.

**Upcoming**: As the MVS is still under development, many changes will still occur in the code as well as code structure. If you want to try the MVS, please make sure to check this project regularly.

To set up the MVS, follow the steps below:

* If python3 is not pre-installed: Install miniconda (for python 3.7: https://docs.conda.io/en/latest/miniconda.html)

* Open Anaconda prompt (or other software as Pycharm) to create and activate a virtual environment

    `conda create -n [your_env_name] python=3.6`
    `activate [your env_name]`


* Install the latest [MVS release](https://github.com/rl-institut/multi-vector-simulator/releases)

    `pip install multi-vector-simulator`


* Download the [cbc-solver](https://projects.coin-or.org/Cbc) into your system from https://ampl.com/dl/open/cbc/ and integrate it in your system, ie. unzip, place into chosen path, add path to your system variables  (Windows: “System Properties” -->”Advanced”--> “Environment Variables”, requires admin-rights).

    You can also follow the [steps](https://oemof.readthedocs.io/en/latest/installation_and_setup.html) from the oemof setup instructions


* Test if that the cbc solver is properly installed by typing

    `oemof_installation_test`

    You should at least get a confirmation that the cbc solver is working::

        *****************************
        Solver installed with oemof:

        cbc: working
        glpk: not working
        gurobi: not working
        cplex: not working

        *****************************
        oemof successfully installed.
        *****************************

* Test if the MVS installation was successful by executing

    `mvs_tool`

This should create a folder `MVS_outputs` with the example simulation's results

Using the MVS
-------------

To run the MVS with custom inputs you have several options:


Use the command line
^^^^^^^^^^^^^^^^^^^^

Edit the json input file (or csv files) and run

    `mvs_tool -i path_input_folder -ext json -o path_output_folder`

With
`path_input_folder`: path to folder with input data,

`ext`: json for using a json file and csv for using csv files

and `path_output_folder`: path of the folder where simulation results should be stored.

For more information about the possible command lines options

    `mvs_tool -h`

Use the `main()` function
^^^^^^^^^^^^^^^^^^^^^^^^^

You can also execute the mvs within a script, for this you need to import

`from multi_vector_simulator.cli import main`

The possible arguments to this functions are:
- `overwrite` (bool): Determines whether to replace existing results in `path_output_folder` with the results of the current simulation (True) or not (False) (Command line "-f"). Default: `False`.
- `input_type` (str): Defines whether the input is taken from the `mvs_config.json` file ("json") or from csv files ('csv') located within <path_input_folder>/csv_elements/ (Command line "-ext"). Default: `json`.
- `path_input_folder` (str): The path to the directory where the input CSVs/JSON files are located. Default: `inputs/` (Command line "-i").
- `path_output_folder` (str): The path to the directory where the results of the simulation such as the plots, time series, results JSON files are saved by MVS E-Lands (Command line "-o"). Default: `MVS_outputs/`.
- `display_output` (str): Sets the level of displayed logging messages. Options: "debug", "info", "warning", "error". Default: "info".
- `lp_file_output` (bool): Specifies whether linear equation system generated is saved as lp file. Default: False.
- `pdf_report` (bool): Specify whether pdf report of the simulation's results is generated or not (Command line "-pdf"). Default: False.
- `param save_png` (bool): Specify whether png figures with the simulation's results are generated or not (Command line "-png"). Default: False.


Edit the csv files (or, for devs, the json file) and run the `main()` function. The following `kwargs` are possible:


Default settings
^^^^^^^^^^^^^^^^

If you execute the `mvs_tool` command in a path where there is a folder named `inputs` (you can use the folder
`input_template` for inspiration) this folder will be taken as default input folder and you can simply run

    `mvs_tool`

A default output folder will be created, if you run the same simulation several time you would
 have to either overwrite the existing output file with

    `mvs_tool -f`

Or provide another output folder's path

    `mvs_tool -o <path_to_other_output_folder>`

Generate pdf report or an app in your browser to visualise the results of the simulation
----------------------------------------------------------------------------------------

To use the report feature you need to install extra dependencies first

    `pip install multi-vector-simulator[report]`

Generate a report after running a simulation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the option `-pdf` in the command line  `mvs_tool` to generate a pdf report in the
 simulation's output folder (by default in `MVS_outputs/report/simulation_report.pdf`):

    `mvs_tool -pdf`

Generate only the figures of a simulation's results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the option `-png` in the command line  `mvs_tool` to generate png figures of the results in the
 simulation's output folder (by default in `MVS_outputs/`):

    `mvs_tool -png`


post-processing
^^^^^^^^^^^^^^^
To generate a report of the simulation's results, run the following command **after** a simulation
 generated an output folder:

    `mvs_report -i path_simulation_output_folder -o path_pdf_report`

where `path_simulation_output_folder` should link to the folder of your simulation's output, or directly to a json file (default `MVS_outputs/json_input_processed.json`)
and `path_pdf_report` is the path where the report should be saved as a pdf file.


The report should appear in your browser (at http://127.0.0.1:8050) as an interactive Plotly Dash app.

You can then print the report via your browser print functionality (ctrl+p), however the layout of
 the pdf report is only well optimized for chrome or chromium browser.

It is also possible to automatically save the report as pdf by using the option `-pdf`

    `mvs_report -i path_simulation_output_folder -pdf`

By default, it will save the report in a `report` folder within your simulation's output folder default (`MVS_outputs/report/`).
See `mvs_report.py -h` for more information about possible options. The css and images used to make the report pretty should be located under
`report/assets`.

Contributing and additional information for developers
------------------------------------------------------

If you want to contribute to this project, please read [CONTRIBUTING.md](https://github.com/rl-institut/multi-vector-simulator/blob/dev/CONTRIBUTING.md). For less experienced github users we propose a workflow. [Link](https://github.com/rl-institut/multi-vector-simulator/wiki/Examplary-Workflow).

For advanced programmers: You can also use the dev version that includes the latest updates and changes, but which in turn might not be tested. You can find the CHANGELOG.md on this`page <https://github.com/rl-institut/multi-vector-simulator/blob/dev/CHANGELOG.md>`_.
