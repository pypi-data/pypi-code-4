__all__ = [
    "in_polygon",
    "hash_ndarray",
    "NDArrayDict",
    ]


from collections.abc import MutableMapping
from hashlib import sha1
import logging

import numpy as np

log = logging.getLogger(__name__)


def in_polygon(points, vertices):
    from matplotlib.path import Path
    v = np.empty((vertices.size, 2))
    v[:, 0] = vertices.real
    v[:, 1] = vertices.imag
    path = Path(v)
    p = np.empty((points.size, 2))
    p[:, 0] = points.real
    p[:, 1] = points.imag
    return path.contains_points(p)


def hash_ndarray(array):
    h = sha1(array.view(np.uint8))
    return h.digest()


class NDArrayDict(MutableMapping):

    def __init__(self):
        self.backing_dict = dict()

    def __getitem__(self, array):
        return self.backing_dict.__getitem__(hash_ndarray(array))

    def __setitem__(self, array, item):
        self.backing_dict.__setitem__(hash_ndarray(array), item)

    def __delitem__(self, array):
        self.backing_dict.__delitem__(hash_ndarray(array))

    def __iter__(self):
        return self.backing_dict.__iter__()

    def __len__(self):
        return self.backing_dict.__len__()
