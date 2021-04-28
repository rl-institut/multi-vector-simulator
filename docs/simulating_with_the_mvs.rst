=======================
Simulating with the MVS
=======================

The MVS can perform capacity as well as dispatch optimisations of a specific energy system.
This means that both the extra capacity that is to be bought is optimised as well as the respective asset's operation.
To perform an energy system simulation, a multitude of input parameters is needed. They are described in details in the :ref:`input parameters <input_parameters>` section.
They include economic parameters, technological parameters and project settings.
Together they define all aspects of the energy system to be simulated and optimised.
With these parameters, the MVS builds an energy system model which is translated to a system of linear equations. The MVS tries to find an optimal solution which minimizes the annual costs of demand supply.

In this section, we want to provide you with all information needed to design your own energy system and run your own optimisations.
First we will explain the two possible ways to provide the input parameters to the MVS. Then how to draft an energy system model out of a real local energy system configuration.

.. TODO: provide the example

Input files
-----------

All input files need to be within a folder with the following structure.

| input_folder
|     ├── csv_elements
|             ├── constraints.csv
|             ├── economic_data.csv
|             ├── energyBusses.csv
|             ├── energyConsumption.csv
|             ├── energyConversion.csv
|             ├── energyProduction.csv
|             ├── energyProviders.csv
|             ├── energyStorage.csv
|             ├── fixcost.csv
|             ├── project_data.csv
|             ├── simulation_settings.csv
|             └── storage_01.csv
|     ├── time_series
|            └── blank
|     └── mvs_config.json


The name and location of the :code:`input_folder` is up to the user. The underlying structure and file names within this folder should not be altered.

There are two allowed formats to provide input data to the MVS: Json or CSV (comma separated values).

For the Json format, only the :code:`file mvs_config.json` is required, whereas for the CSV format only the folder :code:`csv_elements` is required.
The folder :code:`time_series` is always required, it should contain the timeseries for energy demand or production.

The CSV format is more user-friendly to design a local energy system model and the Json format is more compact (the whole model is contained in only one file)

Csv files: csv_elements folder
##############################

To use the CSV format, each of the following files have to be present in the folder :code:`csv_elements`.

Files containting enumeration of energy system's assets (or components):

- `energyConsumption.csv  <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/energyConsumption.csv>`__ - Energy demands and paths to their time series as csv
- `energyConversion.csv <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/energyConversion.csv>`__ - Conversion/transformer objects, eg. transformers, generators, heat pumps
- `energyProduction.csv <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/energyProduction.csv>`__ - Act as energy "sources", ie. PV or wind plants, with paths to their generation time series as csv
- `energyProviders.csv <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/energyProviders.csv>`__ - Specifics of energy providers, ie. DSOs that are connected to the local energy system, including energy prices and feed-in tariffs
- `energyStorage.csv <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/energyStorage.csv>`__ - List of energy storages of the energy system
- `storage_01.csv <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/storage_01.csv>`__ - Technical parameters of each energy system
- `energyBusses.csv  <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/energyBusses.csv>`__ - Energy busses of the energy system to be simulated

Files containing enumeration of energy system's global parameters:

- `fixcost.csv <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/fixcost.csv>`__ - fix project development/maintenance costs (should not be used currently)
- `simulation_settings.csv <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/simulation_settings.csv>`__ - Simulation settings, including start date and duration
- `project_data.csv <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/project_data.csv>`__ - some generic project information
- `constraints.csv <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/constraints.csv>`__ - Constraints on the energy system
- `economic_data.csv <https://github.com/rl-institut/multi-vector-simulator/blob/dev/input_template/csv_elements/economic_data.csv>`__ - Major economic parameters of the project

The detailed description of the content of those files is available in the :ref:`input parameters <input_csv_categories>` section. Moreover, an input folder template is available `here <https://github.com/rl-institut/multi-vector-simulator/tree/dev/input_template>`__.

You can conveniently create a copy of this folder in your local path with the command (after having followed :ref:`the installation steps<installation-steps>`)
.. code::

    mvs_create_input_template

A simple example system is setup with this `input folder <https://github.com/rl-institut/multi-vector-simulator/tree/dev/tests/inputs>`__.

.. note::
    Currently only one of :code:`,`, :code:`;` or :code:`&` is allowed as value separation for the CSV files (each file should make a coherent use of a unique separator, otherwise leading to parsing problems).

    *For developpers*: the allowed separators for csv files are located in :code:`src/constants.py` under the :code:`CSV_SEPARATORS` variable.

.. note::
    The name (or label) of each assets needs to be unique and used coherently across the various csv files.

.. note::
    If the user used the CSV format to simulate a local energy system, the MVS will automatically create a Json file (:code:`mvs_csv_config.json`) from the provided input data.
    The user could rename this file :code:`mvs_config.json` and use it as input for the simulation.

Json file: mvs_config.json
##########################

The structure of the Json file matches the one described by the :code:`csv_elements` folder. The Json format is intended for easier exchange: via http requests for online services such as EPA for example

Use of Json file is recommended for advanced users only.

There can only be a single Json file in your input folder and it must be named :code:`mvs_config.json`.

An example of a Json file structure is available from the `default scenario <https://github.com/rl-institut/blob/dev/tests/inputs/mvs_config.json>`__ of the MVS


.. _time_series_folder:

Time series: time_series folder
###############################
Some parameters value in the CSV/Json files are filenames. Those filenames correspond to files which must be present in the folder :code:`time_series` in your input folder, formatted as CSV.
As an example, if one asset listed in :ref:`energy production <production>` has :code:`generation_pv.csv` as value for the :ref:`file_name <filename-label>`. The file :code:`generation_pv.csv` containing a value of the pv generation for each timestep of the simulation should be present in the :code:`time_series` folder.

.. note::
    The time series describing a non-dispatchable demand or when a time series defines an otherwise scalar value of a parameter (eg. energy price), the time series can have any absolute values.

.. note::
    For non-dispatchable sources, eg. the generation of a PV plant, you need to provide a specific time series (unit: kWh/kWp, etc.). For the latter, make sure that its values are between zero and one ([0, 1]).

Defining an energy system
-------------------------

To define your energy system you have to fill out the CSV sheets that are provided in the folder :code:`csv_elements`.
For each asset you want to add, you have to add a new column to a file.
If you do not have an asset of a specific type,
simply leave the columns empty (but leave the columns with the parameter names and units).

The unit columns can indicate you what is the type of the parameter which is required from you (string, boolean, number) if it is not a physical unit.
In case of doubts, also consider having a look in the :ref:`parameter list <input_list_parameters>`.

.. warning::
    Do not delete any of the rows of the CSV´s – each parameter is needed for the simulation.
    There will also be warnings if a parameters is missing or misspelled.

Example of simple energy systems
################################

Please refer to the :ref:`Examples <benchmarks_examples>` section


Building a model from assets and energy flows
#############################################

Simulating an energy system with the MVS requires a certain level of abstraction.
In general, as it is based on the programming framework oemof,
it will depict the energy system only as linearized model.
This allows for the quick computation of the optimal system sizing and approximate dispatch,
but does not replace operational management.

The level of abstraction and system detail needed for an MVS simulation will be explained based on an exemplary local energy system.
Let's assume that we want to simulate an industrial site with some electrical demand, the grid connection, a battery as well as a PV plant.
A schematic of such a system is shown below.

.. image:: images/energy_system.png
 :width: 200

We can see that we have an electricity bus, to which all other components are connected,
specifically demand external electricity supply and the local assets (battery and PV).
However even though all those components belong to the same sector,
their interconnection with the electricity bus or here the electricity grid could be detailed in the deeper manner.

As such, in reality, the battery may be on an own DC electricity bus,
which is either the separate from or identical to the DC bus of the PV plant.
Both DC busses would have to be interconnected with the main electricity bus (AC) through an inverter,
or in case of bi-directional flow for the battery with an rectifier as well.

Just like so, the DSO could either be only providing electricity also allowing feed in,
or the demand may be split up into multiple demand profiles.
This granularity of information would be something that the MVS model requires to properly depict the system behaviour and resulted optimal capacities and dispatch.
The information fed into the MVS via the CSV's would therefore define following components:

.. image:: images/energy_system_model.png
 :width: 200

Ideally you scratch down the energy system you want to simulate with the above-mentioned granularity
and only using sources, sinks, transformers and buses (meaning the oemof components).
When interconnecting different assets make sure that you use the correct bus name in each of the CSV input files.
The bus names are defined with *input_direction* and *output_direction*.
If you interconnect your assets or buses incorrectly the system will still be built but the simulation terminated.
If you're not sure whether or not you build your system correctly change the parameter *plot_networkx_graph* in the simulation_settings to True.
When executing the simulation, the MVS will now generate a rough graphic visualisation of your energy system.
There, all components and buses should be part of a single system (i.e. linked to each other) - otherwise you misconfigured your energy system.

**You need to be aware that you yourself have to make sure that the units you assign to your assets and energy flows make sense.
The MVS does neither perform a logical check, nor does it transform units, eg. from MWh to kWh.**