# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
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
    fs = 5e9  # S/s
    n_samples = 10000
    f = 125e6
    t = np.linspace(0, n_samples / fs, n_samples, endpoint=False)
    y = np.sin(2 * np.pi * f * t)
    result = extract_singletone(y, fs, approx_freq=125e6)
    expected = (125000000.00062592, 1.0000002210999446)
    assert np.allclose(result, expected)
