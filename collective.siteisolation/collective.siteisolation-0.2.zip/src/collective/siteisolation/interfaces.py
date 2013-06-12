# -*- coding: utf-8 -*-
from zope.interface import Interface


class IIsolatedObject(Interface):
    """
    Marker interface for object to isolate from their siblings
    """


class IPotentialBadRequest(Interface):
    """
    Marker interface for a request to isolate traversed object from the
    IIsolatedObject siblings
    """


class IObjectToIsolate(Interface):
    """
    Marker interface for object(s) in root that you cannot acquire
    while traversing
    """
