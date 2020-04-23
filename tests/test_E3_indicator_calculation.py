import os
import json
import pandas as pd
import pytest

import src.E3_indicator_calculation as E3
from src.constants import KPI_DICT, KPI_SCALARS_DICT, KPI_UNCOUPLED_DICT, KPI_COST_MATRIX

numbers = [10, 15, 20, 25]

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

with open(os.path.join("tests", "test_data", "test_json_for_E3_res.json")) as json_file:
    dict_renewable_energy_use = json.load(json_file)

flow_small = 50
flow_medium = 100
renewable_share_dso = 0.1

dict_renewable_energy_use["energyProduction"]["DSO_consumption_period_1"]["total_flow"]["value"] = flow_small
dict_renewable_energy_use["energyProduction"]["DSO_consumption_period_2"]["total_flow"]["value"] = flow_small
dict_renewable_energy_use["energyProduction"]["pv_plant_01"]["total_flow"]["value"] = flow_medium
dict_renewable_energy_use["energyProviders"]["DSO"]["renewable_share"]["value"] = renewable_share_dso
exp_res = flow_medium + (flow_small * 2 * renewable_share_dso)
exp_non_res = (flow_small * 2 * (1 - renewable_share_dso))

class TestGeneralEvaluation:
    def test_totalling_scalars_values(self):
        E3.all_totals(dict_scalars)
        return dict_scalars[KPI_DICT][KPI_SCALARS_DICT] == scalars_expected

    def test_total_dispatch_of_each_asset(self):
        assert 0 == 0

    def test_total_demand_of_each_sector(self):
        assert 0 == 0

    def test_total_renewable_and_non_renewable_origin_of_each_sector(self):
        E3.total_renewable_and_non_renewable_energy_origin(dict_renewable_energy_use)
        assert "Total internal renewable generation" in dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]
        assert "Total renewable energy use" in dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]
        assert "Total internal non-renewable generation" in dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]
        assert "Total non-renewable energy use" in dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]
        assert dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]["Total internal renewable generation"]["Electricity"] == flow_medium
        assert dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]["Total internal non-renewable generation"]["Electricity"] == 0
        assert dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]["Total renewable energy use"]["Electricity"] == exp_res
        assert dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]["Total non-renewable energy use"]["Electricity"] == exp_non_res

    def test_intersectoral_energy_flows_unilateral(self):
        assert 0 == 0

    def test_intersectoral_energy_flows_bilateral(self):
        assert 0 == 0


class TestTechnicalParameters:
    #def test_weighting_for_sector_coupled_parameters_unknown_parameters(self):
    #    with pytest.raises(TypeError):
    #        E3.weighting_for_sector_coupled_parameters()

    #def test_weighting_for_sector_coupled_parameters_one_sector(self):
    #    E3.weighting_for_sector_coupled_parameters()
    #    assert 0 == 0

    #def test_weighting_for_sector_coupled_parameters_multiple_sectors(self):
    #    E3.weighting_for_sector_coupled_parameters()
    #    assert 0 == 0

    def test_renewable_share_one_sector_is_0(self):
        assert 0 == 0

    def test_renewable_share_one_sector_below_1(self):
        E3.total_renewable_and_non_renewable_energy_origin(dict_renewable_energy_use)
        E3.renewable_share_sector_specific(dict_renewable_energy_use)
        exp = exp_res / (exp_non_res + exp_res)
        assert dict_renewable_energy_use[KPI_DICT][KPI_UNCOUPLED_DICT]["Renewable share"]["Electricity"] == exp

    def test_renewable_share_one_sector_is_1(self):
        assert 0 == 0

    def test_renewable_share_one_sector_above_1(self):
        assert 0 == 0

    def test_renewable_share_two_sectors_below_1(self):
        assert 0 == 0

    def test_renewable_share_two_sectors_is_1(self):
        assert 0 == 0

    def test_renewable_share_two_sectors_above_1(self):
        assert 0 == 0

    def test_degree_of_autonomy_below_1(self):
        assert 0 == 0

    def test_degree_of_autonomomy_is_1(self):
        assert 0 == 0

    def test_degree_of_autonomy_above_1(self):
        assert 0 == 0

    def test_degree_of_sector_coupling_below_1(self):
        assert 0 == 0

    def test_degree_of_sector_coupling_is_1(self):
        assert 0 == 0

    def test_degree_of_sector_coupling_above_1(self):
        assert 0 == 0

    def test_onsite_energy_fraction_below_1(self):
        assert 0 == 0

    def test_onsite_energy_fraction_is_1(self):
        assert 0 == 0

    def test_onsite_energy_fraction_above_1(self):
        assert 0 == 0

    def test_onsite_energy_matching_below_1(self):
        assert 0 == 0

    def test_onsite_energy_matching_is_1(self):
        assert 0 == 0

    def test_onsite_energy_matching_above_1(self):
        assert 0 == 0
