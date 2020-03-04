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

import src.A0_initialization as initializing
import src.A1_csv_to_json as load_data_from_csv
import src.B0_data_input_json as data_input
import src.C0_data_processing as data_processing
import src.D0_modelling_and_optimization as modelling
import src.E0_evaluation as evaluation
import src.F0_output as output_processing

from src.constants import (
    CSV_ELEMENTS,
    CSV_FNAME
)


def main(**kwargs):
    # Display welcome text
    version = (
        "0.1.1"  # update_me Versioning scheme: Major release.Minor release.Patches
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

    user_input = initializing.process_user_arguments(
        welcome_text=welcome_text, **kwargs
    )

    # Read all inputs
    #    print("")
    #    # todo: is user input completely used?
    #    dict_values = data_input.load_json(user_input["path_input_file"])

    if user_input["input_type"] == "csv":
        logging.debug("Accessing script: A1_csv_to_json")
        load_data_from_csv.create_input_json(
            input_directory=os.path.join(user_input["path_input_folder"],
                                         CSV_ELEMENTS),
            output_filename=CSV_FNAME
        )
        user_input.update({"path_input_file": path_to_json_from_csv})

    logging.debug("Accessing script: B0_data_input_json")
    dict_values = data_input.load_json(
        user_input["path_input_file"],
        path_input_folder=user_input["path_input_folder"],
        path_output_folder=user_input["path_output_folder"],
    )

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

    # """
    print("")
    logging.debug("Accessing script: E0_evaluation")
    evaluation.evaluate_dict(dict_values, results_main, results_meta)

    logging.debug("Accessing script: F0_outputs")
    output_processing.evaluate_dict(dict_values)
    return 1


if __name__ == "__main__":
    main()
