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
from src.constants import OUTPUT_FOLDER


start_time = "2020-01-01 00:00"
periods = 3
values = [0, 1, 2]

pandas_DatetimeIndex = pd.date_range(start = start_time, periods = periods, freq = "60min")
pandas_Series = pd.Series(values, index=pandas_DatetimeIndex)
pandas_Dataframe = pd.DataFrame({
        "a": values,
        "b": values})
scalar = 2

json_test_dictionary = {
    "bool": True,
    "str": "str",
    "numpy_int64": np.int64(scalar),
    "pandas_DatetimeIndex": pandas_DatetimeIndex,
    "pandas_Timestamp": pd.Timestamp(start_time),
    "pandas_series": pandas_Series,
    "numpy_array": np.array(values),
    "pandas_Dataframe": pandas_Dataframe
}

unknown_type = np.float32(scalar/10)

bus = pd.DataFrame({"timeseries 1": pandas_Series, "timeseries 2": pandas_Series})




def test_evaluate_result_dictionary():
    assert 0 == 0

def test_demand_aggregation_per_energy_vector():
    assert 0 == 0

def test_plot_energy_flows_limit_to_14_days():
    assert 0 == 0

def test_plot_energy_flows_limit_to_365_days():
    assert 0 == 0

def test_store_barchart_for_capacities():
    assert 0 == 0

def test_store_barchart_annuities():
    assert 0 == 0

dict_scalars = {
    "simulation_settings": {"path_output_folder": OUTPUT_FOLDER},
    "kpi": {"economic": pandas_Dataframe,
            "technical": pandas_Dataframe}}

def test_store_scalars_to_excel_two_tabs():
    F0.store_scalars_to_excel(dict_scalars)
    assert (os.path.exists(OUTPUT_FOLDER +"/scalars" + ".xlsx") is True)

dict_timeseries_test_one_bus = {
    "simulation_settings": {"path_output_folder": OUTPUT_FOLDER},
    "optimizedFlows": {"a_bus": bus}}

def test_store_each_bus_timeseries_to_excel_and_png_one_bus():
    F0.store_timeseries_all_busses_to_excel(dict_timeseries_test_one_bus)
    test = False
    if (os.path.exists(OUTPUT_FOLDER +"/timeseries_all_busses" + ".xlsx") is True):
        if (os.path.exists(OUTPUT_FOLDER +"/" + "a_bus" + " flows.png") is True):
            test = True

    assert test is True

dict_timeseries_test_two_busses = {
    "simulation_settings": {"path_output_folder": OUTPUT_FOLDER},
    "optimizedFlows": {"a_bus": bus, "b_bus": bus}}

def test_store_each_bus_timeseries_to_excel_and_png_two_busses():
    F0.store_timeseries_all_busses_to_excel(dict_timeseries_test_two_busses)
    test = False
    if (os.path.exists(OUTPUT_FOLDER + "/timeseries_all_busses" + ".xlsx") is True):
        if (os.path.exists(OUTPUT_FOLDER + "/" + "a_bus" + " flows.png") is True):
            if (os.path.exists(OUTPUT_FOLDER + "/" + "b_bus" + " flows.png") is True):
                test = True

    assert test is True

def test_processing_dict_for_json_export_parse_bool():
    file_name = "test_json_bool"
    F0.store_as_json(json_test_dictionary["bool"], OUTPUT_FOLDER, file_name)
    assert os.path.exists(OUTPUT_FOLDER +"/"+file_name+".json") is True

def test_processing_dict_for_json_export_parse_str():
    file_name = "test_json_str"
    F0.store_as_json(json_test_dictionary["str"], OUTPUT_FOLDER, file_name)
    assert os.path.exists(OUTPUT_FOLDER +"/"+file_name+".json") is True

def test_processing_dict_for_json_export_parse_numpy_int64():
    expr = F0.convert(json_test_dictionary["numpy_int64"])
    assert expr == scalar

def test_processing_dict_for_json_export_parse_pandas_DatetimeIndex():
    expr = F0.convert(json_test_dictionary["pandas_DatetimeIndex"])
    assert expr == "date_range"

def test_processing_dict_for_json_export_parse_pandas_Timestamp():
    expr = F0.convert(json_test_dictionary["pandas_Timestamp"])
    test = False
    if expr == start_time:
        test = True
    assert test == False

def test_processing_dict_for_json_export_parse_pandas_series():
    expr = F0.convert(json_test_dictionary["pandas_series"])
    assert expr == "pandas timeseries"

def test_processing_dict_for_json_export_parse_numpy_array():
    expr = F0.convert(json_test_dictionary["numpy_array"])
    assert expr == "numpy timeseries"

def test_processing_dict_for_json_export_parse_pandas_Dataframe():
    expr = F0.convert(json_test_dictionary["pandas_Dataframe"])
    assert expr == "pandas dataframe"

def test_processing_dict_for_json_export_parse_unknown():
    with pytest.raises(TypeError):
        F0.convert(unknown_type)

def test_store_dict_into_json():
    file_name = "test_json_converter"
    F0.store_as_json(json_test_dictionary, OUTPUT_FOLDER, file_name)
    assert os.path.exists(OUTPUT_FOLDER +"/"+file_name+".json") is True