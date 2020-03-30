=======================
Simulating with the MVS
=======================

In the MVS can perform a capacity as well as dispatch optimisation of a specific energy system. This means that both the capacity that is to be bought is optimised as well as the respective assets operation. To perform an energy system simulation, a multitude of input parameters needed, which are described in link. They include economic parameters, technological parameters and project settings. Together they define all aspects of the energy system to the simulated and optimised. With this, the MVS builds an energy system model which is translated to an equation system which is to be solved. The MVS tries to minimise the annual costs of demand supply.

In this section, we want to provide you with all information needed to run your own optimisations. First we will explain the two input types, json and csv, and then how to make an energy system model out of your real local energy system configuration.

Input files
-----------

All input files stored in a specifically formatted input folder. The path to the input folder is up to you.

.. image:: images/folder_structure_inputs.png
 :width: 400

There are two options to insert all input data – Json and CSV. These will be explained below.

Json file: mvs_config.json
##########################

In combination especially with the planned graphical user interface for the MVS (EPA), a json file will be used to store and provide all input data necessary to understand relation. The Json file itself is created by the EPA, ie. there are no manual changes. You can use a specific Json input file if you want to test a simulation that has been made public online, one test simulation, or as a developer that has knowingly edited the Json file.

As this requires to adhere to quite specific formatting rules, this can really only be recommended for advanced users.

There can only be a single Json file in your input folder. As some parameters in the Json file link to a time series provided as a CSV, the folder "time_series" should be present in your input folder and provide all necessary input data that is an timeseries format. This can include for example PV generation time series demand time series.

Csv files: csv_elements folder
##############################

Usually user, that is not using the MVS in combination with the EPA, will use CSV input files to define the local energy system, and respectively, the scenario.

Specifically, the MVS will create a Json file ("mvs_csv_config.json") from the provided input data, that works just like above described "mvs_config.json".
For that, each of the following files have to be present in the folder "csv_elements":

- economic_data.csv - Major economic parameters of the project
- energyConsumption.csv - Energy demands and paths to their time series as csv
- energyConversion.csv - Conversion/transformer objects, eg. transformers, generators, heat pumps
- energyProduction.csv - Act as energy "sources", ie. PV or wind plants, with paths to their generation time series as csv
- energyProviders.csv - Specifics of energy providers, ie. DSOs that are connected to the local energy system, including energy prices and feed-in tariffs
- energyStorage.csv - List of energy storages of the energy system
- storage_01.csv - Technical parameters of each energy system
- fixcost.csv - fix project development/maintenance costs (should not be used currently)
- simulation_settings.csv - Simulation settings, including start date and duration
- project_data.csv - some generic project information

When defining your energy system with this CSV files, please also refer to the definition of parameters that you can find here: [stable](https://mvs-eland.readthedocs.io/en/stable/MVS_parameters.html) / [latest](https://mvs-eland.readthedocs.io/en/latest/MVS_parameters.html).

Defining an energy system
-------------------------

Building a model from assets and energy flows
#############################################

Adding a timeseries for a parameter
###################################

Using multiple in- or output busses
###################################
