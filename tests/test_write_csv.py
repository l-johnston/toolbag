"""Test write_csv"""
import tempfile
import os
from unyt import unyt_array
from unyt.testing import allclose_units
from toolbag import write_csv, read_csv

# pylint:disable=missing-function-docstring
def test_rowheader():
    file = tempfile.NamedTemporaryFile(mode="wt", delete=False)
    data = [["frequency (Hz)", "1"], ["power (dBm)", "2", "3"]]
    write_csv(file, data)
    file.close()
    readback = read_csv(file.name)
    assert allclose_units(readback.frequency, unyt_array([1], "Hz"))
    os.remove(file.name)


def test_append():
    file = tempfile.NamedTemporaryFile(mode="wt", delete=False)
    data = [["frequency (Hz)", "1"], ["power (dBm)", "2", "3"]]
    write_csv(file, data)
    file.close()
    data = [["loss (dB)", "4", "5"]]
    write_csv(file.name, data, mode="a")
    readback = read_csv(file.name)
    assert allclose_units(readback.loss, unyt_array([4, 5], "dB"))
    os.remove(file.name)
