# `toolbag`
Various Python tools for use here at NI

## Installation

    $ git clone git@github.com:l-johnston/toolbag.git
    $ python setup.py

## Documentation
### Reading from LabVIEW generated CSV files
A fairly common workflow is to generate some data in LabVIEW such as from
a hardware acquisition and then complete the processing in Python. It is possible to
export data from an indicator on a LabVIEW front panel by right click 'Export Data to
Excel'. In the following example, we have the array [1e-12, 2e-6, 3e3] s in a CSV file.

    >>> from toolbag import read_csv
    >>> from io import StringIO
    >>> file = StringIO("My data\nTime (s),1p,2u,3k")
    >>> data = read_csv(file)
    >>> file.close()
    >>> data.header
    'My data'
    >>> data.Time
    unyt_array([1.e-12, 2.e-06, 3.e+03], 's')

### Reading from LTSpice text data files
It is possible to read the trace data text files from LTSpice 'File -> Export data as text'.

    >>> from toolbag import read_ltxt
    >>> from io import StringIO
    >>> file = StringIO("time\tV(out)\n0.0e+0\t1.0e+0\n1.0e+0\t2.0e+0")
    >>> data = read_ltxt(file)
    >>> file.close()
    >>> print(data.header)
    time    V(out)
    >>> data.time
    unyt_array([0., 1.], 's')
    >>> data.V_out
    unyt_array([1., 2.], 'V')