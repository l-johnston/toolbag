"""Test reset_plot"""
import matplotlib.pyplot as plt
from toolbag import reset_plot

plt.ion()

# pylint: disable = missing-function-docstring
def test_reset_plot():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3])
    plt.close()
    reset_plot(fig)
    assert id(ax) == id(fig.gca())
    plt.close()
