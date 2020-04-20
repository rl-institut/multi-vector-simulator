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

import src.A0_initialization as initializing

def test_demand_aggregation_per_energy_vector():
    assert 0

def test_store_plot_energy_flows_two_busses():
    assert 0

def test_plot_energy_flows_limit_to_14_days():
    assert 0

def test_plot_energy_flows_limit_to_365_days():
    assert 0

def test_store_barchart_for_capacities():
    assert 0

def test_store_barchart_annuities():
    assert 0

def test_store_scalars_to_excel():
    assert 0

def test_store_timeseries_to_excel():
    assert 0

def test_processing_dict_for_json_export_parse_int():
    assert 0

def test_processing_dict_for_json_export_parse_pd_DatetimeIndex():
    assert 0

def test_processing_dict_for_json_export_parse_pd_datetime():
    assert 0

def test_processing_dict_for_json_export_parse_pd_series():
    assert 0

def test_processing_dict_for_json_export_parse_np_array():
    assert 0

def test_processing_dict_for_json_export_parse_pd_Dataframe():
    assert 0

def test_processing_dict_for_json_export_parse_unknown():
    assert TypeError

def test_store_dict_into_json():
    assert 0