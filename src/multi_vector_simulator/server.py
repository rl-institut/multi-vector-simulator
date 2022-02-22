"""
This is the main file of the tool "Multi-vector simulation tool".

Tool structure:

(parent)    multi_vector_simulator.py

(child)    constants.py

(child)     --A0_initialization.py

(child)      --B0_data_input.py

(child)     --C0_data_processing.py
(child sub)    --C1_verification.py
(child sub)    --C2_economic_processing.py

(child)     --D0_modelling_and_optimization.py
(child sub)    --D1_model_components.py
(child sub)    --D2_model_constraints.py

(child)     --E0_evaluation.py
(child sub)    --E1_process_results.py
(child sub)    --E2_verification_of_constraints.py
(child sub)    --E4_verification.py

(child)    --F0_output.py
(child sub)    --F1_plotting.py
(child sub)    --F2_autoreport.py
patent:     Main file, all children connected through parent
child:      Child file, one of the main functions of the tool.
            Internal processes, feeds output back to parent
child-sub:  Sub-child function, feeds only back to child functions
"""

import logging
import json
import os
import tempfile

from oemof.tools import logger

# Loading all child functions
import multi_vector_simulator.B0_data_input_json as B0
import multi_vector_simulator.C0_data_processing as C0
import multi_vector_simulator.D0_modelling_and_optimization as D0
import multi_vector_simulator.E0_evaluation as E0
import multi_vector_simulator.F0_output as F0
from multi_vector_simulator.version import version_num, version_date
from multi_vector_simulator.utils import (
    data_parser,
    nested_dict_crawler,
    get_nested_value,
)


from multi_vector_simulator.utils.constants_json_strings import (
    SIMULATION_SETTINGS,
    OUTPUT_LP_FILE,
    VALUE,
    UNIT,
)
from multi_vector_simulator.utils.constants import TYPE_STR


def run_simulation(json_dict, epa_format=True, **kwargs):
    r"""
     Starts MVS tool simulation from an input json file

     Parameters
    -----------
     json_dict: dict
         json from http request
     epa_format: bool, optional
         Specifies whether the output is formatted for EPA standards
         Default: True

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
    display_output = kwargs.get("display_output", None)

    if display_output == "debug":
        screen_level = logging.DEBUG
    elif display_output == "info":
        screen_level = logging.INFO
    elif display_output == "warning":
        screen_level = logging.WARNING
    elif display_output == "error":
        screen_level = logging.ERROR
    else:
        screen_level = logging.INFO

    # Define logging settings and path for saving log
    logger.define_logging(screen_level=screen_level)

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
        + "\n Reference: https://zenodo.org/record/4610237 \n \n "
    )

    logging.info(welcome_text)

    logging.debug("Accessing script: B0_data_input_json")
    dict_values = B0.convert_from_json_to_special_types(json_dict)

    # if True will return the lp file's content in dict_values
    lp_file_output = dict_values[SIMULATION_SETTINGS][OUTPUT_LP_FILE][VALUE]
    # to avoid the lp file being saved somewhere on the server
    dict_values[SIMULATION_SETTINGS][OUTPUT_LP_FILE][VALUE] = False

    print("")
    logging.debug("Accessing script: C0_data_processing")
    C0.all(dict_values)

    print("")
    logging.debug("Accessing script: D0_modelling_and_optimization")
    results_meta, results_main, local_energy_system = D0.run_oemof(
        dict_values, return_les=True
    )

    if lp_file_output is True:
        logging.debug("Saving the content of the model's lp file")
        with tempfile.TemporaryDirectory() as tmpdirname:
            local_energy_system.write(
                os.path.join(tmpdirname, "lp_file.lp"),
                io_options={"symbolic_solver_labels": True},
            )
            with open(os.path.join(tmpdirname, "lp_file.lp")) as fp:
                file_content = fp.read()

        dict_values[SIMULATION_SETTINGS][OUTPUT_LP_FILE][VALUE] = file_content
        dict_values[SIMULATION_SETTINGS][OUTPUT_LP_FILE][UNIT] = TYPE_STR

    print("")
    logging.debug("Accessing script: E0_evaluation")
    E0.evaluate_dict(dict_values, results_main, results_meta)

    logging.debug("Convert results to json")

    if epa_format is True:
        epa_dict_values = data_parser.convert_mvs_params_to_epa(dict_values)

        json_values = F0.store_as_json(epa_dict_values)
        answer = json.loads(json_values)

    else:
        answer = dict_values

    return answer


def run_sensitivity_analysis_step(
    json_input, step_idx, output_variables, epa_format=True, **kwargs
):
    r"""
     Starts MVS tool simulation from an input json file

     Parameters
    -----------
    json_input: dict
        json from http request
    step_idx: int
        step of the sensitivity analysis
    output_variables: tuple of str
        collection of output variables names
    epa_format: bool, optional
        Specifies whether the output is formatted for EPA standards
        Default: True

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

    # Process the argument json_input based on its type
    if isinstance(json_input, str):
        # load the file if it is a path
        simulation_input = B0.load_json(json_input)
    elif isinstance(json_input, dict):
        # this is already a json variable
        simulation_input = json_input
    else:
        simulation_input = None
        logging.error(
            f"Simulation input `{json_input}` is neither a file path, nor a json dict. "
            f"It can therefore not be processed."
        )

    sim_output_json = run_simulation(
        simulation_input, display_output="error", epa_format=epa_format
    )
    output_variables_paths = nested_dict_crawler(sim_output_json)

    output_parameters = {}
    # for each of the output parameter path, add the value located under this path in
    # the final json dict, that could also be applied to the full json dict as
    # post-processing
    for output_param in output_variables:
        output_param_pathes = output_variables_paths.get(output_param, [])

        if len(output_param_pathes) == 0:
            output_parameters[output_param] = dict(
                value=None,
                path=f"Not found in mvs results (version {version_num}), check if you have typos in output parameter name",
            )

        for output_param_path in output_param_pathes:
            if output_param not in output_parameters:
                output_parameters[output_param] = dict(
                    value=[get_nested_value(sim_output_json, output_param_path)],
                    path=[".".join(output_param_path)],
                )
            else:
                output_parameters[output_param]["value"].append(
                    get_nested_value(sim_output_json, output_param_path)
                )
                output_parameters[output_param]["path"].append(
                    ".".join(output_param_path)
                )

    return {"step_idx": step_idx, "output_values": output_parameters}
