"""Utilities."""

_booleans = {
    'yes': True, 'true': True, 'on': True, '1': True,
    'no': False, 'false': False, 'off': False, '0': False,
    }


def boolean(setting):
    try:
        return _booleans[str(setting).lower()]
    except KeyError:
        raise ValueError('Invalid Boolean setting: %r' % (setting,))
