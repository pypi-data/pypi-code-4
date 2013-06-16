import sys

__all__ = ['Enum', 'IntEnum']

pyver = float('%s.%s' % sys.version_info[:2])

if pyver < 3:
    from enum.py2_enum import _RouteClassAttributeToGetattr, _is_dunder, _is_sunder, _make_class_unpicklable
    from enum.py2_enum import _EnumDict, EnumMeta, Enum, IntEnum
else:
    from enum.py3_enum import _RouteClassAttributeToGetattr, _is_dunder, _is_sunder, _make_class_unpicklable
    from enum.py3_enum import _EnumDict, EnumMeta, Enum, IntEnum
