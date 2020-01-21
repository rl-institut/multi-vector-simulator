#!/usr/bin/env python
import pytest
import os

from ..mvs_eland_tool import main


def test_run_smoothly():
    # Ensure that code does not terminate
    assert main(test=True) == 1
