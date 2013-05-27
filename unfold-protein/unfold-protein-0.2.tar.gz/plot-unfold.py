#!/usr/bin/env python
#
# Copyright

import os.path as _os_path

import h5py as _h5py
import matplotlib as _matplotlib
import matplotlib.pyplot as _matplotlib_pyplot


FIGURE = _matplotlib_pyplot.figure()


class BadDataError (ValueError):
    pass


def convert_to_png(filename):
    with _h5py.File(filename) as f:
        png = filename + '.png'
        if not _os_path.isfile(png):
            FIGURE.clear()
            axes = FIGURE.add_subplot(1, 1, 1)
            axes.hold(True)
            try:
                z = f['approach']['z']
                d = f['approach']['deflection']
            except KeyError, e:
                raise BadDataError(e)
            plot = axes.plot(z, d, '.')
            try:
                z = f['unfold']['z']
                d = f['unfold']['deflection']
            except KeyError, e:
                raise BadDataError(e)
            plot = axes.plot(z, d, '.')
            axes.autoscale(tight=True)
            FIGURE.savefig(png)


if __name__ == '__main__': 
    import sys as _sys

    for filename in _sys.argv[1:]:
        try:
            convert_to_png(filename)
        except BadDataError:
            print('Error converting {}'.format(filename))
