"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""

import os
from multi_vector_simulator.utils import analysis

from _constants import TEST_REPO_PATH


if __name__ == "__main__":
    print(
        analysis.single_param_variation_analysis(
            [1, 2, 3],
            os.path.join(
                TEST_REPO_PATH, "benchmark_test_inputs", "rerun", "mvs_config.json"
            ),
            ("simulation_settings", "evaluated_period", "value"),
            json_path_to_output_value=(
                ("kpi", "KPI individual sectors", "Renewable factor", "Electricity"),

            ),
        )
    )
