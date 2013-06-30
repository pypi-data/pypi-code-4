"""This package contains a set of utilites for building RESTful services.

This package is powered by werkzeug. In fact, most of the "functionality" of
this package is simply a wrapper around or extension of werkzeug features.
"""

try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
