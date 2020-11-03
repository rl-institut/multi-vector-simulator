import pandas as pd
import pytest

import multi_vector_simulator.E3_indicator_calculation as E3
from multi_vector_simulator.utils.constants import (
    DEFAULT_WEIGHTS_ENERGY_CARRIERS,
    PROJECT_DATA,
)
from multi_vector_simulator.utils.constants_json_strings import (
    ECONOMIC_DATA,
    ENERGY_PRODUCTION,
    ENERGY_PROVIDERS,
    LABEL,
    VALUE,
    CRF,
    SECTORS,
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
    TOTAL_RENEWABLE_GENERATION_IN_LES,
    TOTAL_NON_RENEWABLE_GENERATION_IN_LES,
    TOTAL_RENEWABLE_ENERGY_USE,
    TOTAL_NON_RENEWABLE_ENERGY_USE,
    RENEWABLE_SHARE,
    TOTAL_DEMAND,
    SUFFIX_ELECTRICITY_EQUIVALENT,
    ATTRIBUTED_COSTS,
    LCOeleq,
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

flow_small = 50
flow_medium = 100
renewable_share_dso = 0.1

dict_renewable_energy_use = {
    ENERGY_PRODUCTION: {
        dso
        + DSO_CONSUMPTION: {
            ENERGY_VECTOR: electricity,
            TOTAL_FLOW: {VALUE: flow_small},
        },
        pv_plant: {
            ENERGY_VECTOR: electricity,
            TOTAL_FLOW: {VALUE: flow_medium},
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
    PROJECT_DATA: {SECTORS: {electricity: electricity}},
}

exp_res = flow_medium + (flow_small * renewable_share_dso)
exp_non_res = flow_small * (1 - renewable_share_dso)


def test_total_renewable_and_non_renewable_origin_of_each_sector():
    """ """
    E3.total_renewable_and_non_renewable_energy_origin(dict_renewable_energy_use)
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
        == flow_medium
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


# Tests renewable share
def test_renewable_share_one_sector():
    """ """
    E3.total_renewable_and_non_renewable_energy_origin(dict_renewable_energy_use)
    E3.renewable_share(dict_renewable_energy_use)
    exp = exp_res / (exp_non_res + exp_res)
    assert RENEWABLE_SHARE in dict_renewable_energy_use[KPI][KPI_UNCOUPLED_DICT]
    assert (
        electricity
        in dict_renewable_energy_use[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_SHARE]
    )
    assert (
        dict_renewable_energy_use[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_SHARE][electricity]
        == exp
    )
    assert dict_renewable_energy_use[KPI][KPI_SCALARS_DICT][RENEWABLE_SHARE] == exp


def test_renewable_share_two_sectors():
    # Add second sector to dict_renewable_energy_use
    dso_h2 = "DSO_H2"
    dict_renewable_energy_use[ENERGY_PRODUCTION].update(
        {dso_h2 + DSO_CONSUMPTION: {ENERGY_VECTOR: h2, TOTAL_FLOW: {VALUE: flow_small}}}
    )
    dict_renewable_energy_use[ENERGY_PROVIDERS].update(
        {dso_h2: {RENEWABLE_SHARE_DSO: {VALUE: 0}, ENERGY_VECTOR: h2}}
    )
    dict_renewable_energy_use[PROJECT_DATA][SECTORS].update({h2: h2})

    E3.total_renewable_and_non_renewable_energy_origin(dict_renewable_energy_use)
    E3.renewable_share(dict_renewable_energy_use)
    assert RENEWABLE_SHARE in dict_renewable_energy_use[KPI][KPI_UNCOUPLED_DICT]

    exp_total_res = flow_medium + flow_small * renewable_share_dso
    exp_total_non_res_el = flow_small * (1 - renewable_share_dso)
    exp_total_non_res_h2 = flow_small * DEFAULT_WEIGHTS_ENERGY_CARRIERS[h2][VALUE]

    exp_res = exp_total_res / (
        exp_total_non_res_el + exp_total_non_res_h2 + exp_total_res
    )

    exp_res_sector = {
        electricity: exp_total_res / (exp_total_non_res_el + exp_total_res),
        h2: 0 / (exp_total_non_res_h2),
    }

    for k in [electricity, h2]:
        assert k in dict_renewable_energy_use[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_SHARE]
        assert (
            dict_renewable_energy_use[KPI][KPI_UNCOUPLED_DICT][RENEWABLE_SHARE][k]
            == exp_res_sector[k]
        )

    assert dict_renewable_energy_use[KPI][KPI_SCALARS_DICT][RENEWABLE_SHARE] == exp_res


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
    PROJECT_DATA: {SECTORS: {"Water": "Water"}},
    KPI: {
        KPI_UNCOUPLED_DICT: {RENEWABLE_SHARE: {"Water": numbers[0]}},
        KPI_SCALARS_DICT: {},
    },
}

dict_weighting_one_sector = {
    PROJECT_DATA: {SECTORS: {electricity: electricity}},
    KPI: {
        KPI_UNCOUPLED_DICT: {RENEWABLE_SHARE: {electricity: numbers[1]}},
        KPI_SCALARS_DICT: {},
    },
}

dict_weighting_two_sectors = {
    PROJECT_DATA: {SECTORS: {electricity: electricity, h2: h2}},
    KPI: {
        KPI_UNCOUPLED_DICT: {
            RENEWABLE_SHARE: {electricity: numbers[1], h2: numbers[2]}
        },
        KPI_SCALARS_DICT: {},
    },
}


def test_weighting_for_sector_coupled_kpi_unknown_sector():
    """ """
    with pytest.raises(ValueError):
        E3.weighting_for_sector_coupled_kpi(
            dict_weighting_unknown_sector, RENEWABLE_SHARE
        )


def test_weighting_for_sector_coupled_kpi_one_sector():
    """ """
    E3.weighting_for_sector_coupled_kpi(dict_weighting_one_sector, RENEWABLE_SHARE)
    assert RENEWABLE_SHARE in dict_weighting_one_sector[KPI][KPI_SCALARS_DICT]
    assert (
        dict_weighting_one_sector[KPI][KPI_SCALARS_DICT][RENEWABLE_SHARE] == numbers[1]
    )


def test_weighting_for_sector_coupled_kpi_multiple_sectors():
    """ """
    E3.weighting_for_sector_coupled_kpi(dict_weighting_two_sectors, RENEWABLE_SHARE)
    exp = numbers[1] + numbers[2] * DEFAULT_WEIGHTS_ENERGY_CARRIERS[h2][VALUE]
    assert RENEWABLE_SHARE in dict_weighting_two_sectors[KPI][KPI_SCALARS_DICT]
    assert dict_weighting_two_sectors[KPI][KPI_SCALARS_DICT][RENEWABLE_SHARE] == exp


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
    PROJECT_DATA: {SECTORS: {electricity: electricity}},
}


def test_add_levelized_cost_of_energy_carriers_one_sector():
    E3.add_levelized_cost_of_energy_carriers(dict_values)

    exp = {
        ATTRIBUTED_COSTS + electricity: 1000,
        LCOeleq
        + electricity: 1000 * dict_values[ECONOMIC_DATA][CRF][VALUE] / total_demand,
        LCOeleq: 1000 * dict_values[ECONOMIC_DATA][CRF][VALUE] / total_demand,
    }

    for kpi in [ATTRIBUTED_COSTS, LCOeleq]:
        assert kpi + electricity in dict_values[KPI][KPI_SCALARS_DICT]
        assert (
            dict_values[KPI][KPI_SCALARS_DICT][kpi + electricity]
            == exp[kpi + electricity]
        )

    assert LCOeleq in dict_values[KPI][KPI_SCALARS_DICT]
    assert dict_values[KPI][KPI_SCALARS_DICT][LCOeleq] == exp[LCOeleq]


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
    dict_values[PROJECT_DATA][SECTORS].update({h2: h2})
    E3.add_levelized_cost_of_energy_carriers(dict_values)

    exp = {
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
    exp.update(
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
            == exp[kpi + electricity]
        )

    assert LCOeleq in dict_values[KPI][KPI_SCALARS_DICT]
    assert dict_values[KPI][KPI_SCALARS_DICT][LCOeleq] == exp[LCOeleq]


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


def test_equation_degree_of_autonomy():
    """ """
    total_generation = 30
    total_demand = 100
    degree_of_autonomy = E3.equation_degree_of_autonomy(total_generation, total_demand)
    assert degree_of_autonomy == total_generation / total_demand, (
        f"The degree_of_autonomy ({degree_of_autonomy}) is not calculated correctly. "
        f"It should be equal to {total_generation / total_demand }."
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
