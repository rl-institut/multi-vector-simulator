import os
import shutil

import mock
import pandas as pd

import multi_vector_simulator.A0_initialization as A0
import multi_vector_simulator.A1_csv_to_json as A1
import multi_vector_simulator.B0_data_input_json as B0

from multi_vector_simulator.utils.constants import INPUT_FOLDER, OUTPUT_FOLDER
from multi_vector_simulator.utils.constants_json_strings import (
    SIMULATION_SETTINGS,
    VALUE,
    START_DATE,
    EVALUATED_PERIOD,
    TIMESTEP,
    END_DATE,
    TIME_INDEX,
    PERIODS,
)
from _constants import (
    JSON_PATH,
    CSV_PATH,
    CSV_FNAME,
    CSV_ELEMENTS,
    JSON_CSV_PATH,
    CSV_EXT,
    PATH_INPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
    PATH_OUTPUT_FOLDER_INPUTS,
    TEST_REPO_PATH,
    DATA_TYPE_JSON_KEY,
    TYPE_DATETIMEINDEX,
    TYPE_SERIES,
    TYPE_NDARRAY,
    TYPE_DATAFRAME,
    TYPE_TIMESTAMP,
)


def test_load_json_overwrite_output_folder_from_json():
    dict_values = B0.load_json(JSON_PATH, path_output_folder="test")
    assert dict_values[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER] == "test"
    assert dict_values[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER_INPUTS] == os.path.join(
        "test", INPUT_FOLDER
    )


def test_load_json_overwrite_input_folder_from_json():
    dict_values = B0.load_json(JSON_PATH, path_input_folder="test")
    assert dict_values[SIMULATION_SETTINGS][PATH_INPUT_FOLDER] == "test"


# process start_date/simulation_duration to pd.datatimeindex (future: Also consider timesteplenghts)
def test_retrieve_datetimeindex_for_simulation():
    simulation_settings = {
        START_DATE: "2020-01-01",
        EVALUATED_PERIOD: {VALUE: 1},
        TIMESTEP: {VALUE: 60},
    }
    B0.retrieve_date_time_info(simulation_settings)
    for k in (START_DATE, END_DATE, TIME_INDEX):
        assert (
            k in simulation_settings.keys()
        ), f"Function does not add {k} to the simulation settings."
    assert simulation_settings[START_DATE] == pd.Timestamp(
        "2020-01-01 00:00:00"
    ), f"Function incorrectly parses the timestamp."
    assert simulation_settings[END_DATE] == pd.Timestamp(
        "2020-01-01 23:00:00"
    ), f"Function incorrectly parses the timestamp."
    assert (
        simulation_settings[PERIODS] == 24
    ), f"Function incorrectly identifies the number of evaluated periods."


PARSER = A0.mvs_arg_parser()


class TestTemporaryJsonFileDisposal:

    test_in_path = os.path.join(TEST_REPO_PATH, INPUT_FOLDER)
    test_out_path = os.path.join(TEST_REPO_PATH, OUTPUT_FOLDER)

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            [
                "-f",
                "-log",
                "warning",
                "-i",
                test_in_path,
                "-o",
                test_out_path,
                "-ext",
                CSV_EXT,
            ]
        ),
    )
    def test_load_json_removes_json_file_from_inputs_folder(self, m_args):
        A0.process_user_arguments()

        A1.create_input_json(input_directory=CSV_PATH, pass_back=True)
        dict_values = B0.load_json(
            JSON_CSV_PATH, path_output_folder=self.test_out_path, move_copy=True
        )

        assert os.path.exists(os.path.join(CSV_PATH, CSV_ELEMENTS, CSV_FNAME,)) is False

        assert os.path.exists(os.path.join(CSV_PATH, CSV_FNAME,)) is False

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            [
                "-f",
                "-log",
                "warning",
                "-i",
                test_in_path,
                "-o",
                test_out_path,
                "-ext",
                CSV_EXT,
            ]
        ),
    )
    def test_load_json_copies_json_file_to_output_folder(self, m_args):
        A0.process_user_arguments()

        A1.create_input_json(input_directory=CSV_PATH, pass_back=True)
        dict_values = B0.load_json(
            JSON_CSV_PATH, path_output_folder=self.test_out_path, move_copy=True
        )

        assert (
            os.path.exists(
                os.path.join(
                    dict_values[SIMULATION_SETTINGS][PATH_OUTPUT_FOLDER_INPUTS],
                    CSV_FNAME,
                )
            )
            is True
        )

    def teardown_method(self):
        if os.path.exists(self.test_out_path):
            shutil.rmtree(self.test_out_path, ignore_errors=True)


class TestConversionJsonToPythonTypes:
    def setup(self):
        self.n_days = 4
        self.start_date = pd.to_datetime("2018-01-01 00:00:00")
        self.end_date = self.start_date + pd.DateOffset(days=self.n_days - 1)
        self.ti = pd.date_range(start=self.start_date, end=self.end_date, freq="1D",)
        self.ti_long = pd.date_range(
            start=self.start_date, end=self.end_date, freq="1H",
        )
        self.test_dict_series = {
            "series": {
                DATA_TYPE_JSON_KEY: TYPE_SERIES,
                VALUE: [d + 1 for d in range(self.n_days)],
            }
        }

        self.test_result_series = pd.Series(
            [d + 1 for d in range(self.n_days)], index=self.ti
        )

    def test_parse_pandas_series_provided_time_index(self):

        pd_series = B0.convert_from_json_to_special_types(
            self.test_dict_series, time_index=self.ti
        )
        assert (pd_series["series"] == self.test_result_series).all()

    def test_parse_pandas_series_provided_shorter_time_index(self, caplog):

        pd_series = B0.convert_from_json_to_special_types(
            self.test_dict_series, time_index=self.ti[:3]
        )

        # collect warning message
        log_msg = caplog.record_tuples[0]

        # check it is a warning
        assert log_msg[1] == 30
        assert (
            "The time index inferred from simulation_settings is longer as the timeserie under the field series"
            in log_msg[2]
        )
        assert (pd_series["series"].values == self.test_result_series.values).all()

    def test_parse_pandas_series_provided_longer_time_index(self, caplog):

        pd_series = B0.convert_from_json_to_special_types(
            self.test_dict_series, time_index=self.ti_long
        )

        # collect warning message
        log_msg = caplog.record_tuples[0]

        # check it is a warning
        assert log_msg[1] == 30
        assert (
            "The time index inferred from simulation_settings is shorter as the timeserie under the field series"
            in log_msg[2]
        )
        assert (pd_series["series"].values == self.test_result_series.values).all()
