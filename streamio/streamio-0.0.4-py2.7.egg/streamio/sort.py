# Module:   sort
# Date:     18th December 2012
# Author:   James Mills, j dot mills at griffith dot edu dot au

"""sort"""


import heapq
from json import dumps


from py._path.local import LocalPath
from progress.bar import ChargingBar
from funcy import count, first, ichunks, ifilter, imap


from .stream import jsonstream


class ProgressBar(ChargingBar):
    """Customized Progress Bar"""

    suffix = "%(index)d/%(max)d %(percent).1f%% - Rate: %(avg).1fs ETA: %(eta)s"
    message = "Processing"


def merge(*iterables, **kwargs):
    """Take a list of ordered iterables; return as a single ordered generator.

    :param key:     function, for each item return key value

    Directly borrowed from: http://stackoverflow.com/questions/5023266/merge-join-two-generators-in-python
    """

    key = kwargs.get("key", lambda x: x)

    _heapify = heapq.heapify
    _heappop = heapq.heappop
    _StopIteration = StopIteration
    _heapreplace = heapq.heapreplace

    # preprocess iterators as heapqueue
    h = []
    for itnum, it in enumerate(map(iter, iterables)):
        try:
            next = it.next
            data = next()
            keyval = key(data)
            h.append([keyval, itnum, data, next])
        except _StopIteration:
            pass
    _heapify(h)

    # process iterators in ascending key order

    while True:
        try:
            while True:
                keyval, itnum, data, next = s = h[0]  # get smallest-key value
                                                      # raises IndexError when h is empty
                yield data

                # load replacement value from same iterator
                s[2] = data = next()        # raises StopIteration when exhausted
                s[0] = key(s[2])
                _heapreplace(h, s)          # restore heap condition
        except _StopIteration:
            _heappop(h)                     # remove empty iterator
        except IndexError:
            return


def mergesort(filename, output=None, key=None, maxitems=1e6):
    """Given an input file sort it by performing a merge sort on disk.

    :param filename: Either a filename as a ``str`` or a ``py._path.local.LocalPath`` instance.
    :type filename:  ``str`` or ``py._path.local.LocalPath``

    :param output: An optional output filename as a ``str`` or a ``py._path.local.LocalPath`` instance.
    :type output:  ``str`` or ``py._path.local.LocalPath`` or ``None``

    :param key: An optional key to sort the data on.
    :type key:  ``function`` or ``None``

    :param maxitems: Maximum number of items to hold in memory at a time.
    :type maxitems:  ``int``

    This uses ``py._path.local.LocalPath.make_numbered_dir`` to create temporry scratch space to work
    with when splitting the input file into sorted chunks. The mergesort is processed iteratively in-memory
    using the ``~merge`` function which is almost identical to ``~heapq.merge`` but adds in the support of
    an optional key function.
    """

    p = filename if isinstance(filename, LocalPath) else LocalPath(filename)
    output = p if output is None else output
    key = key if key is not None else lambda x: x

    scratch = LocalPath.make_numbered_dir(prefix="mergesort-")

    nlines = sum(1 for line in p.open("r"))

    # Compute a reasonable chunksize < maxitems
    chunksize = first(ifilter(lambda x: x < maxitems, imap(lambda x: nlines / (2**x), count(1))))

    # Split the file up into n sorted files
    bar = ProgressBar("Split/Sorting Data", max=(nlines / chunksize))
    for i, items in enumerate(ichunks(chunksize, jsonstream(p))):
        with scratch.ensure("{0:d}.json".format(i)).open("w") as f:
            f.write("\n".join(map(dumps, sorted(items, key=key))))
        bar.next()
    bar.finish()

    q = scratch.listdir("*.json")
    with output.open("w") as f:
        bar = ProgressBar("Merge/Sorting Data", max=nlines)
        for item in merge(*imap(jsonstream, q)):
            f.write("{0:s}\n".format(dumps(item)))
            bar.next()
        bar.finish()

__all__ = ("merge", "mergesort",)
