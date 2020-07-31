import pandas as pd
import pytest

import src.C0_data_processing as C0

from src.constants_json_strings import (
    UNIT,
    ENERGY_PROVIDERS,
    ENERGY_STORAGE,
    ENERGY_CONSUMPTION,
    ENERGY_PRODUCTION,
    ENERGY_CONVERSION,
    ENERGY_BUSSES,
OUTFLOW_DIRECTION,
INFLOW_DIRECTION,
    PROJECT_DURATION,
    DISCOUNTFACTOR,
    TAX,
    VALUE,
    LABEL,
    DISPATCH_PRICE,
    SPECIFIC_COSTS_OM,
    DEVELOPMENT_COSTS,
    SPECIFIC_COSTS,
    LIFETIME,
    SIMULATION_SETTINGS,
    PEAK_DEMAND_PRICING_PERIOD,
    EVALUATED_PERIOD,
    START_DATE,
    END_DATE,
    TIMESTEP,
    TIME_INDEX,
    ANNUITY_FACTOR,
    SIMULATION_ANNUITY,
    LIFETIME_SPECIFIC_COST,
    CRF,
    ANNUITY_SPECIFIC_INVESTMENT_AND_OM,
    LIFETIME_SPECIFIC_COST_OM,
    LIFETIME_PRICE_DISPATCH,
    PERIODS,
    BUS_SUFFIX,
)
from .constants import TYPE_STR

# process start_date/simulation_duration to pd.datatimeindex (future: Also consider timesteplenghts)
def test_retrieve_datetimeindex_for_simulation():
    simulation_settings = {
        START_DATE: "2020-01-01",
        EVALUATED_PERIOD: {VALUE: 1},
        TIMESTEP: {VALUE: 60},
    }
    C0.simulation_settings(simulation_settings)
    for k in (START_DATE, END_DATE, TIME_INDEX):
        assert k in simulation_settings.keys()
    assert simulation_settings[START_DATE] == pd.Timestamp("2020-01-01 00:00:00")
    assert simulation_settings[END_DATE] == pd.Timestamp("2020-01-01 23:00:00")
    assert simulation_settings[PERIODS] == 24


def test_adding_economic_parameters_C2():
    economic_parameters = {
        PROJECT_DURATION: {VALUE: 20},
        DISCOUNTFACTOR: {VALUE: 0.15},
    }
    C0.economic_parameters(economic_parameters)
    # the actual value of the annuity factor should have been checked in C2
    for k in (ANNUITY_FACTOR, CRF):
        assert k in economic_parameters.keys()


settings = {EVALUATED_PERIOD: {VALUE: 365}}

economic_data = {
    PROJECT_DURATION: {VALUE: 20},
    ANNUITY_FACTOR: {VALUE: 1},
    CRF: {VALUE: 1},
    DISCOUNTFACTOR: {VALUE: 0},
    TAX: {VALUE: 0},
}

dict_asset = {
    SPECIFIC_COSTS_OM: {VALUE: 1, UNIT: "a_unit"},
    CRF: {VALUE: 1},
    SPECIFIC_COSTS: {VALUE: 1, UNIT: "a_unit"},
    DISPATCH_PRICE: {VALUE: 1},
    DEVELOPMENT_COSTS: {VALUE: 1},
    LIFETIME: {VALUE: 20},
    UNIT: "a_unit",
}


def test_evaluate_lifetime_costs_adds_all_parameters():
    C0.evaluate_lifetime_costs(settings, economic_data, dict_asset)
    for k in (
        LIFETIME_SPECIFIC_COST,
        ANNUITY_SPECIFIC_INVESTMENT_AND_OM,
        LIFETIME_SPECIFIC_COST_OM,
        LIFETIME_PRICE_DISPATCH,
        SIMULATION_ANNUITY,
    ):
        assert k in dict_asset.keys()


def test_determine_lifetime_price_dispatch_as_int():
    dict_asset = {DISPATCH_PRICE: {VALUE: 1}}
    C0.determine_lifetime_price_dispatch(dict_asset, economic_data)
    assert LIFETIME_PRICE_DISPATCH in dict_asset.keys()
    assert isinstance(dict_asset[LIFETIME_PRICE_DISPATCH][VALUE], float) or isinstance(
        dict_asset[LIFETIME_PRICE_DISPATCH][VALUE], int
    )


def test_determine_lifetime_price_dispatch_as_float():
    dict_asset = {DISPATCH_PRICE: {VALUE: 1.5}}
    C0.determine_lifetime_price_dispatch(dict_asset, economic_data)
    assert LIFETIME_PRICE_DISPATCH in dict_asset.keys()
    assert isinstance(dict_asset[LIFETIME_PRICE_DISPATCH][VALUE], float)


def test_determine_lifetime_price_dispatch_as_list():
    dict_asset = {DISPATCH_PRICE: {VALUE: [1.0, 1.0]}}
    C0.determine_lifetime_price_dispatch(dict_asset, economic_data)
    assert LIFETIME_PRICE_DISPATCH in dict_asset.keys()
    assert isinstance(dict_asset[LIFETIME_PRICE_DISPATCH][VALUE], float)
    # todo this should be here some time, shouldnt it? assert isinstance(dict_asset[LIFETIME_OPEX_VAR][VALUE], list)

TEST_START_TIME = "2020-01-01 00:00"
TEST_PERIODS = 3
VALUES = [0, 1, 2]

pandas_DatetimeIndex = pd.date_range(
    start=TEST_START_TIME, periods=TEST_PERIODS, freq="60min"
)
pandas_Series = pd.Series(VALUES, index=pandas_DatetimeIndex)

def test_determine_lifetime_price_dispatch_as_timeseries():
    dict_asset = {DISPATCH_PRICE: {VALUE: pandas_Series}}
    C0.determine_lifetime_price_dispatch(dict_asset, economic_data)
    assert LIFETIME_PRICE_DISPATCH in dict_asset.keys()
    assert isinstance(dict_asset[LIFETIME_PRICE_DISPATCH][VALUE], pd.Series)

def test_determine_lifetime_price_dispatch_is_other():
    dict_asset = {DISPATCH_PRICE: {VALUE: TYPE_STR}}
    with pytest.raises(ValueError):
        C0.determine_lifetime_price_dispatch(dict_asset, economic_data)


def test_define_dso_sinks_and_sources_raises_PeakDemandPricingPeriodsOnlyForYear():
    dict_test = {
        ENERGY_PROVIDERS: {"a_dso": {PEAK_DEMAND_PRICING_PERIOD: {VALUE: 2}}},
        SIMULATION_SETTINGS: {EVALUATED_PERIOD: {VALUE: 30}},
    }
    with pytest.raises(ValueError):
        C0.define_dso_sinks_and_sources(dict_test, "a_dso")

def test_define_energyBusses():
    asset_names = ["asset_name_" + str(i) for i in range(0,6)]
    in_bus_names = ["in_bus_name_" + str(i) for i in range(0,6)]
    out_bus_names = ["out_bus_name_" + str(i) for i in range(0,6)]

    dict_test = {
        ENERGY_PROVIDERS: {
            asset_names[0]: {
                LABEL: asset_names[0],
                OUTFLOW_DIRECTION: out_bus_names[0],
                INFLOW_DIRECTION: in_bus_names[0]}},
        ENERGY_STORAGE: {
            asset_names[1]: {
                LABEL: asset_names[1],
                OUTFLOW_DIRECTION: out_bus_names[1],
                INFLOW_DIRECTION: in_bus_names[1]}},
        ENERGY_CONSUMPTION: {
            asset_names[2]: {
                LABEL: asset_names[2],
                INFLOW_DIRECTION: in_bus_names[2]}},
        ENERGY_PRODUCTION: {
            asset_names[3]: {
                LABEL: asset_names[3],
                OUTFLOW_DIRECTION: out_bus_names[2]}},
        ENERGY_CONVERSION: {
            asset_names[4]: {
                LABEL: asset_names[4],
                OUTFLOW_DIRECTION: out_bus_names[3],
                INFLOW_DIRECTION: in_bus_names[3]},
            asset_names[5]: {
                LABEL: asset_names[5],
                OUTFLOW_DIRECTION: [out_bus_names[4], out_bus_names[5]],
                INFLOW_DIRECTION: [in_bus_names[4], in_bus_names[5]]}},
    }

    C0.define_busses(dict_test)
    assert ENERGY_BUSSES in dict_test.keys()
    # assert that bus list in/put in ENERGY_BUSSES

def test_bus_suffix_correct():
    bus = "a"
    bus_name = C0.bus_suffix(bus)
    assert bus_name == bus + BUS_SUFFIX

def test_asess_energyVectors_and_add_to_project_data():
    C2.identify_energy_vectors(dict_values)
    assert 1 == 0
    # assert "sector" in dict_values[PROJECT_DATA].keys()

#Create a sink for each energyVector (this actually might be changed in the future - create an excess sink for each bus?)
def test_create_excess_sinks_for_each_energyVector():
    assert 1 == 0



#- Add demand sinks to energyVectors (this should actually be changed and demand sinks should be added to bus relative to input_direction, also see issue #179)
def test_adding_demand_sinks_to_energyVectors():
    assert 1 == 0

def test_naming_busses():
    assert 1 == 0

def test_check_for_missing_data():
    assert 1 == 0

def test_add_missing_data_to_automatically_generated_objects():
    assert 1 == 0

def test_reading_timeseries_of_assets_one_column():
    assert 1 == 0

def test_reading_timeseries_of_assets_multi_column_csv():
    assert 1 == 0

def test_reading_timeseries_of_assets_delimiter_comma():
    assert 1 == 0

def test_reading_timeseries_of_assets_delimiter_semicolon():
    assert 1 == 0

# Read timeseries for parameter of an asset, eg. efficiency
def test_reading_timeseries_of_asset_for_parameter():
    assert 1 == 0

def test_parse_list_of_inputs_one_input():
    assert 1 == 0

def test_parse_list_of_inputs_two_inputs():
    assert 1 == 0

def test_parse_list_of_inputs_one_output():
    assert 1 == 0

def test_parse_list_of_inputs_two_outputs():
    assert 1 == 0

def test_parse_list_of_inputs_two_inputs_two_outputs():
    assert 1 == 0

def test_raise_error_message_multiple_inputs_not_multilpe_parameters():
    assert 1 == 0

def test_raise_error_message_multiple_outputs_multilpe_parameters():
    assert 1 == 0

# Define dso sinks, soures, transformer stations (this will be changed due to bug #119), also for peak demand pricing
def test_generation_of_dso_side():
    assert 1 == 0

# Add a source if a conversion object is connected to a new input_direction (bug #186)
def test_add_source_when_unknown_input_direction():
    assert 1 == 0

# Define all necessary energyBusses and add all assets that are connected to them specifically with asset name and label
def test_defined_energyBusses_complete():
    assert 1 == 0

def test_verification_executing_C1():
    assert 1 == 0
"""
