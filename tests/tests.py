#!/usr/bin/env python
import pytest
import os

from ..mvs_eland_tool import main

def test_run_smoothly():
    # Ensure that code does not terminate
    assert main(test=True) == 1

def test_blacks_main():
    # Testing code formatting in main folder
    r = os.system("black --check *.py")
    assert r == 0

def test_blacks_code_folder():
    # Testing code formatting in code folder
    r = os.system("black --check code_folder/*.py")
    assert r == 0