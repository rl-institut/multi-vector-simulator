import json
import logging
from oemof.tools import logger
from multi_vector_simulator.cli import main

logger.define_logging(
    logpath=".",
    logfile="log",
    file_level=logging.DEBUG,
    screen_level="DEBUG",
)

from multi_vector_simulator.utils.constants_json_strings import KPI, KPI_COST_MATRIX, KPI_SCALAR_MATRIX

from multi_vector_simulator.utils import (
    get_nested_value,
    set_nested_value,
    split_nested_path,
)
from multi_vector_simulator.server import run_simulation
from multi_vector_simulator.B0_data_input_json import (
    load_json,
    convert_from_json_to_special_types,
)


def single_param_variation_analysis(
    param_values, json_input, json_path_to_param_value, json_path_to_output_value=None
):
    r"""Run mvs simulations by varying one of the input parameters to access output's sensitivity

    Parameters
    ----------
    param_values: list of values (type can vary)
    json_input: path or dict
        input parameters for the multi-vector simulation
    json_path_to_param_value: tuple or str
        succession of keys which lead the value of the parameter to vary in the json_input dict
        potentially nested structure. The order of keys is to be read from left to right. In the
        case of str, each key should be separated by a `.` or a `,`.
    json_path_to_output_value: tuple of tuple or str, optional
        collection of succession of keys which lead the value of an output parameter of interest in
        the json dict of the simulation's output. The order of keys is to be read from left to
        right. In the case of str, each key should be separated by a `.` or a `,`.

    Returns
    -------
    The simulation output json matched to the list of variied parameter values
    """

    # Process the argument json_input based on its type
    if isinstance(json_input, str):
        # load the file if it is a path
        simulation_input = load_json(json_input)
    elif isinstance(json_input, dict):
        # this is already a json variable
        simulation_input = json_input
    else:
        simulation_input = None
        logging.error(
            f"Simulation input `{json_input}` is neither a file path, nor a json dict. "
            f"It can therefore not be processed."
        )
    param_path_tuple = split_nested_path(json_path_to_param_value)
    answer = []
    if simulation_input is not None:
        for param_val in param_values:
            # modify the value of the parameter before running a new simulation
            modified_input = set_nested_value(
                simulation_input, param_val, param_path_tuple
            )
            # run a simulation with next value of the variable parameter and convert the result to
            # mvs special json type
            #try:

            sim_output_json = run_simulation(
                    modified_input, display_output="error", epa_format=False
                )

            if json_path_to_output_value is None:
                answer.append(sim_output_json)
            else:
                output_parameters = {}
                # for each of the output parameter path, add the value located under this path in
                # the final json dict, that could also be applied to the full json dict as
                # post-processing
                for output_param in json_path_to_output_value:
                    # For KPI_COST_MATRIX and KPI_SCALAR_MATRIX items of a pd.DataFrame need to be accessed
                    if KPI_COST_MATRIX in output_param or KPI_SCALAR_MATRIX in output_param:
                        # Get corresponding matrix
                        matrix = sim_output_json[output_param[0]][output_param[1]]
                        # Only get row with relevant asset
                        matrix = matrix[(matrix == output_param[3]).any(axis=1)]
                        # Make sure there is only one asset with string output_param[3]
                        if len(matrix.index) > 1:
                            logging.warning(f"The matrix with asset {output_param[3]} has multiple rows: {matrix}")
                        # Get parameter value for the asset from the matrix
                        output_parameters[output_param] = matrix[output_param[2]]

                    # For others, the output can be identified following the json structure.
                    else:
                        output_param = split_nested_path(output_param)
                        output_parameters[output_param] = get_nested_value(
                            sim_output_json, output_param
                    )
                answer.append(output_parameters)
            #except:
            #    logging.warning(f"The sensitivity did not work.")
            #    answer.append(None)
    print({"parameters": param_values, "outputs": answer})
    return {"parameters": param_values, "outputs": answer}
