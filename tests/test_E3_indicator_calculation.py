import os
import json
import pandas as pd
import pytest

import src.E3_indicator_calculation as E3
from src.constants import (
    KPI_DICT,
    KPI_SCALARS_DICT,
    KPI_UNCOUPLED_DICT,
    KPI_COST_MATRIX,
)
from src.constants import DEFAULT_WEIGHTS_ENERGY_CARRIERS

numbers = [10, 15, 20, 25]

# for test_totalling_scalars_values
dict_scalars = {
    KPI_DICT: {
        KPI_COST_MATRIX: pd.DataFrame(
            {
                "label": ["asset_1", "asset_2"],
                "cost": [numbers[1], numbers[3]],
                "annuity": [numbers[0], numbers[2]],
            }
        ),
        KPI_SCALARS_DICT: {},
    }
}
scalars_expected = {"cost": numbers[1] + numbers[3], "annuity": numbers[0] + numbers[2]}

# for this test_total_renewable_and_non_renewable_origin_of_each_sector test
from src.B0_data_input_json import load_json

dict_renewable_energy_use = load_json(
    os.path.join("tests", "test_data", "test_json_for_E3.json")
)

flow_small = 50
flow_medium = 100
renewable_share_dso = 0.1
dict_renewable_energy_use["energyProduction"]["DSO_consumption_period_1"]["total_flow"][
    "value"
] = flow_small
dict_renewable_energy_use["energyProduction"]["DSO_consumption_period_2"]["total_flow"][
    "value"
] = flow_small
dict_renewable_energy_use["energyProduction"]["pv_plant_01"]["total_flow"][
    "value"
] = flow_medium
dict_renewable_energy_use["energyProviders"]["DSO"]["renewable_share"][
    "value"
] = renewable_share_dso
exp_res = flow_medium + (flow_small * 2 * renewable_share_dso)
exp_non_res = flow_small * 2 * (1 - renewable_share_dso)

# for weighting_for_sector_coupled_kpi
a_kpi_name = "renewable share"
dict_weighting_unknown_sector = {
    "project_data": {"sectors": {"Heat": "He"}},
    KPI_DICT: {
        KPI_UNCOUPLED_DICT: {a_kpi_name: {"Heat": numbers[0]}},
        KPI_SCALARS_DICT: {},
    },
}

dict_weighting_one_sector = {
    "project_data": {"sectors": {"Electricity": "E"}},
    KPI_DICT: {
        KPI_UNCOUPLED_DICT: {a_kpi_name: {"Electricity": numbers[1]}},
        KPI_SCALARS_DICT: {},
    },
}

dict_weighting_two_sectors = {
    "project_data": {"sectors": {"Electricity": "E", "H2": "H"}},
    KPI_DICT: {
        KPI_UNCOUPLED_DICT: {a_kpi_name: {"Electricity": numbers[1], "H2": numbers[2]}},
        KPI_SCALARS_DICT: {},
    },
}


class TestGeneralEvaluation:
    """ """

    def test_totalling_scalars_values(self):
        """ """
        E3.all_totals(dict_scalars)
        return dict_scalars[KPI_DICT][KPI_SCALARS_DICT] == scalars_expected

    def test_total_dispatch_of_each_asset(self):
        """ """
        assert 0 == 0

    def test_total_demand_of_each_sector(self):
        """ """
        assert 0 == 0

    def test_total_renewable_and_non_renewable_origin_of_each_sector(self):
        """ """
        E3.total_renewable_and_non_renewable_energy_origin(dict_renewable_energy_use)
        assert (
            "Total internal renewable generation"
            in dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]
        )
        assert (
            "Total renewable energy use"
            in dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]
        )
        assert (
            "Total internal non-renewable generation"
            in dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]
        )
        assert (
            "Total non-renewable energy use"
            in dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]
        )
        assert (
            "Total internal renewable generation"
            in dict_renewable_energy_use[KPI_DICT][KPI_SCALARS_DICT]
        )
        assert (
            "Total renewable energy use"
            in dict_renewable_energy_use[KPI_DICT][KPI_SCALARS_DICT]
        )
        assert (
            "Total internal non-renewable generation"
            in dict_renewable_energy_use[KPI_DICT][KPI_SCALARS_DICT]
        )
        assert (
            "Total non-renewable energy use"
            in dict_renewable_energy_use[KPI_DICT][KPI_SCALARS_DICT]
        )
        assert (
            dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT][
                "Total internal renewable generation"
            ]["Electricity"]
            == flow_medium
        )
        assert (
            dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT][
                "Total internal non-renewable generation"
            ]["Electricity"]
            == 0
        )
        assert (
            dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT][
                "Total renewable energy use"
            ]["Electricity"]
            == exp_res
        )
        assert (
            dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT][
                "Total non-renewable energy use"
            ]["Electricity"]
            == exp_non_res
        )

    def test_intersectoral_energy_flows_unilateral(self):
        """ """
        assert 0 == 0

    def test_intersectoral_energy_flows_bilateral(self):
        """ """
        assert 0 == 0


class TestTechnicalParameters:
    """ """

    def test_weighting_for_sector_coupled_kpi_unknown_sector(self):
        """ """
        with pytest.raises(ValueError):
            E3.weighting_for_sector_coupled_kpi(
                dict_weighting_unknown_sector, a_kpi_name
            )

    def test_weighting_for_sector_coupled_kpi_one_sector(self):
        """ """
        E3.weighting_for_sector_coupled_kpi(dict_weighting_one_sector, a_kpi_name)
        assert a_kpi_name in dict_weighting_one_sector[KPI_DICT][KPI_SCALARS_DICT]
        assert (
            dict_weighting_one_sector[KPI_DICT][KPI_SCALARS_DICT][a_kpi_name]
            == numbers[1]
        )

    def test_weighting_for_sector_coupled_kpi_multiple_sectors(self):
        """ """
        E3.weighting_for_sector_coupled_kpi(dict_weighting_two_sectors, a_kpi_name)
        exp = numbers[1] + numbers[2] * DEFAULT_WEIGHTS_ENERGY_CARRIERS["H2"]["value"]
        assert a_kpi_name in dict_weighting_two_sectors[KPI_DICT][KPI_SCALARS_DICT]
        assert dict_weighting_two_sectors[KPI_DICT][KPI_SCALARS_DICT][a_kpi_name] == exp

    def test_renewable_share_one_sector(self):
        """ """
        E3.total_renewable_and_non_renewable_energy_origin(dict_renewable_energy_use)
        E3.renewable_share(dict_renewable_energy_use)
        exp = exp_res / (exp_non_res + exp_res)
        assert (
            "Renewable share" in dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]
        )
        assert (
            "Electricity"
            in dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT][
                "Renewable share"
            ]
        )
        assert (
            dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]["Renewable share"][
                "Electricity"
            ]
            == exp
        )
        assert (
            dict_renewable_energy_use[KPI_DICT][KPI_SCALARS_DICT]["Renewable share"]
            == exp
        )

    def test_renewable_share_equation_is_1(self):
        """ """
        tot_res = 100
        tot_non_res = 0
        renewable_share = E3.equation_renewable_share(tot_res, tot_non_res)
        assert renewable_share == tot_res / (tot_res + tot_non_res)

    def test_renewable_share_equation_is_0(self):
        """ """
        tot_res = 0
        tot_non_res = 100
        renewable_share = E3.equation_renewable_share(tot_res, tot_non_res)
        assert renewable_share == tot_res / (tot_res + tot_non_res)

    def test_renewable_share_equation_below_1(self):
        """ """
        tot_res = 20
        tot_non_res = 100
        renewable_share = E3.equation_renewable_share(tot_res, tot_non_res)
        assert renewable_share == tot_res / (tot_res + tot_non_res)

    def test_degree_of_autonomy_below_1(self):
        """ """
        assert 0 == 0

    def test_degree_of_autonomomy_is_1(self):
        """ """
        assert 0 == 0

    def test_degree_of_autonomy_above_1(self):
        """ """
        assert 0 == 0

    def test_degree_of_sector_coupling_below_1(self):
        """ """
        assert 0 == 0

    def test_degree_of_sector_coupling_is_1(self):
        """ """
        assert 0 == 0

    def test_degree_of_sector_coupling_above_1(self):
        """ """
        assert 0 == 0

    def test_onsite_energy_fraction_below_1(self):
        """ """
        assert 0 == 0

    def test_onsite_energy_fraction_is_1(self):
        """ """
        assert 0 == 0

    def test_onsite_energy_fraction_above_1(self):
        """ """
        assert 0 == 0

    def test_onsite_energy_matching_below_1(self):
        """ """
        assert 0 == 0

    def test_onsite_energy_matching_is_1(self):
        """ """
        assert 0 == 0

    def test_onsite_energy_matching_above_1(self):
        """ """
        assert 0 == 0
