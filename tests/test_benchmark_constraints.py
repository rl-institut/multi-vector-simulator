"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""
import argparse
import os
import shutil
import json

import mock
import pandas as pd
import pytest
import random

from pytest import approx
from mvs_eland_tool import main
from src.B0_data_input_json import load_json
import src.C2_economic_functions as C2

from .constants import (
    TEST_REPO_PATH,
    CSV_EXT,
)

from src.constants import JSON_WITH_RESULTS

from src.constants_json_strings import (
    VALUE,
    KPI,
    KPI_SCALARS_DICT,
    RENEWABLE_SHARE,
    CONSTRAINTS,
    MINIMAL_RENEWABLE_SHARE,
)

TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_inputs")
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_outputs")


class Test_Constraints:
    def setup_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
        if os.path.exists(TEST_OUTPUT_PATH) is False:
            os.mkdir(TEST_OUTPUT_PATH)

    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_minimal_renewable_share_constraint(self, margs):
        r"""
        Notes
        -----
        With this benchmark test, the minimal renewable share constraint is validated.
        Constraint_minimal_renewable_share_0 does not have a minimal renewable share.
        Constraint_minimal_renewable_share_50 has a minimal renewable share of 50%.
        If the renewable share of Constraint_minimal_renewable_share_0 is lower than 50%,
        but the one of Constraint_minimal_renewable_share_50 is 50%, then the benchmark test passes.
        """

        # define the two cases needed for comparison (no minimal renewable share) and (minimal renewable share of 50%)
        use_case = [
            "Constraint_minimal_renewable_share_0",
            "Constraint_minimal_renewable_share_50",
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
                os.path.join(TEST_OUTPUT_PATH, use_case, JSON_WITH_RESULTS)
            )
            renewable_shares.update(
                {case: data[KPI][KPI_SCALARS_DICT][RENEWABLE_SHARE]}
            )
            minimal_renewable_shares.update(
                {case: data[CONSTRAINTS][MINIMAL_RENEWABLE_SHARE][VALUE]}
            )
            assert minimal_renewable_shares[case] <= pytest.approx(
                renewable_shares[case], rel=1e-6
            )

        assert renewable_shares[use_case[0]] < pytest.approx(
            renewable_shares[use_case[1]]
        )

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
