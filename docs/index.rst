..
  SPDX-FileCopyrightText: MVS Authors

  SPDX-License-Identifier: CC-BY-4.0

.. _Flowchart:

Multi-vector simulator
======================
.. only:: html

    .. image:: https://readthedocs.org/projects/multi-vector-simulator/badge/?version=latest
        :target: https://multi-vector-simulator.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

    .. image:: https://github.com/rl-institut/multi-vector-simulator/workflows/CI/badge.svg
        :alt: Build status

    .. image:: https://coveralls.io/repos/github/rl-institut/multi-vector-simulator/badge.svg
        :target: https://coveralls.io/github/rl-institut/multi-vector-simulator
        :alt: Test coverage

    .. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4610237.svg
        :target: https://doi.org/10.5281/zenodo.4610237
        :alt: Zenodo DOI

    .. image:: https://img.shields.io/badge/License-GPL%20v2-blue.svg
        :target: https://img.shields.io/badge/License-GPL%20v2-blue.svg
        :alt: License gpl2

    .. image:: https://badge.fury.io/py/multi-vector-simulator.svg
        :target: https://pypi.org/project/multi-vector-simulator/
        :alt: Pypi version

    .. image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :target: https://github.com/psf/black
        :alt: black linter

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

Follow the  :doc:`Quick start guide <Installation>`

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
   :caption: Examples

   examples/time_series_params
   examples/multiple_busses

Model Reference
===============

* **How the energy system is modelled**: :doc:`Assumption behind the model <model/assumptions>` | :doc:`Available components for modelling <model/components>` | :doc:`Setting constraints on model or components <model/constraints>` | :doc:`Scope and limitation of the model <model/limitations>`
* **Description of parameters**: :doc:`Input parameters <model/input_parameters>` | :doc:`Output variables and KPIs <model/simulation_outputs>`
* **Validation of the model**: :doc:`Benchmark tests <model/validation>`

    .. maybe add Pilot projects here as well?

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Model Reference

   model/assumptions
   model/components
   model/constraints
   model/limitations
   model/input_parameters
   model/simulation_outputs
   model/validation
   model/eland_requirements

..
    release_notes (for website, remove for report, not implemented yet, nice to have)
    contributing (here paste content of contributing.md --> convert to RST and include it as we did for readme, the mention to contributing in getting started will link to this chapter)


API Reference
=============

* **Documentation**: :doc:`Modules and functions <references/code>`
* **Getting involved**: :doc:`Contributing guidelines and protocols <references/contributing>`
* **Academic references**: :doc:`Publications <references/publications>` | :doc:`Cite MVS <references/citations>`
* **Using or modifying MVS**: :doc:`License <references/license>` | :doc:`Cite MVS <references/citations>`
* **Getting help**: :doc:`Know issues and workaround <references/troubleshooting>` | :doc:`Report a bug or issue <references/bug_report>`

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: References

   references/code
   references/release_notes
   references/license
   references/contributing
   references/publications
   references/citations
   references/troubleshooting
   references/bug_report


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
