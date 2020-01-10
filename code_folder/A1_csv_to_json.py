import pandas as pd
import os
import json
from pathlib import Path


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
    output_filename = "working_example3.json"

    create_input_json(input_directory, output_filename)



def create_input_json(input_directory, output_filename, pass_back=False):

    """
    reads all csv files in "mvs_eland/inputs/elements/csv", checks if all
    required parameters for each csv file are available and saves them into
    one json file

    :param input_directory: str
        name of the input directory where the csv's can be found
    :param output_filename: str
        name of the output file with ending
    :param pass_back: binary
        if pass_back=True: the final json dict is returned. Otherwise it is only
        saved

    :return: None
        saves
    """
    input_json = {}
    for f in os.listdir(os.path.join(input_directory, "csv/")):

        if f == 'energyConsumption.csv':
            parameters=['dsm', 'file_name', 'label', 'type_asset',
                        'type_oemof']
            single_dict=create_json_from_csv(input_directory,
                                 filename="energyConsumption",
                                 parameters=parameters)
            input_json.update(single_dict)
        elif f == 'energyConversion.csv':

            parameters = ['age_installed', 'capex_fix', 'capex_var',
                          'efficiency','inflow_direction', 'installedCap',
                          'label', 'lifetime', 'opex_fix','opex_var',
                          'optimizeCap', 'outflow_direction', 'type_oemof']
            single_dict=create_json_from_csv(input_directory,
                                 filename="energyConversion",
                                 parameters=parameters)
            input_json.update(single_dict)

        elif f == 'energyStorage.csv':
            parameters = ['inflow_direction', 'label', 'optimizeCap',
                       'outflow_direction',
                       'type_oemof', 'storage_filename']
            single_dict=create_json_from_csv(input_directory,
                                 filename="energyStorage",
                                 parameters=parameters)
            input_json.update(single_dict)
        elif f == 'energyProduction.csv':

            parameters = ['age_installed', 'capex_fix', 'capex_var',
                          'file_name', 'installedCap', 'label',
                          'lifetime', 'opex_fix', 'opex_var',
                          'optimizeCap', 'outflow_direction',
                          'type_oemof', 'unit']
            single_dict=create_json_from_csv(input_directory,
                                 filename="energyProduction",
                                 parameters=parameters)
            input_json.update(single_dict)
        elif f == "energyProviders.csv":
            parameters = ['energy_price', 'feedin_tariff', 'inflow_direction',
                          'label','optimizeCap', 'outflow_direction',
                          'peak_demand_pricing','peak_demand_pricing_period',
                          'type_oemof']
            single_dict=create_json_from_csv(input_directory,
                                 filename="energyProviders",
                                 parameters=parameters)
            input_json.update(single_dict)
        elif f == "project.csv":
            parameters = ['capex_fix', 'capex_var', 'label', 'lifetime',
                          'opex_fix', 'opex_var']
            single_dict=create_json_from_csv(input_directory,
                                 filename="project",
                                 parameters=parameters)
            input_json.update(single_dict)
        elif f == "fixcost.csv":
            parameters = ['age_installed', 'capex_fix', 'capex_var', 'label',
                          'lifetime','opex_fix', 'opex_var']
            single_dict=create_json_from_csv(input_directory,
                                 filename="fixcost",
                                 parameters=parameters)
            input_json.update(single_dict)
        elif f == "simulation_settings.csv":
            parameters = ['display_output', 'evaluated_period',
                          'input_file_name', 'label','oemof_file_name',
                          'output_lp_file', 'overwrite', 'path_input_file',
                            'path_input_folder', 'path_output_folder',
                          'path_output_folder_inputs',
                          'restore_from_oemof_file', 'start_date',
                          'store_oemof_results', 'timestep']
            single_dict=create_json_from_csv(input_directory,
                                 filename="simulation_settings",
                                 parameters=parameters)
            input_json.update(single_dict)
        elif f == "project_data.csv":
            parameters = ['country', 'label', 'latitude', 'longitude',
                          'project_id','project_name', 'scenario_id',
                          'scenario_name', 'sectors']
            single_dict=create_json_from_csv(input_directory,
                                 filename="project_data",
                                 parameters=parameters)
            input_json.update(single_dict)
        elif f == "economic_data.csv":
            parameters = ['currency', 'discount_factor', 'label',
                          'project_duration', 'tax']
            single_dict=create_json_from_csv(input_directory,
                                 filename="economic_data",
                                 parameters=parameters)
            input_json.update(single_dict)
        elif "storage_" in f:
            pass
        else:
            print('The file', f, 'is not in the input list.')

    with open(os.path.join(input_directory, output_filename),
              "w") as outfile:
        json.dump(input_json, outfile, skipkeys=True, sort_keys=True, indent=4)


def create_json_from_csv(input_directory, filename, parameters):

    """
    One csv file is loaded and it's parameters are checked. The csv file is
    then converted to a dictionary; the name of the csv file is used as the
    main key of the dictionary. Exceptions are made for the files
    ['economic_data', 'project', 'project_data', 'simulation_settings'], here
    no main key is added. Another exception is made for the file
    "energyStorage". When this file is processed, the according "storage_"
    files (names of the 'storage_'-columns in "energyStorage" are called and
    added to the energyStorage Dictionary.


    :param input_directory: str
        directory name in which the csv files are stored in
    :param filename: str
        name of the file that is transformed into a json, without ending
    :param parameters: list
        List of parameters names that are required
    :return: dict
        the converted dictionary
    """
    df = pd.read_csv(os.path.join(input_directory, "csv/",
                                  "%s.csv" % filename),
                     sep=",", header=0, index_col=0)

    #check parameters
    extra = list(set(parameters) ^ set(df.index))
    if len(extra) > 0:
        for i in extra:
            if i in parameters:
                print('The %s' %filename, ' parameter', i, 'is missing.')
            else:
                print('The %s' %filename, 'parameter', i, 'is does not exist.')

    # convert csv to json
    single_dict2 = {}
    single_dict = {}
    for column in df:
        if column != "unit":
            column_dict={}
            for i, row in df.iterrows():
                if row["unit"]=="str":
                    column_dict.update({i: row[column]})
                else:
                    column_dict.update({i: {"value": row[column],
                                       "unit": row["unit"]}})
            single_dict.update({column : column_dict})
            # add exception for energyStorage
            if filename == 'energyStorage':
                storage_dict=add_storage(column, input_directory)
                single_dict[column].update(storage_dict)
    # add exception for single dicts
    if filename in ['economic_data', 'project', 'project_data',
                    'simulation_settings']:
        return single_dict
    elif "storage_" in filename:
        return single_dict

    else:
        single_dict2.update({filename : single_dict})
        return single_dict2


def add_storage(storage_filename, input_directory):
    if os.path.exists(
            os.path.join(input_directory, 'csv/',
                         "%s.csv" % storage_filename)):  # todo: hier verallgemeinern
        parameters = ['age_installed', 'capex_fix', 'capex_var',
                      'crate', 'efficiency', 'installedCap', 'label',
                      'lifetime', 'opex_fix', 'opex_var', 'soc_initial',
                      'soc_max', 'soc_min', 'unit']
        single_dict = create_json_from_csv(input_directory,
                                            filename=storage_filename,
                                            parameters=parameters)
        return single_dict
    else:
        print("File %s.csv" % storage_filename, "is missing")

if __name__ == '__main__':
    infer_resources()
