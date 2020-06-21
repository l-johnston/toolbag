"""Test read_ltxt"""
from io import StringIO
from unyt import unyt_array
from unyt.testing import allclose_units
from toolbag import read_ltxt

# pylint: disable=missing-function-docstring
def test_time():
    file = StringIO("time\tV(out)\n0.0e+0\t1.0e+0\n1.0e+0\t2.0e+0")
    data = read_ltxt(file)
    file.close()
    assert data.header == "time\tV(out)"
    assert data.legends == ["time", "V(out)"]
    expected = unyt_array([0.0, 1.0], "s")
    assert allclose_units(data.time, expected)
    assert allclose_units(data["time"], expected)
    assert allclose_units(data[0], expected)
    expected = unyt_array([1.0, 2.0], "V")
    assert allclose_units(data.V_out, expected)
    assert allclose_units(data["V(out)"], expected)
    assert allclose_units(data[1], expected)
