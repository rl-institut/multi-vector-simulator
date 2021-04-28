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

The Multi-Vector Simulator (hereafter MVS) is an `oemof <https:/github.com/oemof>`__ -based Python package which aims at facilitating the modelling of multi-energy carriers energy systems in island or grid connected mode.

The main goals of the MVS are

#. to minimize the production costs by determining the generating units' optimal output, which meets the total demand

#. to optimize near-future investments in generation and storage assets with the least possible cost of energy.



The MVS graphical model is divided into three connected blocks that trace the logic sequence: inputs, system model, and outputs. This is a typical representation of a simulation model:

.. image:: images/MVS_flowchart.png
 :width: 600

The user is asked to provide the required data via a collection of csv files or a unique json file with particular format. The input data is split into the following categories:

*	**Project description**, which entails the general information regarding the project (country, coordinates, etc.), as well as the economic data such as the discount factor, project duration, or tax

*	**Energy consumption**, which is expressed as times series based on the type of energy (in this case: electrical and thermal)

*	**System configuration**, in which the user specifies the technical and financial data of each asset

*	**Meteorological data**, which is related to the components that generate electricity by harnessing an existing source of energy that is weather- and time-dependent (e.g., solar and wind power)

This set of input data is then translated to a linear programming problem, also known as a constrained optimization problem. The MVS is based on the `oemof-solph <https://github.com/oemof/oemof-solph>`__ python library that describes the problem by specifying an objective function to minimize the annual energy supply costs, the decision variables and the bounds and constraints.

The simulation outputs are also separated into categories:

* Economic results used for the financial evaluation, such as the levelized cost of electricity/heat or the net present value of the projected investments
* Technical results that include the optimized capacities and dispatch of each asset
* Environmental results assessing the system’s environmental contribution in terms of CO2 emissions.

Additionally, different vizualizations of the results can be provided, eg. as pie charts, plots of asset dispatch and an automatic summary report.


Maintainers
===========

The multi-vector simulator is currently maintained by staff from `Reiner Lemoine Institute <https://reiner-lemoine-institut.de/>`__.

The MVS is developed as a work package in the European Union’s Horizon 2020 Research `E-Land project <https://elandh2020.eu/>`__
:Acknowledgement: This project has received funding from the European Union’s Horizon 2020 Research and Innovation programme under Grant Agreement No 824388. 
:Disclaimer: The information and views set out in this poster are those of the author(s) and do not necessarily reflect the official opinion of the European Union. Neither the European Union institutions and bodies nor any person acting on their behalf may be held responsible for the use which may be made of the information contained herein

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
