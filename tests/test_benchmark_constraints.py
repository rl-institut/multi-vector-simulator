"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""
import argparse
import os
import shutil

import pytest
import mock

from multi_vector_simulator.cli import main
from multi_vector_simulator.B0_data_input_json import load_json

from _constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    TEST_REPO_PATH,
    CSV_EXT,
)

from multi_vector_simulator.utils.constants import (
    JSON_WITH_RESULTS,
    JSON_FILE_EXTENSION,
)

from multi_vector_simulator.utils.constants_json_strings import (
    VALUE,
    KPI,
    KPI_SCALARS_DICT,
    RENEWABLE_FACTOR,
    CONSTRAINTS,
    MINIMAL_RENEWABLE_FACTOR,
    MAXIMUM_EMISSIONS,
    TOTAL_EMISSIONS,
    SPECIFIC_EMISSIONS_ELEQ,
    UNIT_EMISSIONS,
    UNIT_SPECIFIC_EMISSIONS,
    KPI_SCALAR_MATRIX,
    OPTIMIZED_ADD_CAP,
    LABEL,
    TOTAL_FLOW,
)

TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_inputs")
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_outputs")


class Test_Constraints:
    def setup_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
        if os.path.exists(TEST_OUTPUT_PATH) is False:
            os.mkdir(TEST_OUTPUT_PATH)

    # this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
    # alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_minimal_renewable_share_constraint(self, margs):
        r"""
        Notes
        -----
        With this benchmark test, the minimal renewable factor constraint is validated.
        Constraint_minimal_renewable_share_0 does not have a minimal renewable factor.
        Constraint_minimal_renewable_share_50 has a minimal renewable factor of 70%.
        If the renewable share of Constraint_minimal_renewable_share_0 is lower than 70%,
        but the one of Constraint_minimal_renewable_share_50 is 70%, then the benchmark test passes.
        """

        # define the two cases needed for comparison (no minimal renewable factor) and (minimal renewable factor of 70%)
        use_case = [
            "Constraint_minimal_renewable_share_0",
            "Constraint_minimal_renewable_share_70",
        ]
        # define an empty dictionary for excess electricity
        renewable_shares = {}
        minimal_renewable_shares = {}
        for case in use_case:
            main(
                overwrite=True,
                display_output="warning",
                path_input_folder=os.path.join(TEST_INPUT_PATH, case),
                input_type=CSV_EXT,
                path_output_folder=os.path.join(TEST_OUTPUT_PATH, case),
            )
            data = load_json(
                os.path.join(
                    TEST_OUTPUT_PATH, case, JSON_WITH_RESULTS + JSON_FILE_EXTENSION
                )
            )
            renewable_shares.update(
                {case: data[KPI][KPI_SCALARS_DICT][RENEWABLE_FACTOR]}
            )
            minimal_renewable_shares.update(
                {case: data[CONSTRAINTS][MINIMAL_RENEWABLE_FACTOR][VALUE]}
            )

            assert minimal_renewable_shares[case] < renewable_shares[case] + 10 ** (
                -6
            ), f"The minimal renewable share is not at least as high as the minimal renewable share requires."

        assert (
            renewable_shares[use_case[0]] < minimal_renewable_shares[use_case[1]]
        ), f"The renewable share of the scenario without minimal renewable share constraint is with {renewable_shares[use_case[0]]} higher than the minimal renewable share defined for the scenario with constraint ({minimal_renewable_shares[use_case[1]]}). This test therefore can not validate that the constraint works. To debug, increase the cost of PV."
        assert (
            renewable_shares[use_case[0]] < renewable_shares[use_case[1]]
        ), f"The renewable share of the scenario with the constraint is not higher than the one without, so the test does not make sense."

    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_maximum_emissions_constraint(self, margs):
        r"""
        Tests the maximum emissions constraint in a system with PV, DSO and a diesel generator.
        The şystem defined in `\Constraint_maximum_emissions_None` does not have maximum emissions constraint,
        while the system defined in `\Constraint_maximum_emissions_low` has a low maximum emissions constraint of 800 kgCO2eq/a.
        A third system, `\Constraint_maximum_emissions_low_grid_RE_100`, includes a renewable share in the grid of 100 %.

        The following checks are made:
        - total emissions of energy system <= maximum emissions constraint
            (for Constraint_maximum_emissions_low and Constraint_maximum_emissions_low_grid_RE_100)
        - total emissions of case without constraint > total emissions of case with constraint
        - specific emissions eleq of case without constraint > specific emissions eleq of case with constraint
        - optimized added pv capacity lower for case without constraint than for case with constraint
        - total flow of grid consumption higher for case with 100 % RE share in grid than for case with emissions from grid

        """
        # define the two cases needed for comparison
        use_case = [
            "Constraint_maximum_emissions_None",
            "Constraint_maximum_emissions_low",
            "Constraint_maximum_emissions_low_grid_RE_100",
        ]
        # define an empty dictionary for excess electricity
        total_emissions = {}
        maximum_emissions = {}
        specific_emissions_eleq = {}
        pv_capacities = {}
        grid_total_flows = {}
        for case in use_case:
            main(
                overwrite=True,
                display_output="warning",
                path_input_folder=os.path.join(TEST_INPUT_PATH, case),
                input_type=CSV_EXT,
                path_output_folder=os.path.join(TEST_OUTPUT_PATH, case),
            )
            data = load_json(
                os.path.join(
                    TEST_OUTPUT_PATH, case, JSON_WITH_RESULTS + JSON_FILE_EXTENSION
                )
            )
            total_emissions.update({case: data[KPI][KPI_SCALARS_DICT][TOTAL_EMISSIONS]})
            maximum_emissions.update(
                {case: data[CONSTRAINTS][MAXIMUM_EMISSIONS][VALUE]}
            )
            specific_emissions_eleq.update(
                {case: data[KPI][KPI_SCALARS_DICT][SPECIFIC_EMISSIONS_ELEQ]}
            )
            pv_capacities.update(
                {
                    case: data[KPI][KPI_SCALAR_MATRIX].set_index(LABEL)[
                        OPTIMIZED_ADD_CAP
                    ]["pv_plant_01"]
                }
            )
            grid_total_flows.update(
                {
                    case: data[KPI][KPI_SCALAR_MATRIX].set_index(LABEL)[TOTAL_FLOW][
                        "Electricity_grid_DSO_consumption_source"
                    ]
                }
            )
            if case != "Constraint_maximum_emissions_None":
                assert total_emissions[case] <= maximum_emissions[case] + 10 ** (
                    -5
                ), f"The total emissions of use case {case} exceed the maximum emisssions constraint."

        assert (
            total_emissions[use_case[0]] > total_emissions[use_case[1]]
        ), f"The total emissions of the scenario without maximum emissions constraint are with {total_emissions[use_case[0]]} {UNIT_EMISSIONS} lower than the total emissions of the scenario with the maximum emissions constraint  ({total_emissions[use_case[1]]} {UNIT_EMISSIONS}). This test therefore can not validate that the constraint works."
        assert (
            specific_emissions_eleq[use_case[0]] > specific_emissions_eleq[use_case[1]]
        ), f"The specific emissions per electricity equivalent of the scenario without maximum emissions constraint are with {specific_emissions_eleq[use_case[0]]} {UNIT_SPECIFIC_EMISSIONS} lower than in the scenario with the maximum emissions constraint  ({specific_emissions_eleq[use_case[1]]} {UNIT_SPECIFIC_EMISSIONS})."
        assert (
            pv_capacities[use_case[0]] < pv_capacities[use_case[1]]
        ), f"The optimized installed pv capacity of the scenario without maximum emissions constraint is with {pv_capacities[use_case[0]]} kW higher than in the scenario with the maximum emissions constraint ({pv_capacities[use_case[1]]} kW), but it should be the other way round."
        assert (
            grid_total_flows[use_case[2]] > grid_total_flows[use_case[1]]
        ), f"The total flow of the grid consumption of the scenario with 100 % RE in the grid is with {grid_total_flows[use_case[2]]} kWh lower than in the scenario with emissions from the grid ({grid_total_flows[use_case[1]]} kWh). When the grid has zero emissions it should be used more, while PV is more expensive."

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
