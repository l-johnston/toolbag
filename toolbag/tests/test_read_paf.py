"""Test read_paf"""
import tempfile
import pytest
from toolbag import read_paf

# pylint: disable=missing-function-docstring
@pytest.fixture(scope="module")
def paf_file():
    def resetptr(file):
        file.seek(0)
        return file

    file = tempfile.TemporaryFile(mode="w+t", encoding="utf-8")
    file.write(
        (
            ".A 1\n"
            ".LAYER 1\n"
            "..B 2\n"
            '..NETNAME "GND"\n'
            "...C 3\n"
            '..NETNAME "VIN"\n'
            "...D 4\n"
            ".LAYER 2\n"
            "..E 5\n"
            '..NETNAME "VOUT"\n'
            "...F 6"
        )
    )
    yield resetptr(file)
    file.close()


def test_fileproperties(paf_file):
    paf = read_paf(paf_file)
    assert paf["A"] == "1"
    assert paf.n_layers == 2
    assert paf.layer_properties(1) == {"B": "2"}
    assert paf.net_names(1) == ["GND", "VIN"]
    assert paf.net_properties(1, "GND") == {"C": "3"}
    assert paf["layers"][1] == {"E": "5"}
    assert paf["layer 2:nets"][0] == {"F": "6"}
