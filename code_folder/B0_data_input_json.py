import pandas as pd
import pprint as pp
import json


class data_input:
    def get(self, user_input):
        """

        Parameters
        ----------
        user_input

        Returns
        -------

        """
        with open(user_input["path_input_file"]) as json_file:
            dict_values = json.load(json_file)
        return dict_values
