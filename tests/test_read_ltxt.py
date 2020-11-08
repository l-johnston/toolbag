"""Test read_ltxt"""
from tempfile import TemporaryFile
from unyt import unyt_array
from unyt.testing import allclose_units
from toolbag import read_ltxt


# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
def test_time():
    with TemporaryFile(mode="w+t", encoding="utf-8") as file:
        file.write("time\tV(out)\n0.0e+0\t1.0e+0\n1.0e+0\t2.0e+0")
        file.seek(0)
        data = read_ltxt(file)
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


def test_frequency_dBdeg():
    with TemporaryFile(mode="w+t", encoding="utf-8") as file:
        file.write(
            """Freq.\tV(out)
            0.0e+0\t(0.0e+0dB,0.0e+0°)
            1.0e+0\t(-3.0e+0dB,-9.0e+1°)"""
        )
        file.seek(0)
        data = read_ltxt(file)
    assert data.header == "frequency\tV(out)"
    expected = unyt_array([0.0, 1.0], "Hz")
    assert allclose_units(data.frequency, expected)
    expected = unyt_array([0.0, -3.0], "dB")
    assert allclose_units(data.V_out[0], expected)
    expected = unyt_array([0.0, -90.0], "degree")
    assert allclose_units(data.V_out[1], expected)


def test_frequency_reim():
    with TemporaryFile(mode="w+t", encoding="utf-8") as file:
        file.write(
            """Freq.\tV(out)
            0.0e+0\t0.0e+0,0.0e+0
            1.0e+0\t2.0e+0,3.0e+0"""
        )
        file.seek(0)
        data = read_ltxt(file)
    assert data.header == "frequency\tV(out)"
    expected = unyt_array([0.0, 1.0], "Hz")
    assert allclose_units(data.frequency, expected)
    expected = unyt_array([0.0, 2.0], "V")
    assert allclose_units(data.V_out[0], expected)
    expected = unyt_array([0.0, 3.0], "V")
    assert allclose_units(data.V_out[1], expected)
