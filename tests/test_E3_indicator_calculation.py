import pandas as pd

import src.E3_indicator_calculation as E3

dict_scalars = {
    "kpi": {
        "cost_matrix": pd.DataFrame(
            {"label": ["asset_1", "asset_2"], "cost": [15, 25], "annuity": [10, 20]}
        ),
        "scalars": {},
    }
}

print(dict_scalars)

scalars_expected = {"cost": 40, "annuity": 30}


class TestEconomicIndicators:
    def test_totalling_scalars_values(self):
        E3.all_totals(dict_scalars)
        return dict_scalars["kpi"]["scalars"] == scalars_expected
