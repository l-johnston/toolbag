"""Test read_ltraw"""
import pathlib
from unyt import unyt_array
from unyt.testing import allclose_units
from toolbag import read_ltraw

data_dir = pathlib.Path("tests/data files")

# pylint: disable=missing-function-docstring
def test_vsource():
    sim = read_ltraw(data_dir.joinpath("vsource.raw"))
    assert sim.variables == [
        "time",
        "V(v1)",
        "V(v2)",
        "I(R2)",
        "I(R1)",
        "I(V2)",
        "I(V1)",
    ]
    assert allclose_units(sim.time[-1], unyt_array(0.001, "s"))
    assert allclose_units(sim["V(v1)"], unyt_array(4 * [1.0], "V"))
    assert allclose_units(sim["I(R1)"], unyt_array(4 * [2.0], "A"))
    assert allclose_units(sim["V(v2)"], unyt_array(4 * [3.0], "V"))
    assert allclose_units(sim["I(R2)"], unyt_array(4 * [4.0], "A"))


def test_vsourceac():
    sim = read_ltraw(data_dir.joinpath("vsource ac.raw"))
    assert sim.variables == ["frequency", "V(v1)", "I(C1)", "I(V1)"]
    assert allclose_units(sim.frequency, unyt_array([1, 2, 3], "Hz"))
    assert allclose_units(sim["V(v1)"], unyt_array(3 * [complex(1, 0)], "V"))
    assert allclose_units(sim["I(C1)"].imag, unyt_array([1, 2, 3], "A"))
