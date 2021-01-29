import os
import logging
import pytest
import pandas as pd
import numpy as np

import multi_vector_simulator.A1_csv_to_json as A1
import multi_vector_simulator.B0_data_input_json as data_input

import multi_vector_simulator.utils as utils

from multi_vector_simulator.utils.exceptions import (
    MissingParameterError,
    WrongParameterWarning,
    CsvParsingError,
    WrongStorageColumn,
)
from multi_vector_simulator.utils.constants import (
    WARNING_TEXT,
    REQUIRED_IN_CSV_ELEMENTS,
    DEFAULT_VALUE,
    HEADER,
    INPUT_FOLDER,
    CSV_ELEMENTS,
)

from multi_vector_simulator.utils.constants_json_strings import (
    UNIT,
    VALUE,
    DISPATCH_PRICE,
    DEVELOPMENT_COSTS,
    AGE_INSTALLED,
    INSTALLED_CAP,
    FILENAME,
    C_RATE,
    SOC_INITIAL,
    SOC_MAX,
    SOC_MIN,
    LABEL,
    STORAGE_CAPACITY,
    INPUT_POWER,
    OUTPUT_POWER,
    THERM_LOSSES_REL,
    THERM_LOSSES_ABS,
)
from _constants import (
    CSV_PATH,
    CSV_FNAME,
    DUMMY_CSV_PATH,
    REQUIRED_CSV_FILES,
    PATHS_TO_PLOTS,
    TYPE_BOOL,
    TEST_REPO_PATH,
)

CSV_PARAMETERS = ["param1", "param2"]

CSV_EXAMPLE = {"col1": {"param1": "val11", "param2": {VALUE: 21, UNIT: "factor"}}}
CSV_TIMESERIES = {
    "param1": {VALUE: {FILENAME: "test_time_series.csv", HEADER: "power"}, UNIT: "kW",}
}

CSV_LIST = {
    "param1": ["one", "two"],
    "param2": {UNIT: "factor", VALUE: [1.02, 3.04]},
    "param3": {UNIT: "currency/kWh", VALUE: [0.2, 0.7]},
    "param4": {UNIT: TYPE_BOOL, VALUE: [True, False, True]},
    "param5": {UNIT: "year", VALUE: [2, 7]},
}

CONVERSION_TYPE = {
    "param_str_empty": np.nan,
    "param_str": "one",
    "param_factor": {UNIT: "factor", VALUE: 1.04},
    "param_cur": {UNIT: "currency/kWh", VALUE: 18.9},
    "param_bool1": {UNIT: TYPE_BOOL, VALUE: True},
    "param_bool2": {UNIT: TYPE_BOOL, VALUE: True},
    "param_bool3": {UNIT: TYPE_BOOL, VALUE: False},
    "param_bool4": {UNIT: TYPE_BOOL, VALUE: False},
    "param_bool5": {UNIT: TYPE_BOOL, VALUE: True},
    "param_bool6": {UNIT: TYPE_BOOL, VALUE: False},
    "param_year": {UNIT: "year", VALUE: 8},
}


### Test function

filename_a = "a_file"
filename_b = "b_file"
df_no_new_parameter = pd.DataFrame(["a", "b"], index=["unit", "value"])

parameters = ["unit", "value"]

list_of_new_parameter = {
    "max": {
        WARNING_TEXT: "a test warning",
        REQUIRED_IN_CSV_ELEMENTS: [filename_a],
        DEFAULT_VALUE: False,
    }
}


def test_create_input_json_creation_of_json_file():
    A1.create_input_json(input_directory=CSV_PATH)
    assert os.path.exists(os.path.join(CSV_PATH, CSV_FNAME))


def test_create_input_json_already_existing_json_file_raises_FileExistsError():
    with open(os.path.join(CSV_PATH, CSV_FNAME), "w") as of:
        of.write("something")
    with pytest.raises(FileExistsError):
        A1.create_input_json(input_directory=CSV_PATH)


def test_create_input_json_raises_FileNotFoundError_if_missing_required_csv_files():
    with pytest.raises(FileNotFoundError):
        A1.create_input_json(input_directory=DUMMY_CSV_PATH)


def test_create_input_json_required_fields_are_filled():
    js_file = A1.create_input_json(input_directory=CSV_PATH, pass_back=True)
    js = data_input.load_json(js_file)
    for k in js.keys():
        assert k in REQUIRED_CSV_FILES + (PATHS_TO_PLOTS,)


def test_create_json_from_csv_file_not_exist_raises_filenotfound_error():
    with pytest.raises(FileNotFoundError):
        A1.create_json_from_csv(
            input_directory=CSV_PATH, filename="not_existing", parameters=[]
        )


def test_create_json_from_csv_with_comma_separated_csv():
    d = A1.create_json_from_csv(
        DUMMY_CSV_PATH, "csv_comma", CSV_PARAMETERS, asset_is_a_storage=False
    )
    assert d == {"csv_comma": CSV_EXAMPLE}


def test_create_json_from_csv_with_semicolon_separated_csv():
    d = A1.create_json_from_csv(
        DUMMY_CSV_PATH, "csv_semicolon", CSV_PARAMETERS, asset_is_a_storage=False
    )

    assert d == {"csv_semicolon": CSV_EXAMPLE}


def test_create_json_from_csv_with_ampersand_separated_csv():
    d = A1.create_json_from_csv(
        DUMMY_CSV_PATH, "csv_ampersand", CSV_PARAMETERS, asset_is_a_storage=False
    )

    assert d == {"csv_ampersand": CSV_EXAMPLE}


def test_create_json_from_csv_with_unknown_separator_for_csv_raises_CsvParsingError():

    with pytest.raises(CsvParsingError):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_unknown_separator",
            CSV_PARAMETERS,
            asset_is_a_storage=False,
        )


def test_create_json_from_csv_without_providing_parameters_raises_MissingParameterError():

    with pytest.raises(MissingParameterError):
        d = A1.create_json_from_csv(
            DUMMY_CSV_PATH, "csv_comma", parameters=[], asset_is_a_storage=False
        )
        utils.compare_input_parameters_with_reference(d, flag_missing=True)


def test_create_json_from_csv_with_uncomplete_parameters_raises_MissingParameterError():

    with pytest.raises(MissingParameterError):
        d = A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_comma",
            parameters=["param1", "param2", "param3"],
            asset_is_a_storage=False,
        )
        utils.compare_input_parameters_with_reference(d, flag_missing=True)


def test_create_json_from_csv_with_wrong_parameters_raises_WrongParameterWarning():

    with pytest.warns(WrongParameterWarning):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_wrong_parameter",
            parameters=["param1", "param2"],
            asset_is_a_storage=False,
        )


def test_create_json_from_csv_ignore_extra_parameters_in_csv():

    d = A1.create_json_from_csv(
        DUMMY_CSV_PATH,
        "csv_wrong_parameter",
        parameters=["param1", "param2"],
        asset_is_a_storage=False,
    )
    assert d == {"csv_wrong_parameter": CSV_EXAMPLE}


def test_create_json_from_csv_for_time_series():

    d = A1.create_json_from_csv(
        DUMMY_CSV_PATH,
        "csv_timeseries",
        parameters=["param1"],
        asset_is_a_storage=False,
    )
    for k, v in d["csv_timeseries"]["col1"].items():
        assert v == CSV_TIMESERIES[k]


def test_create_json_from_csv_for_list():

    d = A1.create_json_from_csv(
        DUMMY_CSV_PATH,
        "csv_list",
        parameters=["param1", "param2", "param3", "param4", "param5"],
        asset_is_a_storage=False,
    )
    for k, v in d["csv_list"]["col1"].items():
        assert v == CSV_LIST[k]


def test_conversion():

    d = A1.create_json_from_csv(
        DUMMY_CSV_PATH,
        "csv_type",
        parameters=[
            "param_str",
            "param_factor",
            "param_cur",
            "param_bool1",
            "param_bool2",
            "param_bool3",
            "param_bool4",
            "param_bool5",
            "param_bool6",
            "param_year",
        ],
        asset_is_a_storage=False,
    )
    for k, v in d["csv_type"]["col1"].items():
        assert v == CONVERSION_TYPE[k]


def test_create_json_from_csv_storage_raises_WrongParameterWarning():

    with pytest.warns(WrongParameterWarning):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_storage_wrong_parameter",
            parameters=[AGE_INSTALLED, DEVELOPMENT_COSTS],
            asset_is_a_storage=True,
        )


def test_create_json_from_csv_storage_raises_MissingParameterError():

    with pytest.raises(MissingParameterError):
        d = A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_storage_wrong_parameter",
            parameters=[
                AGE_INSTALLED,
                DEVELOPMENT_COSTS,
                C_RATE,
                DISPATCH_PRICE,
                SOC_INITIAL,
                SOC_MAX,
                SOC_MIN,
                INSTALLED_CAP,
            ],
            asset_is_a_storage=True,
        )
        utils.compare_input_parameters_with_reference(d, flag_missing=True)


def test_create_json_from_csv_storage_raises_WrongParameterWarning_for_wrong_values():

    with pytest.warns(WrongParameterWarning):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_storage_wrong_values",
            parameters=[AGE_INSTALLED, DEVELOPMENT_COSTS],
            asset_is_a_storage=True,
        )


def test_create_json_from_csv_storage_raises_WrongStorageColumn():
    with pytest.raises(A1.WrongStorageColumn):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_storage_wrong_column_name",
            parameters=[AGE_INSTALLED, DEVELOPMENT_COSTS],
            asset_is_a_storage=True,
        )


def test_create_json_from_csv_float_int_parsing():
    exp = {
        "param1": {UNIT: "years", VALUE: 50.0},
        "param2": {UNIT: "factor", VALUE: 0.2},
        "param3": {UNIT: "currency", VALUE: 65.5},
    }
    json = A1.create_json_from_csv(
        DUMMY_CSV_PATH,
        "csv_float_int",
        parameters=["param1", "param2", "param3"],
        asset_is_a_storage=False,
    )
    for param in exp:
        assert json["csv_float_int"]["col1"][param][VALUE] == exp[param][VALUE]

    assert type(json["csv_float_int"]["col1"]["param1"][VALUE]) is int
    assert type(json["csv_float_int"]["col1"]["param2"][VALUE]) is float
    assert type(json["csv_float_int"]["col1"]["param3"][VALUE]) is float


def test_add_storage_components_label_correctly_added():
    storage_label = "ESS Li-Ion"
    input_directory = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS)
    single_dict = A1.add_storage_components(
        storage_filename="storage_01",
        input_directory=input_directory,
        storage_label=storage_label,
    )

    for column_name in [STORAGE_CAPACITY, INPUT_POWER, OUTPUT_POWER]:
        assert (
            single_dict[column_name][LABEL] == f"{storage_label} {column_name}"
        ), f"Label of storage {storage_label} defined incorrectly, should be: '{storage_label} {column_name}'."


def teardown_function():
    if os.path.exists(os.path.join(CSV_PATH, CSV_FNAME)):
        os.remove(os.path.join(CSV_PATH, CSV_FNAME))


def test_default_values_storage_without_thermal_losses():
    exp = {
        THERM_LOSSES_REL: {UNIT: "no_unit", VALUE: 0},
        THERM_LOSSES_ABS: {UNIT: "kWh", VALUE: 0},
    }

    data_path = os.path.join(
        TEST_REPO_PATH,
        "benchmark_test_inputs",
        "Feature_stratified_thermal_storage",
        "csv_elements",
    )

    json = A1.create_json_from_csv(
        input_directory=data_path,
        filename="storage_fix_without_fixed_thermal_losses",
        parameters=[
            "age_installed",
            "development_costs",
            "specific_costs",
            "efficiency",
            "installedCap",
            "lifetime",
            "specific_costs_om",
            "unit",
        ],
        asset_is_a_storage=True,
    )
    for param, result in exp.items():
        assert (
            json["storage capacity"][param][VALUE] == result[VALUE]
        ), f"The losses set to default value should match {result[VALUE]}"


def test_default_values_storage_with_thermal_losses():
    exp = {
        THERM_LOSSES_REL: {UNIT: "no_unit", VALUE: 0.001},
        THERM_LOSSES_ABS: {UNIT: "kWh", VALUE: 0.00001},
    }

    data_path = os.path.join(
        TEST_REPO_PATH,
        "benchmark_test_inputs",
        "Feature_stratified_thermal_storage",
        "csv_elements",
    )

    json = A1.create_json_from_csv(
        input_directory=data_path,
        filename="storage_fix_with_fixed_thermal_losses_float",
        parameters=[
            "age_installed",
            "development_costs",
            "specific_costs",
            "efficiency",
            "installedCap",
            "lifetime",
            "specific_costs_om",
            "unit",
        ],
        asset_is_a_storage=True,
    )
    for param, result in exp.items():
        assert (
            json["storage capacity"][param][VALUE] == result[VALUE]
        ), f"{param} should match {result[VALUE]}"
