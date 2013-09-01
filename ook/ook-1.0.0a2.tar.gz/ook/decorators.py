"""Decorators."""

from ook.util import Version

MIN_VERSION = Version(2.6)
MAX_VERSION = Version("inf")
PY_VERSION = Version()


def patch(scope, *args, **kwargs):
    """Monkeypatch a function or method for specified Python versions."""
    versions = tuple(map(Version, args))
    min_version = Version(kwargs.get("min", MIN_VERSION))
    max_version = Version(kwargs.get("max", MAX_VERSION))
    matches = (PY_VERSION in versions)
    unspecified = (not versions)
    in_range = (min_version <= PY_VERSION <= max_version)
    if (matches or unspecified) and in_range:

        def decorator(func):
            """Monkeypatch `scope.func`."""
            setattr(scope, func.__name__, func)
            return func

    else:
        decorator = lambda x: x

    return decorator
