"""AWR Microwave Office utilities"""
import re
import numpy as np
from toolbag.common import Error, singleton, DataLabel, DCBase

# regex pattern for mantissa of numeric value
P1 = r"[+-]?[0-9]+\.?[0-9]*"
# pattern for exponent in scientific notation
P2 = "[eE][+-][0-9]+"
NUMBER = f"^(?P<mantissa>{P1})(?P<exponent>{P2})?$"
VALIDIDENTIFIER = "^[a-zA-Z][a-zA-Z0-9_]*$"


@singleton
class ReadTraceData:
    """Read AWR generated text files containing graph trace data

    Parameters
    ----------
    file : file descriptor, str, or path-like
    """

    def _initialize_attributes(self):
        """Initialize attributes for subsequent calls."""
        self._rawtdv = []
        self.header = ""
        self.labels = []
        self.data = []

    def __init__(self):
        self._rawtdv = []
        self.header = ""
        self.labels = []
        self.data = []

    @staticmethod
    def _parsenumber(mantissa, exponent):
        if exponent is None:
            value = float(mantissa) if "." in mantissa else int(mantissa)
        else:
            value = float(mantissa + exponent)
        return value

    def __call__(self, file):
        self._initialize_attributes()
        try:
            for line in file.readlines():
                self._rawtdv.append(line.strip().split("\t"))
        except AttributeError:
            with open(file, "rt", encoding="utf-8") as f:
                for line in f.readlines():
                    self._rawtdv.append(line.strip().split("\t"))
        self.header = " ".join(self._rawtdv[0])
        self.labels = [DataLabel(l, None, None, l) for l in self._rawtdv[0]]
        for line in self._rawtdv[1:]:
            row = []
            for column in line:
                match = re.match(NUMBER, column)
                if match is None:
                    raise Error(f"Non numeric value '{column}' found in data array")
                row.append(self._parsenumber(*match.groups()))
            self.data.append(row)
        self.data = np.transpose(self.data)
        return DataContainer(self.data, self.labels, header=self.header)

    def __dir__(self):
        return list(filter(lambda s: not s.startswith("_"), super().__dir__()))

    def __repr__(self):
        return "<function toolbag.read_awr_tracedata(file)>"


class DataContainer(DCBase):
    """DataContainer holds the parsed content of the CSV file.

    DataContainer is a hybrid container with attribute, mapping and sequence access
    to the underlying CSV content.

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

    def _parselabels(self):
        """Parse labels"""
        labels = [axis.label for axis in self._labels]
        for axis in self._labels:
            unique = labels.count(axis.label) == 1
            valid = re.match(VALIDIDENTIFIER, axis.label) is not None
            if unique:
                if valid:
                    self._valid_identifiers.append(axis.label)
                else:
                    self._valid_identifiers.append(f'["{axis.label}"]')
            self.legends.append(axis.legend)

    def __getitem__(self, item):
        try:
            return self._item_cache[item]
        except KeyError:
            labels = [axis.label for axis in self._labels]
            names = [axis.name for axis in self._labels]
            if isinstance(item, int):
                self._item_cache[item] = self._data[item]
            elif isinstance(item, str):
                try:
                    i = names.index(item)
                except ValueError:
                    try:
                        i = labels.index(item)
                    except ValueError:
                        raise KeyError(f"{item}") from None
                self._item_cache[item] = self._data[i]
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

    @property
    def columns(self):
        """Return list of column labels"""
        return [dl.label for dl in self._labels]
