# pylint: disable-msg=W0212
# W0212 Access to a protected member _headers of a client class

"""metadata.

Author   : Rob Cakebread <cakebread @ gmail>

License  : BSD (See COPYING)

Desc     : Return metadata for Python distribution installed by setuptools
           in a dict

           Note: The metadata uses RFC 2822-based message documents.

"""

import email


def get_metadata(dist):
    """Return dictionary of metadata for given dist.

    @param dist: distribution
    @type dist: pkg_resources Distribution object

    @returns: dict of metadata or None

    """
    if not dist.has_metadata('PKG-INFO'):
        return

    try:
        metadata = {}
        msg = email.message_from_string(dist.get_metadata('PKG-INFO'))
        for header in [l for l in msg._headers]:
            metadata[header[0]] = header[1]
    except IOError:
        # no egg-file, installed using other package manager
        pass
    return metadata
