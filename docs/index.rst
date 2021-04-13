..
  SPDX-FileCopyrightText: MVS Authors

  SPDX-License-Identifier: CC-BY-4.0

.. _Flowchart:

Multi-vector simulator
======================

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


Maintainers
===========

Say who develop and maintains this

Say a word about funding

Origin
======

What started MVS

Getting Started
===============

Follow the  :ref:`Quick start guide <installation-steps>`

.. Documentation
.. =============

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Getting Started

   Installation
   simulating_with_the_mvs


.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: References

   references/license
   references/contributing
   references/publications
   references/citations
   references/troubleshooting
   references/bug_report



==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



