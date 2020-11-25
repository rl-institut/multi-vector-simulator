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

            assert minimal_renewable_shares[case] < renewable_shares[case] + 10 ** (-6)

        assert renewable_shares[use_case[0]] < minimal_renewable_shares[use_case[1]]
        assert renewable_shares[use_case[0]] < renewable_shares[use_case[1]]

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
