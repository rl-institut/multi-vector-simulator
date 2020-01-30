import os
import mock
import argparse
import shutil

from mvs_eland_tool.mvs_eland_tool import main

OUTPUT_PATH = os.path.join(".", "tests", "MVS_outputs_simulation")


def setup_module():
    if os.path.exists(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH, ignore_errors=True)


@mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
def test_run_smoothly(mock_args):

    main(path_output_folder=OUTPUT_PATH)
    assert 1 == 1


def teardown_module():
    shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
