"""Test read_csv"""
from io import StringIO
import numpy as np
from unyt import unyt_array, unyt_quantity
from unyt.testing import allclose_units
from toolbag import read_csv
from toolbag.labview_utilities import DataContainer
from toolbag import convert_timestamp

# pylint: disable=missing-function-docstring
def test_singlerow():
    data = read_csv("./toolbag/tests/single row.csv")
    assert np.all(data == np.arange(10))


def test_singlerow_header():
    data = read_csv("./toolbag/tests/single row header.csv")
    assert np.all(data == np.arange(10))
    assert read_csv.header == "My data"


def test_singlerow_header_datalabel():
    data = read_csv("./toolbag/tests/single row header data label.csv")
    assert allclose_units(data.Time, unyt_array(np.arange(10), "s"))
    assert data.header == "My data"


def test_singlecolumn():
    data = read_csv("./toolbag/tests/single column.csv")
    assert np.all(data == np.arange(10))


def test_singlecolumn_header_datalabel():
    data = read_csv("./toolbag/tests/single column header data label.csv")
    expected_array = unyt_array(np.arange(10), "dimensionless")
    assert allclose_units(data.Time, expected_array)
    assert read_csv.header == "My data"


def test_2darray():
    data = read_csv("./toolbag/tests/2d array.csv")
    assert np.all(data[:, 0] == np.arange(10))
    assert np.all(data[:, 1] == np.arange(10) ** 2)


def test_column_header_nodatalabels():
    data = read_csv("./toolbag/tests/column header no data labels.csv")
    assert np.all(data[:, 0] == np.arange(10))
    assert np.all(data[:, 1] == np.arange(10) ** 2)
    assert read_csv.header == "My data"


def test_column_noheader_datalabelsnounits():
    data = read_csv("./toolbag/tests/column no header data labels no units.csv")
    assert isinstance(data, DataContainer)
    expected_array = unyt_array(np.arange(10), "dimensionless")
    assert allclose_units(data[0], expected_array)
    assert allclose_units(data["Time"], expected_array)
    assert allclose_units(data["Time - Plot 0"], expected_array)
    expected_array = unyt_array(np.arange(10) ** 2, "dimensionless")
    assert allclose_units(data[1], expected_array)
    assert allclose_units(data["Amplitude"], expected_array)
    assert allclose_units(data["Amplitude - Plot 0"], expected_array)
    assert data.header == ""
    assert data.legends == ["Plot 0", "Plot 0"]


def test_column_noheader_datalabels():
    data = read_csv("./toolbag/tests/column no header data labels.csv")
    expected_array = unyt_array(np.arange(10), "s")
    assert allclose_units(data["Time (s) - Plot 0"], expected_array)
    expected_array = unyt_array(np.arange(10) ** 3, "V")
    assert allclose_units(data["Amplitude (V) - Plot 1"], expected_array)


def test_column_header_datalabels():
    data = read_csv("./toolbag/tests/column header data labels.csv")
    expected_array = unyt_array(np.arange(10), "s")
    assert allclose_units(data.Time, expected_array)
    expected_array = unyt_array(np.arange(10) ** 2, "V")
    assert allclose_units(data.Voltage, expected_array)
    assert (
        data.header
        == "Some data generated in LabVIEW\nPartioned into columns of Time, Voltage"
    )


def test_prefixes():
    data = read_csv("./toolbag/tests/column header data labels units prefixes.csv")
    expected_array = unyt_array([0.0, 1.0e-6, 3.0e6], "s")
    assert allclose_units(data.Time, expected_array)
    expected_array = unyt_array([0.001, 2000.0, 4.0e9], "V")
    assert allclose_units(data.Voltage, expected_array)


def test_row_header_datalabels():
    data = read_csv("./toolbag/tests/row header data labels.csv")
    expected_array = unyt_array([0, 1, 2], "s")
    assert allclose_units(data.R0, expected_array)
    expected_array = unyt_array([3, 4, 5], "V/m")
    assert allclose_units(data.R1, expected_array)
    assert data.header == "My data"


def test_row_noheader_datalabels():
    data = read_csv("./toolbag/tests/row no header data labels.csv")
    expected_array = unyt_array([0, 1, 2], "s")
    assert allclose_units(data.R0, expected_array)
    expected_array = unyt_array([3, 4, 5], "V/m")
    assert allclose_units(data.R1, expected_array)
    assert data.header == ""


def test_nan():
    data = read_csv("./toolbag/tests/single column with NaN Inf -Inf.csv")
    assert np.isnan(data[0])
    assert np.isposinf(data[1])
    assert np.isneginf(data[2])


def test_singlerow_timestamps():
    ts = convert_timestamp(read_csv("./toolbag/tests/single row timestamps.csv"))
    expected_array = np.asarray(
        [np.datetime64(f"2020-01-01T00:00:0{v}.000000") for v in range(3)]
    )
    assert np.all(ts == expected_array)


def test_file():
    file = StringIO("My data\nTime (s),1p,2u,3k")
    data = read_csv(file)
    file.close()
    assert data.header == "My data"
    assert allclose_units(data.Time, unyt_array([1e-12, 2e-6, 3e3], "s"))


def test_extraspaceinname():
    data = read_csv("./toolbag/tests/extra space in name.csv")
    assert allclose_units(data.I_bat[0], unyt_quantity(10e-6, "A"))


def test_unequal_lengths():
    data = read_csv("./toolbag/tests/unequal lengths.csv")
    assert np.isnan(data[2, 2])


def test_dir_invalid_name():
    file = StringIO("500_MHz,1_GHz\n1.0,2.0")
    data = read_csv(file)
    assert '["500_MHz"]' in dir(data)


def test_headerwithoutquantity():
    file = StringIO(
        "Coarse Amplitude DAC code - Plot 0,Attenuation (dB) - Plot 0\n1.0,2.0"
    )
    data = read_csv(file)
    assert np.all(data["Coarse Amplitude DAC code - Plot 0"] == np.asarray([1.0]))
    assert np.all(data.Attenuation == unyt_array([2.0], "dB"))
