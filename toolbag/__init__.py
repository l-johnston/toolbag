"""`toolbag` is a collection of micellaneous functions used in processing data."""
from unyt import matplotlib_support
from toolbag.labview_utilities import ReadCSV, convert_timestamp
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
]


def __dir__():
    return __all__


read_csv = ReadCSV()
read_ltxt = ReadLTxt()
read_ltraw = ReadLTraw()
read_paf = ReadPAF()

matplotlib_support()
matplotlib_support.label_style = "/"
