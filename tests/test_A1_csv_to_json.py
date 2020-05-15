import os
import pytest

import src.A1_csv_to_json as A1
import src.B0_data_input_json as data_input

from .constants import CSV_PATH, CSV_FNAME, DUMMY_CSV_PATH, REQUIRED_CSV_FILES
from src.constants import  PATHS_TO_PLOTS

CSV_PARAMETERS = ["param1", "param2"]

CSV_EXAMPLE = {"col1": {"param1": "val11", "param2": {"value": 21, "unit": "factor"}}}
CSV_TIMESERIES = {
    "param1": {
        "value": {"file_name": "test_time_series.csv", "header": "power"},
        "unit": "kW",
    }
}

CSV_LIST = {
    "param1": ["one", "two"],
    "param2": {"unit": "factor", "value": [1.02, 3.04]},
    "param3": {"unit": "currency/kWh", "value": [0.2, 0.7]},
    "param4": {"unit": "bool", "value": [True, False, True]},
    "param5": {"unit": "year", "value": [2, 7]},
}

CONVERSION_TYPE = {
    "param_str": "one",
    "param_factor": {"unit": "factor", "value": 1.04},
    "param_cur": {"unit": "currency/kWh", "value": 18.9},
    "param_bool1": {"unit": "bool", "value": True},
    "param_bool2": {"unit": "bool", "value": True},
    "param_bool3": {"unit": "bool", "value": False},
    "param_bool4": {"unit": "bool", "value": False},
    "param_bool5": {"unit": "bool", "value": True},
    "param_bool6": {"unit": "bool", "value": False},
    "param_year": {"unit": "year", "value": 8},
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
        assert k in REQUIRED_CSV_FILES + PATHS_TO_PLOTS


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

    with pytest.raises(A1.CsvParsingError):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_unknown_separator",
            CSV_PARAMETERS,
            asset_is_a_storage=False,
        )


def test_create_json_from_csv_without_providing_parameters_raises_MissingParameterError():

    with pytest.raises(A1.MissingParameterError):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH, "csv_comma", parameters=[], asset_is_a_storage=False
        )


def test_create_json_from_csv_with_uncomplete_parameters_raises_WrongParameterWarning():

    with pytest.raises(A1.MissingParameterError):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_comma",
            parameters=["param1", "param2", "param3"],
            asset_is_a_storage=False,
        )


def test_create_json_from_csv_with_wrong_parameters_raises_WrongParameterWarning():

    with pytest.warns(A1.WrongParameterWarning):
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

    with pytest.warns(A1.WrongParameterWarning):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_storage_wrong_parameter",
            parameters=["age_installed", "capex_fix"],
            asset_is_a_storage=True,
        )


def test_create_json_from_csv_storage_raises_MissingParameterError():

    with pytest.raises(A1.MissingParameterError):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_storage_wrong_parameter",
            parameters=[
                "age_installed",
                "capex_fix",
                "c_rate",
                "opex_var",
                "soc_initial",
                "soc_max",
                "soc_min",
                "installedCap",
            ],
            asset_is_a_storage=True,
        )


def test_create_json_from_csv_storage_raises_WrongParameterWarning_for_wrong_values():

    with pytest.warns(A1.WrongParameterWarning):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_storage_wrong_values",
            parameters=["age_installed", "capex_fix"],
            asset_is_a_storage=True,
        )


def test_create_json_from_csv_storage_raises_WrongStorageColumn():

    with pytest.raises(A1.WrongStorageColumn):
        A1.create_json_from_csv(
            DUMMY_CSV_PATH,
            "csv_storage_wrong_column_name",
            parameters=["age_installed", "capex_fix"],
            asset_is_a_storage=True,
        )


def teardown_function():
    if os.path.exists(os.path.join(CSV_PATH, CSV_FNAME)):
        os.remove(os.path.join(CSV_PATH, CSV_FNAME))
