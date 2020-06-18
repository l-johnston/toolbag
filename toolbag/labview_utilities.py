"""LabVIEW utilities."""
import re
from collections import namedtuple
from enum import Enum
from datetime import datetime, timedelta, timezone
import numpy as np
from unyt import matplotlib_support, define_unit, unyt_array

__all__ = ["ReadCSV", "convert_timestamp"]

matplotlib_support()
define_unit("dBm", (1, "dB"))


class Error(Exception):
    """General exception class for this module."""


P1 = r"[+-]?[0-9]+\.?[0-9]*|NaN|Inf|-Inf"
P2 = "[eE][+-][0-9]+"
# LabVIEW SI prefixes only multiples of 10**3 and u means µ
SI_PREFIXES = "yzafpnum kMGTPEZY"
P3 = f"[{SI_PREFIXES}]"
NUMBER = re.compile(f"^(?P<mantissa>{P1})(?P<exponent>{P2}|{P3})?$")
DATALABEL = re.compile(
    r"^(?P<name>[\w]+)( )?(?P<unit>\(.+\))?( - )?(?P<legend>[\w ]+)?$"
)
VALIDIDENTIFIER = re.compile("^[a-zA-Z][a-zA-Z0-9_]*$")
DataLabel = namedtuple("DataLabel", ["label", "name", "unit", "legend"])


class ArrayOrientation(Enum):
    """Array orientation enum"""

    ROW = 0
    COLUMN = 1
    UNKNOWN = 2


class DataContainer:
    """DataContainer"""

    def __init__(self, data, header, labels):
        self._data = data
        self.header = header
        self._labels = labels
        self._valid_identifiers = []
        self._item_cache = {}
        self.legends = []
        self._parselabels()
        self._objstr = str(self.__class__).split(".")[-1].strip("'>")

    def _parselabels(self):
        """Parse labels"""
        names = [axis.name for axis in self._labels]
        for axis in self._labels:
            unique = names.count(axis.name) == 1
            valid = re.match(VALIDIDENTIFIER, axis.name) is not None
            if unique and valid:
                self._valid_identifiers.append(axis.name)
            self.legends.append(axis.legend)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"'{self._objstr}' object has no attribute '{name}'"
            ) from None

    def __getitem__(self, item):
        try:
            return self._item_cache[item]
        except KeyError:
            labels = [axis.label for axis in self._labels]
            names = [axis.name for axis in self._labels]
            units = [axis.unit for axis in self._labels]
            if isinstance(item, int):
                self._item_cache[item] = unyt_array(
                    self._data[item], units[item], name=names[item]
                )
            elif isinstance(item, str):
                try:
                    i = names.index(item)
                except ValueError:
                    try:
                        i = labels.index(item)
                    except ValueError:
                        raise KeyError(f"{item}") from None
                self._item_cache[item] = unyt_array(
                    self._data[i], units[i], name=names[i]
                )
            else:
                raise KeyError(f"{item}") from None
            return self._item_cache[item]
        except TypeError:
            if isinstance(item, slice):
                rows = self._data.shape[0]
                start = item.start if item.start is not None else 0
                stop = item.stop if item.stop is not None else rows
                step = item.step if item.step is not None else 1
                return [self[i] for i in range(start, stop, step)]
            raise KeyError(f"{item}") from None

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


class ReadCSV:
    """Read text files containing comma-separted values (CSV).

    ReadCSV is a singleton class instantiated as `read_csv` at the package level and
    is callable. This reader supports a number of scenarios from a single array with
    no header or data label to 2D arrays with multi-line header and data labels. It will
    automatically determine the orientation of a 2D array if data labels are present.

    The optional header can span multiple lines with the only constranit that a line
    can't start with numerical values such as '1,1,some text...'.

    A data label describes one axis (row or column) of the data. The format is
    '<name> (<unit>) - <legend>' where <unit> and <legend> are optional. Place the
    unit expression in parentheses and indicate the presence of the legend with ' - '.

    The array consists of real, floating point values with supported formats of
    floating point, scientific and SI prefixes (e.g. 1.0p = 1.0E-12). The values
    'NaN', 'Inf' and '-Inf' are also supported.

    Note:
        Complex numbers are not yet supported.

    Parameters
    ----------
        file: string file name

    Attributes
    ----------
        data: Numpy ndarray of numerical values in the file
        header: string of header information at the top of the file if present
        labels: list of DataLabel for data labels if present

    Returns
    -------
        ndarray if no data labels are present. DataContainer if data labels are
        present.
    """

    _instantiated = False

    def _initialize_attributes(self):
        """Initialize attributes for subsequent calls."""
        self._rawcsv = []
        self._array_row_start = 0
        self._array_column_start = 0
        self._orientation = ArrayOrientation.UNKNOWN
        self.header = []
        self.labels = []
        self.data = []

    def __init__(self):
        if not ReadCSV._instantiated:
            self._rawcsv = []
            self._array_row_start = 0
            self._array_column_start = 0
            self._orientation = ArrayOrientation.UNKNOWN
            self.header = []
            self.labels = []
            self.data = []
            ReadCSV._instantiated = True
        else:
            raise Error("ReadCSV is a singleton class")

    @staticmethod
    def _parsenumber(mantissa, exponent):
        """Parse number"""
        if exponent is None:
            value = float(mantissa)
        else:
            if exponent.startswith("e") or exponent.startswith("E"):
                value = float(mantissa + exponent)
            else:
                index = SI_PREFIXES.index(exponent)
                value = float(mantissa) * 10 ** (-24 + 3 * index)
        return value

    def _findarray(self):
        """Find where the numeric data is located and parse into numbers"""
        # The CSV file is assummed to be a numeric array with optional header lines
        # and data labels. Here are the rules:
        # 1. Numeric values are real floating point values
        # 2. Zero or more header lines where last cell is non-numeric
        # 3. Data array is contiguous block oriented in rows or columns
        # 4. Number of data labels matches number of columns if column oriented or rows
        #    if row oriented.
        # 5. Data label format is '<name> (<unit>) - <legend>' where unit and legend
        #    are optional.
        # 6. If data labels are present, read_csv returns DataContainer.
        self._array_row_start = 0
        self._array_column_start = 0
        for line in self._rawcsv:
            if re.match(NUMBER, line[-1]) is None:
                self._array_row_start += 1
                continue
            if re.match(NUMBER, line[0]) is None:
                self._array_column_start = 1
            row = []
            for column in line[self._array_column_start :]:
                match = re.match(NUMBER, column)
                if match is None:
                    raise Error(f"Non numeric value '{column}' found in data array")
                row.append(ReadCSV._parsenumber(*match.groups()))
            self.data.append(row)
        self.data = np.asarray(self.data)

    def _parselabels(self, labels):
        """Parse labels"""
        for label in labels:
            match = re.match(DATALABEL, label)
            if match is not None:
                fields = ["name", "unit", "legend"]
                values = []
                for field in fields:
                    value = match.group(field)
                    if field == "unit" and value is not None:
                        value = value.strip("()")
                    values.append(value)
                self.labels.append(DataLabel(label, *values))
            else:
                self.labels.append(DataLabel(label, *[None] * 3))

    def _parseheader(self):
        """Parse header"""
        if self._array_row_start > 0:
            self.header = self._rawcsv[: self._array_row_start]
        if self._array_column_start > 0:
            labels = [line[0] for line in self._rawcsv[self._array_row_start :]]
            if len(labels) == self.data.shape[0]:
                self._orientation = ArrayOrientation.ROW
                self._parselabels(labels)
        elif len(self.header) > 0:
            labels = self.header[-1]
            if len(labels) == self.data.shape[1]:
                self.header.pop()
                self._orientation = ArrayOrientation.COLUMN
                self._parselabels(labels)
        self.header = "\n".join(map(",".join, self.header))

    def __call__(self, file):
        self._initialize_attributes()
        with open(file, "rt", encoding="utf-8-sig") as f:
            for line in f.readlines():
                self._rawcsv.append(line.strip().split(","))
        self._findarray()
        self._parseheader()
        if self._orientation == ArrayOrientation.UNKNOWN:
            rows, columns = self.data.shape
            if rows == 1 or columns == 1:
                self.data = self.data.reshape((self.data.size,))
            return self.data
        if self._orientation == ArrayOrientation.COLUMN:
            self.data = self.data.T
        return DataContainer(self.data, self.header, self.labels)

    def __dir__(self):
        return list(filter(lambda s: not s.startswith("_"), super().__dir__()))

    def __repr__(self):
        return "<function toolbag.read_csv(file)>"


def convert_timestamp(timestamp):
    """Convert LabVIEW's timestamp to datetime.

    Parameters
    ----------
        timestamp: float seconds in LabVIEWS's epoch and UTC.
            Also supports ndarray of timestamps.

    Returns
    -------
        date and time in machine's local time zone and time zone naive
        datetime if timestamp is scalar or ndarray of np.datetime64 if array
    """
    # LabVIEW's timestamp is UTC
    def _convert(ts):
        dt = datetime(1904, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=ts)
        return dt.astimezone().replace(tzinfo=None)

    if isinstance(timestamp, np.ndarray):
        return np.vectorize(_convert, otypes=[np.datetime64])(timestamp)
    return _convert(timestamp)