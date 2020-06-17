"""Test read_csv"""
import numpy as np
from toolbag import read_csv

# pylint: disable=missing-function-docstring
def test_singlerow():
    data = read_csv("./toolbag/tests/single row.csv")
    assert np.all(data == np.arange(10))
