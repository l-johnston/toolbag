"""Mentor Graphics utilities"""
import re
from toolbag.common import Error, singleton

LINE_PATTERN = r"^(?P<level>[\.]{1,3})(?P<key>[\w]+) (?P<value>.+)$"


@singleton
class ReadPAF:
    """Read Planes Assignments file (PAF).

    Parameters
    ----------
        file: file, string file name or pathlib.Path

    Returns
    -------
        PAFContainer
    """

    def __init__(self):
        self._rawpaf = []
        self._paf = {}

    def _initialize_attributes(self):
        self._rawpaf = []
        self._paf = {}

    def _parsepaf(self):
        current_key = None
        current_dict = {}
        stack = [(None, self._paf)]
        for i, line in enumerate(self._rawpaf):
            level, key, value = self._parseline(line)
            level = len(level)
            value = value.strip('"')
            try:
                next_line = self._rawpaf[i + 1]
            except IndexError:
                next_level = "."
            else:
                next_level, _, _ = self._parseline(next_line)
            next_level = len(next_level)
            if level == next_level:
                current_dict[key] = value
            elif level < next_level:
                up_key, up_dict = stack.pop()
                if up_key is None:
                    up_dict.update(current_dict)
                else:
                    up_dict[up_key].update(current_dict)
                current_key = f"{key} {value}"
                current_dict = {}
                if up_key is None:
                    up_dict.setdefault(current_key, {})
                else:
                    up_dict[up_key].setdefault(current_key, {})
                stack.append((up_key, up_dict))
                stack.append((current_key, {current_key: {}}))
            else:
                current_dict[key] = value
                down_key, down_dict = stack.pop()
                down_dict[down_key].update(current_dict)
                for _ in range(level - next_level):
                    up_key, up_dict = stack.pop()
                    if up_key is None:
                        up_dict.update(down_dict)
                    else:
                        up_dict[up_key].update(down_dict)
                    down_dict = up_dict
                stack.append((up_key, up_dict))
                current_key = up_key
                current_dict = {}

    def __call__(self, file):
        self._initialize_attributes()
        try:
            self._rawpaf = file.readlines()
        except AttributeError:
            with open(file, "rt", encoding="utf-8") as f:
                self._rawpaf = f.readlines()
        self._parsepaf()
        return PAFContainer(self._paf)

    @staticmethod
    def _parseline(line):
        if (match := re.match(LINE_PATTERN, line)) is not None:
            return match.groups()
        raise Error(f"'{line}' not recognized")

    def __repr__(self):
        return "<function toolbag.read_paf(file)>"


class PAFContainer:
    """PAFContainer.

    Parameters
    ----------
        paf: Planes Assignments file in a dict
    """

    def __init__(self, paf):
        self._paf = paf

    @property
    def file_properties(self):
        """list of file properties"""

        def func(t):
            _, v = t
            return not isinstance(v, dict)

        return dict(filter(func, self._paf.items()))

    @property
    def n_layers(self):
        """int number of layers"""
        layers = list(filter(lambda k: k.startswith("LAYER"), self._paf.keys()))
        return len(layers)

    def layer_properties(self, n):
        """Layer properties for layer n"""
        ld = self._paf[f"LAYER {n}"]
        return dict(filter(lambda t: not isinstance(t[1], dict), ld.items()))

    def net_names(self, n):
        """Net names on layer n"""
        ld = self._paf[f"LAYER {n}"]
        return [
            n.split(" ")[1]
            for n in filter(lambda k: k.startswith("NETNAME"), ld.keys())
        ]

    def net_properties(self, n, name):
        """Net properties for net name on layer n"""
        return self._paf[f"LAYER {n}"][f"NETNAME {name}"]

    def __getitem__(self, item):
        try:
            value = self._paf[item]
        except KeyError:
            if item in ["layers", "LAYERS"]:
                value = [self.layer_properties(n + 1) for n in range(self.n_layers)]
            elif (match := re.match(r"layer (?P<n>[\d]+):nets", item)) is not None:
                n = match.group("n")
                value = [self.net_properties(n, name) for name in self.net_names(n)]
            else:
                raise KeyError(f"'{item}'") from None
        return value

    def __repr__(self):
        return "<PAFContainer>"
