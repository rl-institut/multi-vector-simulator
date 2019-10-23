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

(child)     --F0_output.py
(child sub)    --E1_process_results.py
(child sub)    --E2_verification_of_constraints.py
(child sub)    --E3_indicator_calculation.py

patent:     Main file, all children connected through parent
child:      Child file, one of the main functions of the tool.
            Internal processes, feeds output back to parent
child-sub:  Sub-child function, feeds only back to child functions
'''

import logging

# Loading all child functions
try:
    from .code.A_initialization import initializing
    from .code.B0_data_input import data_input
    from .code.C0_data_processing import data_processing
    from .code.D0_modelling_and_optimization import modelling
    from .code.E0_evaluation import evaluation
    from .code.F0_output import output_processing

except ModuleNotFoundError:
    from code.A_initialization import initializing
    from code.B0_data_input import data_input
    from code.C0_data_processing import data_processing
    from code.D0_modelling_and_optimization import modelling
    from code.E0_evaluation import evaluation
    from code.F0_output import output_processing

def main():
    # Display welcome text
    version = '0.0.1' #update_me Versioning scheme: Major release.Minor release.Patches
    date = '19.09.2019' #update_me Update date

    welcome_text = \
        '\n \n Multi-Vector Simulation Tool (MVS) V' + version + ' ' + \
        '\n Version: ' + date + ' ' + \
        '\n Part of the toolbox of H2020 project "E-LAND", ' + \
        'Integrated multi-vector management system for Energy isLANDs' + \
        '\n Coded at: Reiner Lemoine Institute (Berlin) ' + \
        '\n Contributors: Martha M. Hoffmann \n \n '

    logging.debug('Accessing script: A_initialization')
    user_input = initializing.welcome(welcome_text)
    # Read all inputs
    print('')
    import json

    if user_input['input_file_name'][-4:] == "json":
        with open(user_input['path_input_file']) as json_file:
            dict_values = json.load(json_file)

    elif user_input['input_file_name'][-4:] == "xlsx":
        logging.info('Input data has to be red from excel file.')
        logging.debug('Accessing script: B0_data_input')
        dict_values, included_assets = data_input.all(user_input)
        dict_values.update({'user_input': user_input})

    else:
        logging.error("Wrong input file format. Can only be json or xlsx!")

    print('')
    logging.debug('Accessing script: C0_data_processing')
    data_processing.all(dict_values)
    print('')
    logging.debug('Accessing script: D0_modelling_and_optimization')
    results_meta, results_main, dict_model = modelling.run_oemof(dict_values)

    print('')
    logging.debug('Accessing script: E0_evaluation')
    evaluation.evaluate_dict(dict_values, results_main, results_meta, dict_model)

    logging.debug('Accessing script: F0_outputs')
    output_processing.evaluate_dict(dict_values)

    return 1

if __name__=="__main__":
    print('in main')
    main()