"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""

import os
from multi_vector_simulator.utils import analysis

from _constants import TEST_REPO_PATH, REPO_PATH

"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""

import os
import numpy as np
import pandas as pd
from multi_vector_simulator.utils import analysis


def save_result(res, fn, mp):
    """

    Parameters
    ----------
    res: dict,
        MVS simulation results.
    fn: str,
        file_name to save the concise results
    mp: dict,
        dict where we match the path of the changing parameters to be picked within the MVS simulation
        and to be saved inside the concise simulation

    Returns
    -------

    """
    head = []
    bigdata = []
    for i, p in enumerate(res["parameters"]):
        data = []
        data.append(p)
        for k, v in parameter_output.items():
            for vn in v:
                data.append(res["outputs"][i][(k + (vn,))])
            head = head + v
        bigdata.append(data)
    df = pd.DataFrame(bigdata, columns=["MaxCap_WT"] + head)  # I put title of first column manually here
    df.to_csv(fn, index=False)  # save into csv


op = ["Degree of autonomy", "Renewable factor", "Onsite energy fraction", "Onsite energy matching",
      'Total_feedin_electricity_equivalent',
      "Total_consumption_from_energy_provider_electricity_equivalent",
      'Levelized costs of electricity equivalent']  # I can put the output parameters that I want to look at here
od = ["b", "dfvdf"]
parameter_output = {("kpi", "scalars"): op, ("trajet_2",): od}  # path in jason

json_path_to_output_value = []

for k, v in parameter_output.items():
    for vn in v:
        json_path_to_output_value.append(k + (vn,))

json_files = [fn for fn in os.listdir(".") if fn.endswith(".json")]  # need an existing simulation json file to work
for j, file in enumerate(json_files):
    res = analysis.single_param_variation_analysis(
        [d for d in np.arange(0, 20500, 500)],  # 1st value, last value + increment, increment
        file,
        ("energyProduction", "Wind_turbine", "maximumCap", "value"),  # What parameter I want to iterate
        json_path_to_output_value=json_path_to_output_value,
        # Check out 'list comprehension' for this special 'for' loop
        output_file=f"outputs\json_with_results_{j + 1}"

    )
    save_result(res, f"outputs\parameter_output_{j + 1}.csv",
                parameter_output)  # can specify a sub folder here, HAS TO EXIST already

if __name__ == "__main__":
    print(
        analysis.single_param_variation_analysis(
            [1, 2, 3],
            os.path.join(REPO_PATH, "MVS_outputs", "json_input_processed.json"),
            ("simulation_settings", "evaluated_period", "value"),
            json_path_to_output_value=(("kpi", "KPI individual sectors"),),
        )
    )
