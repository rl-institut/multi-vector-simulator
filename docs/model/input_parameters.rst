================
Input parameters
================


************************************
Parameters in each category/CSV file
************************************

Important note: Each asset and bus needs to have an unique label.
In the `csv` input files, these are defined by the column headers.
The input parameters are gathered under the following categories. These categories reflect the structure of the `csv` input files or the firsts keys of the `json` input file.

.. This file is generated automatically when conf.py is executed (function generate_parameter_categories)

.. include:: parameters/MVS_parameters_categories.inc


******************
List of parameters
******************

Below is the list of all the parameters of MVS, sorted in alphabetical order. Each parameter is provided with the definition, unit, type and example values as well to make it easy for users to provide custom values for their systems.

Each of the parameters has the following properties

:Definition: parameter's definition, could also contain potential use cases of the parameter
:Type: str (text), numeric (integer or double precision number), boolean (True or False)
:Unit: physical unit
:Example: an example of parameter's value
:Restrictions: specific restrictions on the parameter's value (e.g., "positive integer number", "must be an even number", "must be one of ['val1', 'val2']"
:Default: default parameter's value

.. This file is generated automatically when conf.py is executed (function generate_parameter_description)

.. include:: parameters/MVS_parameters_list.inc


*******************
Table of parameters
*******************

.. This file is generated automatically when conf.py is executed (function generate_parameter_table)

.. csv-table:: Parameters summary
   :file: parameters/MVS_parameters_list.tbl
   :header-rows: 1