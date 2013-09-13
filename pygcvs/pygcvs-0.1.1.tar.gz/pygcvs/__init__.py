from __future__ import unicode_literals, print_function

from .parser import GcvsParser

try:
    import ephem
except ImportError:
    ephem = None


__version_info__ = (0, 1, 1, 'final', 0)


def get_version():
    version = '%s.%s' % (__version_info__[0], __version_info__[1])
    if __version_info__[2]:
        version = '%s.%s' % (version, __version_info__[2])
    if __version_info__[3] != 'final':
        version = '%s%s' % (version, __version_info__[3])
        if __version_info__[4]:
            version = '%s%s' % (version, __version_info__[4])
    return version


__version__ = get_version()


def read_gcvs(filename):
    """
    Reads variable star data in `GCVS format`_.

    :param filename: path to GCVS data file (usually ``iii.dat``)

    .. _`GCVS format`: http://www.sai.msu.su/gcvs/gcvs/iii/html/
    """
    with open(filename, 'rb') as fp:
        parser = GcvsParser(fp)
        for star in parser:
            yield star


def dict_to_body(star_dict):
    """
    Converts a dictionary of variable star data to a `Body` instance.

    Requires `PyEphem <http://rhodesmill.org/pyephem/>`_ to be installed.
    """
    if ephem is None:
        raise NotImplementedError("Please install PyEphem in order to use dict_to_body.")
    body = ephem.FixedBody()
    body.name = star_dict['name']
    body._ra = ephem.hours(str(star_dict['ra']))
    body._dec = ephem.degrees(str(star_dict['dec']))
    body._epoch = ephem.J2000
    return body
