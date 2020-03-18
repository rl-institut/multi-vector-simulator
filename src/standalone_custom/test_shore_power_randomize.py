import pandas as pd
import pytest

from src.standalone_custom.shore_power_randomize import randomize_shore_power

def test_randomize_shore_power():
    shore_power_df = {
        "1000": {"Number": 1, "Duration": 2, "Power": 500},
        "400": {"Number": 1, "Duration": 4, "Power": 100}
    }
    shore_power_df = pd.DataFrame(shore_power_df)

    time = pd.date_range(start="1.1.2017 00:00", freq="h", periods=8760)

    sum_exp = 1400
    profile = randomize_shore_power(times=time, shore_power=shore_power_df)
    assert profile.sum() == sum_exp
