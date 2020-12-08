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


def extract_singletone(x, fs, approx_freq=None, search=0.05):
    """Extract single tone from a time domain signal

    Finds the frequency and amplitude of the largest amplitude tone in the
    time domain signal.

    Parameters
    ----------
    x : array-like
        time domain signal
    fs : float
        sample frequency
    approx_freq : float
        approximate frequency to search for
        if None, find the maximum amplitude
    search : float
        search ± percentage around approx_freq if given

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
    fmin_bin = 0
    fmax_bin = mid
    if approx_freq is not None:
        fmin = approx_freq * (1 - search)
        fmax = approx_freq * (1 + search)
        df = fs / n_samples
        fmin_bin = np.floor(fmin / df).astype(int)
        fmin_bin = 0 if fmin_bin < 0 else fmin_bin
        fmax_bin = np.ceil(fmax / df).astype(int) + 1
        fmax_bin = n_samples if fmax_bin > mid else fmax_bin
    tone_bin = fmin_bin + spectrum[fmin_bin:fmax_bin].argmax()
    a = np.log10(spectrum[tone_bin - 1])
    b = np.log10(spectrum[tone_bin])
    g = np.log10(spectrum[tone_bin + 1])
    p = (a - g) / (2 * (a - 2 * b + g))
    f_est = (tone_bin + p) * fs / n_samples
    amp_est = 10 ** ((b - (a - g) * p / 4) - np.log10(n_samples * coherent_gain / 2))
    return (f_est, amp_est)
