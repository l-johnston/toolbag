"""Extract single tone

Quadratic Interpolation of Spectral Peaks
https://ccrma.stanford.edu/~jos/sasp/Quadratic_Interpolation_Spectral_Peaks.html
"""
import numpy as np


def gaussianwindow(x, sigma=0.2):
    """Gaussian FFT window

    Parameters
    ----------
    sigma : float
    """
    i = np.arange(len(x))
    m = (len(x) - 1) / 2
    return x * np.exp(-((i - m) ** 2) / (2 * (sigma * len(x)) ** 2))


def extract_singletone(x, fs):
    """Extract single tone from a time domain signal

    Finds the frequency and amplitude of the largest amplitude tone in the
    time domain signal.

    Parameters
    ----------
    x : array-like
        time domain signal
    fs : float
        sample frequency

    Returns
    -------
    single_tone : 2-tuple of float
        estimated parameters of single tone (frequency, amplitude)
    """
    n_samples = len(x)
    mid = n_samples // 2
    xw = gaussianwindow(x)
    coherent_gain = gaussianwindow(np.ones(n_samples)).sum() / n_samples
    spectrum = np.abs(np.fft.fft(xw)[:mid])
    tone_bin = spectrum.argmax()
    a = np.log10(spectrum[tone_bin - 1])
    b = np.log10(spectrum[tone_bin])
    g = np.log10(spectrum[tone_bin + 1])
    p = (a - g) / (2 * (a - 2 * b + g))
    f_est = (tone_bin + p) * fs / n_samples
    amp_est = 10 ** ((b - (a - g) * p / 4) - np.log10(n_samples * coherent_gain / 2))
    return (f_est, amp_est)
