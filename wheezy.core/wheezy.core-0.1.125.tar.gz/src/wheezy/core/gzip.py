""" One-shot compression and decompression.
"""

from wheezy.core.comp import BytesIO
from wheezy.core.comp import GzipFile


def compress(data, compresslevel=9):
    """ Compress data in one shot.
    """
    s = BytesIO()
    f = GzipFile(fileobj=s, mode='wb', mtime=0)
    f.write(data)
    f.close()
    return s.getvalue()


def decompress(data):
    """ Decompress data in one shot.
    """
    return GzipFile(fileobj=BytesIO(data), mode='rb').read()
