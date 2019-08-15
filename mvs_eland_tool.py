'''
This is the main file of the tool "Multi-vector simulation tool".

Tool structure:

(parent)    mvs_eland_tool.py
(child)     --A_initialization.py

(child)      --B0_data_input.py

(child)     --C0_data_processing.py
(child sub)    --C1_verification.py
(child sub)    --C2_economic_processing.py

(child)     --D0_modelling_and_optimization.py
(child sub)    --D1_model_components.py
(child sub)    --D2_model_constraints.py

(child)     --E0_output_processing.py
(child sub)    --E1_flow_aggregation.py
(child sub)    --E2_verification_of_constraints.py
(child sub)    --E3_indicator_calculation.py

patent:     Main file, all children connected through parent
child:      Child file, one of the main functions of the tool.
            Internal processes, feeds output back to parent
child-sub:  Sub-child function, feeds only back to child functions
'''

import logging

# Loading all child functions
from A_initialization import initializing
from B0_data_input import data_input
from C0_data_processing import data_processing
from D0_modelling_and_optimization import modelling
import E0_output_processing

# Display welcome text 
version = '0.0.1' #update_me Versioning scheme: Major release.Minor release.Patches
date = '01.08.2019' #update_me Update date

welcome_text = \
    '\n \n Multi-Vector Simulation Tool (MVST)  V' + version + ' ' + \
    '\n Version: ' + date + ' ' + \
    '\n Part of the toolbox of H2020 project "E-LAND", ' + \
    'Integrated multi-vector management system for Energy isLANDs' + \
    '\n Coded at: Reiner Lemoine Institute (Berlin) ' + \
    '\n Contributors: Martha M. Hoffmann \n \n '

logging.debug('Accessing script: A_initialization')
user_input = initializing.welcome(welcome_text)
# Read all inputs
print('')
logging.debug('Accessing script: B0_data_input')
dict_values, included_assets = data_input.all(user_input)
dict_values.update({'user_input': user_input})
print('')
logging.debug('Accessing script: C0_data_processing')
data_processing.all(dict_values)
print('')
logging.debug('Accessing script: D0_modelling_and_optimization')
modelling.run_oemof(dict_values)