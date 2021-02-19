=======================================
Parameters and Definitions in CSVs/JSON
=======================================

******************
List of parameters
******************

Below is the list of all the parameters of MVS, sorted in alphabetical order. Each parameter is provided with the definition, unit, type and example values as well to make it easy for users to provide custom values for their systems.

.. This file is generated automatically when conf.py is executed

.. include:: MVS_parameters_list.inc


***************************
Parameters in each CSV file
***************************

Important note: Each asset and bus needs to have an unique label.
In the `csv` input files, these are defined by the column heads.

constraints.csv
^^^^^^^^^^^^^^^

The file `constraints.csv` includes the following parameter(s):

* :ref:`minrenshare-label`
* :ref:`maxemissions-label`
* :ref:`minda-label`
* :ref:`nzeconstraint-label`

economic_data.csv
^^^^^^^^^^^^^^^^^

The file `economic_data.csv` includes all economic data that the simulation will use. This includes the following parameters:

* :ref:`currency-label`
* :ref:`projectduration-label`
* :ref:`discountfactor-label`
* :ref:`tax-label`

eneryBusses.csv
^^^^^^^^^^^^^^^

The file `energyBusses.csv` defines all busses required to build the energy system. It includes following parameters:

* :ref:`energyvector-label`

energyConsumption.csv
^^^^^^^^^^^^^^^^^^^^^

The file `energyConsumption.csv` defines all energy demands that should be included in the energy system.
It includes the following parameters:

* :ref:`unit-label`
* :ref:`inflowdirection-label`
* :ref:`energyvector-label`
* :ref:`filename-label`
* :ref:`typeasset-label`
* :ref:`typeoemof-label`
* :ref:`dsm-label`

energyConversion.csv
^^^^^^^^^^^^^^^^^^^^

The file `energyConversion.csv` defines the assets that convert one energy carrier into another one, eg. inverters or generators.
Following parameters define them:

* :ref:`unit-label`
* :ref:`optimizecap-label`
* :ref:`installedcap-label`
* :ref:`age_ins-label`
* :ref:`lifetime-label`
* :ref:`developmentcosts-label`
* :ref:`specificcosts-label`
* :ref:`specificomcosts-label`
* :ref:`dispatchprice-label`
* :ref:`efficiency-label`
* :ref:`inflowdirection-label`
* :ref:`outflowdirec-label`
* :ref:`energyvector-label`
* :ref:`typeoemof-label`

energyProduction.csv
^^^^^^^^^^^^^^^^^^^^

The file `energyProduction.csv` defines the assets that serve as energy sources, eg. fuel sources or PV plants.
 They include the following parameters:

* :ref:`unit-label`
* :ref:`optimizecap-label`
* :ref:`maxcap-label`
* :ref:`installedcap-label`
* :ref:`age_ins-label`
* :ref:`lifetime-label`
* :ref:`developmentcosts-label`
* :ref:`specificcosts-label`
* :ref:`specificomcosts-label`
* :ref:`dispatchprice-label`
* :ref:`outflowdirec-label`
* :ref:`filename-label`
* :ref:`energyvector-label`
* :ref:`renewableasset-label`
* :ref:`emissionfactor-label`
* :ref:`typeoemof-label`

energyProviders.csv
^^^^^^^^^^^^^^^^^^^

The file `energyProviders.csv` defines the energy providers of the energy system. They include the following parameters:

* :ref:`unit-label`
* :ref:`optimizecap-label`
* :ref:`energyprice-label`
* :ref:`feedintariff-label`
* :ref:`peakdemand-label`
* :ref:`peakdemandperiod-label`
* :ref:`renshare-label`
* :ref:`inflowdirection-label`
* :ref:`outflowdirec-label`
* :ref:`energyvector-label`
* :ref:`emissionfactor-label`
* :ref:`typeoemof-label`

energyStorage.csv
^^^^^^^^^^^^^^^^^

The file `energyStorage.csv` defines the storage assets included in the energy system.
It does not hold all needed parameters, but requires `storage_xx.csv` to be defined as well.
The file `energyStorage.csv` includes the following parameters:

* :ref:`optimizecap-label`
* :ref:`inflowdirection-label`
* :ref:`outflowdirec-label`
* :ref:`storagefilename-label`
* :ref:`energyvector-label`
* :ref:`typeoemof-label`

fixcost.csv
^^^^^^^^^^^

The parameters must be filled for all three columns/components namely: *distribution_grid*, *engineering* and *operation*.
The file `fixcost.csv` includes the following parameters:

* :ref:`labl-label`
* :ref:`age_ins-label`
* :ref:`lifetime-label`
* :ref:`developmentcosts-label`
* :ref:`specificcosts-label`
* :ref:`specificomcosts-label`
* :ref:`dispatchprice-label`

project_data.csv
^^^^^^^^^^^^^^^^

The file `project_data.csv` includes the following parameters:

* :ref:`country-label`
* :ref:`latitude-label`
* :ref:`longitude-label`
* :ref:`projectid-label`
* :ref:`projectname-label`
* :ref:`scenarioid-label`
* :ref:`scenarioname-label`
* :ref:`scenariodescription-label`

simulation_settings.csv
^^^^^^^^^^^^^^^^^^^^^^^

The file `simulation_settings.csv` includes the following parameters:

* :ref:`startdate-label`
* :ref:`evaluatedperiod-label`
* :ref:`timestep-label`
* :ref:`outputlpfile-label`

.. _storage_csv:

storage_*.csv
^^^^^^^^^^^^^^

The `*` in the storage filename is the number identifying the storage. It depends on the number of storage components (such as batteries, etc.) present in the system. For e.g., there should be two storage files named storage_01.csv and storage_02.csv if the system contains two storage components.
The file `storage_xx.csv` contains the following parameters:

* :ref:`unit-label`
* :ref:`installedcap-label`
* :ref:`age_ins-label`
* :ref:`lifetime-label`
* :ref:`developmentcosts-label`
* :ref:`specificcosts-label`
* :ref:`specificomcosts-label`
* :ref:`dispatchprice-label`
* :ref:`crate-label`
* :ref:`efficiency-label`
* :ref:`socin-label`
* :ref:`socmax-label`
* :ref:`socmin-label`
