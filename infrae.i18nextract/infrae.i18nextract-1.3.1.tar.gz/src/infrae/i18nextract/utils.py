# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: utils.py 50858 2013-05-23 11:19:23Z sylvain $

import os


def load_products(products):
    """Load Zope products: their import path is incomplete.
    """
    import Products
    Products.__path__.extend(
        map(lambda p: os.path.abspath(p),
            filter(lambda p: os.path.exists(p) and os.path.isdir(p),
                   products)))
