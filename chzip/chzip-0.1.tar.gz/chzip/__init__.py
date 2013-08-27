#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""The `chzip` package provides a quick and easy Python interface
to look for zip codes and cities in Switzerland.

.. moduleauthor:: Mathieu Clément <mathieu.clement@freebourg.org>"""

__author__ = 'Mathieu Clément'

# Make functions and other things defined in this file accessible
# from . import *

# import os
# def include(filename):
#     f = os.path.join(os.path.dirname(__file__), filename)
#     if os.path.exists(f):
#         execfile(f)
#     else:
#         raise Exception(str(f) + ' can NOT be opened.')


import os
from warnings import warn

from chzip.ch_zip import ChZip
from chzip.common import Locality, ZipType
import chzip.zipcodes

# TODO Remove static methods and use constructor parameter from ChZip
# TODO Update documentation acccordingly

def download_and_unpack_all(download_dir=chzip.ch_zip._default_res_dir()):
    """download_and_unpack_all(download_dir='chzip/install/path/res')
    
    Download and unpack all (available) resources.

    Use :py:meth:`upgrade_all` if you don't want to re-download
    everything but only update what has changed.
    This method begins by erasing previous versions in the download
    directory.

    :param str download_dir: Download directory (with write permissions)

    .. :raises: :py:meth:`chzip.exceptions.DownloadException`, 
    ..          :py:meth:`chzip.exceptions.UnpackingException`

    .. note::
        You are very unlikely to ever call this method, except if you included
        chzip directly in your project, without installing it.

    """
    try:
        os.makedirs(download_dir)
    except:
        print(download_dir + ' already exists. upgrade_all() may be what you are looking for.')
    chzip.zipcodes.Downloader.download_and_unpack(
        chzip.zipcodes.Downloader(), download_dir)

def upgrade_all(download_dir=chzip.ch_zip._default_res_dir(), force=False):
    """upgrade_all(download_dir='chzip/install/path/res', force=False)
    
    Upgrade all resources.

    Unlike `download_all` resources files that have not been changed will
    not be erased and downloaded again.
    Also, it takes care of keeping old (working) files if the upgrade fails
    (network error, bad download, corrupted file, error when unpacking,
    etc.)

    It is recommended to run this method regularly to get up-to-date data.

    :param str download_dir: Download directory (with write permission)
                             containing previous versions of the resource
                             files.
    :param bool force: Force upgrade, even if files are up-to-date.

    .. :raises: UpgradeException, DownloadException, UnpackingException
    """
    chzip.zipcodes.Downloader.upgrade_and_unpack(
        chzip.zipcodes.Downloader(), download_dir, force)

from . import *
