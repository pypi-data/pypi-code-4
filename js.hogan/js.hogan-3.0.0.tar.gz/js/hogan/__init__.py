#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# js.hogan
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-05-27

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from fanstatic import Library, Resource

__author__ = "Manuel Vázquez Acosta <mva.led@gmail.com>"
__date__ = "Mon May 27 20:44:48 2013"


lib = Library('js.hogan', '.')
hogan = Resource(lib, 'js/hogan-3.0.0.js',
                 minified='js/hogan-3.0.0.min.js')
