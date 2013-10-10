
""" ``comp`` module.
"""

import sys


PY_MAJOR = sys.version_info[0]
PY_MINOR = sys.version_info[1]
PY2 = PY_MAJOR == 2
PY3 = PY_MAJOR >= 3


if PY3:  # pragma: nocover
    iterkeys = lambda d: d.keys()
    iteritems = lambda d: d.items()
    copyitems = lambda d: list(d.items())
    regex_pattern = (str,)
else:  # pragma: nocover
    iterkeys = lambda d: d.iterkeys()
    iteritems = lambda d: d.iteritems()
    copyitems = lambda d: d.items()
    regex_pattern = (str, unicode)


from gettext import NullTranslations
null_translations = NullTranslations()

if PY3:  # pragma: nocover
    ref_gettext = lambda t: t.gettext
else:  # pragma: nocover
    ref_gettext = lambda t: t.ugettext


def ref_getter(model):
    # if model is a dict
    if hasattr(model, '__iter__'):
        return type(model).__getitem__
    else:
        return getattr


if PY3 and PY_MINOR >= 3:  # pragma: nocover
    from decimal import Decimal
else:  # pragma: nocover
    try:
        from cdecimal import Decimal  # noqa
    except ImportError:
        from decimal import Decimal  # noqa


if PY2 and PY_MINOR == 4:  # pragma: nocover
    __import__ = __import__
else:  # pragma: nocover
    # perform absolute import
    __saved_import__ = __import__
    __import__ = lambda n, g=None, l=None, f=None: \
        __saved_import__(n, g, l, f, 0)
