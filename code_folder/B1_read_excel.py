import pandas as pd
import logging
import pprint as pp
import shutil


class read_template:
    def overview_energy_system(user_input):
        """
        Called by B0_data input.
        This function determines the energy system defined in tab 'Overview'
        Each asset is added to the dictionary, if it is included in the energy system
        In a next step, in B0_data_input, each asset is attributed its technical values.
        Asset groups: sectors, energy_providers, generation_assets, storage_assets, conversion_assets, demands
        :param user_input: includes location of input file
        :return: all assets included in energy system, saved in a dict
        (keys: asset groups, linked to list of strings of included assets)
        """
        tab_name = "Overview"

        logging.debug('Determining assets from tab "Overview".')

        # Definition on where to find data on tab overview.
        # There, all included assets are marked with yes/no
        # Currently, only one asset type can be included
        dict_of_overview_info = {
            "sectors": {
                "title": "Energy sectors/carriers to be considered",
                "tab_name": tab_name,
                "first_row": 14,
                "number_of_rows": 6,
                "column_string": "B:C",
                "index_col": 1,
            },
            "energy_providers": {
                "title": "External energy providers",
                "tab_name": tab_name,
                "first_row": 24,
                "number_of_rows": 5,
                "column_string": "B:C",
                "index_col": 1,
            },
            "generation_assets": {
                "title": "Generation",
                "tab_name": tab_name,
                "first_row": 29,
                "number_of_rows": 6,
                "column_string": "B:C",
                "index_col": 1,
            },
            "storage_assets": {
                "title": "Storage",
                "tab_name": tab_name,
                "first_row": 35,
                "number_of_rows": 5,
                "column_string": "B:C",
                "index_col": 1,
            },
            "conversion_assets": {
                "title": "Conversion",
                "tab_name": tab_name,
                "first_row": 40,
                "number_of_rows": 5,
                "column_string": "B:C",
                "index_col": 1,
            },
            "demands": {
                "title": "Demands",
                "tab_name": tab_name,
                "first_row": 45,
                "number_of_rows": 5,
                "column_string": "B:C",
                "index_col": 1,
            },
        }

        included_assets = (
            {}
        )  # todo - if energy provider includes electricity etc, it actually adds anther asset: transformer station, ie.
        for asset_group_name in dict_of_overview_info.keys():
            # Reads and checks info on all asset groups. Returns list of strings.
            included = read_template.get_included_assets(
                user_input,
                tab_name,
                asset_group_name,
                dict_of_overview_info[asset_group_name],
            )
            # Saves group names with list of strings of included assets in dictionary
            included_assets.update({asset_group_name: included})

        return included_assets

    def get_included_assets(user_input, tab_name, asset_group_name, dict_of_asset):
        """
        Determining which assets of a asset group are included in energy system defined by "Overview" tab
        :param user_input: includes file path
        :param tab_name: Tab 'Overview'
        :param asset_group_name: Name of asset group, ie. sectors, energy_providers, generation_assets, storage_assets, conversion_assets, demands
        :param dict_of_asset: Defines where info on asset group is stored in tab 'Overview'
        :return: A list of strings naming the included assets #todo this list is capitalized.
        """

        logging.debug("Determinging included %s.", asset_group_name)
        # Read from excel file
        assets = read_template.read_excel_dict(user_input, dict_of_asset)

        included = []
        asset_string = ""
        for asset_item in assets[dict_of_asset["title"]]:
            # Add all activated assets of an asset group...
            if assets[dict_of_asset["title"]][asset_item] == "Yes":
                if asset_item == "(National) Electricity grid":
                    short_asset_item = "transformer_station"
                    # ...to list of included assets
                    included.append(short_asset_item)
                    # ...string of included assets
                    asset_string = (
                        asset_string + asset_item + " (" + short_asset_item + ")" + ", "
                    )

                else:
                    # (only using first line of asset name in excel table)
                    short_asset_item = asset_item.split("\n", 1)
                    # ...to list of included assets
                    included.append(short_asset_item[0])
                    # ...string of included assets
                    asset_string = asset_string + short_asset_item[0] + ", "

        # Display included assets
        asset_string = asset_string[:-2]
        if len(asset_string) < 1:
            logging.info("This simulation does not include %s.", asset_group_name)
        else:
            logging.info(
                "This simulation includes following %s: %s",
                asset_group_name,
                asset_string,
            )

        return included

    def read_excel_dict(user_input, dict_excel_data):
        data = pd.read_excel(
            user_input["path_input_file"],
            sheet_name=dict_excel_data["tab_name"],
            skiprows=dict_excel_data["first_row"] - 1,
            index_col=dict_excel_data["index_col"],
            usecols=dict_excel_data["column_string"],
            nrows=dict_excel_data["number_of_rows"] - 1,
        )
        data = data.to_dict(orient="dict")
        return data

    def read_excel_tab(user_input, dict_excel_data):
        data = pd.read_excel(
            user_input["path_input_file"],
            sheet_name=dict_excel_data["tab_name"],
            skiprows=dict_excel_data["first_row"] - 1,
            index_col=dict_excel_data["index_col"],
            usecols=dict_excel_data["column_string"],
            nrows=dict_excel_data["number_of_rows"] - 1,
        )
        return data
