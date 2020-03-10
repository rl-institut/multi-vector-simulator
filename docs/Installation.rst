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

    

Additional information for developers
-------------------------------

For advanced programmers: You can also use the dev version that includes the latest updates and changes, but which in turn might not be tested. You can find the CHANGELOG.md `here <https://github.com/rl-institut/mvs_eland/blob/dev/CHANGELOG.md>`_. 

If you want to contribute to this project, please read `CONTRIBUTING.md <https://github.com/rl-institut/mvs_eland/blob/dev/CONTRIBUTING.md>`. 

For less experienced github users we propose a workflow `here <https://github.com/rl-institut/mvs_eland/wiki/Examplary-Workflow>`.


Using MVS
---------

To run the MVS with custom inputs, change the "input" folder without changing the folder structure and execute following command from root of the repository:

    python mvs_tool.py [-h] [-i [PATH_INPUT_FOLDER]] [-ext [{json,csv}]]
                          [-o [PATH_OUTPUT_FOLDER]]
                          [-log [{debug,info,error,warning}]] [-f [OVERWRITE]]

Optional arguments:
  -h, --help            show this help message and exit
  -i [PATH_INPUT_FOLDER]
                        path to the input folder
  -ext [{json,csv}]     type (json or csv) of the input files (default: 'json'
  -o [PATH_OUTPUT_FOLDER]
                        path to the output folder for the simulation's results
  -log [{debug,info,error,warning}]
                        level of logging in the console
  -f [OVERWRITE]        overwrite the output folder if True (default: False)
  
 Ie. if you want to run the MVS with csv input, type
 
         python mvs_tool.py -i path_input_folder -ext json
         
 If you want to run it with json input, type:
 
         python mvs_tool.py -i path_input_folder -ext csv
