# -*- coding: utf-8 -*-
"""
TailorDev Contact

A simple contact form for your django projects.
"""

__version__ = '0.4.0'


def get_version():
    return ".".join(__version__.split('.')[:2])


def get_release():
    return __version__
