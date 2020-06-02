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

import src.A0_initialization as initializing
import src.B0_data_input_json as B0
import src.F0_output as F0
from src.constants_json_strings import LABEL, PROJECT_DATA, SECTORS
from mvs_eland_tool import main
from .constants import (
    EXECUTE_TESTS_ON,
    TESTS_ON_MASTER,
    TEST_REPO_PATH,
    DICT_PLOTS,
    PDF_REPORT,
    TYPE_DATETIMEINDEX,
    TYPE_DATAFRAME,
    TYPE_SERIES,
    TYPE_TIMESTAMP,
)

PARSER = initializing.create_parser()

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
    "bool": True,
    "str": "str",
    "numpy_int64": np.int64(SCALAR),
    "pandas_DatetimeIndex": pandas_DatetimeIndex,
    "pandas_Timestamp": pd.Timestamp(START_TIME),
    "pandas_series": pandas_Series,
    "pandas_series_tuple_name": pandas_Series_tuple_name,
    "numpy_array": np.array(VALUES),
    "pandas_Dataframe": pandas_Dataframe,
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

    def test_store_barchart_for_capacities_no_additional_capacities(self):
        """ """
        dict_scalar_capacities = {
            "simulation_settings": {"path_output_folder": OUTPUT_PATH},
            PROJECT_DATA: {"project_name": "a_project", "scenario_name": "a_scenario",},
            "kpi": {
                "scalar_matrix": pd.DataFrame(
                    {LABEL: ["asset_a", "asset_b"], "optimizedAddCap": [0, 0]}
                )
            },
        }
        dict_scalar_capacities.update(copy.deepcopy(DICT_PLOTS))
        show_optimal_capacities = F0.plot_optimized_capacities(dict_scalar_capacities)
        assert show_optimal_capacities is False

    def test_store_barchart_for_capacities_with_additional_capacities(self):
        """ """
        dict_scalar_capacities = {
            "simulation_settings": {"path_output_folder": OUTPUT_PATH},
            PROJECT_DATA: {"project_name": "a_project", "scenario_name": "a_scenario",},
            "kpi": {
                "scalar_matrix": pd.DataFrame(
                    {LABEL: ["asset_a", "asset_b"], "optimizedAddCap": [1, 2]}
                )
            },
        }
        dict_scalar_capacities.update(copy.deepcopy(DICT_PLOTS))
        show_optimal_capacities = F0.plot_optimized_capacities(dict_scalar_capacities)
        assert show_optimal_capacities is True

    def test_store_scalars_to_excel_two_tabs_dict(self):
        """ """
        dict_scalars_two_tabs_dict = {
            "simulation_settings": {"path_output_folder": OUTPUT_PATH},
            "kpi": {
                "economic": pandas_Dataframe,
                "technical": {"param1": 1, "param2": 2},
            },
        }
        F0.store_scalars_to_excel(dict_scalars_two_tabs_dict)
        assert os.path.exists(os.path.join(OUTPUT_PATH, "scalars.xlsx")) is True

    def test_store_scalars_to_excel_two_tabs_no_dict(self):
        """ """
        dict_scalars_two_tabs = {
            "simulation_settings": {"path_output_folder": OUTPUT_PATH},
            "kpi": {"economic": pandas_Dataframe, "technical": pandas_Dataframe},
        }

        F0.store_scalars_to_excel(dict_scalars_two_tabs)
        assert os.path.exists(os.path.join(OUTPUT_PATH, "scalars.xlsx")) is True

    def test_store_each_bus_timeseries_to_excel_and_png_one_bus(self):
        """ """
        dict_timeseries_test_one_bus = {
            PROJECT_DATA: {"project_name": "a_project", "scenario_name": "a_scenario",},
            "simulation_settings": {"path_output_folder": OUTPUT_PATH},
            "optimizedFlows": {"a_bus": BUS},
        }
        dict_timeseries_test_one_bus.update(copy.deepcopy(DICT_PLOTS))
        F0.store_timeseries_all_busses_to_excel(dict_timeseries_test_one_bus)
        assert (
            os.path.exists(os.path.join(OUTPUT_PATH, "timeseries_all_busses.xlsx"))
            is True
        )
        assert (
            os.path.exists(os.path.join(OUTPUT_PATH, "a_bus_flows_365_days.png"))
            is True
        )

    def test_store_each_bus_timeseries_to_excel_and_png_two_busses(self):
        """ """
        dict_timeseries_test_two_busses = {
            PROJECT_DATA: {"project_name": "a_project", "scenario_name": "a_scenario",},
            "simulation_settings": {"path_output_folder": OUTPUT_PATH},
            "optimizedFlows": {"a_bus": BUS, "b_bus": BUS},
        }
        print(DICT_PLOTS)
        dict_timeseries_test_two_busses.update(copy.deepcopy(DICT_PLOTS))
        F0.store_timeseries_all_busses_to_excel(dict_timeseries_test_two_busses)
        assert (
            os.path.exists(os.path.join(OUTPUT_PATH, "timeseries_all_busses.xlsx"))
            is True
        )
        assert (
            os.path.exists(os.path.join(OUTPUT_PATH, "a_bus_flows_365_days.png"))
            is True
        )
        assert (
            os.path.exists(os.path.join(OUTPUT_PATH, "b_bus_flows_365_days.png"))
            is True
        )

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
        return_value=PARSER.parse_args(["-o", OUTPUT_PATH, "-pdf"]),
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
        F0.store_as_json(JSON_TEST_DICTIONARY["bool"], OUTPUT_PATH, file_name)
        assert os.path.exists(os.path.join(OUTPUT_PATH, file_name + ".json")) is True

    def test_processing_dict_for_json_export_parse_str(self):
        """ """
        file_name = "test_json_str"
        F0.store_as_json(JSON_TEST_DICTIONARY["str"], OUTPUT_PATH, file_name)
        assert os.path.exists(os.path.join(OUTPUT_PATH, file_name + ".json")) is True

    def test_processing_dict_for_json_export_parse_numpy_int64(self):
        """ """
        expr = F0.convert(JSON_TEST_DICTIONARY["numpy_int64"])
        assert expr == SCALAR

    def test_processing_dict_for_json_export_parse_pandas_DatetimeIndex(self):
        """ """
        expr = F0.convert(JSON_TEST_DICTIONARY["pandas_DatetimeIndex"])
        assert (
            expr
            == TYPE_DATETIMEINDEX
            + '{"columns":[0],"index":[1577836800000,1577840400000,1577844000000],"data":[[1577836800000],[1577840400000],[1577844000000]]}'
        )

    def test_processing_dict_for_json_export_parse_pandas_Timestamp(self):
        """ """
        expr = F0.convert(JSON_TEST_DICTIONARY["pandas_Timestamp"])
        assert expr == TYPE_TIMESTAMP + "2020-01-01 00:00:00"

    def test_processing_dict_for_json_export_parse_pandas_series(self):
        """ """
        expr = F0.convert(JSON_TEST_DICTIONARY["pandas_series"])
        assert (
            expr
            == TYPE_SERIES
            + '{"name":null,"index":[1577836800000,1577840400000,1577844000000],"data":[0,1,2]}'
        )

    def test_processing_dict_for_json_export_parse_numpy_array(self):
        """ """
        expr = F0.convert(JSON_TEST_DICTIONARY["numpy_array"])
        assert expr == '{"array": [0, 1, 2]}'

    def test_processing_dict_for_json_export_parse_pandas_Dataframe(self):
        """ """
        expr = F0.convert(JSON_TEST_DICTIONARY["pandas_Dataframe"])
        assert (
            expr
            == TYPE_DATAFRAME
            + '{"columns":["a","b"],"index":[0,1,2],"data":[[0,0],[1,1],[2,2]]}'
        )

    def test_processing_dict_for_json_export_parse_unknown(self):
        """ """
        with pytest.raises(TypeError):
            F0.convert(UNKNOWN_TYPE)

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
            os.path.join(OUTPUT_PATH, self.file_name + ".json")
        )

    def test_load_json_parse_pandas_series(self):
        """ """
        k = "pandas_series"
        assert self.value_dict[k].equals(JSON_TEST_DICTIONARY[k])

    def test_load_json_parse_pandas_series_tuple_name(self):
        """ """
        k = "pandas_series_tuple_name"
        assert self.value_dict[k].equals(JSON_TEST_DICTIONARY[k])

    def test_load_json_parse_numpy_array(self):
        """ """
        k = "numpy_array"
        assert np.array_equal(self.value_dict[k], JSON_TEST_DICTIONARY[k])

    def test_load_json_export_parse_pandas_Dataframe(self):
        """ """
        k = "pandas_Dataframe"
        assert self.value_dict[k].equals(JSON_TEST_DICTIONARY[k])

    def test_load_json_export_parse_pandas_DatatimeIndex(self):
        """ """
        k = "pandas_DatetimeIndex"
        assert self.value_dict[k].equals(JSON_TEST_DICTIONARY[k])

    def test_load_json_export_parse_pandas_Timestamp(self):
        """ """
        k = "pandas_Timestamp"
        assert self.value_dict[k] == JSON_TEST_DICTIONARY[k]

    def teardown_class(self):
        """ """
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
