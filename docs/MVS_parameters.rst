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

constraints.csv
^^^^^^^^^^^^^^^

The file `constraints.csv` includes the following parameter(s):

* :ref:`minrenshare-label`

economic_data.csv
^^^^^^^^^^^^^^^^^

The file `economic_data.csv` includes the following parameters:

* :ref:`labl-label`
* :ref:`currency-label`
* :ref:`projectduration-label`
* :ref:`discountfactor-label`
* :ref:`tax-label`

energyConsumption.csv
^^^^^^^^^^^^^^^^^^^^^

The file `energyConsumption.csv` includes the following parameters:

* :ref:`labl-label`
* :ref:`unit-label`
* :ref:`inflowdirection-label`
* :ref:`energyvector-label`
* :ref:`filename-label`
* :ref:`typeasset-label`
* :ref:`typeoemof-label`
* :ref:`dsm-label`

energyConversion.csv
^^^^^^^^^^^^^^^^^^^^

The file `energyConversion.csv` includes the following parameters:

* :ref:`labl-label`
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

The file `energyProduction.csv` includes the following parameters:

* :ref:`labl-label`
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
* :ref:`typeoemof-label`

energyProviders.csv
^^^^^^^^^^^^^^^^^^^

The file `energyProviders.csv` includes the following parameters:

* :ref:`labl-label`
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
* :ref:`typeoemof-label`

energyStorage.csv
^^^^^^^^^^^^^^^^^

The file `energyStorage.csv` includes the following parameters:

* :ref:`labl-label`
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

* :ref:`labl-label`
* :ref:`country-label`
* :ref:`latitude-label`
* :ref:`longitude-label`
* :ref:`projectid-label`
* :ref:`projectname-label`
* :ref:`scenarioid-label`
* :ref:`scenarioname-label`

simulation_settings.csv
^^^^^^^^^^^^^^^^^^^^^^^

The file `simulation_settings.csv` includes the following parameters:

* :ref:`labl-label`
* :ref:`startdate-label`
* :ref:`evaluatedperiod-label`
* :ref:`timestep-label`
* :ref:`outputlpfile-label`
* :ref:`storeoemoefresults-label`

storage_xx.csv
^^^^^^^^^^^^^^

The "xx" in the storage filename is the number identifying the storage. It depends on the number of storage components (such as batteries, etc.) present in the system. For e.g., there should be two storage files named storage_01.csv and storage_02.csv if the system contains two storage components.
The file `storage_xx.csv` contains the following parameters:

* :ref:`labl-label`
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
