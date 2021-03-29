import pytest
import pandas as pd
import os
import json
import logging
from copy import deepcopy

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
    TIMESERIES_PEAK,
    ASSET_DICT,
    RENEWABLE_ASSET_BOOL,
    ENERGY_PRODUCTION,
    ENERGY_CONVERSION,
    ENERGY_CONSUMPTION,
    ENERGY_BUSSES,
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
    INSTALLED_CAP,
    OUTPUT_POWER,
    OUTFLOW_DIRECTION,
    CONSTRAINTS,
    MAXIMUM_EMISSIONS,
    EMISSION_FACTOR,
    RENEWABLE_SHARE_DSO,
    ENERGY_BUSSES,
    ASSET_DICT,
    DSO_PEAK_DEMAND_SUFFIX,
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


# Constants to be used in dict_values_fulfill_demand
elec_bus = "Elec"
demand = "Demand"
generator = "Generator"
storage = "Storage"
energy_vector = "Electricity"
production = "Production"
time_series = pd.Series([0, 10, 100, 10, 0])
# Dictionary to be used in the tests for check_energy_system_can_fulfill_max_demand()
dict_values_fulfill_demand = {
    ENERGY_BUSSES: {
        elec_bus: {
            ENERGY_VECTOR: energy_vector,
            ASSET_DICT: {
                demand: demand + LABEL,
                generator: generator + LABEL,
                production: production + LABEL,
                storage: storage + LABEL,
            },
        }
    },
    ENERGY_CONSUMPTION: {
        demand: {
            ENERGY_VECTOR: energy_vector,
            TIMESERIES_PEAK: {VALUE: max(time_series)},
            DISPATCHABILITY: {VALUE: False},
        }
    },
    ENERGY_CONVERSION: {
        generator: {
            ENERGY_VECTOR: energy_vector,
            INSTALLED_CAP: {VALUE: 0},
            MAXIMUM_CAP: {VALUE: None},
            OPTIMIZE_CAP: {VALUE: False},
            OUTFLOW_DIRECTION: elec_bus,
        }
    },
    ENERGY_PRODUCTION: {
        production: {
            ENERGY_VECTOR: energy_vector,
            INSTALLED_CAP: {VALUE: 0},
            MAXIMUM_CAP: {VALUE: None},
            OPTIMIZE_CAP: {VALUE: False}
        }
    },
    ENERGY_STORAGE: {
        storage: {
            ENERGY_VECTOR: energy_vector,
            OPTIMIZE_CAP: {VALUE: False},
            OUTPUT_POWER: {INSTALLED_CAP: {VALUE: 0}},
        }
    },
}


def test_check_energy_system_can_fulfill_max_demand_sufficient_capacities(caplog):
    dict_values_v1 = deepcopy(dict_values_fulfill_demand)
    dict_values_v1[ENERGY_CONVERSION][generator].update({MAXIMUM_CAP: {VALUE: 100}})
    dict_values_v1[ENERGY_CONVERSION][generator].update({OPTIMIZE_CAP: {VALUE: True}})

    with caplog.at_level(logging.DEBUG):
        peak_generation, peak_demand = C1.check_energy_system_can_fulfill_max_demand(
            dict_values_v1
        )
        assert (
            peak_generation == 100
        ), f"The peak generation should have been 100 but is {peak_generation}"
        assert (
            peak_demand == 100
        ), f"The peak demand should have been 100 but is {peak_demand}"
    assert (
        "The check for assets having sufficient capacities to fulfill the maximum demand has successfully passed"
        in caplog.text
    ), f"As the maximum/installed capacities of the assets in an energy system are sufficient, a successful debug message should have be logged. This did not happen, with peak generation of {peak_generation} and peak demand of {peak_demand}."


def test_check_energy_system_can_fulfill_max_demand_no_maximum_capacity(caplog):
    dict_values_v2 = deepcopy(dict_values_fulfill_demand)
    dict_values_v2[ENERGY_CONVERSION][generator].update({MAXIMUM_CAP: {VALUE: None}})
    dict_values_v2[ENERGY_CONVERSION][generator].update({OPTIMIZE_CAP: {VALUE: True}})

    with caplog.at_level(logging.DEBUG):
        C1.check_energy_system_can_fulfill_max_demand(dict_values_v2)
    assert (
        "The check for assets having sufficient capacities to fulfill the maximum demand has successfully passed"
        in caplog.text
    ), f"If the maximum capacity of an optimizable asset is set to None, a successful debug message should have been logged."


def test_check_energy_system_can_fulfill_max_demand_insufficient_capacities(caplog):
    dict_values_v3 = deepcopy(dict_values_fulfill_demand)
    dict_values_v3[ENERGY_CONVERSION][generator].update({MAXIMUM_CAP: {VALUE: 90}})
    dict_values_v3[ENERGY_CONVERSION][generator].update({OPTIMIZE_CAP: {VALUE: True}})

    with caplog.at_level(logging.WARNING):
        peak_generation, peak_demand = C1.check_energy_system_can_fulfill_max_demand(
            dict_values_v3
        )
    assert (
        "might have insufficient capacities" in caplog.text
    ), f"If the maximum/installed capacities of the assets in an energy system are insufficient, a warning message should have been logged. This did not happen, with peak generation of {peak_generation} and peak demand of {peak_demand}."


def test_check_energy_system_can_fulfill_max_demand_with_storage(caplog):
    dict_values_v4 = deepcopy(dict_values_fulfill_demand)
    dict_values_v4[ENERGY_CONVERSION][generator].update({INSTALLED_CAP: {VALUE: 80}})
    dict_values_v4[ENERGY_STORAGE][storage].update({OPTIMIZE_CAP: {VALUE: True}})

    with caplog.at_level(logging.DEBUG):
        C1.check_energy_system_can_fulfill_max_demand(dict_values_v4)
    assert (
        "this check does not determine if the storage can be sufficiently"
        in caplog.text
    ), f"If a storage asset is included in the energy system, a successful debug message should have been logged."


def test_check_for_sufficient_assets_on_busses_example_bus_passes():
    dict_values = {
        ENERGY_BUSSES: {
            "Bus": {
                ASSET_DICT: {
                    "asset_1": "asset_1",
                    "asset_2": "asset_2",
                    "asset_3": "asset_3",
                }
            }
        }
    }
    output = C1.check_for_sufficient_assets_on_busses(dict_values)
    assert (
        output == True
    ), f"The bus has 3 assets connected to it, but the test does not pass."


def test_check_for_sufficient_assets_on_busses_example_bus_fails(caplog):
    dict_values = {
        ENERGY_BUSSES: {
            "Bus": {ASSET_DICT: {"asset_1": "asset_1", "asset_2": "asset_2"}}
        }
    }
    with caplog.at_level(logging.ERROR):
        C1.check_for_sufficient_assets_on_busses(dict_values)
    assert (
        "too few assets connected to it" in caplog.text
    ), f"The bus has less then 3 assets connected to it, but the test passes."


def test_check_for_sufficient_assets_on_busses_skipped_for_peak_demand_pricing_bus():
    dict_values = {
        ENERGY_BUSSES: {
            "Bus"
            + DSO_PEAK_DEMAND_SUFFIX: {
                ASSET_DICT: {"asset_1": "asset_1", "asset_3": "asset_3"}
            }
        }
    }
    output = C1.check_for_sufficient_assets_on_busses(dict_values)
    assert (
        output == True
    ), f"The bus is a peak demand pricing bus and has less then 3 assets connected to it.Still, the test should pass, as it should not be applied to the peak demand pricing bus."


def test_check_energy_system_can_fulfill_max_demand_sufficient_dispatchable_production(caplog):
    dict_values_v5 = deepcopy(dict_values_fulfill_demand)
    dict_values_v5[ENERGY_PRODUCTION][production].update({MAXIMUM_CAP: {VALUE: 100}})
    dict_values_v5[ENERGY_PRODUCTION][production].update({OPTIMIZE_CAP: {VALUE: True}})

    with caplog.at_level(logging.DEBUG):
        peak_generation, peak_demand = C1.check_energy_system_can_fulfill_max_demand(
            dict_values_v5
        )
        assert (
            peak_generation == 100
        ), f"The peak generation should have been 100 but is {peak_generation}"
        assert (
            peak_demand == 100
        ), f"The peak demand should have been 100 but is {peak_demand}"
    assert (
        "The check for assets having sufficient capacities to fulfill the maximum demand has successfully passed"
        in caplog.text
    ), f"As the maximum/installed capacities of the assets in an energy system are sufficient, a successful debug message should have be logged. This did not happen, with peak generation of {peak_generation} and peak demand of {peak_demand}."


def test_check_energy_system_can_fulfill_max_demand_insufficient_dispatchable_production(caplog):
    dict_values_v6 = deepcopy(dict_values_fulfill_demand)
    dict_values_v6[ENERGY_PRODUCTION][production].update({MAXIMUM_CAP: {VALUE: 90}})
    dict_values_v6[ENERGY_PRODUCTION][production].update({OPTIMIZE_CAP: {VALUE: True}})

    with caplog.at_level(logging.WARNING):
        peak_generation, peak_demand = C1.check_energy_system_can_fulfill_max_demand(
            dict_values_v6
        )
    assert (
        "might have insufficient capacities" in caplog.text
    ), f"If the maximum/installed capacities of the assets in an energy system are insufficient, a warning message should have been logged. This did not happen, with peak generation of {peak_generation} and peak demand of {peak_demand}."


def test_check_energy_system_can_fulfill_max_demand_sufficient_non_dispatchable_production(caplog):
    dict_values_v7 = deepcopy(dict_values_fulfill_demand)
    dict_values_v7[ENERGY_PRODUCTION][production].update({MAXIMUM_CAP: {VALUE: 200}})
    dict_values_v7[ENERGY_PRODUCTION][production].update({OPTIMIZE_CAP: {VALUE: True}})
    dict_values_v7[ENERGY_PRODUCTION][production].update({TIMESERIES_PEAK: {VALUE: 0.5}})

    with caplog.at_level(logging.DEBUG):
        peak_generation, peak_demand = C1.check_energy_system_can_fulfill_max_demand(
            dict_values_v7
        )                                                                                      
        assert (
            peak_generation == 100
        ), f"The peak generation should have been 100 but is {peak_generation}"
        assert (
            peak_demand == 100
        ), f"The peak demand should have been 100 but is {peak_demand}"
    assert (
        "The check for assets having sufficient capacities to fulfill the maximum demand has successfully passed"
        in caplog.text
    ), f"As the maximum/installed capacities of the assets in an energy system are sufficient, a successful debug message should have be logged. This did not happen, with peak generation of {peak_generation} and peak demand of {peak_demand}."


def test_check_energy_system_can_fulfill_max_demand_insufficient_non_dispatchable_production(caplog):
    dict_values_v8 = deepcopy(dict_values_fulfill_demand)
    dict_values_v8[ENERGY_PRODUCTION][production].update({MAXIMUM_CAP: {VALUE: 100}})
    dict_values_v8[ENERGY_PRODUCTION][production].update({OPTIMIZE_CAP: {VALUE: True}})
    dict_values_v8[ENERGY_PRODUCTION][production].update({TIMESERIES_PEAK: {VALUE: 0.5}})

    with caplog.at_level(logging.WARNING):
        peak_generation, peak_demand = C1.check_energy_system_can_fulfill_max_demand(
            dict_values_v8
        )                                                                                                                                                                                                                                      
    assert (
        "might have insufficient capacities" in caplog.text
    ), f"If the maximum/installed capacities of the assets in an energy system are insufficient, a warning message should have been logged. This did not happen, with peak generation of {peak_generation} and peak demand of {peak_demand}."


from multi_vector_simulator.cli import main
import shutil
import mock
import argparse
from _constants import (
    TEST_REPO_PATH,
    CSV_EXT,
)
from multi_vector_simulator.utils.constants import LOGFILE


@mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
def test_check_energy_system_can_fulfill_max_demand_fails_mvs_runthrough(caplog):
    """This test makes sure that the C1.check_energy_system_can_fulfill_max_demand not only works as a function, but as an integrated function of the MVS model, as it is dependent on a lot of pre-processing steps where things in the future may be changed."""
    TEST_INPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_inputs")
    TEST_OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "benchmark_test_outputs")
    if os.path.exists(TEST_OUTPUT_PATH):
        shutil.rmtree(TEST_OUTPUT_PATH, ignore_errors=True)

    try:
        use_case = "validity_check_insufficient_capacities"
        main(
            overwrite=True,
            display_output="warning",
            path_input_folder=os.path.join(TEST_INPUT_PATH, use_case),
            input_type=CSV_EXT,
            path_output_folder=os.path.join(TEST_OUTPUT_PATH, use_case),
        )
    except:
        pass

    logfile = open(os.path.join(TEST_OUTPUT_PATH, use_case, LOGFILE), "r")
    log = logfile.read()

    assert "might have insufficient capacities" in log

# def test_check_input_values():
#     pass
#     # todo note: function is not used so far

# def test_all_valid_intervals():
#     pass
#     # todo note: function is not used so far
