import numpy as np
from toolbag import extract_singletone


def test_extract_singletone():
    fs = 5000  # S/s
    f = 2000.001  # Hz
    T = 2  # s
    t = np.arange(0, T, 1 / fs)
    y = 1.101 * np.sin(2 * np.pi * f * t)
    result = extract_singletone(y, fs)
    expected = (2000.0010475648544, 1.101000569162536)
    assert np.allclose(result, expected)
