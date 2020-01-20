"""
This is the main file of the tool "Multi-vector simulation tool".

Tool structure:

(parent)    mvs_eland_tool.py
(child)     --A0_initialization.py

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
"""

import logging
import os

# Loading all child functions
try:
    # for tests
    from .code_folder.A0_initialization import initializing
    from .code_folder.A1_csv_to_json import DataInputFromCsv

    #    from .code_folder.B0_data_input_json import data_input
    from .code_folder.C0_data_processing import data_processing
    from .code_folder.D0_modelling_and_optimization import modelling
    from .code_folder.E0_evaluation import evaluation
    from .code_folder.F0_output import output_processing

except ModuleNotFoundError:
    # for terminal execution
    from code_folder.A0_initialization import initializing
    from code_folder.A1_csv_to_json import DataInputFromCsv

    #    from code_folder.B0_data_input_json import data_input
    from code_folder.C0_data_processing import data_processing
    from code_folder.D0_modelling_and_optimization import modelling
    from code_folder.E0_evaluation import evaluation
    from code_folder.F0_output import output_processing


def main(**kwargs):
    # Display welcome text
    version = (
        "0.0.2"  # update_me Versioning scheme: Major release.Minor release.Patches
    )
    date = "25.11.2019"  # update_me Update date

    welcome_text = (
        "\n \n Multi-Vector Simulation Tool (MVS) V"
        + version
        + " "
        + "\n Version: "
        + date
        + " "
        + '\n Part of the toolbox of H2020 project "E-LAND", '
        + "Integrated multi-vector management system for Energy isLANDs"
        + "\n Coded at: Reiner Lemoine Institute (Berlin) "
        + "\n Contributors: Martha M. Hoffmann \n \n "
    )

    logging.debug("Accessing script: A0_initialization")
    user_input = initializing.welcome(welcome_text, **kwargs)

    # Read all inputs
    #    print("")
    #    # todo: is user input completely used?
    #    dict_values = data_input.get(user_input)

    logging.debug("Accessing script: A1_csv_to_json")
    dict_values = DataInputFromCsv.create_input_json()

    print("")
    logging.debug("Accessing script: C0_data_processing")
    data_processing.all(dict_values)

    print("")
    logging.debug("Accessing script: D0_modelling_and_optimization")
    results_meta, results_main = modelling.run_oemof(dict_values)
    """
    if dict_values['simulation_settings']['restore_from_oemof_file'] == True:
        if os.path.isfile(dict_values['simulation_settings']['path_output_folder'] + '/' + dict_values['simulation_settings']['oemof_file_name'])== False:
            print('')
            logging.debug('Accessing script: D0_modelling_and_optimization')
            results_meta, results_main = modelling.run_oemof(dict_values)
        else:
            logging.debug('Restore the energy system and the results.')
            import oemof.solph as solph
            model = solph.EnergySystem()
            model.restore(dpath=dict_values['simulation_settings']['path_output_folder'],
                                  filename=dict_values['simulation_settings']['oemof_file_name'])
            results_main = model.results['main']
            results_meta = model.results['meta']
            
    """
    print("")
    logging.debug("Accessing script: E0_evaluation")
    evaluation.evaluate_dict(dict_values, results_main, results_meta)

    logging.debug("Accessing script: F0_outputs")
    output_processing.evaluate_dict(dict_values)
    return 1


if __name__ == "__main__":
    main()
