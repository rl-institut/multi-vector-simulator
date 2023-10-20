#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""

import os
import numpy as np
import pandas as pd
import logging

from multi_vector_simulator.utils.constants_json_strings import *

from multi_vector_simulator.utils import analysis

SENSITIVITY_PARAMETERS = "parameters"
SENSITIVITY_OUTPUTS = "outputs"

FILE_SENSITIVITY_EXPERIMENT_PARAMETER_GROUPS = "senstivity_experiment_parameters_groups.csv"
FILE_SENSITIVITY_EXPERIMENT_PARAMETER_SETTINGS = "senstivity_experiment_parameters_settings.csv"

ASSET_GROUP = "asset group"
ASSET ="asset"
PARAMETER = "parameter"
MIN = "min"
MAX = "max"
STEP = "step"

"""PATH_INPUT_FOLDER = """

def save_result(res, filename, dict_sensitivity_experiment_paths):
    """
    
    Parameters
    ----------
    res: dict,
        MVS simulation results.
    filename: str,
        file name to save the concise results
    dict_sensitivity_experiment_paths: dict,
        dict where we match the path of the changing parameters to be picked within the MVS simulation 
        and to be saved inside the concise simulation 

    Returns
    -------

    """
    head=[]
    bigdata=[]
    for i,p in enumerate(res[SENSITIVITY_PARAMETERS]):
        data=[]
        data.append(p)
        for k,v in dict_sensitivity_experiment_paths.items():
            for vn in v:
                data.append(res[SENSITIVITY_OUTPUTS][i][(k+ (vn,))])
                if i == 0:
                    if k == (KPI, KPI_COST_MATRIX, LCOE_ASSET):
                        head.append("LCOE_" + vn) #for the df matrix into dict formatting, usefull to add precisions for columns heads when saved into csv
                    elif k == (KPI, KPI_SCALAR_MATRIX, OPTIMIZED_ADD_CAP):
                        head.append("AddedCap_" + vn)
                    elif k == (KPI, KPI_SCALAR_MATRIX, PEAK_FLOW):
                        head.append("Peak_" + vn)
                    else:
                        head.append(vn)
        bigdata.append(data)
    df=pd.DataFrame(bigdata,columns=["DOA"]+ head) #I put title of first column manually here

    df.to_csv(filename, index=False) #save into csv
    logging.info(f"Saved sensitivity analysis results to file {filename}.")

def read_senstivity_parameters_from_file():
    dict_senstivity_parameter_groups =  pd.read_csv(FILE_SENSITIVITY_EXPERIMENT_PARAMETER_GROUPS)
    logging.info(f"There are {len(dict_senstivity_parameter_groups.index)} parameters in the asset groups that are subject to the sensitivity analysis.")
    logging.debug(dict_senstivity_parameter_groups)

    dict_senstivity_parameter_settings = pd.read_csv(FILE_SENSITIVITY_EXPERIMENT_PARAMETER_SETTINGS)
    logging.info(f"There are {len(dict_senstivity_parameter_settings.index)} parameters in settings that are subject to the sensitivity analysis.")
    logging.debug(dict_senstivity_parameter_settings)
    return dict_senstivity_parameter_groups, dict_senstivity_parameter_settings

def define_output_keys(dict_senstivity_parameter_groups):
    output_keys = [LCOeleq, RENEWABLE_FACTOR, DEGREE_OF_AUTONOMY, ONSITE_ENERGY_FRACTION, ONSITE_ENERGY_FRACTION]
    for item in dict_senstivity_parameter_groups:
        output_keys.append()

def run_sensitivity_tests_on_one_parameter():
    pass
#dict_senstivity_parameter_groups, dict_senstivity_parameter_settings = read_senstivity_parameters_from_file()

"""
for item in dict_senstivity_parameter_groups.index:
    touple_to_parameter = (ASSET_GROUP, ASSET, PARAMETER, VALUE)
    logging.info(f"Sensitivity parameter {item} of the asset groups: "
                 f"\n Asset group: {dict_senstivity_parameter_groups[item][ASSET_GROUP]}"
                 f"\n Asset: {dict_senstivity_parameter_groups[item][ASSET]}"
                 f"\n Parameter: {dict_senstivity_parameter_groups[item][PARAMETER]}"
                 f"\n Range: min {dict_senstivity_parameter_groups[MIN]}, max {dict_senstivity_parameter_groups[MAX]}, step {dict_senstivity_parameter_groups[STEP]}")
    logging.debug(f"The expected type of the parameter is a {VALUE}. The sensitivity analysis does not work for other types.")

"""
r"""Run mvs simulations by varying one of the input parameters to access output's sensitivity

    Parameters
    ----------
    param_values: list of values (type can vary)
    json_input: path or dict
        input parameters for the multi-vector simulation
    json_path_to_param_value: tuple or str
        succession of keys which lead the value of the parameter to vary in the json_input dict
        potentially nested structure. The order of keys is to be read from left to right. In the
        case of str, each key should be separated by a `.` or a `,`.
    json_path_to_output_value: tuple of tuple or str, optional
        collection of succession of keys which lead the value of an output parameter of interest in
        the json dict of the simulation's output. The order of keys is to be read from left to
        right. In the case of str, each key should be separated by a `.` or a `,`.

    Returns
    -------
    The simulation output json matched to the list of variied parameter values
    """


op = [DEGREE_OF_AUTONOMY, ONSITE_ENERGY_FRACTION, RENEWABLE_FACTOR, ONSITE_ENERGY_MATCHING, 'Total_feedin_electricity_equivalent',
      "Total_consumption_from_energy_provider_electricity_equivalent", 'Levelized costs of electricity equivalent'] #I can put the output parameters that I want to look at here
od = ["PV", "Heat_pump", "Battery storage capacity", "Electric_generator", "Heat_generator"]
ot = ["Transmission_system_operator_consumption_source", "Transmission_system_operator_feedin_sink_sink"]
og = ["PV", "Biogas", "Battery storage capacity", "Electric_generator", "Heat_generator"]
parameter_output = {(KPI, KPI_SCALARS_DICT):op,
                    (KPI, KPI_COST_MATRIX, LCOE_ASSET):og,
                    (KPI, KPI_SCALAR_MATRIX, OPTIMIZED_ADD_CAP):od,
                    (KPI, KPI_SCALAR_MATRIX, PEAK_FLOW):ot} #path in jason :parmaters dict

json_path_to_output_value = []
for k,v in parameter_output.items():
    for vn in v:
        json_path_to_output_value.append(k+ (vn,))
json_files = [fn for fn in os.listdir(".") if fn.endswith(".json")] #need an existing simulation json file to work e.g.: json_input_processed-01

for j, file in enumerate(json_files):
    print(json_path_to_output_value)
    res = analysis.single_param_variation_analysis(
        [d for d in np.arange(0, 1, 0.5)], #1st value, last value + increment, increment
        file,
        (CONSTRAINTS, MINIMAL_RENEWABLE_FACTOR, VALUE), #What parameter I want to iterate through
        json_path_to_output_value=json_path_to_output_value,
        #output_file = f"outputs\json_with_results_{j+1}"

    )
    save_result(res, f"parameter_output_{j+1}.csv", parameter_output) #can specify a folder path here but it HAS TO EXIST already


from multi_vector_simulator.utils.constants_json_strings import *
from multi_vector_simulator.B0_data_input_json import load_json


dict_values = load_json(os.path.abspath("json_input_processed.json"))
try:
    df = dict_values[ENERGY_BUSSES, "Transmission grid", ENERGY_VECTOR]
    df.set_index(LABEL).to_dict()[ANNUAL_TOTAL_FLOW]
except:
    logging.info(dict_values)

op = [DEGREE_OF_AUTONOMY,RENEWABLE_FACTOR, ONSITE_ENERGY_FRACTION, ONSITE_ENERGY_MATCHING, 'Total_feedin_electricity_equivalent',
      "Total_consumption_from_energy_provider_electricity_equivalent", 'Levelized costs of electricity equivalent'] #I can put the output parameters that I want to look at here
od = ["PV",  "Wind_turbine"]
parameter_output = {(KPI, KPI_SCALARS_DICT):op,(KPI, KPI_COST_MATRIX, LCOE_ASSET):od} #path in jason

json_path_to_output_value = []
for k,v in parameter_output.items():
    for vn in v:
        json_path_to_output_value.append(k+ (vn,))
        print(json_path_to_output_value)


# In[ ]:


import os
[fn for fn in os.listdir(".") if fn.endswith(".json")]

parameter_output.keys()


res.keys()


print(len(res[SENSITIVITY_OUTPUTS]))
type(res[SENSITIVITY_OUTPUTS])


res[SENSITIVITY_PARAMETERS]


res[SENSITIVITY_OUTPUTS]


#old method for saving in excel (only one param output dict)
import pandas as pd
bigdata=[]

for i,p in enumerate(res[SENSITIVITY_PARAMETERS]):
    data=[]
    data.append(p)
    for o in op:
        print(o)
        data.append(res[SENSITIVITY_OUTPUTS][i][(KPI, KPI_SCALARS_DICT, o)])
    bigdata.append(data)
df=pd.DataFrame(bigdata,columns=["variable_parameter"]+op)
df.to_csv("min_DOA.csv",index=False) #save into csv



##Pour avoir nom de fichiers en output
banana=["name1", "name2"]
for of, file in zip(banana, json_files): #with zip it uses smallest of two list : Banana needs to be same length as my matrix (in my example)
    res = analysis.single_param_variation_analysis(
        [d for d in np.arange(0, 2, 1)], #1st value, last value + increment, increment
        file,
        (CONSTRAINTS, MINIMAL_RENEWABLE_FACTOR, VALUE), #What parameter I want to iterate
        json_path_to_output_value=[(KPI, KPI_SCALARS_DICT, o) for o in op], #Check out 'list comprehension' for this special 'for' loop
        #output_file = f"outputs\output_{of}"

    )


