"""A Simple Mail Queue Backend for Django

A Simple Mail Queue Backend for Django that protects against temporary
smtp server failures.

"""
__version_raw__ = ['0','1','0']
__version__ = VERSION = '.'.join(__version_raw__)
def get_version():# pragma: no cover
    return VERSION