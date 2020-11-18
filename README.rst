# MVS - Multi-Vector Simulator of the E-Land toolbox

[![Documentation Status](https://readthedocs.org/projects/multi-vector-simulator/badge/?version=latest)](https://multi-vector-simulator.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/rl-institut/mvs_eland.svg?branch=dev)](https://travis-ci.com/rl-institut/mvs_eland)
[![Coverage Status](https://coveralls.io/repos/github/rl-institut/multi-vector-simulator/badge.svg)](https://coveralls.io/github/rl-institut/multi-vector-simulator)

Rights: [Reiner Lemoine Institut (Berlin)](https://reiner-lemoine-institut.de/)

The multi-vector simulator (MVS) allows the evaluation of local sector-coupled energy systems that include the energy carriers electricity, heat and/or gas. The MVS has three main features:

- Analysis of an energy system model, which can be defined from csv or json files, including its
 costs and performance parameters.
 - Near-future investments into power generation and storage assets can be optimized aiming at
  least-cost supply of electricity and heat.
 - Future energy supply scenarios that integrate emerging technologies helping to meet sustainability goals and decrease adverse climate effects can be evaluated, e.g. through high renewable energy shares or sector-coupling technologies.

The tool is being developed within the scope of the H2020 project E-LAND (Integrated multi-vector management system for Energy isLANDs, project homepage [HERE](https://elandh2020.eu/)). A graphical user interface for the MVS will be integrated.

*Latest release*
Check the [latest release](https://github.com/rl-institut/multi-vector-simulator/releases/latest). Please check the [CHANGELOG.md](https://github.com/rl-institut/multi-vector-simulator/blob/master/CHANGELOG.md) for past updates and changes.

*Disclaimer*
As the MVS is still under development, changes might still occur in the code as well as code
 structure. If you want to try the MVS, please make sure to check this project regularly.

For advanced programmers: You can also use the `dev` branch that includes the latest updates and
 changes. You find the changelog [HERE](https://github.com/rl-institut/multi-vector-simulator/blob/dev/CHANGELOG.md).

# Getting started

If you are interested to try out the code, please feel free to do so! In case that you are planning to use it for a specific or a larger-scale project, we would be very happy if you would get in contact with us, eg. via issue. Maybe you have ideas that can help the MVS move forward? Maybe you noticed a bug that we can resolve?

We are still working on including a readthedocs for the MVS. Some information on this tool and code is already available [here](https://multi-vector-simulator.readthedocs.io/en/stable/) (stable version, latest developments [here](https://multi-vector-simulator.readthedocs.io/en/latest/)).

## Setup and installation

.. include:: docs/Installation.rst

## Contributing

If you want to contribute to this project, please read [CONTRIBUTING.md](https://github.com/rl-institut/multi-vector-simulator/blob/dev/CONTRIBUTING.md). For less experienced github users we propose a workflow [HERE](https://github.com/rl-institut/multi-vector-simulator/wiki/Examplary-Workflow).
