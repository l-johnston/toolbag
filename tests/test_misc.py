"""Test miscellaneous functions"""
# pylint:disable=no-name-in-module
# pylint:disable=missing-function-docstring
from unyt import allclose_units, mV
from toolbag import rf_power, dBm


def test_rf_power():
    assert allclose_units(rf_power(223.6 * mV), -0.00026405907247372323 * dBm)
    assert allclose_units(rf_power(1, condition="pk"), 10 * dBm)
    assert allclose_units(rf_power(2, condition="pk-pk"), 10 * dBm)
