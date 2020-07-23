import os
import shutil
import pandas as pd

from .constants import TEST_REPO_PATH


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
