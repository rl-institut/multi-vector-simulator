import os
import shutil
import pandas as pd
import unittest

from _constants import TEST_REPO_PATH
from multi_vector_simulator.utils import (
    nested_dict_crawler,
    set_nested_value,
    get_nested_value,
)
from multi_vector_simulator.utils.helpers import find_value_by_key
from multi_vector_simulator.utils.constants_json_strings import (
    UNIT,
    LABEL,
    ENERGY_PROVIDERS,
    ENERGY_PRODUCTION,
)


def test_shutil_remove_folder_recursively():
    df = pd.DataFrame(columns=["A", "B"])
    folder_name = "a_folder"
    file_name = "a_file"
    path_folder = os.path.join(TEST_REPO_PATH, folder_name)
    os.makedirs(path_folder)
    path_file = os.path.join(path_folder, file_name)
    df.to_csv(path_file)
    assert os.path.exists(path_file)
    assert os.path.exists(path_folder)
    shutil.rmtree(path_folder)
    assert os.path.exists(path_file) is False
    assert os.path.exists(path_folder) is False


def test_find_value_by_key_no_key_apperance():
    A_LABEL = "a_label"
    dict_values = {ENERGY_PRODUCTION: {"asset": {LABEL: A_LABEL}}}
    result = find_value_by_key(data=dict_values, target=UNIT)
    assert (
        result is None
    ), f"The key {UNIT} does not exist in dict_values but a value {result} is returned instead of None."


def test_find_value_by_key_single_key_apperance():
    ASSET = "asset"
    A_LABEL = "a_label"
    dict_values = {ENERGY_PRODUCTION: {ASSET: {LABEL: A_LABEL}}}
    result = find_value_by_key(data=dict_values, target=LABEL)
    assert isinstance(
        result, str
    ), f"The key {A_LABEL} only exists once, but its value {A_LABEL} is not provided. Instead, result is {result}."
    assert (
        result == A_LABEL
    ), f"The value of the searched key should have been {A_LABEL}, but is {result}."


def test_find_value_by_key_multiple_key_apperance():
    ASSET = "asset"
    A_LABEL = "a_label"
    dict_values = {
        ENERGY_PRODUCTION: {ASSET: {LABEL: A_LABEL}},
        ENERGY_PROVIDERS: {ASSET: {LABEL: A_LABEL}},
    }
    result = find_value_by_key(data=dict_values, target=LABEL)
    assert isinstance(
        result, list
    ), f"The key {LABEL} appears twice in dict_values. Still, no list of occurrences is provided, but {result}."
    expected_output = [A_LABEL, A_LABEL]
    assert (
        result == expected_output
    ), f"Not all key duplicates ({expected_output}) were identified, but {result}."


class TestAccessKPIs(unittest.TestCase):
    """
    KPIs are non dict variables (usually scalars, or a dict containing the keys 'unit' and 'value' only)
    which one can find at the very end path of nested dict
    """

    def test_dict_crawler(self):
        dct = dict(a=dict(a1=1, a2=2), b=dict(b1=dict(b11=11, b12=dict(b121=121))))
        self.assertDictEqual(
            {
                "a1": [("a", "a1")],
                "a2": [("a", "a2")],
                "b11": [("b", "b1", "b11")],
                "b121": [("b", "b1", "b12", "b121")],
            },
            nested_dict_crawler(dct),
        )

    def test_dict_crawler_doubled_path(self):
        """If an KPI is present at two places within the dict, the 2 paths should be returned"""
        dct = dict(a=dict(a1=1, a2=2), b=dict(b1=dict(a2=11)))
        self.assertDictEqual(
            {"a1": [("a", "a1")], "a2": [("a", "a2"), ("b", "b1", "a2")]},
            nested_dict_crawler(dct),
        )

    def test_dict_crawler_finds_non_scalar_value(self):
        """
        If a KPI value is not a simple scalar but a dict in the format {'unit':..., 'value':...},
        the crawler should stop the path finding there and consider this last dict to be the value of the KPI
        """
        dct = dict(
            a=dict(a1=1, a2=dict(unit="EUR", value=30)),
            b=dict(b1=dict(b11=11, b12=dict(unit="kWh", value=12))),
        )
        self.assertDictEqual(
            {
                "a1": [("a", "a1")],
                "a2": [("a", "a2")],
                "b11": [("b", "b1", "b11")],
                "b12": [("b", "b1", "b12")],
            },
            nested_dict_crawler(dct),
        )

    def test_set_nested_value_with_correct_path(self):
        dct = dict(a=dict(a1=1, a2=2), b=dict(b1=dict(b11=11, b12=dict(b121=121))))
        self.assertDictEqual(
            {"a": {"a1": 1, "a2": 2}, "b": {"b1": {"b11": 11, "b12": {"b121": 400}}}},
            set_nested_value(dct, 400, ("b", "b1", "b12", "b121")),
        )

    def test_set_nested_value_with_unexisting_key_at_end_of_path(self):
        dct = dict(a=dict(a1=1, a2=2), b=dict(b1=dict(b11=11, b12=dict(b121=121))))
        with self.assertRaises(KeyError):
            set_nested_value(dct, 400, ("b", "b1", "b12", "b122"))

    def test_set_nested_value_with_unexisting_key_in_middle_of_path(self):
        """because the path diverges """
        dct = dict(a=dict(a1=1, a2=2), b=dict(b1=dict(b11=11, b12=dict(b121=121))))
        with self.assertRaises(KeyError):
            set_nested_value(dct, 400, ("b", "d1", "b12", "b121"))

    def test_get_nested_value_with_unexisting_path(self):
        dct = dict(a=dict(a1=1, a2=2), b=dict(b1=dict(b11=11, b12=dict(b121=121))))
        with self.assertRaises(KeyError):
            get_nested_value(dct, ("b", "b1", "b12", "b122"))
