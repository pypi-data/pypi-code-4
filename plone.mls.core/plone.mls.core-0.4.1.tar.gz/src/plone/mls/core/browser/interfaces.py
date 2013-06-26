# -*- coding: utf-8 -*-
"""Interface definitions."""

# zope imports
from plone.theme.interfaces import IDefaultPloneLayer


class IMLSSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""
