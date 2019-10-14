import pytest
import os

from mvs_eland.mvs_eland_tool import main

def test_run_smoothly():
    assert main() == 1
