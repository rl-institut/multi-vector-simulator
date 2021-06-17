"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""
import argparse
import os
import shutil

import pytest
from pytest import approx
import mock

from multi_vector_simulator.cli import main
from multi_vector_simulator.B0_data_input_json import load_json

from _constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    TEST_REPO_PATH,
    CSV_EXT,
    BENCHMARK_TEST_INPUT_FOLDER,
    BENCHMARK_TEST_OUTPUT_FOLDER,
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
    DEGREE_OF_AUTONOMY,
    CONSTRAINTS,
    MINIMAL_RENEWABLE_FACTOR,
    MINIMAL_DEGREE_OF_AUTONOMY,
    MAXIMUM_EMISSIONS,
    TOTAL_EMISSIONS,
    SPECIFIC_EMISSIONS_ELEQ,
    UNIT_EMISSIONS,
    UNIT_SPECIFIC_EMISSIONS,
    KPI_SCALAR_MATRIX,
    OPTIMIZED_ADD_CAP,
    LABEL,
    TOTAL_FLOW,
    DEGREE_OF_NZE,
    ANNUAL_TOTAL_FLOW,
    ENERGY_BUSSES,
    ASSET_DICT,
    MAXIMUM_CAP,
    MAXIMUM_ADD_CAP,
    INSTALLED_CAP,
    ENERGY_PRODUCTION,
    ENERGY_CONVERSION,
    TIMESERIES,
    FILENAME,
)

TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, BENCHMARK_TEST_INPUT_FOLDER)
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, BENCHMARK_TEST_OUTPUT_FOLDER)


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
        but the one of Constraint_minimal_renewable_share_70 is 70%, then the benchmark test passes.
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
                ),
                flag_missing_values=False,
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
                ),
                flag_missing_values=False,
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
                        "Electricity_grid_DSO_consumption"
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

    # this ensures that the test is only run if explicitly executed, ie not when the `pytest` command
    # alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_benchmark_minimal_degree_of_autonomy_constraint(self, margs):
        r"""
        Notes
        -----
        With this benchmark test, the minimal degree of autonomy constraint is validated.
        constraint_minimal_degree_of_autonomy_0 does not have a minimal degree of autonomy.
        Constraint_minimal_degree_of_autonomy_70 has a minimal degree of autonomy of 70%.
        If the degree of autonomy of constraint_minimal_renewable_share_0 is lower than 70%,
        but the one of constraint_minimal_renewable_share_70 is 70%, then the benchmark test passes.
        """

        # define the two cases needed for comparison (no minimal renewable factor) and (minimal renewable factor of 70%)
        use_case = [
            "constraint_degree_of_autonomy_0",
            "constraint_degree_of_autonomy_70",
        ]
        # define an empty dictionary for excess electricity
        degree_of_autonomy = {}
        minimal_degree_of_autonomy = {}
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
            degree_of_autonomy.update(
                {case: data[KPI][KPI_SCALARS_DICT][DEGREE_OF_AUTONOMY]}
            )
            minimal_degree_of_autonomy.update(
                {case: data[CONSTRAINTS][MINIMAL_DEGREE_OF_AUTONOMY][VALUE]}
            )

            assert minimal_degree_of_autonomy[case] < degree_of_autonomy[case] + 10 ** (
                -6
            ), f"The minimal degree of autonomy is not at least as high as the minimal degree of autonomy requires."

        assert (
            degree_of_autonomy[use_case[0]] < minimal_degree_of_autonomy[use_case[1]]
        ), f"The  degree of autonomy of the scenario without minimal  degree of autonomy constraint is with {degree_of_autonomy[use_case[0]]} higher than the minimal  degree of autonomy defined for the scenario with constraint ({minimal_degree_of_autonomy[use_case[1]]}). This test therefore can not validate that the constraint works. To debug, increase the cost of PV."
        assert (
            degree_of_autonomy[use_case[0]] < degree_of_autonomy[use_case[1]]
        ), f"The  degree of autonomy of the scenario with the constraint is not higher than the one without, so the test does not make sense."

    # this ensures that the test is only run if explicitly executed, ie not when the `pytest` command
    # alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_net_zero_energy_constraint(self, margs):
        r"""
        Notes
        -----
        With this benchmark test, the net zero energy (NZE) constraint is validated in a
        single sector LES and a sector coupled LES.
        Constraint_net_zero_energy_False contains a single sector LES without NZE constraint.
        Constraint_net_zero_energy_true contains a single sector LES with NZE constraint.
        Constraint_net_zero_energy_sector_coupled_False contains a sector-coupled LES without NZE constraint.
        Constraint_net_zero_energy_sector_coupled_true contains a sector-coupled LES with NZE constraint.
        The benchmark test passes if the degree of NZE of the defined energy systems
        without constraint is lower than one and if the degree of NZE of the energy
        systems with constraint equals one or is greater than one.
        For the sector-coupled energy system, instead of the degree of NZE the balance
        between grid feed-in and consumption is used for the assertion to avoid problems
        with energy weighting.

        """
        # define the cases needed for comparison
        use_case = [
            "Constraint_net_zero_energy_False",
            "Constraint_net_zero_energy_true",
            "Constraint_net_zero_energy_sector_coupled_False",
            "Constraint_net_zero_energy_sector_coupled_true",
        ]
        # define empty dictionaries degree of NZE
        degree_of_nze = {}
        consumption_from_grid = {}
        feedin_to_grid = {}
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
            degree_of_nze.update({case: data[KPI][KPI_SCALARS_DICT][DEGREE_OF_NZE]})
            consumption_from_grid.update(
                {
                    case: data[KPI][KPI_SCALAR_MATRIX].set_index(LABEL)[
                        ANNUAL_TOTAL_FLOW
                    ]["Grid_DSO_consumption"]
                }
            )
            feedin_to_grid.update(
                {
                    case: data[KPI][KPI_SCALAR_MATRIX].set_index(LABEL)[
                        ANNUAL_TOTAL_FLOW
                    ]["Grid_DSO_feedin"]
                }
            )

        assert (
            degree_of_nze[use_case[0]] < 1
        ), f"The degree of NZE of a LES without NZE constraint should be lower than 1, so that the benchmark test reasonably confirms the feature, but is {degree_of_nze[use_case[0]]}."
        assert (
            degree_of_nze[use_case[1]] >= 1 - 1e-6
        ), f"The degree of NZE of a LES with the activated NZE constraint should be equal or greater than 1 but is {degree_of_nze[use_case[1]]}."

        assert (
            degree_of_nze[use_case[2]] < 1
        ), f"The degree of NZE of a sector-coupled LES without NZE constraint should be lower than 1, so that the benchmark test reasonably confirms the feature, but is {degree_of_nze[use_case[2]]}."

        balance = feedin_to_grid[use_case[3]] - consumption_from_grid[use_case[3]]
        assert (
            balance >= 0 - 1e-2
        ), f"The balance between feed-in and consumption from grid of the sector-coupled LES with activated NZE constraint (feed-in - consumption) should be equal or greater than 0 but is {balance}."

    def teardown_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)

    # this ensures that the test is only run if explicitly executed, ie not when the `pytest` command
    # alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_maximum_cap_constraint(self, margs):
        r"""
        Notes
        -----
        With this benchmark test, the maximum capacity constraint is validated.
        The benchmark test passes if the optimized added capacity is less than or
        equal to the defined maximum capacity.

        """
        use_case = [
            "Constraint_maximum_capacity",
        ]
        # define empty dictionaries maximum capacity
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

            # Energy conversion assets
            for conv_asset in data[ENERGY_CONVERSION]:
                # ToDo: another test asserting installedCap * time_series == time series in output
                # using the coupled definition for MaximumCap (includes InstalledCap + additional maximum optimizable capacity)
                max_tot_cap = data[ENERGY_CONVERSION][conv_asset][MAXIMUM_CAP][VALUE]
                max_add_cap = data[ENERGY_CONVERSION][conv_asset][MAXIMUM_ADD_CAP][
                    VALUE
                ]
                opt_add_cap = data[ENERGY_CONVERSION][conv_asset][OPTIMIZED_ADD_CAP][
                    VALUE
                ]
                inst_cap = data[ENERGY_CONVERSION][conv_asset][INSTALLED_CAP][VALUE]
                # case a) inst_cap > 0, max_tot_cap is None (optimizable capacity is unbounded)
                if conv_asset == "transformer_station_in":
                    assert (
                        inst_cap <= inst_cap + opt_add_cap
                    ), f"The installed capacity of {conv_asset} prior to optimization should be less than or equal to the total installed capacity after optimization, but here {inst_cap} > {inst_cap} + {opt_add_cap}."
                    assert (
                        max_tot_cap is None
                    ), f"The total maximum capacity of {conv_asset} should be None (as the user has defined it this way), but instead it is {max_tot_cap}."
                    assert (
                        max_add_cap is None
                    ), f"The total maximum capacity of {conv_asset} is set to None which means that the maximum additional capacity should also be None, but here it is {max_add_cap}."
                # case b) inst_cap > 0, max_tot_cap > 0, inst_cap <= max_tot_cap
                if conv_asset == "diesel_generator_1":
                    assert (
                        opt_add_cap <= max_add_cap
                    ), f"The optimized additional capacity of {conv_asset} should be less than or equal to the total maximum capacity - the installed capacity, but {opt_add_cap} > {max_add_cap}."
                    assert (
                        max_tot_cap == inst_cap + max_add_cap
                    ), f"The maximum total capacity of {conv_asset} should be equal to the already installed capacity + the maximum additional optimizable capacity, but {max_tot_cap} is not equal to {inst_cap} + {max_add_cap}."
                # case c) inst_cap = 0, max_tot_cap > 0
                if conv_asset == "solar_inverter_(mono)":
                    assert (
                        max_add_cap == max_tot_cap
                    ), f"Because the installed capacity of {conv_asset} is zero, the maximum additional capacity should be equal to the total maximum capacity, but {max_add_cap} is not equal to {max_tot_cap}."
                    assert (
                        opt_add_cap <= max_add_cap
                    ), f"The optimized additional capacity of {conv_asset} should be less than the maximum possible additional capacity, but {opt_add_cap} > {max_add_cap}."

            for prod_asset in data[ENERGY_PRODUCTION]:
                # using the coupled definition for MaximumCap (includes InstalledCap +  additional maximum optimizable capacity)
                max_tot_cap = data[ENERGY_PRODUCTION][prod_asset][MAXIMUM_CAP][VALUE]
                max_add_cap = data[ENERGY_PRODUCTION][prod_asset][MAXIMUM_ADD_CAP][
                    VALUE
                ]
                opt_add_cap = data[ENERGY_PRODUCTION][prod_asset][OPTIMIZED_ADD_CAP][
                    VALUE
                ]
                inst_cap = data[ENERGY_PRODUCTION][prod_asset][INSTALLED_CAP][VALUE]
                # case a) inst_cap > 0, max_tot_cap is None (optimizable capacity is unbounded)
                if prod_asset == "pv_plant_01":
                    assert (
                        inst_cap <= inst_cap + opt_add_cap
                    ), f"The installed capacity of {prod_asset} prior to optimization should be less than or equal to the total installed capacity after optimization, but here {inst_cap} > {inst_cap} + {opt_add_cap}."
                    assert (
                        max_tot_cap is None
                    ), f"The total maximum capacity of {prod_asset} should be None (as the user has defined it this way), but instead it is {max_tot_cap}."
                    assert (
                        max_add_cap is None
                    ), f"The total maximum capacity of {prod_asset} is set to None which means that the maximum additional capacity should also be None, but here it is {max_add_cap}."
                # case b) inst_cap > 0, max_tot_cap > 0, inst_cap <= max_tot_cap
                if prod_asset == "pv_plant_02":
                    assert (
                        opt_add_cap <= max_add_cap
                    ), f"The optimized additional capacity of the asset should be less than or equal to the total maximum capacity - the installed capacity, but {opt_add_cap} > {max_add_cap}."
                # case c) inst_cap = 0, max_tot_cap > 0
                if prod_asset == "pv_plant_03":
                    assert (
                        max_add_cap == max_tot_cap
                    ), f"Because the installed capacity of {prod_asset} is zero, the maximum additional capacity should be equal to the total maximum capacity, but {max_add_cap} is not equal to {max_tot_cap}."
                    assert (
                        opt_add_cap <= max_add_cap
                    ), f"The optimized additional capacity of {prod_asset} should be less than the maximum possible additional capacity, but {opt_add_cap} > {max_add_cap}."

                if prod_asset in ["pv_plant_01", "pv_plant_02", "pv_plant_03"]:
                    # check that the power output timeseries * total capacity of each production asset is equal to
                    # the calculated total flow (of each asset)
                    assert (opt_add_cap + inst_cap) * data[ENERGY_PRODUCTION][
                        prod_asset
                    ][TIMESERIES].sum() == approx(
                        data[ENERGY_PRODUCTION][prod_asset][TOTAL_FLOW][VALUE], rel=1e-3
                    ), f"The sum of the power output timeseries * total capacity chosen of {prod_asset} should be equal to calculated total flow of the asset, but this is not the case."
