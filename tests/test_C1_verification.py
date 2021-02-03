import pytest
import pandas as pd
import os
import json
import logging

import multi_vector_simulator.C1_verification as C1
from _constants import (
    JSON_PATH,
    ENERGY_PROVIDERS,
    LABEL,
    FEEDIN_TARIFF,
    ENERGY_PRICE,
    UNIT,
)
from multi_vector_simulator.utils.constants_json_strings import (
    TIMESERIES,
    RENEWABLE_ASSET_BOOL,
    ENERGY_PRODUCTION,
    ENERGY_STORAGE,
    PROJECT_DATA,
    ENERGY_VECTOR,
    LES_ENERGY_VECTOR_S,
    VALUE,
    EFFICIENCY,
    STORAGE_CAPACITY,
    SIMULATION_ANNUITY,
    TIMESERIES_TOTAL,
    DISPATCH_PRICE,
    DISPATCHABILITY,
    OPTIMIZE_CAP,
    MAXIMUM_CAP,
    CONSTRAINTS,
    MAXIMUM_EMISSIONS,
    EMISSION_FACTOR,
    RENEWABLE_SHARE_DSO,
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


def test_check_feedin_tariff_vs_energy_price_greater_energy_price():
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
        C1.check_feedin_tariff_vs_energy_price(dict_values)


def test_check_feedin_tariff_vs_energy_price_not_greater_energy_price():
    dict_values = {
        ENERGY_PROVIDERS: {
            "DSO": {
                ENERGY_PRICE: {UNIT: "currency/kWh", VALUE: 0.5},
                FEEDIN_TARIFF: {UNIT: "currency/kWh", VALUE: 0.4},
                LABEL: "test DSO",
            }
        }
    }
    C1.check_feedin_tariff_vs_energy_price(dict_values)


def test_check_feedin_tariff_vs_levelized_cost_of_generation_of_production_dispatchable_lower_dispatch_price():
    energy_vector = "Electricity"
    dict_values = {
        ENERGY_PROVIDERS: {
            "DSO": {
                FEEDIN_TARIFF: {UNIT: "currency/kWh", VALUE: 0.4},
                LABEL: "test DSO",
                ENERGY_VECTOR: energy_vector,
            }
        },
        ENERGY_PRODUCTION: {
            "asset": {
                ENERGY_VECTOR: energy_vector,
                LABEL: "production asset",
                DISPATCH_PRICE: {VALUE: 0.3},
                DISPATCHABILITY: True,
                OPTIMIZE_CAP: {VALUE: True},
                MAXIMUM_CAP: {VALUE: None},
            }
        },
    }
    with pytest.raises(ValueError):
        C1.check_feedin_tariff_vs_levelized_cost_of_generation_of_production(
            dict_values
        ), f"If feed-in tariff > dispatch price of an asset without maximumCap and with optimized capacity a ValueError should be risen."


def test_check_feedin_tariff_vs_levelized_cost_of_generation_of_production_dispatchable_higher_dispatch_price(
    caplog,
):
    energy_vector = "Electricity"
    dict_values = {
        ENERGY_PROVIDERS: {
            "DSO": {
                FEEDIN_TARIFF: {UNIT: "currency/kWh", VALUE: 0.4},
                LABEL: "test DSO",
                ENERGY_VECTOR: energy_vector,
            }
        },
        ENERGY_PRODUCTION: {
            "asset": {
                ENERGY_VECTOR: energy_vector,
                LABEL: "production asset",
                DISPATCHABILITY: True,
                DISPATCH_PRICE: {VALUE: 0.5},
                OPTIMIZE_CAP: {VALUE: True},
                MAXIMUM_CAP: {VALUE: None},
            }
        },
    }
    # no error no logging
    with caplog.at_level(logging.WARNING):
        C1.check_feedin_tariff_vs_levelized_cost_of_generation_of_production(
            dict_values
        )
    assert (
        caplog.text == ""
    ), f"If feed-in tariff < dispatch price of an asset no error and no logging message should occur."


def test_check_feedin_tariff_vs_levelized_cost_of_generation_of_production_non_dispatchable_greater_costs():
    energy_vector = "Electricity"
    dict_values = {
        ENERGY_PROVIDERS: {
            "DSO": {
                FEEDIN_TARIFF: {UNIT: "currency/kWh", VALUE: 0.4},
                LABEL: "test DSO",
                ENERGY_VECTOR: energy_vector,
            }
        },
        ENERGY_PRODUCTION: {
            "asset": {
                ENERGY_VECTOR: energy_vector,
                LABEL: "production asset",
                SIMULATION_ANNUITY: {VALUE: 1},
                TIMESERIES_TOTAL: {VALUE: 10},
                DISPATCHABILITY: False,
                OPTIMIZE_CAP: {VALUE: True},
                MAXIMUM_CAP: {VALUE: None},
            }
        },
    }
    with pytest.raises(ValueError):
        C1.check_feedin_tariff_vs_levelized_cost_of_generation_of_production(
            dict_values
        ), f"If feed-in tariff > dispatch price of an asset without maximumCap and with optimized capacity a ValueError should be risen."


def test_check_feedin_tariff_vs_levelized_cost_of_generation_of_production_non_dispatchable_not_greater_costs(
    caplog,
):
    energy_vector = "Electricity"
    dict_values = {
        ENERGY_PROVIDERS: {
            "DSO": {
                FEEDIN_TARIFF: {UNIT: "currency/kWh", VALUE: 0.4},
                LABEL: "test DSO",
                ENERGY_VECTOR: energy_vector,
            }
        },
        ENERGY_PRODUCTION: {
            "asset": {
                ENERGY_VECTOR: energy_vector,
                LABEL: "production asset",
                SIMULATION_ANNUITY: {VALUE: 10},
                TIMESERIES_TOTAL: {VALUE: 10},
                DISPATCHABILITY: False,
                OPTIMIZE_CAP: {VALUE: True},
                MAXIMUM_CAP: {VALUE: None},
            }
        },
    }
    # no error no logging
    with caplog.at_level(logging.WARNING):
        C1.check_feedin_tariff_vs_levelized_cost_of_generation_of_production(
            dict_values
        )
    assert (
        caplog.text == ""
    ), f"If feed-in tariff < dispatch price of an asset no error and no logging message should occur."


def test_check_feedin_tariff_vs_levelized_cost_of_generation_of_production_non_dispatchable_greater_costs_with_maxcap(
    caplog,
):
    energy_vector = "Electricity"
    dict_values = {
        ENERGY_PROVIDERS: {
            "DSO": {
                FEEDIN_TARIFF: {UNIT: "currency/kWh", VALUE: 0.4},
                LABEL: "test DSO",
                ENERGY_VECTOR: energy_vector,
            }
        },
        ENERGY_PRODUCTION: {
            "asset": {
                ENERGY_VECTOR: energy_vector,
                LABEL: "production asset",
                SIMULATION_ANNUITY: {VALUE: 1},
                TIMESERIES_TOTAL: {VALUE: 10},
                DISPATCHABILITY: False,
                OPTIMIZE_CAP: {VALUE: True},
                MAXIMUM_CAP: {VALUE: 1000},
            }
        },
    }
    # logging.warning
    with caplog.at_level(logging.WARNING):
        C1.check_feedin_tariff_vs_levelized_cost_of_generation_of_production(
            dict_values
        )
    assert (
        "This will cause the optimization to result into the maximum capacity of this asset."
        in caplog.text
    ), f"If a production asset has a maximumCap and the feed-in tariff is greater than the expected lcoe a warning should be logged."


def test_check_feedin_tariff_vs_levelized_cost_of_generation_of_production_non_dispatchable_greater_costs_dispatch_mode(
    caplog,
):
    energy_vector = "Electricity"
    dict_values = {
        ENERGY_PROVIDERS: {
            "DSO": {
                FEEDIN_TARIFF: {UNIT: "currency/kWh", VALUE: 0.4},
                LABEL: "test DSO",
                ENERGY_VECTOR: energy_vector,
            }
        },
        ENERGY_PRODUCTION: {
            "asset": {
                ENERGY_VECTOR: energy_vector,
                LABEL: "production asset",
                SIMULATION_ANNUITY: {VALUE: 1},
                TIMESERIES_TOTAL: {VALUE: 10},
                DISPATCHABILITY: False,
                OPTIMIZE_CAP: {VALUE: False},
                MAXIMUM_CAP: {VALUE: 1000},
            }
        },
    }
    # logging.warning
    with caplog.at_level(logging.DEBUG):
        C1.check_feedin_tariff_vs_levelized_cost_of_generation_of_production(
            dict_values
        )
    assert (
        "No error expected but strange dispatch behaviour might occur." in caplog.text
    ), f"If the capacity of a production asset is not optimized and the feed-in tariff is greater than the expected lcoe a debug msg should be logged."


def test_check_feasibility_of_maximum_emissions_constraint_no_warning_no_constraint(
    caplog,
):
    dict_values = {
        CONSTRAINTS: {MAXIMUM_EMISSIONS: {VALUE: None}},
    }
    # logging.warning
    with caplog.at_level(logging.WARNING):
        C1.check_feasibility_of_maximum_emissions_constraint(dict_values)
    assert (
        caplog.text == ""
    ), f"If the maximum emissions constraint is not used, no msg should be logged."


def test_check_feasibility_of_maximum_emissions_constraint_no_warning_although_emission_constraint(
    caplog,
):
    dict_values = {
        CONSTRAINTS: {MAXIMUM_EMISSIONS: {VALUE: 1000}},
        ENERGY_PRODUCTION: {
            "Energy asset": {
                EMISSION_FACTOR: {VALUE: 0},
                MAXIMUM_CAP: {VALUE: None},
                OPTIMIZE_CAP: {VALUE: True},
            },
        },
    }
    # logging.warning
    with caplog.at_level(logging.WARNING):
        C1.check_feasibility_of_maximum_emissions_constraint(dict_values)
    assert (
        caplog.text == ""
    ), f"If the maximum emissions constraint is used and one production asset with zero emissions has a capacity to be optimized and a maximum capacity of None, no msg should be logged."


def test_check_feasibility_of_maximum_emissions_constraint_maximumcap(caplog):
    dict_values = {
        CONSTRAINTS: {MAXIMUM_EMISSIONS: {VALUE: 1000}},
        ENERGY_PRODUCTION: {
            "Energy asset": {
                EMISSION_FACTOR: {VALUE: 0},
                MAXIMUM_CAP: {VALUE: 1000},
                OPTIMIZE_CAP: {VALUE: True},
            },
        },
    }
    # logging.warning
    with caplog.at_level(logging.WARNING):
        C1.check_feasibility_of_maximum_emissions_constraint(dict_values)
    assert (
        "When the maximum emissions constraint is used and no production asset with zero emissions"
        in caplog.text
    ), f"If the maximum emissions constraint is used and no production asset with zero emissions, capacity to be optimized and maximum capacity of None exists, a warning msg should be logged."


def test_check_feasibility_of_maximum_emissions_constraint_optimizeCap_is_False(caplog):
    dict_values = {
        CONSTRAINTS: {MAXIMUM_EMISSIONS: {VALUE: 1000}},
        ENERGY_PRODUCTION: {
            "Energy asset": {
                EMISSION_FACTOR: {VALUE: 0},
                MAXIMUM_CAP: {VALUE: None},
                OPTIMIZE_CAP: {VALUE: False},
            },
        },
    }
    # logging.warning
    with caplog.at_level(logging.WARNING):
        C1.check_feasibility_of_maximum_emissions_constraint(dict_values)
    assert (
        "When the maximum emissions constraint is used and no production asset with zero emissions"
        in caplog.text
    ), f"If the maximum emissions constraint is used and no production asset with zero emissions, capacity to be optimized and maximum capacity of None exists, a warning msg should be logged."


def test_check_feasibility_of_maximum_emissions_constraint_no_zero_emission_asset(
    caplog,
):
    dict_values = {
        CONSTRAINTS: {MAXIMUM_EMISSIONS: {VALUE: 1000}},
        ENERGY_PRODUCTION: {
            "Energy asset": {
                EMISSION_FACTOR: {VALUE: 1},
                MAXIMUM_CAP: {VALUE: None},
                OPTIMIZE_CAP: {VALUE: True},
            },
        },
    }
    # logging.warning
    with caplog.at_level(logging.WARNING):
        C1.check_feasibility_of_maximum_emissions_constraint(dict_values)
    assert (
        "When the maximum emissions constraint is used and no production asset with zero emissions"
        in caplog.text
    ), f"If the maximum emissions constraint is used and no production asset with zero emissions exists, a warning msg should be logged."


def test_check_emission_factor_of_providers_no_warning_RE_share_lower_1(caplog):
    dict_values = {
        ENERGY_PROVIDERS: {
            "Energy provider": {
                EMISSION_FACTOR: {VALUE: 0.2},
                RENEWABLE_SHARE_DSO: {VALUE: 0.5},
            },
        },
    }
    # logging.warning
    with caplog.at_level(logging.WARNING):
        C1.check_emission_factor_of_providers(dict_values)
    assert (
        caplog.text == ""
    ), f"When the renewable share of the provider is lower than 1, no warning msg should be logged."


def test_check_emission_factor_of_providers_no_warning_emission_factor_0(caplog):
    dict_values = {
        ENERGY_PROVIDERS: {
            "Energy provider": {
                EMISSION_FACTOR: {VALUE: 0},
                RENEWABLE_SHARE_DSO: {VALUE: 1},
            },
        },
    }
    # logging.warning
    with caplog.at_level(logging.WARNING):
        C1.check_emission_factor_of_providers(dict_values)
    assert (
        caplog.text == ""
    ), f"When the emission_factor of the provider is zero, no warning msg should be logged."


def test_check_emission_factor_of_providers_warning(caplog):
    dict_values = {
        ENERGY_PROVIDERS: {
            "Energy provider": {
                EMISSION_FACTOR: {VALUE: 0.2},
                RENEWABLE_SHARE_DSO: {VALUE: 1},
            },
        },
    }
    # logging.warning
    with caplog.at_level(logging.WARNING):
        C1.check_emission_factor_of_providers(dict_values)
    assert (
        "Check if this is what you intended to define." in caplog.text
    ), f"When the emission_factor of the provider is > 0 while the RE share is 1, a warning msg should be logged."


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
def get_dict_vals():
    """ Reads input json file."""
    with open(os.path.join(JSON_PATH)) as json_file:
        dict_values = json.load(json_file)  # todo welches file???
    return dict_values


def test_check_efficiency_of_storage_capacity_is_0(get_dict_vals):
    dict_values = get_dict_vals
    # get storage label (test will work also if 'storage_01' is renamed
    storage_label = list(dict_values[ENERGY_STORAGE])[0]
    # change value of efficiency
    dict_values[ENERGY_STORAGE][storage_label][STORAGE_CAPACITY][EFFICIENCY][VALUE] = 0

    with pytest.raises(ValueError):
        C1.check_efficiency_of_storage_capacity(
            dict_values
        ), f"Although the efficiency of a 'storage_capacity' is zero, no ValueError is risen."


def test_check_efficiency_of_storage_capacity_is_btw_0_and_02(get_dict_vals, caplog):
    dict_values = get_dict_vals
    # get storage label (test will work also if 'storage_01' is renamed
    storage_label = list(dict_values[ENERGY_STORAGE])[0]
    # change value of efficiency
    dict_values[ENERGY_STORAGE][storage_label][STORAGE_CAPACITY][EFFICIENCY][
        VALUE
    ] = 0.1

    with caplog.at_level(logging.WARNING):
        C1.check_efficiency_of_storage_capacity(dict_values)
    assert (
        "You might use an old input file!" in caplog.text
    ), f"Although the efficiency of a 'storage_capacity' is 0.1, no warning is logged."


def test_check_efficiency_of_storage_capacity_is_greater_02(get_dict_vals, caplog):
    dict_values = get_dict_vals
    # get storage label (test will work also if 'storage_01' is renamed
    storage_label = list(dict_values[ENERGY_STORAGE])[0]
    # change value of efficiency
    dict_values[ENERGY_STORAGE][storage_label][STORAGE_CAPACITY][EFFICIENCY][
        VALUE
    ] = 0.3

    # no error, no logging
    with caplog.at_level(logging.WARNING):
        C1.check_efficiency_of_storage_capacity(dict_values)
    assert (
        caplog.text == ""
    ), f"Although the efficiency of a 'storage_capacity' is 0.3, a warning is logged or error is risen."


def test_check_non_dispatchable_source_time_series_passes():
    dict_values = {
        ENERGY_PRODUCTION: {
            "asset": {
                TIMESERIES: pd.Series([0, 0.22, 0.5, 0.99, 1]),
                DISPATCHABILITY: False,
            }
        }
    }
    return_value = C1.check_non_dispatchable_source_time_series(dict_values=dict_values)
    assert return_value is None


def test_check_non_dispatchable_source_time_series_results_in_error_msg():
    dict_values = {
        ENERGY_PRODUCTION: {
            "asset": {
                TIMESERIES: pd.Series([0, 0.22, 0.5, 0.99, 1, 1.01]),
                DISPATCHABILITY: False,
                LABEL: "asset",
            }
        }
    }
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
