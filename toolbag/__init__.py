"""`toolbag` is a collection of micellaneous functions used in processing data."""
from unyt import matplotlib_support, define_unit, Unit
from toolbag.labview_utilities import ReadCSV, convert_timestamp, write_csv
from toolbag.ltspice_utilities import ReadLTxt, ReadLTraw
from toolbag.mentor_utilities import ReadPAF
from toolbag.mpl_utilities import reset_plot
from toolbag.common import format_as_si
from toolbag.version import __version__
from toolbag.extract_singletone import extract_singletone
from toolbag.awr_utilities import ReadTraceData

__all__ = [
    "__version__",
    "read_csv",
    "convert_timestamp",
    "read_ltxt",
    "read_ltraw",
    "read_paf",
    "reset_plot",
    "write_csv",
    "dBm",
    "format_as_si",
    "extract_singletone",
    "read_awr_tracedata",
]


def __dir__():
    return __all__


read_csv = ReadCSV()
read_ltxt = ReadLTxt()
read_ltraw = ReadLTraw()
read_paf = ReadPAF()
read_awr_tracedata = ReadTraceData()

matplotlib_support()
matplotlib_support.label_style = "/"
try:
    define_unit("dBm", (1, "dB"))
except RuntimeError:
    pass
dBm = Unit("dBm")
