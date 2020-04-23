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


class TestEconomicIndicators:
    def test_totalling_scalars_values(self):
        E3.all_totals(dict_scalars)
        return dict_scalars["kpi"]["scalars"] == scalars_expected
