"""
With these benchmark tests the implementation of the stratified thermal energy storage
component is checked.

In this module the tests run over a whole simulation from main, not just single functions of modules.

What should differ between the different functions is the input file

"""

import argparse
import os
import shutil
import pandas as pd

import pytest
import mock

from multi_vector_simulator.cli import main

from _constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    TEST_REPO_PATH,
    CSV_EXT,
)

from multi_vector_simulator.utils.constants_json_strings import (
    INSTALLED_CAP,
    THERM_LOSSES_REL,
    THERM_LOSSES_ABS,
)

TEST_INPUT_PATH = os.path.join(
    TEST_REPO_PATH, "benchmark_test_inputs", "Feature_stratified_thermal_storage"
)
TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_outputs")


class TestStratifiedThermalStorage:
    def setup_method(self):
        if os.path.exists(TEST_OUTPUT_PATH):
            shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)
        if os.path.exists(TEST_OUTPUT_PATH) is False:
            os.mkdir(TEST_OUTPUT_PATH)

        self.inputs_csv = os.path.join(TEST_INPUT_PATH, "csv_elements")
        self.storage_csv = os.path.join(self.inputs_csv, "energyStorage.csv")

        self.storage_fix_without_fixed_losses = (
            "storage_fix_without_fixed_thermal_losses.csv"
        )
        self.storage_opt_without_fixed_losses = (
            "storage_optimize_without_fixed_thermal_losses.csv"
        )
        self.storage_opt_with_fixed_losses_float = (
            "storage_optimize_with_fixed_thermal_losses_float.csv"
        )
        self.storage_opt_with_fixed_losses_series = (
            "storage_optimize_with_fixed_thermal_losses_time_series.csv"
        )
        self.storage_opt_with_zero_fixed_losses_float = (
            "storage_optimize_with_zero_fixed_thermal_losses_float.csv"
        )
        self.storage_opt_with_zero_fixed_losses_series = (
            "storage_optimize_with_zero_fixed_thermal_losses_time_series.csv"
        )

        self.storage_xx = os.path.join(
            self.inputs_csv, self.storage_opt_with_fixed_losses_float
        )

        self.D1 = os.path.abspath(
            os.path.join(
                TEST_REPO_PATH,
                os.pardir,
                "src",
                "multi_vector_simulator",
                "D1_model_components.py",
            )
        )
        self.fixed_losses = [THERM_LOSSES_REL, THERM_LOSSES_ABS]

    # # this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
    # # alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_fix_generic_storage_with_default_losses(self, margs):
        r"""
        This test checks if the fix GenericStorage matches the one with additional
        fixed thermal losses: fixed_thermal_losses_relative and
        fixed_thermal_losses_absolute.
        The simulation needs to run with a simple GenericStorage (Thermal storage without fixed
        thermal losses). To achieve this D1_model_components.py needs to be modified by
        commenting out the two parameters fixed_thermal_losses_relative and
        fixed_thermal_losses_absolute in storage_fix and storage_optimize functions.
        The assertion is a match of the timeseries_all_busses.xlsx files of the modified
        GenericStorage with the one of a simulation run with the implemented GenericStorage
        with fixed_thermal_losses_relative and fixed_thermal_losses_absolute.
        """

        storage_data_original = pd.read_csv(self.storage_csv, header=0, index_col=0)
        storage_data = storage_data_original.copy()
        storage_data["storage_01"][
            "storage_filename"
        ] = self.storage_fix_without_fixed_losses
        storage_data.to_csv(self.storage_csv)

        use_cases = ["Generic_storage_fix", "Stratified_thermal_storage_fix"]
        for use_case in use_cases:
            output_path = os.path.join(TEST_OUTPUT_PATH, use_case)
            if os.path.exists(output_path):
                shutil.rmtree(output_path, ignore_errors=True)
            if os.path.exists(output_path) is False:
                os.mkdir(output_path)

            if use_case == "Generic_storage_fix":
                # Open D1_model_components.py and read its content
                mvs_D1 = open(self.D1).read()

                # Modify the content by commenting the fixed thermal losses out
                # in storage_fix and storage_optimize functions
                fixed_losses_generic_storage = [
                    "fixed_losses_absolute",
                    "fixed_losses_relative",
                ]
                for fixed_losses in fixed_losses_generic_storage:
                    if fixed_losses in mvs_D1:
                        mvs_D1_modified_string = mvs_D1.replace(
                            fixed_losses, "# " + fixed_losses
                        )

                # Open D1_model_components.py in write modus and save the version
                # with commented out fixed losses
                mvs_D1_modified = open(self.D1, "w")
                mvs_D1_modified.write(mvs_D1_modified_string)
                mvs_D1_modified.close()

                # Run the simulation with a fix Generic Storage
                try:
                    main(
                        display_output="warning",
                        path_input_folder=TEST_INPUT_PATH,
                        path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                        input_type="csv",
                        overwrite=True,
                        save_png=False,
                        lp_file_output=True,
                    )
                except:
                    print(
                        "Please check the main input parameters for errors. "
                        "This exception prevents that D1_model_components.py is "
                        "overwritten in case running the main errors out."
                    )

                # Revert changes made in D1_model_components.py
                mvs_D1_modified = open(self.D1, "w")
                mvs_D1_modified.write(mvs_D1)
                mvs_D1_modified.close()

                results_generic_storage = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

            elif use_case == "Stratified_thermal_storage_fix":
                main(
                    display_output="warning",
                    path_input_folder=TEST_INPUT_PATH,
                    path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                    input_type="csv",
                    overwrite=True,
                    save_png=False,
                    lp_file_output=True,
                )

                results_stratified_thermal_storage = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

        assert (
            results_generic_storage["TES input power"].values.all()
            == results_stratified_thermal_storage["TES input power"].values.all()
        ), f"When the parameters {THERM_LOSSES_REL} and {THERM_LOSSES_ABS} are commented out in {self.D1} the results of the simulation should be the same as if {THERM_LOSSES_REL} and {THERM_LOSSES_ABS} are not used in the simulation"
        storage_data_original.to_csv(self.storage_csv)

    # # this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
    # # alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_optimize_generic_storage_with_default_losses(self, margs):
        r"""
        This test checks if the optimized GenericStorage matches the one with additional
        fixed thermal losses: fixed_thermal_losses_relative and
        fixed_thermal_losses_absolute.
        The simulation need to run with a simple GenericStorage (Thermal storage without fixed
        thermal losses). To achieve this D1_model_components.py needs to be modified by
        commenting out the two parameters fixed_thermal_losses_relative and
        fixed_thermal_losses_absolute in storage_fix and storage_optimize functions.
        The assertion is a match of the timeseries_all_busses.xlsx files of the modified
        GenericStorage with the one of a simulation run with the implemented GenericStorage
        with fixed_thermal_losses_relative and fixed_thermal_losses_absolute.
        """

        storage_data_original = pd.read_csv(self.storage_csv, header=0, index_col=0)
        storage_data = storage_data_original.copy()
        storage_data["storage_01"][
            "storage_filename"
        ] = self.storage_opt_without_fixed_losses
        storage_data.to_csv(self.storage_csv)

        use_cases = [
            "Generic_storage_optimize",
            "Stratified_thermal_storage_optimize",
        ]
        for use_case in use_cases:
            output_path = os.path.join(TEST_OUTPUT_PATH, use_case)
            if os.path.exists(output_path):
                shutil.rmtree(output_path, ignore_errors=True)
            if os.path.exists(output_path) is False:
                os.mkdir(output_path)

            if use_case == "Generic_storage_optimize":
                # Open D1_model_components.py and read its content
                mvs_D1 = open(self.D1).read()

                # Modify the content by commenting the fixed thermal losses out
                # in storage_fix and storage_optimize functions
                fixed_losses_generic_storage = [
                    "fixed_losses_absolute",
                    "fixed_losses_relative",
                ]
                for fixed_losses in fixed_losses_generic_storage:
                    if fixed_losses in mvs_D1:
                        mvs_D1_modified_string = mvs_D1.replace(
                            fixed_losses, "# " + fixed_losses
                        )

                # Open D1_model_components.py in write modus and save the version
                # with commented out fixed losses
                mvs_D1_modified = open(self.D1, "w")
                mvs_D1_modified.write(mvs_D1_modified_string)
                mvs_D1_modified.close()

                # Run the simulation with a optimize Generic Storage
                try:
                    main(
                        display_output="warning",
                        path_input_folder=TEST_INPUT_PATH,
                        path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                        input_type="csv",
                        overwrite=True,
                        save_png=False,
                        lp_file_output=True,
                    )
                except:
                    print(
                        "Please check the main input parameters for errors. "
                        "This exception prevents that D1_model_components.py is "
                        "overwritten in case running the main errors out."
                    )

                # Revert changes made in D1_model_components.py
                mvs_D1_modified = open(self.D1, "w")
                mvs_D1_modified.write(mvs_D1)
                mvs_D1_modified.close()

                results_generic_storage = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

            elif use_case == "Stratified_thermal_storage_optimize":
                main(
                    display_output="warning",
                    path_input_folder=TEST_INPUT_PATH,
                    path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                    input_type="csv",
                    overwrite=True,
                    save_png=False,
                    lp_file_output=True,
                )

                results_stratified_thermal_storage = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

        assert (
            results_generic_storage["TES input power"].values.all()
            == results_stratified_thermal_storage["TES input power"].values.all()
        ), f"When the parameters {THERM_LOSSES_REL} and {THERM_LOSSES_ABS} are commented out in {self.D1} the results of the simulation should be the same as if {THERM_LOSSES_REL} and {THERM_LOSSES_ABS} are not used in the simulation"
        storage_data_original.to_csv(self.storage_csv)

    def teardown_method(self):
        use_cases = [
            "Generic_storage_fix",
            "Stratified_thermal_storage_fix",
            "Generic_storage_optimize",
            "Stratified_thermal_storage_optimize",
        ]
        for use_case in use_cases:
            if os.path.exists(os.path.join(TEST_OUTPUT_PATH, use_case)):
                shutil.rmtree(
                    os.path.join(TEST_OUTPUT_PATH, use_case), ignore_errors=True
                )

    # # this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
    # # alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_fixed_losses_higher_invested_storage_capacity_float(self, margs):
        """
        This test checks if the invested storage capacity of an optimized GenericStorage
        without fixed thermal losses is higher than the one of an optimized GenericStorage
        with fixed_thermal_losses_relative and fixed_thermal_losses_absolute, which are
        passed as floats.
        """
        use_cases = ["Thermal_storage_float", "Stratified_thermal_storage_float"]

        for use_case in use_cases:
            output_path = os.path.join(TEST_OUTPUT_PATH, use_case)
            if os.path.exists(output_path):
                shutil.rmtree(output_path, ignore_errors=True)
            if os.path.exists(output_path) is False:
                os.mkdir(output_path)

            if use_case == "Thermal_storage_float":

                storage_data_original = pd.read_csv(
                    self.storage_csv, header=0, index_col=0
                )
                storage_data = storage_data_original.copy()
                storage_data["storage_01"][
                    "storage_filename"
                ] = self.storage_opt_without_fixed_losses
                storage_data.to_csv(self.storage_csv)

                try:
                    main(
                        display_output="warning",
                        path_input_folder=TEST_INPUT_PATH,
                        path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                        input_type="csv",
                        overwrite=True,
                        save_png=False,
                        lp_file_output=True,
                    )
                except:
                    print(
                        "Please check the main input parameters for errors. "
                        "This exception prevents that energyStorage.py is "
                        "overwritten in case running the main errors out."
                    )

                storage_data_original.to_csv(self.storage_csv)
                results_thermal_storage = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

            elif use_case == "Stratified_thermal_storage_float":

                storage_data_original = pd.read_csv(
                    self.storage_csv, header=0, index_col=0
                )
                storage_data = storage_data_original.copy()
                storage_data["storage_01"][
                    "storage_filename"
                ] = self.storage_opt_with_fixed_losses_float
                storage_data.to_csv(self.storage_csv)

                try:
                    main(
                        display_output="warning",
                        path_input_folder=TEST_INPUT_PATH,
                        path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                        input_type="csv",
                        overwrite=True,
                        save_png=False,
                        lp_file_output=True,
                    )
                except:
                    print(
                        "Please check the main input parameters for errors. "
                        "This exception prevents that energyStorage.py is "
                        "overwritten in case running the main errors out."
                    )

                storage_data_original.to_csv(self.storage_csv)
                results_stratified_thermal_storage = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

        assert abs(results_thermal_storage["TES input power"].values.sum()) > abs(
            results_stratified_thermal_storage["TES input power"].values.sum()
        ), f"The invested storage capacity with passed non-zero losses {THERM_LOSSES_REL} and {THERM_LOSSES_ABS} should be lower than without {THERM_LOSSES_REL} and {THERM_LOSSES_ABS}"

    def teardown_method(self):
        use_cases = [
            "Thermal_storage_float",
            "Stratified_thermal_storage_float",
        ]
        for use_case in use_cases:
            if os.path.exists(os.path.join(TEST_OUTPUT_PATH, use_case)):
                shutil.rmtree(
                    os.path.join(TEST_OUTPUT_PATH, use_case), ignore_errors=True
                )

    # # this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
    # # alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_fixed_losses_higher_invested_storage_capacity_series(self, margs):
        """
        This test checks if the invested storage capacity of an optimized GenericStorage
        without fixed thermal losses is higher than the one of an optimized GenericStorage
        with fixed_thermal_losses_relative and fixed_thermal_losses_absolute, which are
        passed as time series.
        """
        use_cases = ["Thermal_storage_series", "Stratified_thermal_storage_series"]

        for use_case in use_cases:
            output_path = os.path.join(TEST_OUTPUT_PATH, use_case)
            if os.path.exists(output_path):
                shutil.rmtree(output_path, ignore_errors=True)
            if os.path.exists(output_path) is False:
                os.mkdir(output_path)

            if use_case == "Thermal_storage_series":

                storage_data_original = pd.read_csv(
                    self.storage_csv, header=0, index_col=0
                )
                storage_data = storage_data_original.copy()
                storage_data["storage_01"][
                    "storage_filename"
                ] = self.storage_opt_without_fixed_losses
                storage_data.to_csv(self.storage_csv)

                try:
                    main(
                        display_output="warning",
                        path_input_folder=TEST_INPUT_PATH,
                        path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                        input_type="csv",
                        overwrite=True,
                        save_png=False,
                        lp_file_output=True,
                    )
                except:
                    print(
                        "Please check the main input parameters for errors. "
                        "This exception prevents that energyStorage.py is "
                        "overwritten in case running the main errors out."
                    )

                storage_data_original.to_csv(self.storage_csv)
                results_thermal_storage = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

            elif use_case == "Stratified_thermal_storage_series":

                storage_data_original = pd.read_csv(
                    self.storage_csv, header=0, index_col=0
                )
                storage_data = storage_data_original.copy()
                storage_data["storage_01"][
                    "storage_filename"
                ] = self.storage_opt_with_fixed_losses_series
                storage_data.to_csv(self.storage_csv)

                try:
                    main(
                        display_output="warning",
                        path_input_folder=TEST_INPUT_PATH,
                        path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                        input_type="csv",
                        overwrite=True,
                        save_png=False,
                        lp_file_output=True,
                    )
                except:
                    print(
                        "Please check the main input parameters for errors. "
                        "This exception prevents that energyStorage.py is "
                        "overwritten in case running the main errors out."
                    )

                storage_data_original.to_csv(self.storage_csv)
                results_stratified_thermal_storage = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

        assert abs(results_thermal_storage["TES input power"].values.sum()) > abs(
            results_stratified_thermal_storage["TES input power"].values.sum()
        ), f"The invested storage capacity with passed non-zero losses {THERM_LOSSES_REL} and {THERM_LOSSES_ABS} should be lower than without {THERM_LOSSES_REL} and {THERM_LOSSES_ABS}"

    def teardown_method(self):
        use_cases = [
            "Thermal_storage_series",
            "Stratified_thermal_storage_series",
        ]
        for use_case in use_cases:
            if os.path.exists(os.path.join(TEST_OUTPUT_PATH, use_case)):
                shutil.rmtree(
                    os.path.join(TEST_OUTPUT_PATH, use_case), ignore_errors=True
                )

    # # this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
    # # alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_default_losses_and_zero_losses_equal_storage_capacity_float(self, margs):
        """
        This test checks if the invested storage capacity of an optimized GenericStorage
        without fixed thermal losses is equal to the one of an optimized GenericStorage
        with fixed_thermal_losses_relative and fixed_thermal_losses_absolute, which are
        zero and passed as floats.
        """
        use_cases = ["Thermal_storage_losses_default", "Thermal_storage_losses_zero"]

        for use_case in use_cases:
            output_path = os.path.join(TEST_OUTPUT_PATH, use_case)
            if os.path.exists(output_path):
                shutil.rmtree(output_path, ignore_errors=True)
            if os.path.exists(output_path) is False:
                os.mkdir(output_path)

            if use_case == "Thermal_storage_losses_default":

                storage_data_original = pd.read_csv(
                    self.storage_csv, header=0, index_col=0
                )
                storage_data = storage_data_original.copy()
                storage_data["storage_01"][
                    "storage_filename"
                ] = self.storage_opt_without_fixed_losses
                storage_data.to_csv(self.storage_csv)

                try:
                    main(
                        display_output="warning",
                        path_input_folder=TEST_INPUT_PATH,
                        path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                        input_type="csv",
                        overwrite=True,
                        save_png=False,
                        lp_file_output=True,
                    )
                except:
                    print(
                        "Please check the main input parameters for errors. "
                        "This exception prevents that energyStorage.py is "
                        "overwritten in case running the main errors out."
                    )

                storage_data_original.to_csv(self.storage_csv)
                results_thermal_storage_losses_default = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

            elif use_case == "Thermal_storage_losses_zero":

                storage_data_original = pd.read_csv(
                    self.storage_csv, header=0, index_col=0
                )
                storage_data = storage_data_original.copy()
                storage_data["storage_01"][
                    "storage_filename"
                ] = self.storage_opt_with_zero_fixed_losses_float
                storage_data.to_csv(self.storage_csv)

                try:
                    main(
                        display_output="warning",
                        path_input_folder=TEST_INPUT_PATH,
                        path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                        input_type="csv",
                        overwrite=True,
                        save_png=False,
                        lp_file_output=True,
                    )
                except:
                    print(
                        "Please check the main input parameters for errors. "
                        "This exception prevents that energyStorage.py is "
                        "overwritten in case running the main errors out."
                    )

                storage_data_original.to_csv(self.storage_csv)
                results_thermal_storage_losses_zero = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

        assert (
            results_thermal_storage_losses_default["TES input power"].values.all()
            == results_thermal_storage_losses_zero["TES input power"].values.all()
        ), f"The invested storage capacity with passed losses {THERM_LOSSES_REL} and {THERM_LOSSES_ABS} that equal zero should be the same as without {THERM_LOSSES_REL} and {THERM_LOSSES_ABS}"

    # # this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
    # # alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_default_losses_and_zero_losses_equal_storage_capacity_series(self, margs):
        """
        This test checks if the invested storage capacity of an optimized GenericStorage
        without fixed thermal losses is equal to the one of an optimized GenericStorage
        with fixed_thermal_losses_relative and fixed_thermal_losses_absolute, which are
        zero and passed as time series.
        """
        use_cases = ["Thermal_storage_losses_default", "Thermal_storage_losses_zero"]

        for use_case in use_cases:
            output_path = os.path.join(TEST_OUTPUT_PATH, use_case)
            if os.path.exists(output_path):
                shutil.rmtree(output_path, ignore_errors=True)
            if os.path.exists(output_path) is False:
                os.mkdir(output_path)

            if use_case == "Thermal_storage_losses_default":

                storage_data_original = pd.read_csv(
                    self.storage_csv, header=0, index_col=0
                )
                storage_data = storage_data_original.copy()
                storage_data["storage_01"][
                    "storage_filename"
                ] = self.storage_opt_without_fixed_losses
                storage_data.to_csv(self.storage_csv)

                try:
                    main(
                        display_output="warning",
                        path_input_folder=TEST_INPUT_PATH,
                        path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                        input_type="csv",
                        overwrite=True,
                        save_png=False,
                        lp_file_output=True,
                    )
                except:
                    print(
                        "Please check the main input parameters for errors. "
                        "This exception prevents that energyStorage.py is "
                        "overwritten in case running the main errors out."
                    )

                storage_data_original.to_csv(self.storage_csv)
                results_thermal_storage_losses_default = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

            elif use_case == "Thermal_storage_losses_zero":

                storage_data_original = pd.read_csv(
                    self.storage_csv, header=0, index_col=0
                )
                storage_data = storage_data_original.copy()
                storage_data["storage_01"][
                    "storage_filename"
                ] = self.storage_opt_with_zero_fixed_losses_series
                storage_data.to_csv(self.storage_csv)

                try:
                    main(
                        display_output="warning",
                        path_input_folder=TEST_INPUT_PATH,
                        path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                        input_type="csv",
                        overwrite=True,
                        save_png=False,
                        lp_file_output=True,
                    )
                except:
                    print(
                        "Please check the main input parameters for errors. "
                        "This exception prevents that energyStorage.py is "
                        "overwritten in case running the main errors out."
                    )

                storage_data_original.to_csv(self.storage_csv)
                results_thermal_storage_losses_zero = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

        assert (
            results_thermal_storage_losses_default["TES input power"].values.all()
            == results_thermal_storage_losses_zero["TES input power"].values.all()
        ), f"The invested storage capacity with passed losses {THERM_LOSSES_REL} and {THERM_LOSSES_ABS} that equal zero should be the same as without {THERM_LOSSES_REL} and {THERM_LOSSES_ABS}"

    def teardown_method(self):
        use_cases = ["Thermal_storage_losses_default", "Thermal_storage_losses_zero"]
        for use_case in use_cases:
            if os.path.exists(os.path.join(TEST_OUTPUT_PATH, use_case)):
                shutil.rmtree(
                    os.path.join(TEST_OUTPUT_PATH, use_case), ignore_errors=True
                )

    # # this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
    # # alone is called
    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in (TESTS_ON_MASTER),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
    def test_installedCap_zero_equal_installedCap_nan(self, margs):
        """
        This test checks if the invested storage capacity of an optimized GenericStorage
        where NaN is passed with installedCap is equal to the one of an optimized GenericStorage
        where zero is passed with installedCap.
        """
        use_cases = [
            "Thermal_storage_installedCap_nan",
            "Thermal_storage_installedCap_zero",
        ]

        storage_data_original = pd.read_csv(self.storage_csv, header=0, index_col=0)
        storage_data = storage_data_original.copy()
        storage_data["storage_01"][
            "storage_filename"
        ] = self.storage_opt_with_fixed_losses_float
        storage_data.to_csv(self.storage_csv)

        for use_case in use_cases:
            output_path = os.path.join(TEST_OUTPUT_PATH, use_case)
            if os.path.exists(output_path):
                shutil.rmtree(output_path, ignore_errors=True)
            if os.path.exists(output_path) is False:
                os.mkdir(output_path)

            if use_case == "Thermal_storage_installedCap_nan":
                storage_xx_data_original = pd.read_csv(
                    self.storage_xx, header=0, index_col=0
                )
                storage_xx_data = storage_xx_data_original.copy()
                storage_xx_data["storage capacity"][INSTALLED_CAP] = "NA"
                storage_xx_data.to_csv(self.storage_xx)
                try:
                    main(
                        display_output="warning",
                        path_input_folder=TEST_INPUT_PATH,
                        path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                        input_type="csv",
                        overwrite=True,
                        save_png=False,
                        lp_file_output=True,
                    )
                except:
                    print(
                        "Please check the main input parameters for errors. "
                        "This exception prevents that energyStorage.py is "
                        "overwritten in case running the main errors out."
                    )

                storage_xx_data_original.to_csv(self.storage_xx, na_rep="NA")
                storage_data_original.to_csv(self.storage_csv)
                results_thermal_storage_installedCap_nan = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

            elif use_case == "Thermal_storage_installedCap_zero":
                try:
                    main(
                        display_output="warning",
                        path_input_folder=TEST_INPUT_PATH,
                        path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
                        input_type="csv",
                        overwrite=True,
                        save_png=False,
                        lp_file_output=True,
                    )
                except:
                    print(
                        "Please check the main input parameters for errors. "
                        "This exception prevents that energyStorage.py is "
                        "overwritten in case running the main errors out."
                    )
                results_thermal_storage_installedCap_zero = pd.read_excel(
                    os.path.join(
                        TEST_OUTPUT_PATH, use_case, "timeseries_all_busses.xlsx"
                    ),
                    sheet_name="Heat",
                )

        assert (
            results_thermal_storage_installedCap_zero["TES input power"].values.all()
            == results_thermal_storage_installedCap_nan["TES input power"].values.all()
        ), f"The invested storage capacity with {INSTALLED_CAP} that equals zero should be the same as with {INSTALLED_CAP} set to NaN"

    def teardown_method(self):
        use_cases = [
            "Thermal_storage_installedCap_nan",
            "Thermal_storage_installedCap_zero",
        ]
        for use_case in use_cases:
            if os.path.exists(os.path.join(TEST_OUTPUT_PATH, use_case)):
                shutil.rmtree(
                    os.path.join(TEST_OUTPUT_PATH, use_case), ignore_errors=True
                )
