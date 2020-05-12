=================
About the Project
=================

H2020 Project E-Land
--------------------

License
-------
The MVS is licensed with the **GNU General Public License v2.0**. The GNU GPL is the most widely used free software license and has a strong copyleft requirement. When distributing derived works, the source code of the work must be made available under the same license. There are multiple variants of the GNU GPL, each with different requirements.

Flowchart
-------
 
The MVS' global flowchart, or graphical model, is divided into three connected blocks that trace the logic sequence: inputs, system model, and outputs. This is a typical representation of a simulation model.

.. image:: images/MVS_flowchart.png
 :width: 200

The user is asked to enter the required data through a web interface. In developer mode, the data is submitted as a number of csv files. This input data is split into  four categories:

1.	Project description, which entails the general information regarding the project (country, coordinates, etc.), as well as the economic data such as the discount factor, project duration, or tax;

2.	Energy consumption, which is expressed as times series based on the type of energy (in this case: electrical and therma);

3.	System configuration, in which the user specifies the technical and financial data of each asset; and

4.	Meteorological data, which is related to the components that generate electricity by harnessing an existing source of energy that is weather- and time-dependent (e.g., solar and wind power).

This set of input data is then translated to a linear programming problem, also known as a constrained optimization problem. The MVS is based on the oemof python library that describes the problem by specifying the objective function, the decision variables and the constraints. The aim is to minimize the production costs by determining the generating units' optimal output, which meets the total demand.
The simulation outputs are also separated into categories. The economic results, such as the levelized cost of electricity or heat or the net present value of the projected investments, are the ones used for financial evaluation and decision making. The technical results also showcase several important values, such as the optimized capacities and dispatch of each asset. Lastly, the system’s environmental contribution is shown through the value of CO2 emissions. 
