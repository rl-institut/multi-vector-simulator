#!/usr/bin/env python
import pytest
import os

from ..mvs_eland_tool import main

def test_run_smoothly():
    assert main(test=True) == 1

import black

def test_blacks():
    r = os.system("black --check mvs_eland_tool.py")
    assert r == 0