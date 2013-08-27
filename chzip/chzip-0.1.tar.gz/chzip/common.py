#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Common classes and utilities functions"""

# Needed for abstract classes / methods
from abc import ABCMeta, abstractmethod

# Support Python 2 and 3
try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Python 2
    from urllib2 import urlopen


import os
import datetime


class Downloader:
    """The parent (abstract) class of Downloaders. Can NOT be instantiated.

    Subclasses can redefine :py:const:`DEFAULT_RES_DIRNAME`.
    """

    __metaclass__ = ABCMeta

    # Can be redefined if wished
    DEFAULT_RES_DIRNAME = 'res'
    """The name of the directory that will contain the downloaded files."""

    @abstractmethod
    def download_and_unpack(self, download_dir):
        """Download and unpack resources files related to this downloader.
        This method should probably not be called on a UI thread or similar
        because this can be a long-running task."""
        pass

    @abstractmethod
    def upgrade_and_unpack(self, download_dir):
        """Similar to :py:meth:`chzip.common.Downloader.download_and_unpack`
        but does not do anything if files are up-to-date and does not let you
        with a broken installation in case of a download or unpacking failure.
        """
        pass

    # Download the file at the specified URL, and return its path afterwards
    # TODO: Add verbose parameter (default value: True) with a
    # progressbar2-like interface. (Unfortunately, progressbar2 is
    # not compatible with Python 3)
    def _download(self, url, abs_download_dir, filename):
        input_f = urlopen(url)

        output_path = os.path.join(abs_download_dir, filename)
        output_f = open(output_path, 'wb')
        output_f.write(input_f.read())
        output_f.close()
        return output_path

    # Method to be optionally implemented by subclasses
    def _is_up_to_date(self, abs_resource_file):
        return True

    # Returns the datetime of the last modification of a file
    @staticmethod
    def _get_lastchange_datetime(path):
        return datetime.datetime.fromtimestamp(os.path.getmtime(path))


class Locality:
    """A locality is the name of a town, village or any "string"
    that goes after the ZIP code in the address.
    """

    def __init__(self, zip=0, short_name=None, long_name=None,
                 canton=None, _zip_type_number=None, _onrp=None):
        self.zip = zip
        self.short_name = short_name
        self.long_name = long_name
        self.canton = canton
        if _zip_type_number:
            self._zip_type_number = _zip_type_number
        self._onrp = _onrp

    # Two localities are equal if they have the same attributes
    def __eq__(self, other):
        return isinstance(other, Locality) \
                   and self.zip == other.zip \
                   and self.short_name == other.short_name \
                   and self.long_name == other.long_name \
                   and self.canton == other.canton \
                   and self._zip_type_number == other._zip_type_number \
            and self._onrp == other._onrp

    # Recommended resource: http://stackoverflow.com/a/2626364/753136
    def __repr__(self):
        return "Locality(zip=%r, short_name=%r, long_name=%r, canton=%r, " \
               "_zip_type_number=%r, _onrp=%r)" % (self.zip, self.short_name,
                                                   self.long_name, self.canton,
                                                   self._zip_type_number,
                                                   self._onrp)

    def __str__(self):
        # TODO May be improved
        return self.__repr__()

    # Primary (most important) fields

    zip = 0  # Warning: shadows the zip() built-in function
    """ZIP code"""

    short_name = None
    """Short name (18 chars)"""

    long_name = None
    """Long name (27 chars). Official designation.
    Must be preferred to `short_name`."""

    canton = None
    """Canton. Official 2-letter uppercased abbreviation as used for
    vehicles number plates.

    .. note::
        FL is used for Liechtenstein addresses, and so is DE for 8238 Büsingen
        and IT for 66911 Campione.
        These are the only exceptions."""

    zip_type = None
    """A ZIP code might be only available for PO boxes, physical adresses,
    both of these, an entreprise, or dedicated for mail sorting.

    .. seealso:: :py:meth:`chzip.common.ZipType`"""

    # Secondary (least important) fields

    _onrp = 0
    """ONRP (Post order number) is an internal code that uniquely identifies any
    ZIP in Switzerland."""

    _zip_type_number = property()
    """A number telling the kind of ZIP code. This is internal stuff, see
    `_zip_type` for normal use."""

    # Where the value of the _zip_type_number property goes
    __zip_type_number = None

    @_zip_type_number.getter
    def _zip_type_number(self):
        return self.__zip_type_number

    @_zip_type_number.setter
    def _zip_type_number(self, value):
        self.__zip_type_number = value
        self.zip_type = ZipType._to_type(value)


# TODO Use the Enum class with Python 3.4

class ZipType:
    """The ZipType tells if A ZIP code might be only available for PO boxes,
    physical adresses, both of these, an entreprise, or dedicated for mail
    sorting."""

    HOMES_AND_PO_BOXES = 10
    """Homes and PO boxes"""

    HOMES_ONLY = 20
    """Homes only"""

    PO_BOXES_ONLY = 30
    """PO boxes only"""

    ENTERPRISES = 40
    """Enterprises"""

    INTERNAL = 80
    """For mail sorting by the post offices. Only used by the Post!"""

    @staticmethod
    def okay_for_stuff_delivery(zip_type):
        """Returns true if the specified ZIP type is appropriate to deliver
        merchandise.
        Returns False for a "PO boxes only" or "internal"
        ZIP code."""
        return zip_type is not ZipType.PO_BOXES_ONLY \
            and zip_type is not ZipType.INTERNAL

    # Mapping between ZIP type numbers and zip types Enum values
    # TODO This is simple but reflection could be used instead
    # Is not done because Python 3.4 will provide Enums out-of-the-box.

    _mapping = {
        10: HOMES_AND_PO_BOXES,
        20: HOMES_ONLY,
        30: PO_BOXES_ONLY,
        40: ENTERPRISES,
        80: INTERNAL
    }

    # Convert number to type. Is used in de-serialization.
    @staticmethod
    def _to_type(number):
        try:
            return ZipType._mapping[number]
        except KeyError as e:
            print('The ZIP type number %d does not exist.' % (number,))
