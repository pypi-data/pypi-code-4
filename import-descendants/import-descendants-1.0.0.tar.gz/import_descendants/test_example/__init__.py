# -*- coding: utf-8 -*-
# (c) 2013 Bright Interactive Limited. All rights reserved.
# http://www.bright-interactive.com | info@bright-interactive.com
from import_descendants import import_descendants
import sys

this_module = sys.modules[__name__]
import_descendants(this_module, globals(), locals())
