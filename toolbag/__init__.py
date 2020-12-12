"""`toolbag` is a collection of micellaneous functions used in processing data."""
import numpy as np
from unyt import matplotlib_support, define_unit, Unit, unyt_array
from toolbag.labview_utilities import (
    ReadCSV,
    convert_timestamp,
    write_csv,
    threshold_1d,
    interpolate_1d,
)
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
    "threshold_1d",
    "dBc",
    "interpolate_1d",
    "rf_power",
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
    define_unit("dBc", (1, "dB"))
except RuntimeError:
    pass
dBm = Unit("dBm")
dBc = Unit("dBc")


def rf_power(amplitude, condition="RMS", ref=50):
    """Compute RF power given amplitude

    Parameters
    ----------
    amplitude : float in volt
    condition : str
        condition of measurement {'peak', 'pk-pk', 'RMS'}
    ref : float in ohm
        refernce impedance

    Returns
    -------
    power : float in dBm
    """
    condition = condition.lower()
    if condition in ["pk", "peak"]:
        amplitude /= np.sqrt(2)
    elif condition in ["pk-pk", "peak-to-peak"]:
        amplitude /= 2 * np.sqrt(2)
    elif condition != "rms":
        raise ValueError(f"invalid '{condition}'")
    if isinstance(amplitude, unyt_array):
        amplitude.convert_to_base()
    if isinstance(ref, unyt_array):
        ref.convert_to_base()
    return 10 * np.log10(amplitude ** 2 / ref * 1000) * dBm
