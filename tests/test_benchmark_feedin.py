import argparse
import os
import shutil
import json

import mock
import pandas as pd
import pytest

from pytest import approx
from multi_vector_simulator.cli import main
from multi_vector_simulator.B0_data_input_json import load_json

from _constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    TEST_REPO_PATH,
    CSV_EXT,
    ENERGY_PRICE,
    OPTIMIZED_ADD_CAP,
    LABEL,
    CSV_ELEMENTS,
)

from multi_vector_simulator.utils.constants import (
    JSON_WITH_RESULTS,
    JSON_FILE_EXTENSION,
)

from multi_vector_simulator.utils.constants_json_strings import (
    DSO_CONSUMPTION,
    DSO_FEEDIN,
    KPI_SCALARS_DICT,
    KPI_COST_MATRIX,
    KPI_SCALAR_MATRIX,
    LCOE_ASSET,
    TOTAL_FLOW,
    COST_TOTAL,
    COST_OPERATIONAL_TOTAL,
    COST_OM,
    COST_DISPATCH,
    ENERGY_CONVERSION,
    ENERGY_PROVIDERS,
    VALUE,
    LCOE_ASSET,
    ENERGY_CONSUMPTION,
    FLOW,
    EFFICIENCY,
    FEEDIN_TARIFF,
    EXCESS_SINK,
)

TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_inputs")
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_outputs")

FEEDIN = f"DSO{DSO_FEEDIN}"
CONSUMPTION = f"DSO{DSO_CONSUMPTION}"
EXCESS_SINK_NAME = f"Electricity{EXCESS_SINK}"


class TestFeedinTariff:
    def setup_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
        if os.path.exists(TEST_OUTPUT_PATH) is False:
            os.mkdir(TEST_OUTPUT_PATH)

    def get_results(self, directory):
        df_busses_flow = pd.read_excel(
            os.path.join(TEST_OUTPUT_PATH, directory, "timeseries_all_busses.xlsx"),
            sheet_name="Electricity",
        ).set_index("Unnamed: 0")
        cost_matrix = pd.read_excel(
            os.path.join(TEST_OUTPUT_PATH, directory, "scalars.xlsx"),
            sheet_name=KPI_COST_MATRIX,
        ).set_index(LABEL)
        scalar_matrix = pd.read_excel(
            os.path.join(TEST_OUTPUT_PATH, directory, "scalars.xlsx"),
            sheet_name=KPI_SCALAR_MATRIX,
        ).set_index(LABEL)
        scalars = (
            pd.read_excel(
                os.path.join(TEST_OUTPUT_PATH, directory, "scalars.xlsx"),
                sheet_name=KPI_SCALARS_DICT,
            )
            .set_index("Unnamed: 0")
            .drop("unit", axis=1)
        )
        return df_busses_flow, cost_matrix, scalar_matrix, scalars

    # this ensures that the test is only run if explicitly executed, i.e. not when the
    # `pytest` command alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_feedin_tariff_dispatch_positive_value(self, margs):
        r"""
        Benchmark test for feed-in in a simple dispatch case with grid connected PV and positive feed-in tariff (earn by feed-in).
        """
        use_case = "Feedin_dispatch"
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(
                TEST_OUTPUT_PATH, use_case, "positive_value"
            ),
        )

        df_busses_flow, cost_matrix, scalar_matrix, scalars = self.get_results(
            os.path.join(use_case, "positive_value")
        )

        # at a positive feed-in tariff all production exceeding the demand should be
        # fed into the grid --> excess is zero
        excess_sum = df_busses_flow[EXCESS_SINK_NAME].sum()
        total_excess_scalar = scalar_matrix[TOTAL_FLOW][EXCESS_SINK_NAME]
        assert (
            excess_sum == 0
        ), f"When the feed-in tariff is positive there should be no electricity excess, however the sum of the excess time series is {excess_sum}"

        assert (
            total_excess_scalar == 0
        ), f"When the feed-in tariff is positive there should be no electricity excess, however the scalar matrix shows an excess of {total_excess_scalar}"

        # costs of DSO feed-in sink in scalars.xlsx should be negative, while they
        # should be substracted from the summed-up costs of the whole system
        # negative costs in cost_matrix:
        assert (
            cost_matrix[COST_TOTAL][FEEDIN] < 0
            and cost_matrix[COST_OPERATIONAL_TOTAL][FEEDIN] < 0
            and cost_matrix[COST_DISPATCH][FEEDIN] < 0
            and cost_matrix[LCOE_ASSET][FEEDIN] < 0
        ), f"When the feed-in tariff is positive the costs of the feed-in should be negative (scalar_matrix: {COST_TOTAL}, {COST_OPERATIONAL_TOTAL}, {COST_DISPATCH}, {LCOE_ASSET})."
        # costs substracted from total costs:
        total_costs_feedin = cost_matrix[COST_TOTAL][FEEDIN]
        total_costs_consumption = cost_matrix[COST_TOTAL][CONSUMPTION]
        total_costs_all_assets = scalars.loc[COST_TOTAL][0]
        assert (
            total_costs_all_assets == total_costs_feedin + total_costs_consumption
        ), f"When the feed-in tariff is positive the costs of the feed-in should be substracted from the total cost (scalars)."

    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_feedin_tariff_dispatch_negative_value(self, margs):
        r"""
        Benchmark test for feed-in in a simple dispatch case with grid connected PV and negative feed-in tariff (pay for feed-in).
        """
        use_case = "Feedin_dispatch"

        # set feed-in tariff to negative value
        filename = os.path.join(
            TEST_INPUT_PATH, use_case, CSV_ELEMENTS, f"{ENERGY_PROVIDERS}.csv"
        )
        df = pd.read_csv(filename).set_index("Unnamed: 0")
        df["DSO"][FEEDIN_TARIFF] = -float(df["DSO"][FEEDIN_TARIFF])
        df.to_csv(filename)

        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(
                TEST_OUTPUT_PATH, use_case, "negative_value"
            ),
        )

        # reset feed-in tariff just in case
        df["DSO"][FEEDIN_TARIFF] = -float(df["DSO"][FEEDIN_TARIFF])
        df.to_csv(filename)

        df_busses_flow, cost_matrix, scalar_matrix, scalars = self.get_results(
            os.path.join(use_case, "negative_value")
        )

        # at a negative feed-in tariff no feed into the grid should take place
        feedin = df_busses_flow[FEEDIN].sum()
        total_feedin_scalar = scalar_matrix[TOTAL_FLOW][FEEDIN]
        assert (
            feedin == 0
        ), f"When the feed-in tariff is negative there should be no feed into the grid, however the sum of the feed-in time series is {feedin}"

        assert (
            total_feedin_scalar == 0
        ), f"When the feed-in tariff is negative there should be no feed into the grid, however the scalar matrix shows feed-in of {total_feedin_scalar}"

        # costs of DSO feed-in sink in scalars.xlsx should be zero.
        assert (
            cost_matrix[COST_TOTAL][FEEDIN] == 0
            and cost_matrix[COST_OPERATIONAL_TOTAL][FEEDIN] == 0
            and cost_matrix[COST_DISPATCH][FEEDIN] == 0
            and cost_matrix[LCOE_ASSET][FEEDIN] == 0
        ), f"When the feed-in tariff is negative the costs of the feed-in should be zero, as no feed-in takes place (scalar_matrix: {COST_TOTAL}, {COST_OPERATIONAL_TOTAL}, {COST_DISPATCH}, {LCOE_ASSET})."

    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_feedin_tariff_optimize_positive_value(self, margs):
        r"""
        Benchmark test for feed-in in a simple invest case with grid connected PV and positive feed-in tariff (earn by feed-in).
        """
        use_case = "Feedin_optimize"
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(
                TEST_OUTPUT_PATH, use_case, "positive_value"
            ),
        )
        # get results
        df_busses_flow, cost_matrix, scalar_matrix, scalars = self.get_results(
            os.path.join(use_case, "positive_value")
        )

        # at a high positive feed-in tariff and moderate specific PV costs the maximum
        # capacity of PV is installed, while feed-in takes place and excess is zero
        optimized_added_cap = scalar_matrix[OPTIMIZED_ADD_CAP]["pv_plant_01"]
        assert (
            optimized_added_cap == 5000
        ), f"At a high positive feed-in tariff and moderate specific PV costs the maximum PV capacity should be installed (5000 kWp), however {optimized_added_cap} kWp is installed."
        excess_sum = df_busses_flow[EXCESS_SINK_NAME].sum()
        assert (
            excess_sum == 0
        ), f"When the feed-in tariff is positive there should be no electricity excess, however the sum of the excess time series is {excess_sum}"

    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_feedin_tariff_optimize_negative_value(self, margs):
        r"""
        Benchmark test for feed-in in a simple invest case with grid connected PV and negative feed-in tariff (pay for feed-in).
        """
        use_case = "Feedin_optimize"
        # set feed-in tariff to negative value
        filename = os.path.join(
            TEST_INPUT_PATH, use_case, CSV_ELEMENTS, f"{ENERGY_PROVIDERS}.csv"
        )
        df = pd.read_csv(filename).set_index("Unnamed: 0")
        df["DSO"][FEEDIN_TARIFF] = -float(df["DSO"][FEEDIN_TARIFF])
        df.to_csv(filename)

        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(
                TEST_OUTPUT_PATH, use_case, "negative_value"
            ),
        )
        # reset feed-in tariff just in case
        df["DSO"][FEEDIN_TARIFF] = -float(df["DSO"][FEEDIN_TARIFF])
        df.to_csv(filename)

        # get results
        df_busses_flow, cost_matrix, scalar_matrix, scalars = self.get_results(
            os.path.join(use_case, "negative_value")
        )

        # at a negative feed-in tariff and sufficiently installed PV capacity no
        # additional PV capacity should be installed, while no feed-in takes place.
        optimized_added_cap = scalar_matrix[OPTIMIZED_ADD_CAP]["pv_plant_01"]
        assert (
            optimized_added_cap == 0
        ), f"At a negative feed-in tariff and sufficiently installed PV capacity no additional PV capacity should be installed, while no feed-in takes place, however {optimized_added_cap} kWp is installed."
        feedin_sum = df_busses_flow[FEEDIN].sum()
        assert (
            feedin_sum == 0
        ), f"When the feed-in tariff is negative there should be no feed-in to the grid, however the sum of the feed-in time series is {feedin_sum}"

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
