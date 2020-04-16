"""
In this module the tests run over whole simulation from main, not just single functions of modules

What should differ between the different functions is the input file

"""
import os
import sys
import argparse
import shutil
import mock
import pytest

from .constants import TEST_REPO_PATH, JSON_EXT, CSV_EXT
from mvs_eland_tool.mvs_eland_tool import main

OUTPUT_PATH = os.path.join(TEST_REPO_PATH, "MVS_outputs_simulation")


def setup_module():
    if os.path.exists(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH, ignore_errors=True)


fname = os.path.basename(__file__)

# this ensure that the test is only ran if explicitly executed, ie not when the `pytest` command
# alone it called
@pytest.mark.skipif(
    "tests/{}".format(fname) not in sys.argv, reason="requires python3.3"
)
@mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
def test_run_smoothly_json(mock_args):
    main(input_type=JSON_EXT, path_output_folder=OUTPUT_PATH)
    # TODO: find typical output values to write better test, currently it only test that main() run
    # TODO: without crashing, but does not test if the output make sense
    assert 1 == 1


@pytest.mark.skipif(
    "tests/{}".format(fname) not in sys.argv, reason="requires python3.3"
)
@mock.patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace())
def test_run_smoothly_csv(mock_args):
    main(input_type=CSV_EXT, path_output_folder=OUTPUT_PATH, overwrite=True)
    assert 1 == 1


def teardown_module():
    if os.path.exists(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
