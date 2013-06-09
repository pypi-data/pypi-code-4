# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo.examples                                  Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
import pyojo.util

def GET(request):
    return pyojo.util.TestPage().html()