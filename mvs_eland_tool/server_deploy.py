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

# Loading all child functions
import src.B0_data_input_json as data_input
import src.C0_data_processing as data_processing
import src.D0_modelling_and_optimization as modelling
import src.E0_evaluation as evaluation
import src.F0_output as output_processing

from mvs_eland_tool import version, version_date


def main(json_dict, **kwargs):
    r"""
    Starts MVS tool simulation from an input json file

    Parameters
   -----------
    json_dict: dict
        json from http request

    Other Parameters
    ----------------
    pdf_report: bool, optional
        Can generate an automatic pdf report of the simulation's results (True) or not (False)
        Default: False.
    display_output : str, optional
        Sets the level of displayed logging messages.
        Options: "debug", "info", "warning", "error". Default: "info".
    lp_file_output : bool, optional
        Specifies whether linear equation system generated is saved as lp file.
        Default: False.
    """

    welcome_text = (
        "\n \n Multi-Vector Simulation Tool (MVS) V"
        + version
        + " "
        + "\n Version: "
        + version_date
        + " "
        + '\n Part of the toolbox of H2020 project "E-LAND", '
        + "Integrated multi-vector management system for Energy isLANDs"
        + "\n Coded at: Reiner Lemoine Institute (Berlin) "
        + "\n Contributors: Martha M. Hoffmann \n \n "
    )

    logging.info(welcome_text)

    logging.debug("Accessing script: B0_data_input_json")
    dict_values = data_input.convert_special_types(json_dict)

    print("")
    logging.debug("Accessing script: C0_data_processing")
    data_processing.all(dict_values)

    print("")
    logging.debug("Accessing script: D0_modelling_and_optimization")
    results_meta, results_main = modelling.run_oemof(dict_values)

    print("")
    logging.debug("Accessing script: E0_evaluation")
    evaluation.evaluate_dict(dict_values, results_main, results_meta)

    logging.debug("Convert results to json")
    json_values = output_processing.store_as_json(dict_values)
    return json_values


if __name__ == "__main__":
    main()
