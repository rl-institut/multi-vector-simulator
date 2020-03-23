===============
Troubleshooting
===============

Installation
------------

Python package pygraphviz
#########################

The installation of pygraphviz can cause errors. 
You can circumvent this issue by setting the *simulation_setting* *plot_nx_graph* to False. 
If you need to plot the network graphs (set parameter *plot_nx_graph* to True), check if we already have a solution for your OS/distribution.

**Ubuntu 18.4**: 
Pygraphviz could not be installed with pip. Solution:

    sudo apt-get install python3-dev graphviz libgraphviz-dev pkg-config
    pip install pygraphviz


Error messages and MVS termination
----------------------------------

Eventhough we try to keep the error messages of the MVS clear and concise, there might be a some that are harder to understand. 
This especially applies to error messages that occur due to the termination of the oemof optimization process.


