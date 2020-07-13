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

import src.A0_initialization as initializing
import src.A1_csv_to_json as load_data_from_csv
import src.B0_data_input_json as data_input
import src.C0_data_processing as data_processing
import src.D0_modelling_and_optimization as modelling
import src.E0_evaluation as evaluation
import src.F0_output as output_processing
from mvs_eland_tool.version import version_num, version_date
from src.constants import (
    CSV_ELEMENTS,
    CSV_EXT,
    PATH_INPUT_FILE,
    PATH_INPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
    INPUT_TYPE,
)


def main(**kwargs):
    # Display welcome text
    r"""
    Starts MVS tool simulations.

    Other Parameters
    ----------------
    overwrite : bool, optional
        Determines whether to replace existing results in `path_output_folder`
        with the results of the current simulation (True) or not (False).
        Default: False.
    pdf_report: bool, optional
        Can generate an automatic pdf report of the simulation's results (True) or not (False)
        Default: False.
    input_type : str, optional
        Defines whether the input is taken from the `mvs_config.json` file
        ("json") or from csv files ('csv') located within
        <path_input_folder>/csv_elements/. Default: 'json'.
    path_input_folder : str, optional
        The path to the directory where the input CSVs/JSON files are located.
        Default: 'inputs/'.
    path_output_folder : str, optional
        The path to the directory where the results of the simulation such as
        the plots, time series, results JSON files are saved by MVS E-Lands.
        Default: 'MVS_outputs/'
    display_output : str, optional
        Sets the level of displayed logging messages.
        Options: "debug", "info", "warning", "error". Default: "info".
    lp_file_output : bool, optional
        Specifies whether linear equation system generated is saved as lp file.
        Default: False.

    """

    welcome_text = (
        "\n \n Multi-Vector Simulation Tool (MVS) V"
        + version_num
        + " "
        + "\n Version: "
        + version_date
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
    #    dict_values = data_input.load_json(user_input[PATH_INPUT_FILE ])

    move_copy_config_file = False

    if user_input[INPUT_TYPE] == CSV_EXT:
        logging.debug("Accessing script: A1_csv_to_json")
        move_copy_config_file = True
        load_data_from_csv.create_input_json(
            input_directory=os.path.join(user_input[PATH_INPUT_FOLDER], CSV_ELEMENTS)
        )

    logging.debug("Accessing script: B0_data_input_json")
    dict_values = data_input.load_json(
        user_input[PATH_INPUT_FILE],
        path_input_folder=user_input[PATH_INPUT_FOLDER],
        path_output_folder=user_input[PATH_OUTPUT_FOLDER],
        move_copy=move_copy_config_file,
    )

    print("")
    logging.debug("Accessing script: C0_data_processing")
    data_processing.all(dict_values)

    print("")
    logging.debug("Accessing script: D0_modelling_and_optimization")
    results_meta, results_main = modelling.run_oemof(dict_values)
    """
    if dict_values['simulation_settings']['restore_from_oemof_file'] is True:
        if os.path.isfile(dict_values['simulation_settings']['path_output_folder'] + '/' + "oemof_simulation_results.oemof)is False:
            print('')
            logging.debug('Accessing script: D0_modelling_and_optimization')
            results_meta, results_main = modelling.run_oemof(dict_values)
        else:
            logging.debug('Restore the energy system and the results.')
            import oemof.solph as solph
            model = solph.EnergySystem()
            model.restore(dpath=dict_values['simulation_settings']['path_output_folder'],
                                  filename="oemof_simulation_results.oemof"])
            results_main = model.results['main']
            results_meta = model.results['meta']

    # """
    print("")
    logging.debug("Accessing script: E0_evaluation")
    evaluation.evaluate_dict(dict_values, results_main, results_meta)

    logging.debug("Accessing script: F0_outputs")
    output_processing.evaluate_dict(
        dict_values, path_pdf_report=user_input.get("path_pdf_report", None)
    )
    return 1


if __name__ == "__main__":
    main()
