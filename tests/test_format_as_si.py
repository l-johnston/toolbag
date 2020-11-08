from toolbag import format_as_si


def test_some_values():
    assert format_as_si(0, "m") == "0 m"
    assert format_as_si(999, "Hz") == "999 Hz"
    assert format_as_si(10000, "Hz") == "10 kHz"
    assert format_as_si(0.001, "m") == "1 mm"
    assert format_as_si(1.000001, "m", 6) == "1.000001 m"
