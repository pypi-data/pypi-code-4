# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
""" This is a module only to do a wild import of all pyojo modules.
"""
import os
import sys

import pyojo
from pyojo.func import pretty

import pyojo.js as js
from pyojo.js import dojo
from pyojo.js import dijit

from pyojo.js.dojo import store

from pyojo.js.dijit import layout
from pyojo.js.dijit import form
from pyojo.js.dijit.icons import ICON, ICON_EDIT

__all__ = ["os", 
           "sys", 
           "pyojo", 
           "pretty", 
           "js",
           "dojo",
           "dijit",
           "store",
           "layout",
           "form",
           "ICON",
           "ICON_EDIT"]