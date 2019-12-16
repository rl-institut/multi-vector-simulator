import pandas as pd
import os
import json
from pathlib import Path

"""
This module reads csv files from "mvs_eland/inputs/elements/csv", converts each
into a json file and stores it in "mvs_eland/inputs/elements/json". Each csv 
file is checked for the right parameters.

In order to add a new component, the according parameters and the json 
structure needs to be added by hand into this script. 

todo (if needed) to make the code more generic:
- a function that converts csv to json and takes the required parameters as an 
    argument 
- a function that joins all single json files and builds the structure 
    (subkeys) from arguments
"""




def infer_resources():

    """
    Method looks at all csv-files in 'mvs_eland/inputs/elements/csv",
    converts them into json files and joins them together into the file
    "mvs_eland/inputs/working_example2.json". When reading the csv files it is
    checked, weather all required parameters for each component are given.
    Missing parameters will return a message.

    Parameters
    -------------
    None

    Returns
    --------------
    None
        the json file "working_example2.json" is saved

    """
    input_directory= os.path.join(Path(os.path.dirname(__file__)).parent,
                                  "inputs/elements/")

    convert_all_csv_to_json(input_directory)

    join_json_files(input_directory)


def convert_all_csv_to_json(input_directory):

    """
    reads all csv files in "mvs_eland/inputs/elements/csv", checks if all
    required parameters for each csv file are available and saves them as
    json into "mvs_eland/inputs/elements/json"

    :param input_directory:
    :return:
    """
    for f in os.listdir(os.path.join(input_directory, "csv/")):

        if f == 'demand.csv':
            parameters=['dsm', 'file_name', 'label', 'type_asset',
                        'type_oemof']
            create_json_from_csv(input_directory,
                                 filename="demand",
                                 parameters=parameters)

        elif f == 'transformer.csv':

            parameters = ['age_installed', 'capex_fix', 'capex_var',
                          'efficiency','inflow_direction', 'installedCap',
                          'label', 'lifetime', 'opex_fix','opex_var',
                          'optimizeCap', 'outflow_direction', 'type_oemof']
            create_json_from_csv(input_directory,
                                 filename="transformer",
                                 parameters=parameters)

        elif f == 'storage01_1.csv':

            parameters = ['inflow_direction', 'label', 'optimizeCap',
                       'outflow_direction',
                       'type_oemof']
            create_json_from_csv(input_directory,
                                 filename="storage01_1",
                                 parameters=parameters)

            if os.path.exists(
                    os.path.join(input_directory, 'csv/', 'storage01_2.csv')):
                parameters = ['age_installed', 'capex_fix', 'capex_var',
                              'crate','efficiency','installedCap', 'label',
                              'lifetime','opex_fix', 'opex_var', 'soc_initial',
                              'soc_max', 'soc_min', 'unit']
                create_json_from_csv(input_directory,
                                     filename="storage01_2",
                                     parameters=parameters)
            else:
                print("File storage01_02.csv is missing")
        elif f == 'storage01_2.csv':
            pass
        elif f == 'pv_plant_01.csv':

            parameters = ['age_installed', 'capex_fix', 'capex_var',
                          'file_name', 'installedCap', 'label',
                          'lifetime', 'opex_fix', 'opex_var',
                          'optimizeCap', 'outflow_direction',
                          'type_oemof', 'unit']
            create_json_from_csv(input_directory,
                                 filename="pv_plant_01",
                                 parameters=parameters)
        elif f == "DSO.csv":
            parameters = ['energy_price', 'feedin_tariff', 'inflow_direction',
                          'label','optimizeCap', 'outflow_direction',
                          'peak_demand_pricing','peak_demand_pricing_period',
                          'type_oemof']
            create_json_from_csv(input_directory,
                                 filename="DSO",
                                 parameters=parameters)
        elif f == "project.csv":
            parameters = ['capex_fix', 'capex_var', 'label', 'lifetime',
                          'opex_fix', 'opex_var']
            create_json_from_csv(input_directory,
                                 filename="project",
                                 parameters=parameters)
        elif f == "fixcost_electricity.csv":
            parameters = ['age_installed', 'capex_fix', 'capex_var', 'label',
                          'lifetime','opex_fix', 'opex_var']
            create_json_from_csv(input_directory,
                                 filename="fixcost_electricity",
                                 parameters=parameters)
        elif f == "simulation_settings.csv":
            parameters = ['display_output', 'evaluated_period',
                          'input_file_name', 'label','oemof_file_name',
                          'output_lp_file', 'overwrite', 'path_input_file',
                            'path_input_folder', 'path_output_folder',
                          'path_output_folder_inputs',
                          'restore_from_oemof_file', 'start_date',
                          'store_oemof_results', 'timestep']
            create_json_from_csv(input_directory,
                                 filename="simulation_settings",
                                 parameters=parameters)
        elif f == "project_data.csv":
            parameters = ['country', 'label', 'latitude', 'longitude',
                          'project_id','project_name', 'scenario_id',
                          'scenario_name', 'sectors']
            create_json_from_csv(input_directory,
                                 filename="project_data",
                                 parameters=parameters)
        elif f == "economic_data.csv":
            parameters = ['currency', 'discount_factor', 'label',
                          'project_duration', 'tax']
            create_json_from_csv(input_directory,
                                 filename="economic_data",
                                 parameters=parameters)
        else:
            print('The file', f, 'is not in the input list.')


def create_json_from_csv(input_directory, filename, parameters):

    """
    :param input_directory: directory dame in which the csv files are in
    :param filename: name of the file that should be transformed, without
            ending
    :param parameters: List of parameters names that are required
    :return: None
        saves a json file with >filename<.json
    """
    df = pd.read_csv(os.path.join(input_directory, "csv/",
                                  "%s.csv" % filename),
                     sep=",", header=0, index_col=0)

    extra = list(set(parameters) ^ set(df.index))
    if len(extra) > 0:
        for i in extra:
            if i in parameters:
                print('The %s' %filename, ' parameter', i, 'is missing.')
            else:
                print('The %s' %filename, 'parameter', i, 'is does not exist.')

    myfile = open(os.path.join(input_directory, "json/",
                                  "%s.json" % filename),"w")
    transformer_data = json.dumps(df.to_dict(), indent=4)
    myfile.write(transformer_data)
    myfile.close()

def join_json_files(input_directory):

    """
    reads all json files in "mvs_eland/inputs/elements/json/" and brings them
    into the right form for the mvs working example input file

    :param input_directory: name of the input directory that contains the
            folders "csv/" and "json/"
    :return: None
    """
    result = {}
    json_input_directory = os.path.join(input_directory, "json/")
    with open(os.path.join(input_directory, "working_example2.json"),
              "w") as outfile:
        for f in os.listdir(json_input_directory):
            with open(os.path.join(json_input_directory,
                                   f), 'rb') as infile:
                if f == 'transformer.json':
                    json_file = {}
                    json_file["energyConversion"] = json.load(infile)
                    result.update(json_file)
                elif f == "demand.json":
                    json_file1 = {}
                    json_file2 = {}
                    json_file1["Electricity (LES)"] = json.load(infile)
                    json_file2["energyConsumption"] = json_file1
                    result.update(json_file2)
                elif f == "storage01_1.json":
                    json_file1 = {}
                    json_file_storage1 = {}
                    json_file1["Electricity (LES)"] = json.load(infile)
                    json_file_storage1["energyStorage"] = json_file1

                    if os.path.exists(
                            os.path.join(input_directory, "json/",
                                         'storage01_2.json')):
                        f = 'storage01_2.json'
                        with open(os.path.join(json_input_directory,
                                               f), 'rb') as infile:
                            json_file_storage1["energyStorage"][
                                "Electricity (LES)"]["storage_01"].update(
                                json.load(infile))
                    else:
                        print("The storage file storage01_2.json is missing")
                    result.update(json_file_storage1)
                elif f == "storage01_2.json":
                    pass
                elif f == "pv_plant_01.json":
                    json_file1 = {}
                    json_file2 = {}
                    json_file1["Electricity (LES)"] = json.load(infile)
                    json_file2["energyProduction"] = json_file1
                    result.update(json_file2)
                elif f == "DSO.json":
                    json_file1 = {}
                    json_file2 = {}
                    json_file1["Electricity (LES)"] = json.load(infile)
                    json_file2["energyProviders"] = json_file1
                    result.update(json_file2)
                elif f == "project.json":
                    json_file1 = {}
                    json_file1["project"] = json.load(infile)
                    result.update(json_file1)
                elif f == "fixcost_electricity.json":
                    json_file1 = {}
                    json_file2 = {}
                    json_file1["electricity"] = json.load(infile)
                    json_file2["fixCost"] = json_file1
                    result.update(json_file2)
                elif f == "simulation_settings.json":
                    json_file1 = {}
                    json_file1 = json.load(infile)
                    result.update(json_file1)
                elif f == "project_data.json":
                    json_file1 = {}
                    json_file1 = json.load(infile)
                    result.update(json_file1)
                elif f == "economic_data.json":
                    json_file1 = {}
                    json_file1 = json.load(infile)
                    result.update(json_file1)
                else:
                    print('The file', f, 'is not in the input list.')
        json.dump(result, outfile, indent=2)


if __name__ == '__main__':
    infer_resources()
