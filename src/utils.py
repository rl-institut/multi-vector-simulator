import os
import json
import pandas as pd
from src.constants import (
    CSV_ELEMENTS,
    OUTPUT_FOLDER,
    JSON_EXT,
    CSV_EXT,
    REQUIRED_MVS_PARAMETERS,
    JSON_FNAME,
    MISSING_PARAMETERS_KEY,
    EXTRA_PARAMETERS_KEY,
)


def find_input_folders(
    path, specific_folder_name=CSV_ELEMENTS, ignore_folders=(OUTPUT_FOLDER,)
):
    """Recursively look in the folder structure until is sees a specific folder

    Parameters
    ----------
    path: str
        the starting point of the search
    specific_folder_name: str
        the name of the special folder which should be present within a folder to add this folder
        name to the list of matching folders
    ignore_folders: tuple of str
        a tuple of folder names which should not be investigated by the function, nor added to
        the list of matching folders

    Returns
    -------
    A list of paths to folders containing a specific folder
    """

    folderlist = [
        fn.name
        for fn in os.scandir(path)
        if fn.is_dir() and fn.name not in ignore_folders
    ]
    if CSV_ELEMENTS in folderlist:
        return [path]
    else:
        answer = []
        for folder in folderlist:
            answer = answer + find_input_folders(
                os.path.join(path, folder), specific_folder_name=specific_folder_name
            )
        return answer


def compare_input_parameters_with_reference(folder_path, ext=JSON_EXT):
    f"""Compare provided MVS input parameters with the required parameters

    Parameters
    ----------
    folder_path: str
        path to the mvs input folder
    ext: str
        one of {JSON_EXT} or {CSV_EXT}

    Returns
    -------
    A dict with the missing parameters and extra parameters
    """
    if ext == JSON_EXT:
        # load the mvs input json file into a dict
        json_file_path = os.path.join(folder_path, JSON_FNAME)
        with open(json_file_path) as fp:
            main_parameters = json.load(fp)
    elif ext == CSV_EXT:
        # list the mvs input csv files
        folder_csv_path = os.path.join(folder_path, CSV_ELEMENTS)
        print(folder_csv_path)
        main_parameters = [
            fn[:-4] for fn in os.listdir(folder_csv_path) if fn.endswith(".csv")
        ]

    extra_parameters = {}
    missing_parameters = {}

    required_parameters = REQUIRED_MVS_PARAMETERS[ext]

    for mp in main_parameters:

        if mp not in required_parameters.keys():
            # the main parameter is provided but is not required --> extra
            extra_parameters[mp] = []
        else:
            # the main parameter is provided and required
            # --> comparison of the sub parameters with the reference
            if ext == JSON_EXT:
                # get the sub parameters from the json structure
                sub_parameters = main_parameters[mp].keys()
            elif ext == CSV_EXT:
                # read the csv file, each line corresponds to a sub_parameter
                df = pd.read_csv(os.path.join(folder_csv_path, mp + ".csv"))
                sub_parameters = df.iloc[:, 0].unique().tolist()

            # intersect the set of provided sub_parameters with the set of required sub parameters
            not_matching_params = list(
                set(sub_parameters) ^ set(required_parameters[mp])
            )

            for sp in not_matching_params:
                if sp in required_parameters[mp]:
                    # the sub parameter is not provided but is required --> missing
                    param_list = missing_parameters.get(mp, [])
                    param_list.append(sp)
                    missing_parameters[mp] = param_list
                else:
                    # the sub parameter is provided but is not required --> extra
                    param_list = extra_parameters.get(mp, [])
                    param_list.append(sp)
                    extra_parameters[mp] = param_list

    for mp in required_parameters.keys():
        if mp not in main_parameters:
            # the main parameter is not provided but is required --> missing
            missing_parameters[mp] = required_parameters[mp]

    answer = {}
    if len(missing_parameters) > 0:
        answer[MISSING_PARAMETERS_KEY] = missing_parameters
    if len(extra_parameters) > 0:
        answer[EXTRA_PARAMETERS_KEY] = extra_parameters

    return answer
