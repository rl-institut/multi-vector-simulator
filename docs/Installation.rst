========================
Getting started with MVS
========================

Rights: `Reiner Lemoine Institut (Berlin) <https://reiner-lemoine-institut.de/en/>`_

The multi-vector simulator (MVS) allows the evaluation of local sector-coupled energy systems that include the energy carriers electricity, heat and/or gas. The MVS has three main features:

Firstly, an analysis of the current energy system, which can be set up automatically from a choice of components, including its costs and performance parameters. As a second step, near-future investments into power generation and storage assets can be optimized aiming at a least-cost supply of electricity and heat. Lastly, future energy supply scenarios that integrate emerging technologies helping to meet sustainability goals and decrease adverse climate effects, e.g. through high renewable energy shares or sector-coupling technologies, can be evaluated.

The tool is being developed within the scope of the H2020 project E-LAND (Integrated multi-vector management system for Energy isLANDs, project homepage `here <https://elandh2020.eu/>`_). A graphical user interface for the MVS will be integrated.

**Latest release**: Check the `latest release <https://github.com/rl-institut/mvs_eland/releases/tag/v0.1.1>`_, and includes the working code of the MVS using json as an input. It is not validated and test coverage is still 0%. Please check the `CHANGELOG.md <https://github.com/rl-institut/mvs_eland/blob/master/CHANGELOG.md>`_ for past updates and changes.

**Upcoming**: As the MVS is still under development, many changes will still occur in the code as well as code structure. If you want to try the MVS, please make sure to check this project regularly.

Setup process for users
------------------------

To set up the MVS, please follow the steps below:

1. If python3 is not pre-installed: Install miniconda (click `here <https://docs.conda.io/en/latest/miniconda.html>`_ for python 3.7)

2. Clone or download the latest `MVS release <https://github.com/rl-institut/mvs_eland/releases>`_. Run this command in your Terminal or Command Prompt to clone MVS::

    git clone https://github.com/rl-institut/mvs_eland.git
   and move to the ``mvs_eland`` folder

3. Download the `cbc-solver <https://projects.coin-or.org/Cbc>`_ into your system from `here <https://ampl.com/dl/open/cbc/>` and integrate it in your system, i.e., unzip, place into chosen path, and add path to your system variables (Windows: “System Properties” --> ”Advanced” --> “Environment Variables”, requires admin-rights).

   You can also follow the `steps <https://oemof.readthedocs.io/en/latest/installation_and_setup.html>` from the oemof setup instructions

4. Open Anaconda prompt (or other software as Pycharm) run the following command to create and activate a virtual environment::

    conda create -n [your_env_name] python=3.5 activate [your env_name]
    
4. Install required packages from requirements.txt file using pip::

    pip install -r requirements.txt
    
5. Test if that the cbc solver is properly installed by typing::

    oemof_installation_test
   You should at least get a confirmation as below that the cbc solver is working::
   
    *****************************
    Solver installed with oemof:

    cbc: working
    glpk: not working
    gurobi: not working
    cplex: not working

    *****************************
    oemof successfully installed.
    *****************************
    
6. Install the mvs_eland package locally::

    python setup.py install
    
7. Test if the MVS is running by executing::

    python mvs_tool.py
    
8. You can also run all existing tests by executing::

    pip install -r tests/test_requirements.txt

    pytest

    
Using the MVS
-------------

To run the MVS with custom inputs you have several options:

##### 1) Use the command line

Edit the json input file (or csv files) and run

    `python mvs_tool.py -i path_input_file -ext json -o path_output_folder`

With 
`path_input_file`: path to json input file,

`ext`: json for using a json file and csv for using csv files

and `path_output_folder`: path of the folder where simulation results should be stored.

For more information about the possible command lines

`python mvs_tool.py -h`

##### 2) Use the `main()` function

Edit the csv files (or, for devs, the json file) and run the `main()` function. The following `kwargs` are possible:

- `overwrite` (bool): Determines whether to replace existing results in `path_output_folder` with the results of the current simulation (True) or not (False). Default: `False`.
- `input_type` (str): Defines whether the input is taken from the `mvs_config.json` file ("json") or from csv files ('csv') located within <path_input_folder>/csv_elements/. Default: `json`.
- `path_input_folder` (str): The path to the directory where the input CSVs/JSON files are located. Default: `inputs/`.
- `path_output_folder` (str): The path to the directory where the results of the simulation such as the plots, time series, results JSON files are saved by MVS E-Lands. Default: `MVS_outputs/`.


Contributing and additional information for developers
------------------------------------------------------

If you want to contribute to this project, please read [CONTRIBUTING.md](https://github.com/rl-institut/mvs_eland/blob/dev/CONTRIBUTING.md). For less experienced github users we propose a workflow [HERE](https://github.com/rl-institut/mvs_eland/wiki/Examplary-Workflow).

For advanced programmers: You can also use the dev version that includes the latest updates and changes, but which in turn might not be tested. You can find the CHANGELOG.md `here <https://github.com/rl-institut/mvs_eland/blob/dev/CHANGELOG.md>`_. 
