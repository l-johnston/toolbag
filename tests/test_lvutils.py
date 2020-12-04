"""Test LabVIEW utilities"""
import numpy as np
from toolbag.labview_utilities import threshold_1d

# pylint: disable=missing-function-docstring
def test_threshold1d():
    array = np.linspace(0, 1, 5)
    threshold = 0.125
    expected_x = 0.5
    assert threshold_1d(array, threshold) == expected_x
    threshold = 0
    expected_x = 0
    assert threshold_1d(array, threshold) == expected_x
    array = [4, 5, 5, 6]
    threshold = 5
    expected_x = 1
    assert threshold_1d(array, threshold) == expected_x
    threshold = 3
    expected_x = 0
    assert threshold_1d(array, threshold) == expected_x
    threshold = 6
    expected_x = 3
    assert threshold_1d(array, threshold) == expected_x
    threshold = 7
    expected_x = 3
    assert threshold_1d(array, threshold) == expected_x
    array = [2.3, 5.2, 7.8, 7.9, 10.0]
    threshold = 6.5
    expected_x = 1.5
    assert threshold_1d(array, threshold) == expected_x
    threshold = 7
    expected_x = 1.6923077
    assert np.allclose(threshold_1d(array, threshold), expected_x)
    array = [2.3, 5.2, 7.8, 7.9, 9.0, 9.1, 10.3, 12.9, 15.5]
    threshold = 14.2
    expected_x = 7.5
    assert np.allclose(threshold_1d(array, threshold, start_index=5), expected_x)
    threshold = 0
    expected_x = 5
    assert np.allclose(threshold_1d(array, threshold, start_index=5), expected_x)
