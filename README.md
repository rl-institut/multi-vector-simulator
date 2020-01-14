# MVS - Multi-Vector Simulator of the E-Land toolbox
Rights: [Reiner Lemoine Institut (Berlin)](https://reiner-lemoine-institut.de/)

The multi-vector simulator (MVS) allows the evaluation of local sector-coupled energy systems that include the energy carriers electricity, heat and/or gas. The MVS has three main features:

Firstly, an analysis of the current energy system, which can be set up automatically from a choice of components, including its costs and performance parameters. As a second step, near-future investments into power generation and storage assets can be optimized aiming at least-cost supply of electricity and heat. Lastly, future energy supply scenarios that integrate emerging technologies helping to meet sustainability goals and decrease adverse climate effects, e.g. through high renewable energy shares or sector-coupling technologies, can be evaluated.

The tool is being developed within the scope of the H2020 project E-LAND (Integrated multi-vector management system for Energy isLANDs, project homepage [HERE](https://elandh2020.eu/)). A graphical user interface for the MVS will be integrated.

*Latest release*
The latest release is [v.0.0.2](https://github.com/smartie2076/mvs_eland/releases), and includes the working code of the MVS using json as an input. It is not validated and test coverage is still 0%. Please check the [CHANGELOG.md](https://github.com/smartie2076/mvs_eland/blob/master/CHANGELOG.md) for past updates and changes.

*Upcoming*
As the MVS is still under development, many changes will still occur in the code as well as code structure. If you want to try the MVS, please make sure to check this project regularly. A new release is planned for end of January ([Issue](https://github.com/smartie2076/mvs_eland/issues/51), [Milestone](https://github.com/smartie2076/mvs_eland/milestone/1)). 

For advanced programmers: You can also use the dev version that includes the latest updates and changes, but which in turn might not be tested. You find the changelog [HERE](https://github.com/smartie2076/mvs_eland/blob/dev/CHANGELOG.md).

# Getting started

If you are interested to try out the code, please feel free to do so! In case that you are planning to use it for a specific or a larger-scale project, we would be very happy if you would get in contact with us, eg. via issue. Maybe you have ideas that can help the MVS move forward? Maybe you noticed a bug that we can resolve?

We are still working on including a readthedocs for the MVS. You will be able to find further information on this tool and code [HERE](https://readthedocs.org/projects/mvs-eland/).

## Setup and installation

To set up the MVS, follow the steps below:

* If python3 is not pre-installed: Install miniconda (for python 3.7: https://docs.conda.io/en/latest/miniconda.html)

* Clone or download the latest [MVS release](https://github.com/smartie2076/mvs_eland/releases)

    `git clone https://github.com/smartie2076/mvs_eland.git`

    and move to the `mvs_eland` folder

* Open Anaconda prompt (or other software as Pycharm) to create and activate a virtual environment

    `conda create -n [your_env_name] python=3.5`
    `activate [your env_name]`

* Install required packages from requirements.txt file using pip

    `pip install -r requirements.txt`

* Download the [cbc-solver](https://projects.coin-or.org/Cbc) into your system from https://ampl.com/dl/open/cbc/ and integrate it in your system, ie. unzip, place into chosen path, add path to your system variables  (Windows: “System Properties” -->”Advanced”--> “Environment Variables”, requires admin-rights). 
You can also follow the [steps](https://oemof.readthedocs.io/en/latest/installation_and_setup.html) from the oemof setup instructions

* Test if that the cbc solver is properly installed by typing

    `oemof_installation_test`

    You should at least get a confirmation that the cbc solver is working

    ```
    *****************************
    Solver installed with oemof:

    cbc: working
    glpk: not working
    gurobi: not working
    cplex: not working

    *****************************
    oemof successfully installed.
    *****************************

    ```
    
* Test if the MVS is running by executing

    `python mvs_eland_tool.py`
    
* You can also run all existing tests by executing

    `pip install -r tests/requirements.txt`
    
    `pytest tests/tests.py`
    
## Using the MVS

Use the MVS by editing the json file (also possible by copy&paste in a new folder) and execute:

    `python mvs_eland_tool.py path_input_file path_output_folder`

With *path_input_file*: Path to folder including json 

and *path_output_folder*: Path where simulation results should be stored

## Contributing

If you want to contribute to this project, please read [CONTRIBUTING.md](https://github.com/smartie2076/mvs_eland/blob/dev/CONTRIBUTING.md). For less experienced github users we propose a workflow [HERE](https://github.com/smartie2076/mvs_eland/wiki/Examplary-Workflow).
