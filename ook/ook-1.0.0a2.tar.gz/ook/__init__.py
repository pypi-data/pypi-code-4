"""Python-version-sensitive monkeypatching."""

from ook.decorators import patch
from ook._version import __version__

__all__ = (
    "patch",
)
