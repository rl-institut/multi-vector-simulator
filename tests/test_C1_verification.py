import pytest
import pandas as pd
import os
import json

import mvs_eland.C1_verification as C1
from _constants import (
    JSON_PATH,
    ENERGY_PROVIDERS,
    LABEL,
    FEEDIN_TARIFF,
    ENERGY_PRICE,
    UNIT,
    VALUE,
)
from mvs_eland.utils.constants_json_strings import (
    TIMESERIES,
    RENEWABLE_ASSET_BOOL,
    ENERGY_PRODUCTION,
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


def test_check_feedin_tariff_greater_energy_price():
    dict_values = {
        ENERGY_PROVIDERS: {
            "DSO": {
                ENERGY_PRICE: {UNIT: "currency/kWh", VALUE: 0.3},
                FEEDIN_TARIFF: {UNIT: "currency/kWh", VALUE: 0.4},
                LABEL: "test DSO",
            }
        }
    }
    with pytest.raises(ValueError):
        C1.check_feedin_tariff(dict_values)


def test_check_feedin_tariff_not_greater_energy_price():
    dict_values = {
        ENERGY_PROVIDERS: {
            "DSO": {
                ENERGY_PRICE: {UNIT: "currency/kWh", VALUE: 0.5},
                FEEDIN_TARIFF: {UNIT: "currency/kWh", VALUE: 0.4},
                LABEL: "test DSO",
            }
        }
    }
    C1.check_feedin_tariff(dict_values)


def test_check_time_series_values_between_0_and_1_True():
    time_series = pd.Series([0, 0.22, 0.5, 0.99, 1])
    result = C1.check_time_series_values_between_0_and_1(time_series=time_series)
    assert result == True


def test_check_time_series_values_between_0_and_1_False_greater_1():
    time_series = pd.Series([0, 0.22, 0.5, 0.99, 1, 1.01])
    result = C1.check_time_series_values_between_0_and_1(time_series=time_series)
    assert result == False


def test_check_time_series_values_between_0_and_1_False_smaller_0():
    time_series = pd.Series([0, 0.22, 0.5, 0.99, 1, -0.01])
    result = C1.check_time_series_values_between_0_and_1(time_series=time_series)
    assert result == False


@pytest.fixture()
def get_json():
    """ Reads input json file and adds time series to non-dispatchable sources. """
    with open(os.path.join(JSON_PATH)) as json_file:
        dict_values = json.load(json_file)

    def _add_time_series_to_dict_values(ts):
        for key, source in dict_values[ENERGY_PRODUCTION].items():
            if source[RENEWABLE_ASSET_BOOL][VALUE] == True:
                dict_values[ENERGY_PRODUCTION][key][TIMESERIES] = ts
        return dict_values

    return _add_time_series_to_dict_values


def test_check_non_dispatchable_source_time_series_passes(get_json):
    dict_values = get_json(pd.Series([0, 0.22, 0.5, 0.99, 1]))
    return_value = C1.check_non_dispatchable_source_time_series(dict_values=dict_values)
    assert return_value == True


def test_check_non_dispatchable_source_time_series_results_in_error_msg(get_json):
    dict_values = get_json(pd.Series([0, 0.22, 0.5, 0.99, 1, 1.01]))
    return_value = C1.check_non_dispatchable_source_time_series(dict_values=dict_values)
    assert return_value == False


# def test_check_input_values():
#     pass
#     # todo note: function is not used so far


# def test_all_valid_intervals():
#     pass
#     # todo note: function is not used so far
