# -*- coding: utf-8 -*-

from dolmen.app.layout.interfaces import IDisplayView
from dolmen.app.layout.skin import *
from dolmen.app.layout.menus import *
from dolmen.app.layout.master import *
from dolmen.app.layout.models import *
from dolmen.app.layout.viewlets import *

# APIs
from zope.interface import moduleProvides
from dolmen.app.layout.interfaces import IDolmenLayoutAPI

moduleProvides(IDolmenLayoutAPI)
__all__ = list(IDolmenLayoutAPI) + ['IDisplayView']
