#!/usr/bin/env python
import pytest
import os

from ..mvs_eland_tool import main

def test_run_smoothly():
    assert main(test=True) == 1

def test_blacks_main():
    r = os.system("black --check mvs_eland_tool.py")
    assert r == 0

def test_blacks_code_folder():
    r = os.system("black --check code_folder/*.py")
    assert r == 0