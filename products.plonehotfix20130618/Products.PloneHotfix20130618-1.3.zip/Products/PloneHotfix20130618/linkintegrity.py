from zExceptions import BadRequest
import zlib

from plone.app.linkintegrity import utils


def decompress(data, maxsize=262144):

    dec = zlib.decompressobj()
    data = dec.decompress(data, maxsize)
    if dec.unconsumed_tail:
        raise BadRequest
    del dec

    return data


utils.decompress = decompress
