import pandas as pd
import pytest
import numpy as np

import multi_vector_simulator.E3_indicator_calculation as E3
from multi_vector_simulator.utils.constants import (
    DEFAULT_WEIGHTS_ENERGY_CARRIERS,
    PROJECT_DATA,
)
from multi_vector_simulator.utils.constants_json_strings import (
    ECONOMIC_DATA,
    ENERGY_PRODUCTION,
    ENERGY_PROVIDERS,
    ENERGY_CONSUMPTION,
    LABEL,
    VALUE,
    CRF,
    LES_ENERGY_VECTOR_S,
    KPI,
    KPI_SCALARS_DICT,
    KPI_UNCOUPLED_DICT,
    KPI_COST_MATRIX,
    COST_TOTAL,
    ANNUITY_TOTAL,
    ENERGY_VECTOR,
    TOTAL_FLOW,
    RENEWABLE_SHARE_DSO,
    RENEWABLE_ASSET_BOOL,
    DSO_CONSUMPTION,
    TOTAL_CONSUMPTION_FROM_PROVIDERS,
    TOTAL_RENEWABLE_GENERATION_IN_LES,
    TOTAL_NON_RENEWABLE_GENERATION_IN_LES,
    TOTAL_RENEWABLE_ENERGY_USE,
    TOTAL_NON_RENEWABLE_ENERGY_USE,
    RENEWABLE_FACTOR,
    RENEWABLE_SHARE_OF_LOCAL_GENERATION,
    TOTAL_DEMAND,
    SUFFIX_ELECTRICITY_EQUIVALENT,
    ATTRIBUTED_COSTS,
    LCOeleq,
    TOTAL_FEEDIN,
    DSO_FEEDIN,
    AUTO_SINK,
    TOTAL_GENERATION_IN_LES,
    ONSITE_ENERGY_FRACTION,
    TOTAL_EXCESS,
    ONSITE_ENERGY_MATCHING,
    DEGREE_OF_AUTONOMY,
    TOTAL_EMISSIONS,
    KPI_SCALAR_MATRIX,
    EMISSION_FACTOR,
    SPECIFIC_EMISSIONS_ELEQ,
    UNIT_SPECIFIC_EMISSIONS,
    UNIT_EMISSIONS,
    DEGREE_OF_NZE,
)

electricity = "Electricity"
h2 = "H2"

numbers = [10, 15, 20, 25]

# for test_totalling_scalars_values
dict_scalars = {
    KPI: {
        KPI_COST_MATRIX: pd.DataFrame(
            {
                LABEL: ["asset_1", "asset_2"],
                COST_TOTAL: [numbers[1], numbers[3]],
                ANNUITY_TOTAL: [numbers[0], numbers[2]],
            }
        ),
        KPI_SCALARS_DICT: {},
    }
}
scalars_expected = {
    COST_TOTAL: numbers[1] + numbers[3],
    ANNUITY_TOTAL: numbers[0] + numbers[2],
}


def test_totalling_scalars_values():
    """ """
    E3.all_totals(dict_scalars)
    return dict_scalars[KPI][KPI_SCALARS_DICT] == scalars_expected


# for this test_total_renewable_and_non_renewable_origin_of_each_sector test

dso = "DSO"
pv_plant = "PV_plant"

flow_dso = 50
flow_pv_local = 100
renewable_share_dso = 0.1

dict_renewable_energy_use = {
    ENERGY_PRODUCTION: {
        dso
        + DSO_CONSUMPTION: {ENERGY_VECTOR: electricity, TOTAL_FLOW: {VALUE: flow_dso},},
        pv_plant: {
            ENERGY_VECTOR: electricity,
            TOTAL_FLOW: {VALUE: flow_pv_local},
            RENEWABLE_ASSET_BOOL: {VALUE: True},
        },
    },
    ENERGY_PROVIDERS: {
        dso: {
            RENEWABLE_SHARE_DSO: {VALUE: renewable_share_dso},
            ENERGY_VECTOR: electricity,
        }
    },
    KPI: {KPI_SCALARS_DICT: {}, KPI_UNCOUPLED_DICT: {}},
    PROJECT_DATA: {LES_ENERGY_VECTOR_S: {electricity: electricity}},
}

exp_res = flow_pv_local + (flow_dso * renewable_share_dso)
exp_non_res = flow_dso * (1 - renewable_share_dso)


def test_total_renewable_and_non_renewable_origin_of_each_sector():
    """ """
    E3.add_total_renewable_and_non_renewable_energy_origin(dict_renewable_energy_use)
    kpi_list = [
        TOTAL_RENEWABLE_GENERATION_IN_LES,
        TOTAL_NON_RENEWABLE_GENERATION_IN_LES,
        TOTAL_RENEWABLE_ENERGY_USE,
        TOTAL_NON_RENEWABLE_ENERGY_USE,
    ]
    for k in kpi_list:
        assert (
            k in dict_renewable_energy_use[KPI][KPI_UNCOUPLED_DICT]
        ), f"k not in {KPI_UNCOUPLED_DICT}"
        assert (
            k in dict_renewable_energy_use[KPI][KPI_SCALARS_DICT]
        ), f"k not in {KPI_SCALARS_DICT}"

    assert (
        dict_renewable_energy_use[KPI][KPI_UNCOUPLED_DICT][
            TOTAL_RENEWABLE_GENERATION_IN_LES
        ][electricity]
        == flow_pv_local
    )
    assert (
        dict_renewable_energy_use[KPI][KPI_UNCOUPLED_DICT][
            TOTAL_NON_RENEWABLE_GENERATION_IN_LES
        ][electricity]
        == 0
    )
    assert (
        dict_renewable_energy_use[KPI][KPI_UNCOUPLED_DICT][TOTAL_RENEWABLE_ENERGY_USE][
            electricity
        ]
        == exp_res
    )
    assert (
        dict_renewable_energy_use[KPI][KPI_UNCOUPLED_DICT][
            TOTAL_NON_RENEWABLE_ENERGY_USE
        ][electricity]
        == exp_non_res
    )


# Tests renewable factor
def test_renewable_factor_one_sector():
    """ """
    dict_res = {
        PROJECT_DATA: {LES_ENERGY_VECTOR_S: {electricity: electricity}},
        KPI: {
            KPI_SCALARS_DICT: {
                TOTAL_NON_RENEWABLE_ENERGY_USE: 50,
                TOTAL_RENEWABLE_ENERGY_USE: 50,
            },
            KPI_UNCOUPLED_DICT: {
                TOTAL_RENEWABLE_ENERGY_USE: {electricity: 50},
                TOTAL_NON_RENEWABLE_ENERGY_USE: {electricity: 50},
            },
        },
    }

    E3.add_renewable_factor(dict_res)
    expected_value = 0.5
    assert (
        RENEWABLE_FACTOR in dict_res[KPI][KPI_UNCOUPLED_DICT]
    ), f"KPI {RENEWABLE_FACTOR} not added to dict_values[KPI][KPI_UNCOUPLED_DICT]"
    assert (
        electricity in dict_res[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_FACTOR]
    ), f"KPI {RENEWABLE_FACTOR} not defined for vector {electricity}."
    assert (
        dict_res[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_FACTOR][electricity]
        == expected_value
    ), f"{RENEWABLE_FACTOR} of {electricity} sector not expected value."
    assert (
        dict_res[KPI][KPI_SCALARS_DICT][RENEWABLE_FACTOR] == expected_value
    ), f"System-wide {RENEWABLE_FACTOR} of not expected value."


def test_renewable_factor_two_sectors():
    dict_res = {
        PROJECT_DATA: {LES_ENERGY_VECTOR_S: {electricity: electricity, h2: h2}},
        KPI: {
            KPI_SCALARS_DICT: {
                TOTAL_NON_RENEWABLE_ENERGY_USE: 100,
                TOTAL_RENEWABLE_ENERGY_USE: 100,
            },
            KPI_UNCOUPLED_DICT: {
                TOTAL_RENEWABLE_ENERGY_USE: {electricity: 50, h2: 50},
                TOTAL_NON_RENEWABLE_ENERGY_USE: {electricity: 50, h2: 50},
            },
        },
    }
    E3.add_renewable_factor(dict_res)
    assert (
        RENEWABLE_FACTOR in dict_res[KPI][KPI_UNCOUPLED_DICT]
    ), f"KPI {RENEWABLE_FACTOR} not added to dict_values[KPI][KPI_UNCOUPLED_DICT]"

    exp_res_sector = {
        electricity: 0.5,
        h2: 0.5,
    }
    expected_value = 0.5
    for k in [electricity, h2]:
        assert (
            k in dict_res[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_FACTOR]
        ), f"{RENEWABLE_FACTOR} not defined for sector {k}."
        assert (
            dict_res[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_FACTOR][k] == exp_res_sector[k]
        ), f"{RENEWABLE_FACTOR} of sector {k} no expected value."

    assert (
        dict_res[KPI][KPI_SCALARS_DICT][RENEWABLE_FACTOR] == expected_value
    ), f"System-wide renewable factor not expected value."


# Tests renewable_share_of_local_generation
def test_renewable_share_of_local_generation_one_sector():
    """ """
    dict_res = {
        PROJECT_DATA: {LES_ENERGY_VECTOR_S: {electricity: electricity}},
        KPI: {
            KPI_SCALARS_DICT: {
                TOTAL_NON_RENEWABLE_GENERATION_IN_LES: 50,
                TOTAL_RENEWABLE_GENERATION_IN_LES: 50,
            },
            KPI_UNCOUPLED_DICT: {
                TOTAL_RENEWABLE_GENERATION_IN_LES: {electricity: 50},
                TOTAL_NON_RENEWABLE_GENERATION_IN_LES: {electricity: 50},
            },
        },
    }
    E3.add_renewable_share_of_local_generation(dict_res)
    assert (
        RENEWABLE_SHARE_OF_LOCAL_GENERATION in dict_res[KPI][KPI_UNCOUPLED_DICT]
    ), f"KPI {RENEWABLE_SHARE_OF_LOCAL_GENERATION} not added to dict_values[KPI][KPI_UNCOUPLED_DICT]"
    assert (
        electricity
        in dict_res[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_SHARE_OF_LOCAL_GENERATION]
    ), f"{RENEWABLE_SHARE_OF_LOCAL_GENERATION} of sector {electricity} not defined."
    assert (
        dict_res[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_SHARE_OF_LOCAL_GENERATION][
            electricity
        ]
        == 0.5
    ), f"{RENEWABLE_SHARE_OF_LOCAL_GENERATION} of sector {electricity} not of expected value."
    assert (
        dict_res[KPI][KPI_SCALARS_DICT][RENEWABLE_SHARE_OF_LOCAL_GENERATION] == 0.5
    ), f"System-wide {RENEWABLE_SHARE_OF_LOCAL_GENERATION} not of expected value."


def test_renewable_share_of_local_generation_two_sectors():
    dict_res = {
        PROJECT_DATA: {LES_ENERGY_VECTOR_S: {electricity: electricity, h2: h2}},
        KPI: {
            KPI_SCALARS_DICT: {
                TOTAL_NON_RENEWABLE_GENERATION_IN_LES: 100,
                TOTAL_RENEWABLE_GENERATION_IN_LES: 100,
            },
            KPI_UNCOUPLED_DICT: {
                TOTAL_RENEWABLE_GENERATION_IN_LES: {electricity: 50, h2: 50},
                TOTAL_NON_RENEWABLE_GENERATION_IN_LES: {electricity: 50, h2: 50},
            },
        },
    }
    E3.add_renewable_share_of_local_generation(dict_res)
    exp_res_sector = {electricity: 0.5, h2: 0.5}
    assert RENEWABLE_SHARE_OF_LOCAL_GENERATION in dict_res[KPI][KPI_UNCOUPLED_DICT]
    for k in [electricity, h2]:
        assert (
            k in dict_res[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_SHARE_OF_LOCAL_GENERATION]
        ), f"{RENEWABLE_SHARE_OF_LOCAL_GENERATION} of sector {k} not added."
        assert (
            dict_res[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_SHARE_OF_LOCAL_GENERATION][k]
            == exp_res_sector[k]
        ), f"Expected value of {RENEWABLE_SHARE_OF_LOCAL_GENERATION} for vector {k} not reached."

    assert (
        dict_res[KPI][KPI_SCALARS_DICT][RENEWABLE_SHARE_OF_LOCAL_GENERATION] == 0.5
    ), f"Expected value of sector-wide {RENEWABLE_SHARE_OF_LOCAL_GENERATION} not reached."


def test_renewable_share_equation_is_1():
    """ """
    tot_res = 100
    tot_non_res = 0
    renewable_share = E3.equation_renewable_share(tot_res, tot_non_res)
    assert renewable_share == tot_res / (tot_res + tot_non_res)


def test_renewable_share_equation_is_0():
    """ """
    tot_res = 0
    tot_non_res = 100
    renewable_share = E3.equation_renewable_share(tot_res, tot_non_res)
    assert renewable_share == tot_res / (tot_res + tot_non_res)


def test_renewable_share_equation_below_1():
    """ """
    tot_res = 20
    tot_non_res = 100
    renewable_share = E3.equation_renewable_share(tot_res, tot_non_res)
    assert renewable_share == tot_res / (tot_res + tot_non_res)


def test_renewable_share_equation_no_generation():
    """ """
    tot_res = 0
    tot_non_res = 0
    renewable_share = E3.equation_renewable_share(tot_res, tot_non_res)
    assert renewable_share == 0


# Tests for weighting_for_sector_coupled_kpi

dict_weighting_unknown_sector = {
    PROJECT_DATA: {LES_ENERGY_VECTOR_S: {"Water": "Water"}},
    KPI: {
        KPI_UNCOUPLED_DICT: {RENEWABLE_FACTOR: {"Water": numbers[0]}},
        KPI_SCALARS_DICT: {},
    },
}

dict_weighting_one_sector = {
    PROJECT_DATA: {LES_ENERGY_VECTOR_S: {electricity: electricity}},
    KPI: {
        KPI_UNCOUPLED_DICT: {RENEWABLE_FACTOR: {electricity: numbers[1]}},
        KPI_SCALARS_DICT: {},
    },
}

dict_weighting_two_sectors = {
    PROJECT_DATA: {LES_ENERGY_VECTOR_S: {electricity: electricity, h2: h2}},
    KPI: {
        KPI_UNCOUPLED_DICT: {
            RENEWABLE_FACTOR: {electricity: numbers[1], h2: numbers[2]}
        },
        KPI_SCALARS_DICT: {},
    },
}


def test_weighting_for_sector_coupled_kpi_unknown_sector():
    """ """
    with pytest.raises(ValueError):
        E3.weighting_for_sector_coupled_kpi(
            dict_weighting_unknown_sector, RENEWABLE_FACTOR
        )


def test_weighting_for_sector_coupled_kpi_one_sector():
    """ """
    E3.weighting_for_sector_coupled_kpi(dict_weighting_one_sector, RENEWABLE_FACTOR)
    assert RENEWABLE_FACTOR in dict_weighting_one_sector[KPI][KPI_SCALARS_DICT]
    assert (
        dict_weighting_one_sector[KPI][KPI_SCALARS_DICT][RENEWABLE_FACTOR] == numbers[1]
    )


def test_weighting_for_sector_coupled_kpi_multiple_sectors():
    """ """
    E3.weighting_for_sector_coupled_kpi(dict_weighting_two_sectors, RENEWABLE_FACTOR)
    expected_value = (
        numbers[1] + numbers[2] * DEFAULT_WEIGHTS_ENERGY_CARRIERS[h2][VALUE]
    )
    assert RENEWABLE_FACTOR in dict_weighting_two_sectors[KPI][KPI_SCALARS_DICT]
    assert (
        dict_weighting_two_sectors[KPI][KPI_SCALARS_DICT][RENEWABLE_FACTOR]
        == expected_value
    )


npc = 1000
total_demand = 100
dict_values = {
    ECONOMIC_DATA: {CRF: {VALUE: 0.10}},
    KPI: {
        KPI_SCALARS_DICT: {
            COST_TOTAL: npc,
            TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT: total_demand,
            TOTAL_DEMAND + electricity: total_demand,
            TOTAL_DEMAND + electricity + SUFFIX_ELECTRICITY_EQUIVALENT: total_demand,
        }
    },
    PROJECT_DATA: {LES_ENERGY_VECTOR_S: {electricity: electricity}},
}


def test_add_levelized_cost_of_energy_carriers_one_sector():
    E3.add_levelized_cost_of_energy_carriers(dict_values)

    expected_value = {
        ATTRIBUTED_COSTS + electricity: 1000,
        LCOeleq
        + electricity: 1000 * dict_values[ECONOMIC_DATA][CRF][VALUE] / total_demand,
        LCOeleq: 1000 * dict_values[ECONOMIC_DATA][CRF][VALUE] / total_demand,
    }

    for kpi in [ATTRIBUTED_COSTS, LCOeleq]:
        assert kpi + electricity in dict_values[KPI][KPI_SCALARS_DICT]
        assert (
            dict_values[KPI][KPI_SCALARS_DICT][kpi + electricity]
            == expected_value[kpi + electricity]
        )

    assert LCOeleq in dict_values[KPI][KPI_SCALARS_DICT]
    assert dict_values[KPI][KPI_SCALARS_DICT][LCOeleq] == expected_value[LCOeleq]


def test_add_levelized_cost_of_energy_carriers_two_sectors():
    dict_values[KPI][KPI_SCALARS_DICT].update({TOTAL_DEMAND + h2: 100})
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {
            TOTAL_DEMAND
            + h2
            + SUFFIX_ELECTRICITY_EQUIVALENT: dict_values[KPI][KPI_SCALARS_DICT][
                TOTAL_DEMAND + h2
            ]
            * DEFAULT_WEIGHTS_ENERGY_CARRIERS[h2][VALUE]
        }
    )
    dict_values[KPI][KPI_SCALARS_DICT].update(
        {
            TOTAL_DEMAND
            + SUFFIX_ELECTRICITY_EQUIVALENT: dict_values[KPI][KPI_SCALARS_DICT][
                TOTAL_DEMAND + electricity + SUFFIX_ELECTRICITY_EQUIVALENT
            ]
            + dict_values[KPI][KPI_SCALARS_DICT][
                TOTAL_DEMAND + h2 + SUFFIX_ELECTRICITY_EQUIVALENT
            ]
        }
    )
    dict_values[PROJECT_DATA][LES_ENERGY_VECTOR_S].update({h2: h2})
    E3.add_levelized_cost_of_energy_carriers(dict_values)

    expected_value = {
        ATTRIBUTED_COSTS
        + electricity: 1000
        * dict_values[KPI][KPI_SCALARS_DICT][
            TOTAL_DEMAND + electricity + SUFFIX_ELECTRICITY_EQUIVALENT
        ]
        / dict_values[KPI][KPI_SCALARS_DICT][
            TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT
        ],
        ATTRIBUTED_COSTS
        + h2: 1000
        * dict_values[KPI][KPI_SCALARS_DICT][
            TOTAL_DEMAND + h2 + SUFFIX_ELECTRICITY_EQUIVALENT
        ]
        / dict_values[KPI][KPI_SCALARS_DICT][
            TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT
        ],
    }
    expected_value.update(
        {
            LCOeleq
            + electricity: dict_values[KPI][KPI_SCALARS_DICT][
                ATTRIBUTED_COSTS + electricity
            ]
            * dict_values[ECONOMIC_DATA][CRF][VALUE]
            / dict_values[KPI][KPI_SCALARS_DICT][TOTAL_DEMAND + electricity],
            LCOeleq
            + electricity: dict_values[KPI][KPI_SCALARS_DICT][ATTRIBUTED_COSTS + h2]
            * dict_values[ECONOMIC_DATA][CRF][VALUE]
            / dict_values[KPI][KPI_SCALARS_DICT][TOTAL_DEMAND + h2],
            LCOeleq: 1000
            * dict_values[ECONOMIC_DATA][CRF][VALUE]
            / dict_values[KPI][KPI_SCALARS_DICT][
                TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT
            ],
        }
    )

    for kpi in [ATTRIBUTED_COSTS, LCOeleq]:
        assert kpi + electricity in dict_values[KPI][KPI_SCALARS_DICT]
        assert (
            dict_values[KPI][KPI_SCALARS_DICT][kpi + electricity]
            == expected_value[kpi + electricity]
        )

    assert LCOeleq in dict_values[KPI][KPI_SCALARS_DICT]
    assert dict_values[KPI][KPI_SCALARS_DICT][LCOeleq] == expected_value[LCOeleq]


def test_equation_levelized_cost_of_energy_carrier_total_demand_electricity_equivalent_larger_0_total_flow_energy_carrier_larger_0():
    (
        lcoe_energy_carrier,
        attributed_costs,
    ) = E3.equation_levelized_cost_of_energy_carrier(
        cost_total=1000,
        crf=0.1,
        total_flow_energy_carrier_eleq=500,
        total_demand_electricity_equivalent=1000,
        total_flow_energy_carrier=100,
    )
    assert attributed_costs == 500 / 1000 * 1000
    assert lcoe_energy_carrier == 500 * 0.1 / 100


def test_equation_levelized_cost_of_energy_carrier_total_demand_electricity_equivalent_larger_0_total_flow_energy_carrier_is_0():
    (
        lcoe_energy_carrier,
        attributed_costs,
    ) = E3.equation_levelized_cost_of_energy_carrier(
        cost_total=1000,
        crf=0.1,
        total_flow_energy_carrier_eleq=0,
        total_demand_electricity_equivalent=1000,
        total_flow_energy_carrier=0,
    )
    assert attributed_costs == 0
    assert lcoe_energy_carrier == 0


def test_equation_levelized_cost_of_energy_carrier_total_demand_electricity_equivalent_is_0_total_flow_energy_carrier_is_0():
    (
        lcoe_energy_carrier,
        attributed_costs,
    ) = E3.equation_levelized_cost_of_energy_carrier(
        cost_total=1000,
        crf=0.1,
        total_flow_energy_carrier_eleq=0,
        total_demand_electricity_equivalent=0,
        total_flow_energy_carrier=0,
    )
    assert attributed_costs == 0
    assert lcoe_energy_carrier == 0


def test_add_total_feedin_electricity_equivalent():
    """ """

    dso = "DSO"
    feedin = 1000
    consumption_asset = str(dso + DSO_FEEDIN + AUTO_SINK)
    dict_values_feedin = {
        ENERGY_PROVIDERS: {dso},
        ENERGY_CONSUMPTION: {
            consumption_asset: {
                ENERGY_VECTOR: "Electricity",
                TOTAL_FLOW: {VALUE: feedin},
            }
        },
        KPI: {KPI_SCALARS_DICT: {}},
        PROJECT_DATA: {LES_ENERGY_VECTOR_S: {electricity: electricity}},
    }

    E3.add_total_feedin_electricity_equivalent(dict_values_feedin)

    assert (
        dict_values_feedin[KPI][KPI_SCALARS_DICT][
            TOTAL_FEEDIN + SUFFIX_ELECTRICITY_EQUIVALENT
        ]
        == feedin
    ), f"The total_feedin_electricity_equivalent is added successfully to the list of KPI's."


def test_add_onsite_energy_fraction():
    """ """

    total_generation = 50
    total_feedin = 20
    dict_values_OEF = {
        KPI: {
            KPI_SCALARS_DICT: {
                TOTAL_GENERATION_IN_LES: total_generation,
                TOTAL_FEEDIN + SUFFIX_ELECTRICITY_EQUIVALENT: total_feedin,
            }
        },
    }
    E3.add_onsite_energy_fraction(dict_values_OEF)

    output = (total_generation - total_feedin) / total_generation

    assert (
        dict_values_OEF[KPI][KPI_SCALARS_DICT][ONSITE_ENERGY_FRACTION] == output
    ), f"The onsite energy fraction is added successfully to the list of KPI's."


def test_add_onsite_energy_matching():
    """ """

    total_generation = 50
    total_feedin = 20
    total_excess = 10
    total_demand = 100
    dict_values_OEM = {
        KPI: {
            KPI_SCALARS_DICT: {
                TOTAL_GENERATION_IN_LES: total_generation,
                TOTAL_FEEDIN + SUFFIX_ELECTRICITY_EQUIVALENT: total_feedin,
                TOTAL_EXCESS + SUFFIX_ELECTRICITY_EQUIVALENT: total_excess,
                TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT: total_demand,
            }
        },
    }
    E3.add_onsite_energy_matching(dict_values_OEM)

    onsite_energy_matching = (
        total_generation - total_feedin - total_excess
    ) / total_demand

    assert (
        dict_values_OEM[KPI][KPI_SCALARS_DICT][ONSITE_ENERGY_MATCHING]
        == onsite_energy_matching
    ), f"The onsite energy matching is added successfully to the list of KPI's."


def test_add_degree_of_autonomy():
    """ """

    total_consumption_from_grid = 50
    total_demand = 100
    dict_values_DA = {
        KPI: {
            KPI_SCALARS_DICT: {
                TOTAL_CONSUMPTION_FROM_PROVIDERS
                + SUFFIX_ELECTRICITY_EQUIVALENT: total_consumption_from_grid,
                TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT: total_demand,
            }
        },
    }
    E3.add_degree_of_autonomy(dict_values_DA)

    degree_of_autonomy = (total_demand - total_consumption_from_grid) / total_demand
    assert (
        DEGREE_OF_AUTONOMY in dict_values_DA[KPI][KPI_SCALARS_DICT]
    ), f"The {DEGREE_OF_AUTONOMY} is not added to {KPI_SCALARS_DICT}"
    assert (
        dict_values_DA[KPI][KPI_SCALARS_DICT][DEGREE_OF_AUTONOMY] == degree_of_autonomy
    ), f"The degree of autonomy is not added successfully to the list of KPI's."


def test_equation_degree_of_autonomy():
    """ """
    total_consumption_from_grid = 30
    total_demand = 100
    degree_of_autonomy = E3.equation_degree_of_autonomy(
        total_consumption_from_grid, total_demand
    )
    exp = (total_demand - total_consumption_from_grid) / total_demand
    assert degree_of_autonomy == exp, (
        f"The degree_of_autonomy ({degree_of_autonomy}) is not calculated correctly. "
        f"It should be equal to {exp}."
    )


def test_add_degree_of_net_zero_energy():
    """ """
    total_feedin = 60
    total_grid_consumption = 100
    total_demand = 10
    dict_values_NZE = {
        KPI: {
            KPI_SCALARS_DICT: {
                TOTAL_FEEDIN + SUFFIX_ELECTRICITY_EQUIVALENT: total_feedin,
                TOTAL_CONSUMPTION_FROM_PROVIDERS
                + SUFFIX_ELECTRICITY_EQUIVALENT: total_grid_consumption,
                TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT: total_demand,
            }
        },
    }
    E3.add_degree_of_net_zero_energy(dict_values_NZE)

    degree_of_nze = 1 + (total_feedin - total_grid_consumption) / total_demand

    assert (
        DEGREE_OF_NZE in dict_values_NZE[KPI][KPI_SCALARS_DICT]
    ), f"The {DEGREE_OF_NZE} is not added to {KPI_SCALARS_DICT}"
    assert (
        dict_values_NZE[KPI][KPI_SCALARS_DICT][DEGREE_OF_NZE] == degree_of_nze
    ), f"The degree of NZE is not added successfully to the list of KPI's."


def test_equation_degree_of_net_zero_energy():
    """ """
    total_feedin = 60
    total_grid_consumption = 80
    total_demand = 100
    degree_of_nze = E3.equation_degree_of_net_zero_energy(
        total_feedin, total_grid_consumption, total_demand
    )
    exp = 1 + (total_feedin - total_grid_consumption) / total_demand
    assert degree_of_nze == exp, (
        f"The degree_of_nze ({degree_of_nze}) is not calculated correctly. "
        f"It should be equal to {exp}."
    )


def test_equation_onsite_energy_fraction():
    """ """
    total_generation = 30
    total_feedin = 10
    onsite_energy_fraction = E3.equation_onsite_energy_fraction(
        total_generation, total_feedin
    )
    assert (
        onsite_energy_fraction == (total_generation - total_feedin) / total_generation
    ), (
        f"The onsite_energy_fraction ({onsite_energy_fraction}) is not calculated correctly. "
        f"It should be equal to {(total_generation - total_feedin)/ total_generation}."
    )


def test_equation_onsite_energy_matching():
    """ """
    total_generation = 30
    total_feedin = 10
    total_excess = 10
    total_demand = 100

    onsite_energy_matching = E3.equation_onsite_energy_matching(
        total_generation, total_feedin, total_excess, total_demand
    )
    assert (
        onsite_energy_matching
        == (total_generation - total_feedin - total_excess) / total_demand
    ), (
        f"The onsite_energy_matching ({onsite_energy_matching}) is not calculated correctly. "
        f"It should be equal to {(total_generation - total_feedin - total_excess) / total_demand}."
    )


def test_calculate_emissions_from_flow():
    dict_asset = {TOTAL_FLOW: {VALUE: 100}, EMISSION_FACTOR: {VALUE: 0.5}}
    E3.calculate_emissions_from_flow(dict_asset)
    assert (
        dict_asset[TOTAL_EMISSIONS][VALUE] == 50
    ), f"{TOTAL_EMISSIONS} [{UNIT_EMISSIONS}] of an asset should be total flow times emission factor (in this case: 100*0.5=50), but is {dict_asset[TOTAL_EMISSIONS][VALUE]}."


def test_calculate_emissions_from_flow_zero_emissions():
    dict_asset = {TOTAL_FLOW: {VALUE: 100}, EMISSION_FACTOR: {VALUE: 0}}
    E3.calculate_emissions_from_flow(dict_asset)
    assert (
        dict_asset[TOTAL_EMISSIONS][VALUE] == 0
    ), f"{TOTAL_EMISSIONS} [{UNIT_EMISSIONS}] of an asset with an emission_factor of zero should be 0, but is {dict_asset[TOTAL_EMISSIONS][VALUE]}."


def test_add_total_emissions():
    dict_values = {
        KPI: {
            KPI_SCALARS_DICT: {TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT: 100},
            KPI_SCALAR_MATRIX: {TOTAL_EMISSIONS: pd.Series([10, 50, 10, np.nan])},
        }
    }
    E3.add_total_emissions(dict_values)
    assert (
        dict_values[KPI][KPI_SCALARS_DICT][TOTAL_EMISSIONS] == 70
    ), f"{TOTAL_EMISSIONS} [{UNIT_EMISSIONS}] should be the sum of the emissions of all assets, in this case 70, but is {dict_values[KPI][KPI_SCALARS_DICT][TOTAL_EMISSIONS]}."


def test_add_specific_emissions_per_electricity_equivalent():
    dict_values = {
        KPI: {
            KPI_SCALARS_DICT: {
                TOTAL_DEMAND + SUFFIX_ELECTRICITY_EQUIVALENT: 100,
                TOTAL_EMISSIONS: 70,
            },
        }
    }
    E3.add_specific_emissions_per_electricity_equivalent(dict_values)
    emissions_kWheleq = dict_values[KPI][KPI_SCALARS_DICT][SPECIFIC_EMISSIONS_ELEQ]
    assert (
        emissions_kWheleq == 0.7
    ), f"{SPECIFIC_EMISSIONS_ELEQ} [{UNIT_SPECIFIC_EMISSIONS}] should be total_emissions / total_demand_electricity_equivalent (in this case: 70/100=0.7), but is {emissions_kWheleq}."


def test_add_total_consumption_from_provider_electricity_equivalent():
    dso = "DSO"
    exp = 100
    consumption_source = str(dso + DSO_CONSUMPTION)
    dict_values = {
        KPI: {KPI_SCALARS_DICT: {}},
        ENERGY_PROVIDERS: {dso: {ENERGY_VECTOR: electricity}},
        ENERGY_PRODUCTION: {
            consumption_source: {TOTAL_FLOW: {VALUE: exp}, ENERGY_VECTOR: electricity}
        },
    }

    E3.add_total_consumption_from_provider_electricity_equivalent(dict_values)
    for kpi in [
        TOTAL_CONSUMPTION_FROM_PROVIDERS + electricity,
        TOTAL_CONSUMPTION_FROM_PROVIDERS + electricity + SUFFIX_ELECTRICITY_EQUIVALENT,
        TOTAL_CONSUMPTION_FROM_PROVIDERS + SUFFIX_ELECTRICITY_EQUIVALENT,
    ]:
        assert (
            kpi in dict_values[KPI][KPI_SCALARS_DICT]
        ), f"The {kpi} is not included in the {KPI_SCALARS_DICT}, which only holds {dict_values[KPI][KPI_SCALARS_DICT].keys()}."
        assert (
            dict_values[KPI][KPI_SCALARS_DICT][kpi] == exp
        ), f"The {kpi} should have been {exp} but is {dict_values[KPI][KPI_SCALARS_DICT][kpi]}."
