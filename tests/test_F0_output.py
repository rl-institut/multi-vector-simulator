"""
- Aggregate demand profiles to a total demand profile
- Plotting all energy flows for both 14 and 365 days for each energy bus
- Store timeseries of all energy flows to excel (one sheet = one energy bus)
- Execute function: plot optimised capacities as a barchart (F1)
- Execute function: plot all annuities as a barchart (F1)
- Store scalars/KPI to excel
- Process dictionary so that it can be stored to Json
- Store dictionary to Json
"""

import copy
import os
import shutil

import mock
import numpy as np
import pandas as pd
import pytest

import multi_vector_simulator.A0_initialization as initializing
import multi_vector_simulator.B0_data_input_json as B0
import multi_vector_simulator.F0_output as F0
from multi_vector_simulator.cli import main
from multi_vector_simulator.utils.constants_json_strings import (
    PROJECT_DATA,
    SIMULATION_SETTINGS,
    PROJECT_NAME,
    SCENARIO_NAME,
    KPI,
    OPTIMIZED_FLOWS,
)
from _constants import (
    EXECUTE_TESTS_ON,
    TEST_REPO_PATH,
    DICT_PLOTS,
    PDF_REPORT,
    DATA_TYPE_JSON_KEY,
    TYPE_DATETIMEINDEX,
    TYPE_DATAFRAME,
    TYPE_SERIES,
    TYPE_NDARRAY,
    TYPE_TIMESTAMP,
    TYPE_BOOL,
    TYPE_INT64,
    TYPE_STR,
    PATH_OUTPUT_FOLDER,
    START_DATE,
)

PARSER = initializing.mvs_arg_parser()

OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "test_outputs")

START_TIME = "2020-01-01 00:00"
PERIODS = 3
VALUES = [0, 1, 2]

pandas_DatetimeIndex = pd.date_range(start=START_TIME, periods=PERIODS, freq="60min")
pandas_Series = pd.Series(VALUES, index=pandas_DatetimeIndex)
pandas_Series_tuple_name = pd.Series(
    VALUES, index=pandas_DatetimeIndex, name=(("A", "B"), "flow")
)
pandas_Dataframe = pd.DataFrame({"a": VALUES, "b": VALUES})
SCALAR = 2

JSON_TEST_DICTIONARY = {
    TYPE_BOOL: True,
    TYPE_STR: "str",
    TYPE_INT64: np.int64(SCALAR),
    TYPE_DATETIMEINDEX: pandas_DatetimeIndex,
    TYPE_TIMESTAMP: pd.Timestamp(START_TIME),
    TYPE_SERIES: pandas_Series,
    "pandas_series_tuple_name": pandas_Series_tuple_name,
    TYPE_NDARRAY: np.array(VALUES),
    TYPE_DATAFRAME: pandas_Dataframe,
}

UNKNOWN_TYPE = np.float32(SCALAR / 10)

BUS = pd.DataFrame({"timeseries 1": pandas_Series, "timeseries 2": pandas_Series})

# def test_evaluate_result_dictionary():
#    assert 0 == 0


# def test_plot_energy_flows_limit_to_14_days():
#    assert 0 == 0


# def test_plot_energy_flows_limit_to_365_days():
#    assert 0 == 0


class TestFileCreation:
    def setup_method(self):
        """ """
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
        os.mkdir(OUTPUT_PATH)

    def test_store_scalars_to_excel_two_tabs_dict(self):
        """ """
        dict_scalars_two_tabs_dict = {
            SIMULATION_SETTINGS: {PATH_OUTPUT_FOLDER: OUTPUT_PATH},
            KPI: {
                "economic": pandas_Dataframe,
                "technical": {"param1": 1, "param2": 2},
            },
        }
        F0.store_scalars_to_excel(dict_scalars_two_tabs_dict)
        assert os.path.exists(os.path.join(OUTPUT_PATH, "scalars.xlsx")) is True

    def test_store_scalars_to_excel_two_tabs_no_dict(self):
        """ """
        dict_scalars_two_tabs = {
            SIMULATION_SETTINGS: {PATH_OUTPUT_FOLDER: OUTPUT_PATH},
            KPI: {"economic": pandas_Dataframe, "technical": pandas_Dataframe},
        }

        F0.store_scalars_to_excel(dict_scalars_two_tabs)
        assert os.path.exists(os.path.join(OUTPUT_PATH, "scalars.xlsx")) is True

    def test_store_each_bus_timeseries_to_excel_and_png_one_bus(self):
        """ """
        dict_timeseries_test_one_bus = {
            PROJECT_DATA: {PROJECT_NAME: "a_project", SCENARIO_NAME: "a_scenario",},
            SIMULATION_SETTINGS: {PATH_OUTPUT_FOLDER: OUTPUT_PATH},
            OPTIMIZED_FLOWS: {"a_bus": BUS},
        }
        dict_timeseries_test_one_bus.update(copy.deepcopy(DICT_PLOTS))
        F0.store_timeseries_all_busses_to_excel(dict_timeseries_test_one_bus)
        assert (
            os.path.exists(os.path.join(OUTPUT_PATH, "timeseries_all_busses.xlsx"))
            is True
        )
        # assert (
        #     os.path.exists(os.path.join(OUTPUT_PATH, "a_bus_flows_365_days.png"))
        #     is True
        # )

    def test_store_each_bus_timeseries_to_excel_and_png_two_busses(self):
        """ """
        dict_timeseries_test_two_busses = {
            PROJECT_DATA: {PROJECT_NAME: "a_project", SCENARIO_NAME: "a_scenario",},
            SIMULATION_SETTINGS: {PATH_OUTPUT_FOLDER: OUTPUT_PATH},
            OPTIMIZED_FLOWS: {"a_bus": BUS, "b_bus": BUS},
        }

        dict_timeseries_test_two_busses.update(copy.deepcopy(DICT_PLOTS))
        F0.store_timeseries_all_busses_to_excel(dict_timeseries_test_two_busses)
        assert (
            os.path.exists(os.path.join(OUTPUT_PATH, "timeseries_all_busses.xlsx"))
            is True
        )
        # assert (
        #     os.path.exists(os.path.join(OUTPUT_PATH, "a_bus_flows_365_days.png"))
        #     is True
        # )
        # assert (
        #     os.path.exists(os.path.join(OUTPUT_PATH, "b_bus_flows_365_days.png"))
        #     is True
        # )

    def test_store_dict_into_json(self):
        """ """
        file_name = "test_json_converter"
        F0.store_as_json(JSON_TEST_DICTIONARY, OUTPUT_PATH, file_name)
        assert os.path.exists(os.path.join(OUTPUT_PATH, file_name + ".json")) is True

    def teardown_method(self):
        """ """
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)


class TestPDFReportCreation:
    def setup_method(self):
        """ """
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)

    @pytest.mark.skipif(
        EXECUTE_TESTS_ON not in ("pdf_report"),
        reason="Benchmark test deactivated, set env variable "
        "EXECUTE_TESTS_ON to 'master' to run this test",
    )
    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=PARSER.parse_args(
            ["-f", "-log", "warning", "-o", OUTPUT_PATH, "-pdf"]
        ),
    )
    def test_generate_pdf_report(self, m_args):
        """Run the simulation with -pdf option to make sure the pdf file is generated """
        main()
        assert os.path.exists(os.path.join(OUTPUT_PATH, PDF_REPORT)) is True

    def teardown_method(self):
        """ """
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)


class TestDictionaryToJsonConversion:
    """ """

    def setup_class(self):
        """ """
        shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
        os.mkdir(OUTPUT_PATH)

    def test_processing_dict_for_json_export_parse_bool(self):
        """ """
        file_name = "test_json_bool"
        F0.store_as_json(JSON_TEST_DICTIONARY[TYPE_BOOL], OUTPUT_PATH, file_name)
        assert os.path.exists(os.path.join(OUTPUT_PATH, file_name + ".json")) is True

    def test_processing_dict_for_json_export_parse_str(self):
        """ """
        file_name = "test_json_str"
        F0.store_as_json(JSON_TEST_DICTIONARY[TYPE_STR], OUTPUT_PATH, file_name)
        assert os.path.exists(os.path.join(OUTPUT_PATH, file_name + ".json")) is True

    def test_processing_dict_for_json_export_parse_numpy_int64(self):
        """ """
        expr = B0.convert_from_special_types_to_json(
            JSON_TEST_DICTIONARY["numpy_int64"]
        )
        assert expr == SCALAR

    def test_processing_dict_for_json_export_parse_pandas_DatetimeIndex(self):
        """ """
        expr = B0.convert_from_special_types_to_json(
            JSON_TEST_DICTIONARY[TYPE_DATETIMEINDEX]
        )
        assert expr == {
            DATA_TYPE_JSON_KEY: TYPE_DATETIMEINDEX,
            "value": [1577836800000000000, 1577840400000000000, 1577844000000000000],
        }

    def test_processing_dict_for_json_export_parse_pandas_Timestamp(self):
        """ """
        expr = B0.convert_from_special_types_to_json(
            JSON_TEST_DICTIONARY[TYPE_TIMESTAMP]
        )
        assert expr == {
            DATA_TYPE_JSON_KEY: TYPE_TIMESTAMP,
            "value": "2020-01-01 00:00:00",
        }

    def test_processing_dict_for_json_export_parse_pandas_series(self):
        """ """
        expr = B0.convert_from_special_types_to_json(JSON_TEST_DICTIONARY[TYPE_SERIES])
        assert expr == {
            DATA_TYPE_JSON_KEY: TYPE_SERIES,
            "value": [0, 1, 2],
        }

    def test_processing_dict_for_json_export_parse_numpy_array(self):
        """ """
        expr = B0.convert_from_special_types_to_json(JSON_TEST_DICTIONARY[TYPE_NDARRAY])
        assert expr == {DATA_TYPE_JSON_KEY: TYPE_NDARRAY, "value": [0, 1, 2]}

    def test_processing_dict_for_json_export_parse_pandas_Dataframe(self):
        """ """
        expr = B0.convert_from_special_types_to_json(
            JSON_TEST_DICTIONARY[TYPE_DATAFRAME]
        )
        assert expr == {
            DATA_TYPE_JSON_KEY: TYPE_DATAFRAME,
            "columns": ["a", "b"],
            "index": [0, 1, 2],
            "data": [[0, 0], [1, 1], [2, 2]],
        }

    def test_processing_dict_for_json_export_parse_unknown(self):
        """ """
        with pytest.raises(TypeError):
            B0.convert_from_special_types_to_json(UNKNOWN_TYPE)

    def teardown_class(self):
        """ """
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)


class TestLoadDictionaryFromJson:
    """ """

    def setup_class(self):
        """ """
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
        os.mkdir(OUTPUT_PATH)
        self.file_name = "test_json_converter"
        F0.store_as_json(JSON_TEST_DICTIONARY, OUTPUT_PATH, self.file_name)
        self.value_dict = B0.load_json(
            os.path.join(OUTPUT_PATH, self.file_name + ".json"),
            flag_missing_values=False,
        )

    # TODO fix input from time parameters for simulation settings
    # def test_load_json_parse_pandas_series(self):
    #     """ """
    #     k = TYPE_SERIES
    #     assert self.value_dict[k].equals(JSON_TEST_DICTIONARY[k])
    #
    # def test_load_json_parse_pandas_series_tuple_name(self):
    #     """ """
    #     k = "pandas_series_tuple_name"
    #     assert self.value_dict[k].equals(JSON_TEST_DICTIONARY[k])

    def test_load_json_parse_numpy_array(self):
        """ """
        k = TYPE_NDARRAY
        assert np.array_equal(self.value_dict[k], JSON_TEST_DICTIONARY[k])

    def test_load_json_export_parse_pandas_Dataframe(self):
        """ """
        k = TYPE_DATAFRAME
        assert self.value_dict[k].equals(JSON_TEST_DICTIONARY[k])

    def test_load_json_export_parse_pandas_DatatimeIndex(self):
        """ """
        k = TYPE_DATETIMEINDEX
        assert self.value_dict[k].equals(JSON_TEST_DICTIONARY[k])
        assert hasattr(self.value_dict[k], "freq")

    def test_load_json_export_parse_pandas_Timestamp(self):
        """ """
        k = TYPE_TIMESTAMP
        assert self.value_dict[k] == JSON_TEST_DICTIONARY[k]

    def teardown_class(self):
        """ """
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
