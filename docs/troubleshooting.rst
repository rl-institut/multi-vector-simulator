===============
Troubleshooting
===============

Installation
------------

Python package "pygraphviz"
###########################

The installation of pygraphviz can cause errors. 
You can circumvent this issue by setting the *simulation_setting* *plot_nx_graph* to False. 
If you need to plot the network graphs (set parameter *plot_nx_graph* to True), check if we already have a solution for your OS/distribution.

**Ubuntu 18.4**: 
Pygraphviz could not be installed with pip. Solution:

    sudo apt-get install python3-dev graphviz libgraphviz-dev pkg-config
    pip install pygraphviz
    
Python package "xlrd"
#####################

On **Windows** there can be issues installing xlrd. This could solve your troubles:

1. Delete xlrd from requirements.txt
2. Download the xlrd-1.2.0-py2.py3-none-any.whl file from: https://pypi.org/project/xlrd/#files
3. Copy the file to main directory of the project on your laptop
4. Install it manually writing pip install xlrd-1.2.0-py2.py3-none-any.whl

Python package "wkhtmltopdf"
############################

There can be issues installing ´wkhtmltopdf´. Solution can be found on the packages documentation here: https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf

cbc-solver
##########

While with Ubuntu the installation of the cbc solver should work rather well, even when adding it to the environment variables (like described in the installation instructions) can sometimes not work on Windows. This was experienced with Windows 10.

A workaround is to directly put the `cbc.exe` file into the pycharm project, ie. in the same folder where also the CHANGELOG.md is located. Python/Oemof/Pyomo then are able to find the solver.

pyppeteer
##########

If you are using OS X, you might need to install this package separately with conda using:
conda install -c conda-forge pyppeteer 
or
conda install -c conda-forge/label/cf202003 pyppeteer

Error messages and MVS termination
----------------------------------

Even though we try to keep the error messages of the MVS clear and concise, there might be a some that are harder to understand. 
This especially applies to error messages that occur due to the termination of the oemof optimization process.

json.decoder.JSONDecodeError
############################

If the error `json.decoder.JSONDecodeError` is raised, there is a formatting issue with the json file that is used as an input file.

Have you changed the json file manually? Please check for correct formatting, ie. aphostrophes, commas, brackets, and so on.

If you have not changed the Json file yourself please consider raising an issue in the github project.


