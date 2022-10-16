import os
import copy
import json
import shutil
import logging
import warnings
import pandas as pd
from .constants import (
    PACKAGE_DATA_PATH,
    JSON_FNAME,
    CSV_ELEMENTS,
    OUTPUT_FOLDER,
    JSON_EXT,
    CSV_EXT,
    REQUIRED_MVS_PARAMETERS,
    KNOWN_EXTRA_PARAMETERS,
    JSON_FNAME,
    MISSING_PARAMETERS_KEY,
    EXTRA_PARAMETERS_KEY,
    TEMPLATE_INPUT_FOLDER,
    DEFAULT_VALUE,
    WARNING_TEXT,
)

from .constants_json_strings import (
    UNIT,
    VALUE,
    PROJECT_DATA,
    ECONOMIC_DATA,
    SIMULATION_SETTINGS,
    CONSTRAINTS,
    ENERGY_CONSUMPTION,
    ENERGY_CONVERSION,
    ENERGY_PRODUCTION,
    ENERGY_STORAGE,
    ENERGY_BUSSES,
    ENERGY_PROVIDERS,
    FIX_COST,
)

from .exceptions import MissingParameterError


class ParameterDocumentation:
    """Helper to access a parameter's information given its variable name"""

    def __init__(
        self, param_info_file, label_header="label",
    ):
        self.param_doc = pd.read_csv(param_info_file).set_index(label_header)
        self.label_hdr = label_header
        self.fname = param_info_file
        self.param_format = {"numeric": float, "str": str, "boolean": bool}

    @property
    def where_to_find_param_documentation(self):
        return (
            "*" * 5
            + f" Note: The documentation about each of the MVS parameters can be found in the csv file {self.fname}. "
            + "*" * 5
        )

    def __get_doc_parameter_info(self, param_label, column_name):
        """Search the value of a parameter information in the parameter doc

        Parameters
        ----------
        param_label: str
            name of the variable as referenced in the column "label" of the
            documentation csv file
        column_name:
            name of the documentation csv file's column corresponding to the
            desired information about the parameter

        Returns
        -------
        str: value of the given parameter information
        """
        if isinstance(param_label, list):
            answer = []
            for p_name in param_label:
                answer.append(self.__get_doc_parameter_info(p_name, column_name))
        else:
            try:
                answer = self.param_doc.loc[param_label][column_name]
            except KeyError as e:
                raise KeyError(
                    f"Either {param_label} is not part of the {self.label_hdr} column of the file {self.fname}, or the column {column_name} does not exist in this file"
                ).with_traceback(e.__traceback__)
        return answer

    def get_doc_verbose(self, param_label):
        answer = self.__get_doc_parameter_info(param_label, "verbose")
        answer_is_list = True
        if not isinstance(param_label, list):
            answer_is_list = False
            answer = [answer]
            param_label = [param_label]

        for i in range(len(answer)):
            if answer[i] == "None":
                answer[i] = param_label[i].replace("_", " ").title()
        if answer_is_list is False:
            answer = answer[0]
        return answer

    def get_doc_definition(self, param_label):
        return self.__get_doc_parameter_info(param_label, ":Definition:")

    def get_doc_default(self, param_label):
        answer = self.__get_doc_parameter_info(param_label, ":Default:")
        param_type = self.get_doc_type(param_label)
        if answer == "None":
            answer = None
        else:
            answer = self.param_format[param_type](answer)
        return answer

    def get_doc_unit(self, param_label):
        return self.__get_doc_parameter_info(param_label, ":Unit:")

    def get_doc_type(self, param_label):
        return self.__get_doc_parameter_info(param_label, ":Type:")


try:
    mvs_parameter_file = "MVS_parameters_list.csv"
    DOC_PATH = os.path.join(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ),
        "docs",
    )
    if os.path.exists(DOC_PATH):
        PARAMETERS_DOC = ParameterDocumentation(
            param_info_file=os.path.join(DOC_PATH, mvs_parameter_file)
        )
    elif os.path.exists(PACKAGE_DATA_PATH):
        PARAMETERS_DOC = ParameterDocumentation(
            param_info_file=os.path.join(PACKAGE_DATA_PATH, mvs_parameter_file)
        )
    else:
        PARAMETERS_DOC = None

except FileNotFoundError:
    PARAMETERS_DOC = None


def find_json_input_folders(
    path, specific_file_name=JSON_FNAME, ignore_folders=(OUTPUT_FOLDER,)
):
    """Recursively look in the folder structure until is sees a specific file

    Parameters
    ----------
    path: str
        the starting point of the search in the folder structure
    specific_file_name: str
        the name of the special file which should be present within a folder to add this folder
        name to the list of matching folders
    ignore_folders: tuple of str
        a tuple of folder names which should not be investigated by the function, nor added to
        the list of matching folders

    Returns
    -------
    A list of paths to folders containing a specific file
    """
    folder_list = [
        fn.name
        for fn in os.scandir(path)
        if fn.is_dir() and fn.name not in ignore_folders
    ]

    if os.path.exists(os.path.join(path, JSON_FNAME)):
        answer = [path]
    else:
        answer = []
        for folder in folder_list:
            answer = answer + find_json_input_folders(
                os.path.join(path, folder),
                specific_file_name=specific_file_name,
                ignore_folders=ignore_folders,
            )
    return answer


def find_csv_input_folders(
    path, specific_folder_name=CSV_ELEMENTS, ignore_folders=(OUTPUT_FOLDER,)
):
    """Recursively look in the folder structure until is sees a specific folder

    Parameters
    ----------
    path: str
        the starting point of the search in the folder structure
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

    folder_list = [
        fn.name
        for fn in os.scandir(path)
        if fn.is_dir() and fn.name not in ignore_folders
    ]
    if CSV_ELEMENTS in folder_list:
        return [path]
    else:
        answer = []
        for folder in folder_list:
            answer = answer + find_csv_input_folders(
                os.path.join(path, folder), specific_folder_name=specific_folder_name
            )
        return answer


def compare_input_parameters_with_reference(
    folder_path, ext=JSON_EXT, flag_missing=False, set_default=False
):
    """Compare provided MVS input parameters with the required parameters

    Extra parameters listed in KNOWN_EXTRA_PARAMETERS are not flagged as missing if
    not provided, instead they take their default value defined in KNOWN_EXTRA_PARAMETERS

    Parameters
    ----------
    folder_path: str
        path to the mvs input folder
    ext: str
        one of {JSON_EXT} or {CSV_EXT}
    flag_missing: bool
        if True, raise MissingParameterError for each missing required parameter
    set_default: bool
        if True, set the default value of a missing required parameter which is listed in
        KNOWN_EXTRA_PARAMETERS

    Returns
    -------
    A dict with the missing parameters under the key {MISSING_PARAMETERS_KEY} and extra parameters
    under the key {EXTRA_PARAMETERS_KEY}

    Notes
    -----
    #todo This function does not check whether the storage-subassets have all necessary parameters, or if excess parameters are provided.
    """
    if ext == JSON_EXT:

        if isinstance(folder_path, dict):
            # the folder_path argument is already a dict
            main_parameters = folder_path
        else:
            # load the mvs input json file into a dict
            json_file_path = os.path.join(folder_path, JSON_FNAME)
            with open(json_file_path) as fp:
                main_parameters = json.load(fp)

    elif ext == CSV_EXT:
        # list the mvs input csv files
        folder_csv_path = os.path.join(folder_path, CSV_ELEMENTS)
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
                if mp in [
                    PROJECT_DATA,
                    ECONOMIC_DATA,
                    SIMULATION_SETTINGS,
                    CONSTRAINTS,
                    FIX_COST,
                ]:
                    # project parameters only
                    sub_params = {"non-asset": main_parameters[mp].keys()}
                elif mp in [
                    ENERGY_CONSUMPTION,
                    ENERGY_CONVERSION,
                    ENERGY_PRODUCTION,
                    ENERGY_STORAGE,
                    ENERGY_BUSSES,
                    ENERGY_PROVIDERS,
                ]:
                    # dict containing assets
                    # TODO this should be modified if the assets are inside a list instead
                    # of inside a dict
                    sub_params = main_parameters[mp]

            elif ext == CSV_EXT:
                # read the csv file, each line corresponds to a sub_parameter
                df = pd.read_csv(os.path.join(folder_csv_path, mp + ".csv"))
                sub_params = {"non-asset": df.iloc[:, 0].unique().tolist()}

            for k in sub_params:
                sub_parameters = sub_params[k]
                if required_parameters[mp] is not None:
                    # intersect the set of provided sub_parameters with the set of required sub parameters
                    not_matching_params = list(
                        set(sub_parameters) ^ set(required_parameters[mp])
                    )
                else:
                    # the parameter is expected to contain user defined names --> those are not checked
                    not_matching_params = []

                for sp in not_matching_params:
                    if sp in required_parameters[mp]:

                        if sp in KNOWN_EXTRA_PARAMETERS and set_default is True:
                            # the sub parameter is not provided but is listed in known extra parameters
                            # --> default value is set for this parameter
                            if k == "non-asset":
                                main_parameters[mp][sp] = {
                                    UNIT: KNOWN_EXTRA_PARAMETERS[sp][UNIT],
                                    VALUE: KNOWN_EXTRA_PARAMETERS[sp][DEFAULT_VALUE],
                                }
                                logging.warning(
                                    f"You are not using the parameter '{sp}' for asset group '{mp}', which "
                                    + KNOWN_EXTRA_PARAMETERS[sp][WARNING_TEXT]
                                    + f"This parameter is set to it's default value ({KNOWN_EXTRA_PARAMETERS[sp][DEFAULT_VALUE]}),"
                                    + " which can influence the results."
                                    + "In the next release, this parameter will required."
                                )
                            else:
                                main_parameters[mp][k][sp] = {
                                    UNIT: KNOWN_EXTRA_PARAMETERS[sp][UNIT],
                                    VALUE: KNOWN_EXTRA_PARAMETERS[sp][DEFAULT_VALUE],
                                }
                                logging.warning(
                                    f"You are not using the parameter '{sp}' for asset '{k}' of asset group '{mp}', which "
                                    + KNOWN_EXTRA_PARAMETERS[sp][WARNING_TEXT]
                                    + f"This parameter is set to it's default value ({KNOWN_EXTRA_PARAMETERS[sp][DEFAULT_VALUE]}),"
                                    + " which can influence the results."
                                    + "In the next release, this parameter will required."
                                )
                        elif set_default is True:

                            main_parameters[mp][k][sp] = {
                                VALUE: PARAMETERS_DOC.get_doc_default(sp),
                                UNIT: PARAMETERS_DOC.get_doc_unit(sp),
                            }
                            logging.warning(
                                f"You are not providing a value for the parameter '{sp}' of asset '{k}' in asset group '{mp}'"
                                + f"This parameter is then set to it's default value ({PARAMETERS_DOC.get_doc_default(sp)}).\n"
                                + PARAMETERS_DOC.where_to_find_param_documentation
                            )
                        else:
                            # the sub parameter is not provided but is required --> missing
                            param_list = missing_parameters.get(mp, [])
                            param_list.append(sp)
                            missing_parameters[mp] = param_list
                    else:
                        # the sub parameter is provided but is not required --> extra
                        param_list = extra_parameters.get(mp, [])
                        if sp not in param_list:
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

    if flag_missing is True:
        warn_missing_parameters(answer)

    return answer


def warn_missing_parameters(comparison_with_reference):
    """Raise error for missing parameters

    Parameters
    ----------
    comparison_with_reference: dict
        dict with possibly two keys: MISSING_PARAMETERS_KEY, EXTRA_PARAMETERS_KEY
    Returns
    -------
    Nothing

    """
    if MISSING_PARAMETERS_KEY in comparison_with_reference:
        error_msg = []

        d = comparison_with_reference[MISSING_PARAMETERS_KEY]

        error_msg.append(" ")
        error_msg.append(" ")
        error_msg.append(
            "The following parameter groups and sub parameters are missing from input parameters:"
        )

        for asset_group in d.keys():
            error_msg.append(asset_group)
            if d[asset_group] is not None:
                for k in d[asset_group]:
                    error_msg.append(f"\t`{k}` parameter")

        raise (MissingParameterError("\n".join(error_msg)))


def set_nested_value(dct, value, keys):
    r"""Set a value within a nested dict structure given the path within the dict

    Parameters
    ----------
    dct: dict
        the (potentially nested) dict from which we want to get a value
    value: variable type
        value to assign within the dict
    keys: tuple
        Tuple containing the succession of keys which lead to the value within the nested dict

    Returns
    -------
    The value under the path within the (potentially nested) dict

    Example
    -------
    >>> dct = dict(a=dict(a1=1, a2=2),b=dict(b1=dict(b11=11,b12=dict(b121=121))))
    >>> print(set_nested_value(dct, 400,("b", "b1", "b12","b121")))
    {'a': {'a1': 1, 'a2': 2}, 'b': {'b1': {'b11': 11, 'b12': {'b121': 400}}}}
    """
    if isinstance(keys, tuple) is True:
        try:
            answer = copy.deepcopy(dct)
            if keys[0] not in answer:
                raise KeyError(
                    ": pathError: that path does not exist in the nested dict"
                )
            if len(keys) > 1:
                answer[keys[0]] = set_nested_value(dct[keys[0]], value, keys[1:])
            elif len(keys) == 1:
                # if the value is a dict with structure {VALUE: ..., UNIT: ...}
                if isinstance(answer[keys[0]], dict):
                    if VALUE in answer[keys[0]]:
                        answer[keys[0]][VALUE] = value
                    else:
                        answer[keys[0]] = value
                else:
                    answer[keys[0]] = value
            else:
                raise ValueError(
                    "The tuple argument 'keys' from set_nested_value() should not be empty"
                )
        except KeyError as e:
            if "pathError" in str(e):
                raise KeyError(keys[0] + ", " + e.args[0])
    elif isinstance(keys, str) is True:
        return set_nested_value(dct, value, split_nested_path(keys))
    else:
        raise TypeError("The argument 'keys' from set_nested_value() should be a tuple")
    return answer


def get_nested_value(dct, keys):
    r"""Get a value from a succession of keys within a nested dict structure

    Parameters
    ----------
    dct: dict
        the (potentially nested) dict from which we want to get a value
    keys: tuple
        Tuple containing the succession of keys which lead to the value within the nested dict

    Returns
    -------
    The value under the path within the (potentially nested) dict

    Example
    -------
    >>> dct = dict(a=dict(a1=1, a2=2),b=dict(b1=dict(b11=11,b12=dict(b121=121))))
    >>> print(get_nested_value(dct, ("b", "b1", "b12","b121")))
    121
    """
    if isinstance(keys, tuple) is True:
        try:
            if len(keys) > 1:
                answer = get_nested_value(dct[keys[0]], keys[1:])
            elif len(keys) == 1:
                answer = dct[keys[0]]
            else:
                raise ValueError(
                    "The tuple argument 'keys' from get_nested_value() should not be empty"
                )
        except KeyError as e:
            if "pathError" in str(e):
                raise KeyError(str(keys[0]) + ", " + str(e))
            else:
                raise KeyError(
                    str(keys[0])
                    + ": pathError: that path does not exist in the nested dict"
                )

    else:
        raise TypeError("The argument 'keys' from get_nested_value() should be a tuple")
    return answer


def split_nested_path(path):
    r"""Separate a single-string path in a nested dict in a list of keys


    Parameters
    ----------
    path: str or tuple
        path within a nested dict which is expressed as a str of a succession of keys separated by
        a `.` or a `,`. The order of keys is to be read from left to right.

    Returns
    -------
    Tuple containing the succession of keys which lead to the value within the nested dict

    """
    SEPARATORS = (".", ",")
    keys_list = None
    if isinstance(path, str):
        separator_count = 0
        keys_separator = None
        for separator in SEPARATORS:
            if separator in path:
                if path.count(separator) > 0:
                    if separator_count > 0:
                        raise ValueError(
                            f"The separator of the nested dict's path is not unique"
                        )
                    separator_count = path.count(separator)
                    keys_separator = separator
        if keys_separator is not None:
            keys_list = tuple(path.split(keys_separator))
    elif isinstance(path, tuple):
        keys_list = path
    else:
        raise TypeError("The argument path is not tuple or str type")

    return keys_list


def nested_dict_crawler(dct, path=None, path_dct=None):
    r"""A recursive algorithm that crawls through a (nested) dictionary and returns
    a dictionary of endkeys mapped to a list of the paths leading to each endkey.
    An endkey is defined the last key in the nested dict before a value of type different than dict or the last key
    before a dict containing only {"unit": ..., "value": ...}
            Parameters
            ----------
            dct: dict
                the (potentially nested) dict from which we want to get the endkeys
            path: list
                storing the current path that the algorithm is on
            path_dct: dict
                result dictionary where each key is assigned to its (multiple) paths within the (nested) dictionary
            Returns
            -------
            Dictionary of key and paths to the respective key within the nested dictionary structure
            Example
            -------
            >>> dct = dict(a=dict(a1=1, a2=2),b=dict(b1=dict(b11=11,b12=dict(b121=121))))
            >>> nested_dict_crawler(dct)
            {
                "a1": [("a", "a1")],
                "a2": [("a", "a2")],
                "b11": [("b", "b1", "b11")],
                "b121": [("b", "b1", "b12", "b121")],
            }
    """
    if path is None:
        path = []
    if path_dct is None:
        path_dct = dict()

    for key, value in dct.items():
        path.append(key)
        if isinstance(value, dict):
            if "value" in value.keys() and "unit" in value.keys():
                if path[-1] in path_dct:
                    path_dct[path[-1]].append(tuple(path))
                else:
                    path_dct[path[-1]] = [tuple(path)]
            else:
                nested_dict_crawler(value, path, path_dct)
        else:
            if path[-1] in path_dct:
                path_dct[path[-1]].append(tuple(path))
            else:
                path_dct[path[-1]] = [tuple(path)]
        path.pop()
    return path_dct


def copy_report_assets(path_destination_folder):
    """Copy the css file and eland logo to the path_destination_folder

    Parameters
    ----------
    path_destination_folder: str
        path where the default report css files and logo should be copied

    Returns
    -------
    Path of the destination folder

    """
    assets_folder = os.path.join(path_destination_folder, "report", "assets")
    if os.path.exists(assets_folder) is False:
        # copy from the default asset folder from mvs package
        try:
            assets_folder = shutil.copytree(
                os.path.join(PACKAGE_DATA_PATH, "assets"), assets_folder
            )
        except FileNotFoundError:
            assets_folder = shutil.copytree(
                os.path.join(".", "report", "assets"), assets_folder
            )
    else:
        logging.warning(
            "The assets folder {} exists already, it will not be replaced by default folder "
            "from multi_vector_simulator's package".format(assets_folder)
        )
    return assets_folder


def copy_inputs_template(path_destination_folder):
    """Copy the inputs template folder

    Parameters
    ----------
    path_destination_folder: str
        path where the inputs template folder should be copied to

    Returns
    -------
    Path of the destination folder

    """
    inputs_template_folder = os.path.join(
        path_destination_folder, TEMPLATE_INPUT_FOLDER
    )
    if os.path.exists(inputs_template_folder) is False:
        # copy from the default asset folder from mvs package
        try:
            inputs_template_folder = shutil.copytree(
                os.path.join(PACKAGE_DATA_PATH, TEMPLATE_INPUT_FOLDER),
                inputs_template_folder,
            )
            logging.info(
                f"The following folder was successfully created into your local "
                f"directory {inputs_template_folder}"
            )
        except FileNotFoundError:
            logging.warning(
                "If you installed the package in develop mode, then you cannot use this command"
            )
    else:
        logging.warning(
            "The inputs template folder {} exists already, it will not be replaced by default "
            "folder from multi_vector_simulator's package".format(TEMPLATE_INPUT_FOLDER)
        )
    return inputs_template_folder
