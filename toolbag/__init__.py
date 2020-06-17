"""Toolbag"""
from toolbag.labview_utilities import ReadCSV

__all__ = ["read_csv"]


def __dir__():
    return __all__


read_csv = ReadCSV()
