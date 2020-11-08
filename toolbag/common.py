"""Common definitions"""
import functools
from collections import namedtuple
from enum import Enum
import numpy as np


class Error(Exception):
    """General exception class for this module."""


def singleton(cls):
    """Decorator function to make class 'cls' a singleton"""

    @functools.wraps(cls)
    def single_cls(*args, **kwargs):
        if single_cls.instance is None:
            single_cls.instance = cls(*args, **kwargs)
        return single_cls.instance

    single_cls.instance = None
    return single_cls


VALIDIDENTIFIER = "^[a-zA-Z][a-zA-Z0-9_]*$"
DataLabel = namedtuple("DataLabel", ["label", "name", "unit", "legend"])


class ArrayOrientation(Enum):
    """Array orientation enum"""

    ROW = 0
    COLUMN = 1
    UNKNOWN = 2


class DCBase:
    """DataContainer holds the parsed content of a text or CSV file.

    DataContainer is a hybrid container with attribute, mapping and sequence access
    to the underlying content.

    Parameters
    ----------
        data: ndarray
        header: string
        labels: list of DataLabel

    Attributes
    ----------
        header: string
        legends: list of strings
        <name>: unyt_array
    """

    def __init__(self, data, labels, *, header=""):
        self._data = data
        self.header = header
        self._labels = labels
        self._valid_identifiers = []
        self._item_cache = {}
        self.legends = []
        self._parselabels()
        self._objstr = str(self.__class__).split(".")[-1].strip("'>")

    def _parselabels(self):
        raise NotImplementedError

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"'{self._objstr}' object has no attribute '{name}'"
            ) from None

    def __getitem__(self, item):
        raise NotImplementedError

    def __len__(self):
        return len(self._data)

    def __setitem__(self, item, value):
        raise TypeError(f"'{self._objstr}' does not support item assignment")

    def __delitem__(self, item):
        raise TypeError(f"'{self._objstr}' does not support item deletion")

    def __contains__(self, item):
        labels = [axis.label for axis in self._labels]
        names = [axis.name for axis in self._labels]
        return item in labels + names

    def __dir__(self):
        attrs = list(filter(lambda s: not s.startswith("_"), super().__dir__()))
        return sorted(attrs + self._valid_identifiers)

    def __repr__(self):
        return repr(self._data)


SIPREFIXES = {
    -24: "y",
    -21: "z",
    -18: "a",
    -15: "f",
    -12: "p",
    -9: "n",
    -6: "µ",
    -3: "m",
    0: "",
    3: "k",
    6: "M",
    9: "G",
    12: "T",
    15: "P",
    18: "E",
    21: "Z",
    24: "Y",
}


def format_as_si(value, unit=None, precision=3):
    """Format value using SI prefixes to improve readability

    Parameters
    ----------
    value : numeric
        value to be scaled to be between (-1000, 1000)
    unit : str
        SI unit symbol such as "m"
    precision : int
        number of decimal places for scaled value

    Returns
    -------
    scaled_value : str
    """
    si_pwr = 0
    sign = np.sign(value)
    value = np.abs(value)
    if value != 0:
        log_value = np.log10(value)
        si_pwr = 3 * np.floor(log_value / 3)
        value = 10 ** (log_value - si_pwr)
    value *= sign
    fractional, _ = np.modf(value)
    if np.isclose(0, fractional, atol=10 ** (-1 * (precision + 1))):
        precision = 0
    if unit is None:
        result = f"{value:.{precision}f}{SIPREFIXES[int(si_pwr)]}"
    else:
        result = f"{value:.{precision}f} {SIPREFIXES[int(si_pwr)]}{unit}"
    return result
