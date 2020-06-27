"""Matplotlib utilities"""
import matplotlib.pyplot as plt


def reset_plot(fig):
    """Reset matplotlib figure.

    After plt.show(), matplotlib automatically creates a new figure instance
    which invalidates the existing figure. In an interactive session, this function
    resets figure 'fig' to the next figure instance and associates the existing
    axes to this new figure. This allows iterative development of a plot in
    an interactive session.

    Parameters
    ----------
        fig : existing matplotlib figure
    """
    old_fig = fig
    ax = fig.axes
    fig = plt.figure(fig.number)
    plt.close(old_fig)
    for a in ax:
        a.figure = fig
        fig.add_axes(a)
