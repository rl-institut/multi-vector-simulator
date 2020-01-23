import os, sys
import logging
import pandas as pd

# web-application: valid input directly connected to cell-input


def lookup_file(file_path, name):
    """

    :param file_path:
    :param name:
    :return:
    """
    if os.path.isfile(file_path) == False:
        logging.critical(
            "Missing file! "
            "\n The timeseries file %s of asset %s can not be found. Operation terminated.",
            file_path,
            name,
        )
        sys.exit()
    return


def check_input_values(dict_values):
    """

    :param dict_values:
    :return:
    """
    for asset_name in dict_values:
        if not (isinstance(dict_values[asset_name], dict)):
            # checking first layer of dict_values
            all_valid_intervals(asset_name, dict_values[asset_name], "")
        else:
            # logging.debug('Asset %s checked for validation.', asset_name)
            for sub_asset_name in dict_values[asset_name]:
                if not (isinstance(dict_values[asset_name][sub_asset_name], dict)):
                    # checking second layer of dict values
                    all_valid_intervals(
                        sub_asset_name,
                        dict_values[asset_name][sub_asset_name],
                        asset_name,
                    )
                else:
                    # logging.debug('\t Sub-asset %s checked for validation.', sub_asset_name)
                    for sub_sub_asset_name in dict_values[asset_name][sub_asset_name]:
                        if not (
                            isinstance(
                                dict_values[asset_name][sub_asset_name][
                                    sub_sub_asset_name
                                ],
                                dict,
                            )
                        ):
                            # checking third layer of dict values
                            all_valid_intervals(
                                sub_sub_asset_name,
                                dict_values[asset_name][sub_asset_name][
                                    sub_sub_asset_name
                                ],
                                asset_name + sub_asset_name,
                            )
                        else:
                            # logging.debug('\t\t Sub-sub-asset %s checked for validation.', sub_sub_asset_name)
                            logging.critical(
                                "Verification Error! Add another layer to evaluation."
                            )

    logging.info(
        "Input values have been verified. This verification can not replace a manual input parameter check."
    )
    return


def all_valid_intervals(name, value, title):
    """

    :param name:
    :param value:
    :param title:
    :return:
    """
    valid_type_string = [
        "project_name",
        "scenario_name",
        "country",
        "parent",
        "type",
        "file_name",
        "label",
        "currency",
        "path_output_folder",
        "display_output",
        "input_file_name",
        "path_input_file",
        "path_input_folder",
        "path_output_folder_inputs",
        "sector",
    ]

    valid_type_int = ["evaluated_period", "time_step", "periods"]

    valid_type_timestamp = ["start_date"]

    valid_type_index = ["index"]

    valid_binary = ["optimize_cap", "dsm", "overwrite"]

    valid_intervals = {
        "longitude": [-180, 180],
        "latitude": [-90, 90],
        "lifetime": ["largerzero", "any"],
        "age_installed": [0, "any"],
        "installedCap": [0, "any"],
        "soc_min": [0, 1],
        "soc_max": [0, 1],
        "soc_initial": [0, 1],
        "crate": [0, 1],
        "efficiency": [0, 1],
        "electricity_cost_fix_annual": [0, "any"],
        "electricity_price_var_kWh": [0, "any"],
        "electricity_price_var_kW_monthly": [0, "any"],
        "feedin_tariff": [0, "any"],
        "capex_fix": [0, "any"],
        "capex_var": [0, "any"],
        "opex_fix": [0, "any"],
        "opex_var": [0, "any"],
        "discount_factor": [0, 1],
        "project_duration": ["largerzero", "any"],
        "tax": [0, 1],
    }

    if name in valid_type_int:
        if not (isinstance(value, int)):
            logging.error(
                'Input error! Value %s/%s is not in recommended format "integer".',
                name,
                title,
            )

    elif name in valid_type_string:
        if not (isinstance(value, str)):
            logging.error(
                'Input error! Value %s/%s is not in recommended format "string".',
                name,
                title,
            )

    elif name in valid_type_index:
        if not (isinstance(value, pd.DatetimeIndex)):
            logging.error(
                'Input error! Value %s/%s is not in recommended format "pd.DatetimeIndex".',
                name,
                title,
            )

    elif name in valid_type_timestamp:
        if not (isinstance(value, pd.Timestamp)):
            logging.error(
                'Input error! Value %s/%s is not in recommended format "pd.DatetimeIndex".',
                name,
                title,
            )

    elif name in valid_binary:
        if not (value == True or value == False):
            logging.error(
                "Input error! Value %s/%s is neither True nor False.", name, title
            )

    elif name in valid_intervals:
        if name == "soc_initial":
            if value != None:
                if not (0 <= value and value <= 1):
                    logging.error(
                        "Input error! Value %s/%s should be None, or between 0 and 1.",
                        name,
                        title,
                    )
        else:

            if valid_intervals[name][0] == "largerzero":
                if value <= 0:
                    logging.error(
                        "Input error! Value %s/%s can not be to be smaller or equal to 0.",
                        name,
                        title,
                    )
            elif valid_intervals[name][0] == "nonzero":
                if value == 0:
                    logging.error("Input error! Value %s/%s can not be 0.", name, title)
            elif valid_intervals[name][0] == 0:
                if value < 0:
                    logging.error(
                        "Input error! Value %s/%s has to be larger than or equal to 0.",
                        name,
                        title,
                    )

            if valid_intervals[name][1] == "any":
                pass
            elif valid_intervals[name][1] == 1:
                if 1 < value:
                    logging.error(
                        "Input error! Value %s/%s can not be larger than 1.",
                        name,
                        title,
                    )

    else:
        logging.warning(
            "VALIDATION FAILED: Code does not define a valid range for value %s/%s",
            name,
            title,
        )

    return
