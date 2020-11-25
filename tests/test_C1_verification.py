import pytest
import pandas as pd
import os
import json

import multi_vector_simulator.C1_verification as C1
from _constants import (
    JSON_PATH,
    ENERGY_PROVIDERS,
    LABEL,
    FEEDIN_TARIFF,
    ENERGY_PRICE,
    UNIT,
    VALUE,
)
from multi_vector_simulator.utils.constants_json_strings import (
    TIMESERIES,
    RENEWABLE_ASSET_BOOL,
    ENERGY_PRODUCTION,
    PROJECT_DATA,
    ENERGY_VECTOR,
    LES_ENERGY_VECTOR_S,
)

from multi_vector_simulator.utils.exceptions import (
    UnknownEnergyVectorError,
    DuplicateLabels,
)


def test_lookup_file_existing_file():
    file_name = JSON_PATH
    # no error is risen
    C1.lookup_file(file_path=file_name, name="test")


def test_lookup_file_non_existing_file_raises_error():
    file_name = "non_existing.json"
    msg = f"Missing file! The timeseries file '{file_name}'"
    with pytest.raises(FileNotFoundError, match=msg):
        C1.lookup_file(file_path=file_name, name="test")


def test_check_if_energy_vector_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS_pass():
    # Function only needs to pass
    C1.check_if_energy_vector_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS(
        "Electricity", "asset_group", "asset"
    )
    assert (
        1 == 1
    ), f"The energy carrier `Electricity` is not recognized to be defined in `DEFAULT_WEIGHTS_ENERGY_CARRIERS`."


def test_check_if_energy_vector_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS_fail():
    with pytest.raises(UnknownEnergyVectorError):
        C1.check_if_energy_vector_is_defined_in_DEFAULT_WEIGHTS_ENERGY_CARRIERS(
            "Bio-Diesel", "asset_group", "asset"
        ), f"The energy carrier `Bio-Diesel` is recognized in the `DEFAULT_WEIGHTS_ENERGY_CARRIERS`, eventhough it should not be defined."


def test_check_if_energy_vector_of_all_assets_is_valid_passes():
    dict_test = {
        PROJECT_DATA: {LES_ENERGY_VECTOR_S: {"Electricity"}},
        ENERGY_PRODUCTION: {ENERGY_VECTOR: "Electricity"},
    }
    C1.check_if_energy_vector_of_all_assets_is_valid(dict_test)
    assert (
        1 == 1
    ), f"The function incorrectly identifies an energy vector as being not defined via the energyBusses (as the project energy vector)."


def test_check_if_energy_vector_of_all_assets_is_valid_fails():
    dict_test = {
        PROJECT_DATA: {LES_ENERGY_VECTOR_S: {"Electricity"}},
        ENERGY_PRODUCTION: {"Asset": {ENERGY_VECTOR: "Heat"}},
    }
    with pytest.raises(ValueError):
        C1.check_if_energy_vector_of_all_assets_is_valid(
            dict_test
        ), f"The function incorrectly accepts an energyVector that is not in the energyBusses (as the project energy vector)."


def test_check_feedin_tariff_abs_greater_energy_price():
    """Feed-in tariff (absolute value) greater than energy price, raises ValueError"""
    dict_values = {
        ENERGY_PROVIDERS: {
            "DSO": {
                ENERGY_PRICE: {UNIT: "currency/kWh", VALUE: 0.3},
                FEEDIN_TARIFF: {UNIT: "currency/kWh", VALUE: -0.4},
                LABEL: "test DSO",
            }
        }
    }
    with pytest.raises(ValueError):
        C1.check_feedin_tariff(dict_values)


def test_check_feedin_tariff_abs_not_greater_energy_price():
    """Feed-in tariff (absolute value) smaller than energy price, no error"""
    dict_values = {
        ENERGY_PROVIDERS: {
            "DSO": {
                ENERGY_PRICE: {UNIT: "currency/kWh", VALUE: 0.5},
                FEEDIN_TARIFF: {UNIT: "currency/kWh", VALUE: -0.4},
                LABEL: "test DSO",
            }
        }
    }
    C1.check_feedin_tariff(dict_values)


def test_check_time_series_values_between_0_and_1_True():
    time_series = pd.Series([0, 0.22, 0.5, 0.99, 1])
    result = C1.check_time_series_values_between_0_and_1(time_series=time_series)
    assert result is True


def test_check_time_series_values_between_0_and_1_False_greater_1():
    time_series = pd.Series([0, 0.22, 0.5, 0.99, 1, 1.01])
    result = C1.check_time_series_values_between_0_and_1(time_series=time_series)
    assert result is False


def test_check_time_series_values_between_0_and_1_False_smaller_0():
    time_series = pd.Series([0, 0.22, 0.5, 0.99, 1, -0.01])
    result = C1.check_time_series_values_between_0_and_1(time_series=time_series)
    assert result is False


@pytest.fixture()
def get_json():
    """ Reads input json file and adds time series to non-dispatchable sources. """
    with open(os.path.join(JSON_PATH)) as json_file:
        dict_values = json.load(json_file)

    def _add_time_series_to_dict_values(ts):
        for key, source in dict_values[ENERGY_PRODUCTION].items():
            if source[RENEWABLE_ASSET_BOOL][VALUE] is True:
                dict_values[ENERGY_PRODUCTION][key][TIMESERIES] = ts
        return dict_values

    return _add_time_series_to_dict_values


def test_check_non_dispatchable_source_time_series_passes(get_json):
    dict_values = get_json(pd.Series([0, 0.22, 0.5, 0.99, 1]))
    return_value = C1.check_non_dispatchable_source_time_series(dict_values=dict_values)
    assert return_value is None


def test_check_non_dispatchable_source_time_series_results_in_error_msg(get_json):
    dict_values = get_json(pd.Series([0, 0.22, 0.5, 0.99, 1, 1.01]))
    return_value = C1.check_non_dispatchable_source_time_series(dict_values=dict_values)
    assert return_value is False


def test_check_for_label_duplicates_fails():
    ASSET = "asset"
    A_LABEL = "a_label"
    dict_values = {
        ENERGY_PRODUCTION: {ASSET: {LABEL: A_LABEL}},
        ENERGY_PROVIDERS: {ASSET: {LABEL: A_LABEL}},
    }
    with pytest.raises(DuplicateLabels):
        C1.check_for_label_duplicates(
            dict_values
        ), f"Eventhough there is a duplicate value of label, no error is raised."


def test_check_for_label_duplicates_passes():
    ASSET = "asset"
    A_LABEL = "a_label"
    B_LABEL = "b_label"
    dict_values = {
        ENERGY_PRODUCTION: {ASSET: {LABEL: A_LABEL}},
        ENERGY_PROVIDERS: {ASSET: {LABEL: B_LABEL}},
    }
    C1.check_for_label_duplicates(dict_values)
    assert (
        1 == 1
    ), f"There is no duplicate value for label, but still an error is raised."


# def test_check_input_values():
#     pass
#     # todo note: function is not used so far


# def test_all_valid_intervals():
#     pass
#     # todo note: function is not used so far
