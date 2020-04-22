"""
- Aggregate demand profiles to a total demand profile
- Plotting all energy flows for both 14 and 365 days for each energy bus
- Store timeseries of all energy flows to excel (one sheet = one energy bus)
- execute function: plot optimised capacities as a barchart (F1)
- execute function: plot all annuities as a barchart (F1)
- store scalars/KPI to excel
- process dictionary so that it can be stored to Json
- store dictionary to Json
"""

import os
import sys
import shutil
import pytest
import argparse
import logging

import pandas as pd
import numpy as np
import src.F0_output as F0

OUTPUT_PATH = os.path.abspath(os.path.join(".", "tests", "test_outputs"))


start_time = "2020-01-01 00:00"
periods = 3
values = [0, 1, 2]

pandas_DatetimeIndex = pd.date_range(start=start_time, periods=periods, freq="60min")
pandas_Series = pd.Series(values, index=pandas_DatetimeIndex)
pandas_Dataframe = pd.DataFrame({"a": values, "b": values})
scalar = 2

json_test_dictionary = {
    "bool": True,
    "str": "str",
    "numpy_int64": np.int64(scalar),
    "pandas_DatetimeIndex": pandas_DatetimeIndex,
    "pandas_Timestamp": pd.Timestamp(start_time),
    "pandas_series": pandas_Series,
    "numpy_array": np.array(values),
    "pandas_Dataframe": pandas_Dataframe,
}

unknown_type = np.float32(scalar / 10)

bus = pd.DataFrame({"timeseries 1": pandas_Series, "timeseries 2": pandas_Series})

# def test_evaluate_result_dictionary():
#    assert 0 == 0


# def test_plot_energy_flows_limit_to_14_days():
#    assert 0 == 0


# def test_plot_energy_flows_limit_to_365_days():
#    assert 0 == 0


class TestFileCreation:
    if not os.path.exists(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)

    def test_store_barchart_for_capacities(self):
        dict_scalar_capacities = {
            "simulation_settings": {"path_output_folder": OUTPUT_PATH},
            "project_data": {
                "project_name": "a_project",
                "scenario_name": "a_scenario",
            },
            "kpi": {
                "scalar_matrix": pd.DataFrame(
                    {"label": ["asset_a", "asset_b"], "optimizedAddCap": [1, 2]}
                )
            },
        }
        F0.plot_optimized_capacities(dict_scalar_capacities)
        assert (
            os.path.exists(
                os.path.join(OUTPUT_PATH, "optimal_additional_capacities.png")
            )
            is True
        )

    def test_store_scalars_to_excel_two_tabs_dict(self):
        dict_scalars_two_tabs_dict = {
            "simulation_settings": {"path_output_folder": OUTPUT_PATH},
            "kpi": {
                "economic": pandas_Dataframe,
                "technical": {"param1": 1, "param2": 2},
            },
        }
        F0.store_scalars_to_excel(dict_scalars_two_tabs_dict)
        assert os.path.exists(os.path.join(OUTPUT_PATH, "scalars" + ".xlsx")) is True

    def test_store_scalars_to_excel_two_tabs_no_dict(self):
        dict_scalars_two_tabs = {
            "simulation_settings": {"path_output_folder": OUTPUT_PATH},
            "kpi": {"economic": pandas_Dataframe, "technical": pandas_Dataframe},
        }

        F0.store_scalars_to_excel(dict_scalars_two_tabs)
        assert os.path.exists(os.path.join(OUTPUT_PATH, "scalars" + ".xlsx")) is True

    def test_store_each_bus_timeseries_to_excel_and_png_one_bus(self):
        dict_timeseries_test_one_bus = {
            "simulation_settings": {"path_output_folder": OUTPUT_PATH},
            "optimizedFlows": {"a_bus": bus},
        }

        F0.store_timeseries_all_busses_to_excel(dict_timeseries_test_one_bus)
        test = False
        if (
            os.path.exists(os.path.join(OUTPUT_PATH, "timeseries_all_busses" + ".xlsx"))
            is True
        ):
            if (
                os.path.exists(os.path.join(OUTPUT_PATH, "a_bus" + " flows.png"))
                is True
            ):
                test = True
        assert test is True

    def test_store_each_bus_timeseries_to_excel_and_png_two_busses(self):
        dict_timeseries_test_two_busses = {
            "simulation_settings": {"path_output_folder": OUTPUT_PATH},
            "optimizedFlows": {"a_bus": bus, "b_bus": bus},
        }
        F0.store_timeseries_all_busses_to_excel(dict_timeseries_test_two_busses)
        test = False
        if (
            os.path.exists(os.path.join(OUTPUT_PATH, "timeseries_all_busses" + ".xlsx"))
            is True
        ):
            if (
                os.path.exists(os.path.join(OUTPUT_PATH, "a_bus" + " flows.png"))
                is True
            ):
                if (
                    os.path.exists(os.path.join(OUTPUT_PATH, "b_bus" + " flows.png"))
                    is True
                ):
                    test = True

        assert test is True

    def test_store_dict_into_json(self):
        file_name = "test_json_converter"
        F0.store_as_json(json_test_dictionary, OUTPUT_PATH, file_name)
        assert os.path.exists(os.path.join(OUTPUT_PATH, file_name + ".json")) is True

    def teardown_module(self):
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)


class TestDictionaryToJsonConversion:
    if not os.path.exists(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)

    def test_processing_dict_for_json_export_parse_bool(self):
        file_name = "test_json_bool"
        F0.store_as_json(json_test_dictionary["bool"], OUTPUT_PATH, file_name)
        assert os.path.exists(os.path.join(OUTPUT_PATH, file_name + ".json")) is True

    def test_processing_dict_for_json_export_parse_str(self):
        file_name = "test_json_str"
        F0.store_as_json(json_test_dictionary["str"], OUTPUT_PATH, file_name)
        assert os.path.exists(os.path.join(OUTPUT_PATH, file_name + ".json")) is True

    def test_processing_dict_for_json_export_parse_numpy_int64(self):
        expr = F0.convert(json_test_dictionary["numpy_int64"])
        assert expr == scalar

    def test_processing_dict_for_json_export_parse_pandas_DatetimeIndex(self):
        expr = F0.convert(json_test_dictionary["pandas_DatetimeIndex"])
        assert expr == "date_range"

    def test_processing_dict_for_json_export_parse_pandas_Timestamp(self):
        expr = F0.convert(json_test_dictionary["pandas_Timestamp"])
        test = False
        if expr == start_time:
            test = True
        assert test == False

    def test_processing_dict_for_json_export_parse_pandas_series(self):
        expr = F0.convert(json_test_dictionary["pandas_series"])
        assert expr == "pandas timeseries"

    def test_processing_dict_for_json_export_parse_numpy_array(self):
        expr = F0.convert(json_test_dictionary["numpy_array"])
        assert expr == "numpy timeseries"

    def test_processing_dict_for_json_export_parse_pandas_Dataframe(self):
        expr = F0.convert(json_test_dictionary["pandas_Dataframe"])
        assert expr == "pandas dataframe"

    def test_processing_dict_for_json_export_parse_unknown(self):
        with pytest.raises(TypeError):
            F0.convert(unknown_type)

    def teardown_module(self):
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
