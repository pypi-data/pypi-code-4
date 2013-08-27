#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join, dirname
import chzip.common
import chzip.zipcodes


DEFAULT_RESOURCES_DIR = chzip.common.Downloader.DEFAULT_RES_DIRNAME
"""The name of the directory that will contain the downloaded files.
It is NOT the absolute path of that directory."""


def _default_res_dir():
    return join(dirname(__file__), DEFAULT_RESOURCES_DIR)


class ChZip:
    """The main entrance for the `chzip` library."""

    def __init__(self, resource_dir=_default_res_dir()):
        """__init__(resource_dir='chzip/install/path/res')

        :param str resource_dir: Resource directory
        """

        self.resource_dir = resource_dir

    def find(self,
             zip=None,
             # Exact matches
             long_name=None, short_name=None,
             # "contains" or SQL LIKE expression
             # long_name_like=None, short_name_like=None,
             canton=None, onrp=None):
        """Refer to :ref:`Usage`."""
#        if long_name_like or short_name_like:
#            raise NotImplementedError('Sorry, the LIKE feature is not '
#                                      'implemented yet')

        db = chzip.zipcodes.ZipCodesDatabase(
            join(self.resource_dir,
                 chzip.zipcodes.ZipCodesDatabase.DEFAULT_FILENAME))

        dic = {'zip': zip, 'long_name': long_name, 'short_name': short_name,
               'canton': canton, 'onrp': onrp}

        localities = db.query(dic)
        del db
        return localities

    def long_names(self, *args, **kwargs):
        """Is the same as :py:meth:`find` but returns a list of long names 
        instead."""
        results = self.find(*args, **kwargs)
        names = []
        for result in results:
            names.append(result.long_name)

        return names

    def all(self):
        db = chzip.zipcodes.ZipCodesDatabase(
            join(self.resource_dir,
                 chzip.zipcodes.ZipCodesDatabase.DEFAULT_FILENAME))
        localities = db.all()
        del db
        return localities
