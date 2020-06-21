"""LTSpice utilities"""
import re
import numpy as np
from unyt import matplotlib_support, Unit, unyt_array
from unyt.exceptions import UnitParseError
from toolbag.common import singleton, VALIDIDENTIFIER, DataLabel, DCBase

__all__ = ["ReadLTxt"]

matplotlib_support()


class Error(Exception):
    """General exception class for this module."""


ATOMICLABEL = r"time|Freq.|frequency|freq|omega|V\(\w+\)|I\(\w+\)"
SIMPLE_EXPRESSION = r"^([VI])\(([\w]+)\)$"


@singleton
class ReadLTxt:
    """Read LTSpice text files of trace data.

    In LTSpice it is possible to export trace data by 'File -> Export data as text'.

    Parameters
    ----------
        file: file, string file name or pathlib.Path

    Returns
    -------
        DataContainer
    """

    def __init__(self):
        self._rawtxt = []
        self._labels = []
        self._units = []
        self._traces = []
        self._data = []

    def _initialize_attributes(self):
        """Initialize attributes for subsequent calls."""
        self._rawtxt = []
        self._labels = []
        self._units = []
        self._traces = []
        self._data = []

    @staticmethod
    def _parsenumber(value):
        ispolar = value.startswith("(")
        values = [v.strip("dB°") for v in value.strip("()").split(",")]
        iscomplex = len(values) == 2
        return (iscomplex, ispolar)

    def _parseheader(self):
        # There is only one line of header text with tab-delimited column data labels
        # First column is the x-axis followed by one or more traces.
        # Possible trace names are {"time", "Freq.", "frequency", "freq", "omega",
        # "V(<node>)", "I(<node>)"} and math expressions there of. A y-axis column
        # can be scalar or complex with numeric values in exponential floating point
        # format. Complex quantities can be polar (dB_deg) or cartesian (re_im).
        for label, value in zip(*self._rawtxt[:2]):
            expr = label
            updated_label = label
            for atom in re.findall(ATOMICLABEL, label):
                if atom == "time":
                    expr = expr.replace(atom, "s")
                elif atom in ["Freq.", "frequency", "freq"]:
                    expr = expr.replace(atom, "Hz")
                    updated_label = label.replace(atom, "frequency")
                elif atom.startswith("V"):
                    expr = expr.replace(atom, "V")
                elif atom.startswith("I"):
                    expr = expr.replace(atom, "A")
                else:
                    pass
            try:
                unit = Unit(expr).get_base_equivalent()
            except UnitParseError:
                unit = "dimensionless"
            if re.match(VALIDIDENTIFIER, updated_label) is not None:
                name = updated_label
            elif (match := re.match(SIMPLE_EXPRESSION, updated_label)) is not None:
                name = "_".join(match.groups())
            else:
                name = None
            iscomplex, ispolar = self._parsenumber(value)
            if not iscomplex:
                self._labels.append(DataLabel(updated_label, name, unit, None))
            elif not ispolar:
                self._labels.append(DataLabel(updated_label, name, [unit, unit], None))
            else:
                self._labels.append(
                    DataLabel(updated_label, name, ["dB", "degree"], None)
                )

    def _makearray(self):
        data = []
        for line in self._rawtxt[1:]:
            row = []
            for column in line:
                values = [float(v.strip("dB°")) for v in column.strip("()").split(",")]
                row.append(complex(*values))
            data.append(row)
        self._data = np.asarray(data).T

    def __call__(self, file):
        self._initialize_attributes()
        try:
            for line in file.readlines():
                self._rawtxt.append(line.strip().split("\t"))
        except AttributeError:
            try:
                f = open(file, "rt", encoding="utf-8")
                for line in f.readlines():
                    self._rawtxt.append(line.strip().split("\t"))
            except UnicodeDecodeError:
                f.close()
                f = open(file, "rt", encoding="cp1252")
                for line in f.readlines():
                    self._rawtxt.append(line.strip().split("\t"))
            f.close()
        self._parseheader()
        self._makearray()
        return DataContainer(self._data, self._labels)

    def __dir__(self):
        return list(filter(lambda s: not s.startswith("_"), super().__dir__()))

    def __repr__(self):
        return "<function toolbag.read_ltxt(file)>"


class DataContainer(DCBase):
    """DataContainer holds the parsed content of the CSV file.

    DataContainer is a hybrid container with attribute, mapping and sequence access
    to the underlying CSV content.

    Parameters
    ----------
        data: ndarray
        labels: list of DataLabel
        header: string

    Attributes
    ----------
        header: string
        legends: list of strings
        <name>: unyt_array
    """

    def _parselabels(self):
        labels = [axis.label for axis in self._labels]
        names = [axis.name for axis in self._labels]
        self.header = "\t".join(labels)
        self.legends = labels
        self._valid_identifiers = list(filter(lambda n: n is not None, names))

    def __getitem__(self, item):
        try:
            return self._item_cache[item]
        except KeyError:
            if isinstance(item, int):
                i = item
                try:
                    self._labels[i]
                except IndexError:
                    raise IndexError(f"{self._objstr} index out of range") from None
            else:
                labels = [axis.label for axis in self._labels]
                names = [axis.name for axis in self._labels]
                try:
                    i = labels.index(item)
                except ValueError:
                    try:
                        i = names.index(item)
                    except ValueError:
                        raise KeyError(f"{item}") from None
            axis = self._labels[i]
            if not isinstance(axis.unit, list):
                self._item_cache[item] = unyt_array(
                    self._data[i].real, axis.unit, name=axis.name
                )
            else:
                self._item_cache[item] = [
                    unyt_array(self._data[i].real, axis.unit[0], name=axis.name),
                    unyt_array(self._data[i].imag, axis.unit[1], name=axis.name),
                ]
            return self._item_cache[item]
        except TypeError:
            if isinstance(item, slice):
                rows = self._data.shape[0]
                start = item.start if item.start is not None else 0
                stop = item.stop if item.stop is not None else rows
                step = item.step if item.step is not None else 1
                return [self[i] for i in range(start, stop, step)]
            raise KeyError(f"{item}") from None
