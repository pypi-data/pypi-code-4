# -*- coding: utf-8 -*-
"""
PyChanDownloader scans the page of a thread and downloads images.

The scanner checks that images have not already been downloaded for the given thread and chanel, but can also check that the image is unique over the whole registry thourgh an MD5 hash comparison.

Dependencies :

* BeautifulSoup >= 3.x (tested with version 3.0.8 )
"""
__all__ = ['parser', 'cli']
__title__ = "PyChanDownloader"
__version__ = "0.0.6"

class ChanBackendError(Exception):
    """
    This class throws exception for errors occuring in ChanDownloader
    """
    pass
