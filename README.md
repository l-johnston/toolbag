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
