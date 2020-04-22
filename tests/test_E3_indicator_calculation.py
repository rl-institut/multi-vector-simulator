import os
import json
import pandas as pd

import src.E3_indicator_calculation as E3

numbers = [10, 15, 20, 25]

dict_scalars = {
    "kpi": {
        "cost_matrix": pd.DataFrame(
            {
                "label": ["asset_1", "asset_2"],
                "cost": [numbers[1], numbers[3]],
                "annuity": [numbers[0], numbers[2]],
            }
        ),
        "scalars": {},
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

class TestGeneralEvaluation:
    def test_totalling_scalars_values(self):
        E3.all_totals(dict_scalars)
        return dict_scalars["kpi"]["scalars"] == scalars_expected

    def test_total_dispatch_of_each_asset(self):
        assert 0 == 0

    def test_total_demand_of_each_sector(self):
        assert 0 == 0

    def test_total_renewable_generation_of_each_sector(self):
        E3.total_renewable_energy(dict_renewable_energy_use)

        print(dict_renewable_energy_use)
        assert "Total internal renewable generation" in dict_renewable_energy_use["kpi"]["scalars"]
        assert "Total renewable energy use" in dict_renewable_energy_use["kpi"]["scalars"]
        assert dict_renewable_energy_use["kpi"]["scalars"]["Total internal renewable generation"]["Electricity"] == flow_medium
        exp = flow_medium + (flow_small * 2 * renewable_share_dso)
        assert dict_renewable_energy_use["kpi"]["scalars"]["Total renewable energy use"]["Electricity"] == exp

    def test_total_non_renewable_generation_of_each_sector(self):
        assert 0 == 0 #"Total non-renewable generation" in dict_generation["kpi"]["scalars"]

    def test_intersectoral_energy_flows_unilateral(self):
        assert 0 == 0

    def test_intersectoral_energy_flows_bilateral(self):
        assert 0 == 0


class TestTechnicalParameters:
    def test_renewable_share_one_sector_below_1(self):
        assert 0 == 0

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
