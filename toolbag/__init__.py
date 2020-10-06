"""`toolbag` is a collection of micellaneous functions used in processing data."""
from unyt import matplotlib_support, define_unit, Unit
from toolbag.labview_utilities import ReadCSV, convert_timestamp, write_csv
from toolbag.ltspice_utilities import ReadLTxt, ReadLTraw
from toolbag.mentor_utilities import ReadPAF
from toolbag.mpl_utilities import reset_plot

__all__ = [
    "read_csv",
    "convert_timestamp",
    "read_ltxt",
    "read_ltraw",
    "read_paf",
    "reset_plot",
    "write_csv",
    "dBm",
]


def __dir__():
    return __all__


read_csv = ReadCSV()
read_ltxt = ReadLTxt()
read_ltraw = ReadLTraw()
read_paf = ReadPAF()

matplotlib_support()
matplotlib_support.label_style = "/"
try:
    define_unit("dBm", (1, "dB"))
except RuntimeError:
    pass
dBm = Unit("dBm")
